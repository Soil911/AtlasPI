"""One-shot targeted boundary fixes identified by the v6.7.0 audit.

Context (v6.7.1): the boundary-quality audit
(`docs/boundary_audit_2026_04_15.md`) surfaced a handful of
individually-broken entities that fall outside the shared-polygon cluster
(those are handled by `cleanup_shared_polygons.py`). This module applies
targeted one-shot fixes:

  1. NULL boundaries on confirmed entities:
     - Pechenegs [id=325]
     - Nogai Ordasy / Nogai Horde [id=338]
     Both are steppe confederations that existed but had no polygon at
     all — we generate a deterministic name-seeded boundary so the
     entity is at least renderable; `status` stays as it was.

  2. Cities with country-scale polygons (aourednik false positive):
     - İstanbul [id=3] — had "Phrygians" polygon (~462,000 km²)
     - Igbo-Ukwu [id=562] — had "Mandes" polygon (~4,329,812 km²)
     Both are CITY entities; we replace with a tight city-radius polygon
     generated from the known coordinates. Sources are preserved.

  3. Small polities carrying the USA polygon:
     - ᏣᎳᎩ / Cherokee [id=218] — confederation, Appalachian range
     - Seminole / Ikaniuksalgi [id=545] — confederation, Florida
     Both had `iso_a3=USA` on NE match which pulled the entire USA
     polygon. We replace with entity-type-radius generated polygons.

  4. Placeholder 5-point bounding boxes (flagged in audit):
     - Republic of Pirates [524]
     - Kurland Colonies [525]
     - Poverty Point Civilization [528]
     - Kingdom of Quito [530]
     - Wanka / Huanca Confederation [531]
     Rather than regenerate geometry we add explicit ethical_notes
     flagging the box as a placeholder, and demote `status` to
     `uncertain` if it was `confirmed` (since the boundary was part of
     the confirmation evidence). Keep the box so the UI still renders
     something; transparency over visual absence.

ETHICS: each mutation records its rationale. Aourednik/NE provenance
fields are cleared for repair class 1-3; class 4 keeps geometry but
annotates it. All `confidence_score` values are capped at the
APPROX_CONFIDENCE (0.4) floor used by ETHICS-004.

Idempotent: re-runs produce zero further mutations once applied.

Usage:
    python -m src.ingestion.fix_bad_boundaries_v671 --dry-run
    python -m src.ingestion.fix_bad_boundaries_v671 --apply
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import GeoEntity
from src.ingestion.boundary_generator import name_seeded_boundary

logger = logging.getLogger(__name__)

ENTITIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"

APPROX_CONFIDENCE = 0.4

# Small-radius city polygon: used for entities that are actually cities
# but ended up with country-scale polygons (Istanbul, Igbo-Ukwu).
CITY_RADIUS_KM = 20.0

# Steppe confederation radius: used for Pechenegs / Nogai Horde.
# Historically these polities controlled corridors ~800-1200 km long,
# so a 700 km radius is a conservative centre-of-mass proxy.
STEPPE_RADIUS_KM = 700.0

# Native confederation radius: used for Cherokee (Appalachian homelands
# ~290,000 km²) and Seminole (Florida, ~170,000 km²). A 250 km radius
# covers ~196,000 km² — inside the historical range of both.
NATIVE_CONFEDERATION_RADIUS_KM = 250.0

PLACEHOLDER_BOX_NOTE = (
    "[v6.7.1] boundary_geojson è un placeholder rettangolare, non il contorno "
    "reale dell'entità. L'estensione effettiva è incerta e richiede revisione "
    "storiografica. Vedi docs/boundary_audit_2026_04_15.md."
)


# ─── Fix specifications ─────────────────────────────────────────────────────


@dataclass
class EntityFix:
    """Declarative spec for a single entity-level repair."""
    entity_id: int
    reason: str
    regenerate_with_radius_km: float | None = None
    demote_status_to: str | None = None
    append_note: str | None = None
    clear_aourednik: bool = True
    clear_ne: bool = True
    keep_geometry: bool = False
    # Backfill capital coords for entities where they're NULL. Only used
    # if the entity currently has no capital_lat/lon — never overwrites
    # existing data.
    backfill_capital_lat: float | None = None
    backfill_capital_lon: float | None = None
    backfill_capital_name: str | None = None


FIXES: list[EntityFix] = [
    # 1. NULL boundaries — backfill steppe-centre capitals and regenerate
    EntityFix(
        entity_id=325,
        reason="NULL boundary + NULL capital — Pechenegs, Pontic-Caspian steppe",
        regenerate_with_radius_km=STEPPE_RADIUS_KM,
        # Approximate centre of Pecheneg control (Dnieper-Don interfluve)
        # in the 9th-11th century. Source: Róna-Tas, "Hungarians and
        # Europe in the Early Middle Ages" (1999).
        backfill_capital_lat=47.5,
        backfill_capital_lon=34.5,
        backfill_capital_name="(stepa pontica)",
    ),
    EntityFix(
        entity_id=338,
        reason="NULL boundary + NULL capital — Nogai Horde, Volga-Ural steppe",
        regenerate_with_radius_km=STEPPE_RADIUS_KM,
        # Saray-Jük on the Ural river — historical Nogai centre.
        # Source: Trepavlov, "The Formation and Early History of the
        # Manghit Yurt" (2001).
        backfill_capital_lat=47.5,
        backfill_capital_lon=51.5,
        backfill_capital_name="Saray-Jük",
    ),
    # 2. Cities with country-scale polygons
    EntityFix(
        entity_id=3,
        reason="City Istanbul had Phrygians (~462k km²) polygon; replace with city radius",
        regenerate_with_radius_km=CITY_RADIUS_KM,
    ),
    EntityFix(
        entity_id=562,
        reason="City Igbo-Ukwu had Mandes (~4.3M km²) polygon; replace with city radius",
        regenerate_with_radius_km=CITY_RADIUS_KM,
    ),
    # 3. Native confederations with USA polygon
    EntityFix(
        entity_id=218,
        reason="Cherokee confederation had full USA polygon; replace with Appalachian radius",
        regenerate_with_radius_km=NATIVE_CONFEDERATION_RADIUS_KM,
    ),
    EntityFix(
        entity_id=545,
        reason="Seminole confederation had full USA polygon; replace with Florida radius",
        regenerate_with_radius_km=NATIVE_CONFEDERATION_RADIUS_KM,
    ),
    # 4. Placeholder 5-point bounding boxes — keep geometry but annotate + demote
    EntityFix(
        entity_id=524,
        reason="Republic of Pirates: 5-point bbox is a placeholder, not real extent",
        keep_geometry=True,
        append_note=PLACEHOLDER_BOX_NOTE,
        demote_status_to="uncertain",
        clear_aourednik=False,
        clear_ne=False,
    ),
    EntityFix(
        entity_id=525,
        reason="Kurland Colonies: 5-point bbox is a placeholder",
        keep_geometry=True,
        append_note=PLACEHOLDER_BOX_NOTE,
        demote_status_to="uncertain",
        clear_aourednik=False,
        clear_ne=False,
    ),
    EntityFix(
        entity_id=528,
        reason="Poverty Point: 5-point bbox is a placeholder",
        keep_geometry=True,
        append_note=PLACEHOLDER_BOX_NOTE,
        demote_status_to="uncertain",
        clear_aourednik=False,
        clear_ne=False,
    ),
    EntityFix(
        entity_id=530,
        reason="Kingdom of Quito: 5-point bbox is a placeholder",
        keep_geometry=True,
        append_note=PLACEHOLDER_BOX_NOTE,
        demote_status_to="uncertain",
        clear_aourednik=False,
        clear_ne=False,
    ),
    EntityFix(
        entity_id=531,
        reason="Wanka/Huanca: 5-point bbox is a placeholder",
        keep_geometry=True,
        append_note=PLACEHOLDER_BOX_NOTE,
        demote_status_to="uncertain",
        clear_aourednik=False,
        clear_ne=False,
    ),
]


# ─── Core apply logic ───────────────────────────────────────────────────────


@dataclass
class FixStats:
    applied: int = 0
    skipped_not_found: list[int] = field(default_factory=list)
    skipped_no_capital: list[int] = field(default_factory=list)
    regenerated_geometry: int = 0
    annotated: int = 0
    demoted: int = 0
    db_committed: bool = False
    json_files_written: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "applied": self.applied,
            "skipped_not_found": list(self.skipped_not_found),
            "skipped_no_capital": list(self.skipped_no_capital),
            "regenerated_geometry": self.regenerated_geometry,
            "annotated": self.annotated,
            "demoted": self.demoted,
            "db_committed": self.db_committed,
            "json_files_written": list(self.json_files_written),
        }


def _append_ethical_note(entity: GeoEntity, note: str) -> None:
    """Append `note` to entity.ethical_notes idempotently (skip if already contains)."""
    cur = entity.ethical_notes or ""
    if note in cur:
        return
    entity.ethical_notes = (cur + "\n\n" + note).strip() if cur else note


def _apply_fix_to_entity(entity: GeoEntity, fix: EntityFix) -> bool:
    """Mutate `entity` in place per `fix`. Returns True on change."""
    changed = False

    # Backfill capital coords if entity lacks them and fix provides defaults.
    if (
        entity.capital_lat is None or entity.capital_lon is None
    ) and fix.backfill_capital_lat is not None and fix.backfill_capital_lon is not None:
        entity.capital_lat = fix.backfill_capital_lat
        entity.capital_lon = fix.backfill_capital_lon
        if fix.backfill_capital_name and not entity.capital_name:
            entity.capital_name = fix.backfill_capital_name
        changed = True

    if not fix.keep_geometry:
        if entity.capital_lat is None or entity.capital_lon is None:
            return False
        new_geom = name_seeded_boundary(
            name=entity.name_original or "",
            lat=float(entity.capital_lat),
            lon=float(entity.capital_lon),
            entity_type=entity.entity_type or "kingdom",
            radius_km=fix.regenerate_with_radius_km,
        )
        entity.boundary_geojson = json.dumps(new_geom)
        entity.boundary_source = "approximate_generated"
        changed = True

    if fix.clear_aourednik:
        if entity.boundary_aourednik_name or entity.boundary_aourednik_year:
            entity.boundary_aourednik_name = None
            entity.boundary_aourednik_year = None
            entity.boundary_aourednik_precision = None
            changed = True

    if fix.clear_ne:
        if entity.boundary_ne_iso_a3:
            entity.boundary_ne_iso_a3 = None
            changed = True

    if fix.append_note:
        pre = entity.ethical_notes or ""
        _append_ethical_note(entity, fix.append_note)
        if (entity.ethical_notes or "") != pre:
            changed = True

    if fix.demote_status_to and entity.status != fix.demote_status_to:
        # Only demote from stronger → weaker (confirmed -> uncertain)
        order = {"confirmed": 3, "uncertain": 2, "disputed": 1}
        cur_rank = order.get(entity.status or "", 0)
        new_rank = order.get(fix.demote_status_to, 0)
        if new_rank < cur_rank:
            entity.status = fix.demote_status_to
            changed = True

    if not fix.keep_geometry:
        if entity.confidence_score is None or entity.confidence_score > APPROX_CONFIDENCE:
            entity.confidence_score = APPROX_CONFIDENCE
            changed = True

    return changed


def _apply_json_side(
    by_id: dict[int, dict],
    fix_by_name: dict[str, tuple[EntityFix, dict]],
    dry_run: bool,
    stats: FixStats,
) -> None:
    """Walk batch_*.json files and propagate DB mutations.

    `fix_by_name` maps name_original -> (fix, pre-computed geojson or None).
    """
    if not ENTITIES_DIR.is_dir():
        logger.warning("Entities directory not found: %s", ENTITIES_DIR)
        return

    for json_file in sorted(ENTITIES_DIR.glob("batch_*.json")):
        try:
            with open(json_file, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            logger.warning("Skipping unreadable %s: %s", json_file.name, exc)
            continue

        container = (
            data["entities"]
            if isinstance(data, dict) and "entities" in data
            else data
        )
        if not isinstance(container, list):
            continue

        file_changed = False
        for entity in container:
            if not isinstance(entity, dict):
                continue
            name = entity.get("name_original")
            if not name or name not in fix_by_name:
                continue
            fix, new_geom = fix_by_name[name]

            # Backfill capital coords if fix provides them and JSON lacks
            if fix.backfill_capital_lat is not None and entity.get("capital_lat") is None:
                entity["capital_lat"] = fix.backfill_capital_lat
            if fix.backfill_capital_lon is not None and entity.get("capital_lon") is None:
                entity["capital_lon"] = fix.backfill_capital_lon
            if fix.backfill_capital_name and not entity.get("capital_name"):
                entity["capital_name"] = fix.backfill_capital_name

            if not fix.keep_geometry and new_geom is not None:
                entity["boundary_geojson"] = new_geom
                entity["boundary_source"] = "approximate_generated"
                entity["confidence_score"] = APPROX_CONFIDENCE

            if fix.clear_aourednik:
                entity.pop("boundary_aourednik_name", None)
                entity.pop("boundary_aourednik_year", None)
                entity.pop("boundary_aourednik_precision", None)

            if fix.clear_ne:
                entity.pop("boundary_ne_iso_a3", None)

            if fix.append_note:
                cur = entity.get("ethical_notes") or ""
                if fix.append_note not in cur:
                    entity["ethical_notes"] = (
                        (cur + "\n\n" + fix.append_note).strip()
                        if cur else fix.append_note
                    )

            if fix.demote_status_to:
                order = {"confirmed": 3, "uncertain": 2, "disputed": 1}
                cur_status = entity.get("status")
                if (
                    order.get(cur_status or "", 0)
                    > order.get(fix.demote_status_to, 0)
                ):
                    entity["status"] = fix.demote_status_to

            file_changed = True

        if file_changed and not dry_run:
            with open(json_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            stats.json_files_written.append(json_file.name)
            logger.info("Wrote v6.7.1 fixes into %s", json_file.name)


def run_fixes(*, dry_run: bool = True, session: Session | None = None) -> dict:
    """Apply every EntityFix in FIXES to DB + JSON."""
    stats = FixStats()
    own_session = session is None
    db: Session = session if session is not None else SessionLocal()

    try:
        fix_by_name: dict[str, tuple[EntityFix, dict | None]] = {}
        for fix in FIXES:
            row = db.query(GeoEntity).filter(GeoEntity.id == fix.entity_id).first()
            if row is None:
                stats.skipped_not_found.append(fix.entity_id)
                logger.warning("Entity id=%d not found; skipping (%s)",
                               fix.entity_id, fix.reason)
                continue
            # Resolve effective capital coords (either existing or backfill).
            eff_lat = row.capital_lat if row.capital_lat is not None else fix.backfill_capital_lat
            eff_lon = row.capital_lon if row.capital_lon is not None else fix.backfill_capital_lon

            if not fix.keep_geometry and (eff_lat is None or eff_lon is None):
                stats.skipped_no_capital.append(fix.entity_id)
                logger.warning(
                    "Entity id=%d %r has no capital coords and no backfill; skipping",
                    row.id, row.name_original,
                )
                continue

            # Pre-compute the replacement geometry for JSON side
            pre_geom: dict | None = None
            if not fix.keep_geometry:
                pre_geom = name_seeded_boundary(
                    name=row.name_original or "",
                    lat=float(eff_lat),
                    lon=float(eff_lon),
                    entity_type=row.entity_type or "kingdom",
                    radius_km=fix.regenerate_with_radius_km,
                )
            fix_by_name[row.name_original] = (fix, pre_geom)

            changed = _apply_fix_to_entity(row, fix)
            if changed:
                stats.applied += 1
                if not fix.keep_geometry:
                    stats.regenerated_geometry += 1
                if fix.append_note:
                    stats.annotated += 1
                if fix.demote_status_to:
                    stats.demoted += 1
                logger.info(
                    "id=%d %r: %s",
                    row.id, row.name_original, fix.reason,
                )

        if not dry_run:
            db.commit()
            stats.db_committed = True
            logger.info("DB committed: %d fixes applied", stats.applied)
        else:
            db.rollback()
            logger.info("DRY-RUN: %d fixes would apply; rolled back", stats.applied)

        # Build id -> entity map for JSON scanning
        by_id: dict[int, dict] = {}
        _apply_json_side(by_id, fix_by_name, dry_run=dry_run, stats=stats)

        return stats.as_dict()
    finally:
        if own_session:
            db.close()


def main() -> int:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true",
                       help="Compute without writing (default).")
    group.add_argument("--apply", action="store_true",
                       help="Perform mutations.")
    args = parser.parse_args()

    dry_run = not args.apply

    result = run_fixes(dry_run=dry_run)

    print(f"\n=== fix_bad_boundaries_v671 (dry_run={dry_run}) ===\n")
    for k, v in result.items():
        print(f"  {k:<25} {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
