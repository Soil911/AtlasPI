"""Cleanup: repair the 133 Natural Earth matches where the entity's
capital falls OUTSIDE the assigned polygon.

ETHICS-006 — the fuzzy matcher in `boundary_match.py` produced ~133
catastrophically wrong matches (e.g. Garenganze -> Russia, Primer
Imperio Mexicano -> Belgium, Mapuche -> Australia). The fix in the
matcher itself is in place; this script cleans the already-persisted
data, both in the running DB and in the batch JSON files.

Strategy for each wrong entry:
  1. Generate an approximate polygon around the capital using
     `boundary_generator.name_seeded_boundary()` — deterministic
     shape derived from the entity's name and type.
  2. Reset `boundary_source = "approximate_generated"`.
  3. Clear `boundary_ne_iso_a3`, `boundary_aourednik_name`,
     `boundary_aourednik_year`, `boundary_aourednik_precision`.
  4. Cap `confidence_score` at 0.4 (ETHICS-004 standard for
     generated boundaries).

Safety rails:
  - DRY-RUN by default. Pass `--apply` to mutate.
  - Refuses to touch entities without `capital_lat` / `capital_lon`
    (we cannot generate a polygon without a center).
  - Refuses to downgrade a `historical_map` or `aourednik` record
    (those are trusted sources; only `natural_earth` is in scope).

Run:
    python -m src.ingestion.cleanup_displaced_ne_matches --dry-run
    python -m src.ingestion.cleanup_displaced_ne_matches --apply
    python -m src.ingestion.cleanup_displaced_ne_matches --apply --json-only
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import GeoEntity
from src.ingestion.boundary_generator import name_seeded_boundary

logger = logging.getLogger(__name__)

ENTITIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"

APPROX_CONFIDENCE = 0.4  # ETHICS-004
APPROX_SOURCE = "approximate_generated"


@dataclass
class CleanupStats:
    inspected: int = 0
    displaced: int = 0  # capital outside polygon
    fixed: int = 0
    skipped_no_capital: int = 0
    skipped_non_ne: int = 0
    skipped_already_clean: int = 0
    json_entities_fixed: int = 0
    json_files_written: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["json_files_written"] = list(self.json_files_written)
        return d


def _capital_in_polygon(geom: dict, lat: float, lon: float) -> bool:
    from shapely.geometry import Point, shape
    try:
        return shape(geom).contains(Point(float(lon), float(lat)))
    except Exception:
        return False


def _needs_repair(entity_dict: dict) -> bool:
    """True if the batch entity has NE source but its capital is not inside
    the polygon. Entities without capital are out of scope (we can't fix them)."""
    if entity_dict.get("boundary_source") != "natural_earth":
        return False
    geom = entity_dict.get("boundary_geojson")
    if not isinstance(geom, dict):
        return False
    lat = entity_dict.get("capital_lat")
    lon = entity_dict.get("capital_lon")
    if lat is None or lon is None:
        return False
    return not _capital_in_polygon(geom, lat, lon)


def _repair_entity_dict(entity: dict) -> bool:
    """Mutate `entity` in place: replace boundary + provenance. Returns True on change."""
    lat = entity.get("capital_lat")
    lon = entity.get("capital_lon")
    if lat is None or lon is None:
        return False
    new_geom = name_seeded_boundary(
        name=entity.get("name_original") or "",
        lat=float(lat),
        lon=float(lon),
        entity_type=entity.get("entity_type") or "kingdom",
    )
    entity["boundary_geojson"] = new_geom
    entity["boundary_source"] = APPROX_SOURCE
    # Clear Natural Earth / aourednik provenance — they're invalid now.
    entity["boundary_ne_iso_a3"] = None
    entity["boundary_aourednik_name"] = None
    entity["boundary_aourednik_year"] = None
    entity["boundary_aourednik_precision"] = None
    cur = entity.get("confidence_score")
    if isinstance(cur, (int, float)) and cur > APPROX_CONFIDENCE:
        entity["confidence_score"] = APPROX_CONFIDENCE
    return True


# ─── JSON side ──────────────────────────────────────────────────────────────

def _cleanup_batch_jsons(dry_run: bool) -> tuple[CleanupStats, dict[str, dict]]:
    """Walk every batch_*.json file and repair displaced entries in place.

    Returns (stats, repaired_index) where repaired_index is
    {name_original: entity_dict} for all fixed entities — so the DB side
    can re-use the generated polygon.
    """
    stats = CleanupStats()
    repaired_by_name: dict[str, dict] = {}

    for json_file in sorted(ENTITIES_DIR.glob("batch_*.json")):
        with open(json_file, encoding="utf-8") as fh:
            data = json.load(fh)
        container = data["entities"] if isinstance(data, dict) and "entities" in data else data
        if not isinstance(container, list):
            continue

        file_changed = False
        for entity in container:
            if not isinstance(entity, dict):
                continue
            stats.inspected += 1
            if _needs_repair(entity):
                stats.displaced += 1
                if dry_run:
                    # Peek at what WOULD be written, but don't persist.
                    preview = dict(entity)
                    _repair_entity_dict(preview)
                    repaired_by_name[entity.get("name_original", "")] = preview
                    stats.json_entities_fixed += 1
                else:
                    if _repair_entity_dict(entity):
                        repaired_by_name[entity.get("name_original", "")] = entity
                        stats.json_entities_fixed += 1
                        file_changed = True

        if file_changed and not dry_run:
            with open(json_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            stats.json_files_written.append(json_file.name)
            logger.info("Wrote %d fixes into %s", stats.json_entities_fixed, json_file.name)

    return stats, repaired_by_name


# ─── DB side ────────────────────────────────────────────────────────────────

def _cleanup_db(
    session: Session, repaired_by_name: dict[str, dict], dry_run: bool
) -> CleanupStats:
    """Apply the same repair to the live DB.

    The DB may hold rows still sourced from an earlier matcher run. We
    re-verify each row against the capital-in-polygon rule and — when
    displaced — overwrite with the generated polygon already computed
    JSON-side (for consistency), or compute one fresh if the JSON didn't
    see this entity.
    """
    stats = CleanupStats()

    rows = (
        session.query(GeoEntity)
        .filter(GeoEntity.boundary_source == "natural_earth")
        .all()
    )
    for row in rows:
        stats.inspected += 1
        geom_str = row.boundary_geojson
        if not geom_str:
            continue
        try:
            geom = json.loads(geom_str)
        except (ValueError, TypeError):
            continue
        if row.capital_lat is None or row.capital_lon is None:
            stats.skipped_no_capital += 1
            continue
        if _capital_in_polygon(geom, row.capital_lat, row.capital_lon):
            stats.skipped_already_clean += 1
            continue

        stats.displaced += 1
        pre_baked = repaired_by_name.get(row.name_original)
        if pre_baked and pre_baked.get("boundary_geojson"):
            new_geom = pre_baked["boundary_geojson"]
        else:
            new_geom = name_seeded_boundary(
                name=row.name_original or "",
                lat=float(row.capital_lat),
                lon=float(row.capital_lon),
                entity_type=row.entity_type or "kingdom",
            )

        if not dry_run:
            row.boundary_geojson = json.dumps(new_geom)
            row.boundary_source = APPROX_SOURCE
            row.boundary_ne_iso_a3 = None
            row.boundary_aourednik_name = None
            row.boundary_aourednik_year = None
            row.boundary_aourednik_precision = None
            if row.confidence_score and row.confidence_score > APPROX_CONFIDENCE:
                row.confidence_score = APPROX_CONFIDENCE
        stats.fixed += 1

    if not dry_run and stats.fixed > 0:
        session.commit()
        logger.info("DB cleanup: committed %d displaced fixes", stats.fixed)
    elif dry_run:
        logger.info("DB cleanup DRY-RUN: would fix %d displaced rows", stats.fixed)
        session.rollback()

    return stats


# ─── Entrypoint ─────────────────────────────────────────────────────────────

def run_cleanup(
    *,
    dry_run: bool,
    json_only: bool = False,
    db_only: bool = False,
    session: Session | None = None,
) -> dict:
    """Run the cleanup. Returns a flat dict of combined stats."""
    json_stats = CleanupStats()
    db_stats = CleanupStats()
    repaired_by_name: dict[str, dict] = {}

    if not db_only:
        json_stats, repaired_by_name = _cleanup_batch_jsons(dry_run=dry_run)

    if not json_only:
        own = session is None
        db: Session = session if session is not None else SessionLocal()
        try:
            db_stats = _cleanup_db(db, repaired_by_name, dry_run=dry_run)
        finally:
            if own:
                db.close()

    return {
        "json": json_stats.as_dict(),
        "db": db_stats.as_dict(),
        "dry_run": dry_run,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="Compute without writing.")
    group.add_argument("--apply", action="store_true", help="Perform mutations.")
    parser.add_argument("--json-only", action="store_true", help="Only touch batch JSONs.")
    parser.add_argument("--db-only", action="store_true", help="Only touch the running DB.")
    args = parser.parse_args()

    dry_run = not args.apply  # defaults to dry-run for safety

    stats = run_cleanup(
        dry_run=dry_run, json_only=args.json_only, db_only=args.db_only,
    )

    print("\n=== ETHICS-006 cleanup stats ===")
    print(f"  dry_run: {stats['dry_run']}")
    print("  [JSON side]")
    for k, v in stats["json"].items():
        print(f"    {k:30s}  {v}")
    print("  [DB side]")
    for k, v in stats["db"].items():
        print(f"    {k:30s}  {v}")


if __name__ == "__main__":
    main()
