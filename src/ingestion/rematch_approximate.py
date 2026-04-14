"""Conservative re-matching of entities whose boundary is approximate_generated.

Context (v6.2): after ETHICS-006 rejected 133 displaced Natural Earth fuzzy
matches in v6.1.2 (Garenganze->Russia, CSA->Italy, Mapuche->Australia, ...),
~209 entities fell back to boundary_source='approximate_generated'. Some of
those entities might have a valid match via *stronger* strategies that the
v6.1.2 audit never retried:

  - NE ISO hint match (iso_a3 field on the AtlasPI entity, if present)
  - NE exact_name match (with the ETHICS-006 capital-in-polygon guard)
  - aourednik historical-basemaps match (year-bounded, capital-in-polygon
    fallback native to the matcher — geographically conservative by design)

Crucially, this module does **not** retry the fuzzy NE strategy that caused
ETHICS-006. Re-enabling it — even with the new centroid-distance guard —
would re-open the door to the pattern-matching-on-generic-tokens class of
bug that ETHICS-006 documented. Conservative = strong strategies only.

Idempotent: re-running produces zero upgrades once the DB is stable. Safe
to call manually from the runbook:

    python -m src.ingestion.rematch_approximate --dry-run
    python -m src.ingestion.rematch_approximate

ETHICS-003: disputed-status entities keep their confidence <= 0.70 cap on
write, identical to the enrichment-time behaviour.
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
from src.db.models import GeoEntity, NameVariant
from src.ingestion.aourednik_match import (
    PRECISION_CONFIDENCE,
    list_snapshots,
    match_entity_aourednik,
)
from src.ingestion.boundary_match import (
    _capital_distance_to_polygon_km,
    _capital_in_geojson,
    _try_exact_name_match,
    _try_iso_match,
)

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
NE_PROCESSED_JSON = ROOT_DIR / "data" / "processed" / "natural_earth_boundaries.json"
ENTITIES_DIR = ROOT_DIR / "data" / "entities"

DISPUTED_CONFIDENCE_CAP = 0.70  # ETHICS-003

# ETHICS-006 v6.2: in re-match-conservativo accettiamo SOLO strategie che
# provano un'identita' nominale tra l'entita' e la feature aourednik.
# Escludiamo esplicitamente:
#   - capital_in_polygon / capital_near_centroid: assegnano il poligono
#     del suzerain o del contenitore, non dell'entita' stessa
#     (es. Republica Ragusina -> Ottoman Empire in 1600: la capitale
#     Dubrovnik e' davvero dentro al poligono ottomano, ma Dubrovnik
#     non e' l'Impero Ottomano).
#   - subjecto / partof: simili — semantica di appartenenza, non identita'.
# Un match geografico-ma-non-nominale e' peggio di un approximate_generated
# esplicitamente marcato come tale: silenzia l'incertezza sotto una
# provenance "aourednik" che l'utente assumerebbe piu' autorevole.
AOUREDNIK_ACCEPTED_STRATEGIES = {"exact_name", "fuzzy_name"}

# ETHICS-006 v6.2: tolleranza geografica per exact_name match aourednik.
# Il matcher upstream non controlla che la capitale sia dentro al poligono,
# e i poligoni storici aourednik hanno digitizzazione meno precisa di NE.
# Entita' come "Konungariket Sverige" -> "Sweden" hanno la capitale 0.4 km
# fuori dal poligono (Stoccolma sul bordo costiero): un guard strict
# rigetterebbe match perfettamente validi. D'altra parte, "မြောက်ဦးခေတ်"
# (Mrauk-U, Burma) -> "Akan" (Africa) aveva la capitale 10.000 km fuori —
# chiaramente falso.
# 50 km e' il compromesso: accetta la maggior parte dei casi di rumore
# digitizzazione (coast polygons semplificati, dipartimenti d'oltremare
# esclusi dal poligono principale) e rigetta il 100% dei match cross-continente
# osservati empiricamente nel dataset AtlasPI post-v6.1.2.
EXACT_NAME_DISPLACEMENT_TOLERANCE_KM = 50.0


# ─── Data structures ────────────────────────────────────────────────────────


@dataclass
class RematchStats:
    total_candidates: int = 0
    upgraded_ne: int = 0
    upgraded_aourednik: int = 0
    unchanged_no_match: int = 0
    unchanged_dry_run: int = 0
    confidence_capped_disputed: int = 0
    skipped_no_capital: int = 0
    errors: int = 0
    json_files_written: int = 0
    json_entities_updated: int = 0
    sample_upgrades: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "total_candidates": self.total_candidates,
            "upgraded_ne": self.upgraded_ne,
            "upgraded_aourednik": self.upgraded_aourednik,
            "unchanged_no_match": self.unchanged_no_match,
            "unchanged_dry_run": self.unchanged_dry_run,
            "confidence_capped_disputed": self.confidence_capped_disputed,
            "skipped_no_capital": self.skipped_no_capital,
            "errors": self.errors,
            "json_files_written": self.json_files_written,
            "json_entities_updated": self.json_entities_updated,
            "sample_upgrades": self.sample_upgrades[:10],
        }


# ─── JSON upgrade payload ───────────────────────────────────────────────────


@dataclass
class JsonUpgrade:
    """What to write back into data/entities/*.json for a single upgrade."""
    name_original: str
    boundary_geojson: dict
    boundary_source: str
    confidence_score: float | None
    boundary_ne_iso_a3: str | None = None
    boundary_aourednik_name: str | None = None
    boundary_aourednik_year: int | None = None
    boundary_aourednik_precision: int | None = None


# ─── Entity → matcher-input dict ────────────────────────────────────────────


def _entity_to_dict(entity: GeoEntity, name_variants: list[NameVariant]) -> dict:
    """Project a GeoEntity + its NameVariants into the dict shape expected by
    boundary_match / aourednik_match (they were written to consume the JSON
    batch format, not ORM rows)."""
    return {
        "name_original": entity.name_original,
        "name_original_lang": entity.name_original_lang,
        "entity_type": entity.entity_type,
        "year_start": entity.year_start,
        "year_end": entity.year_end,
        "capital_lat": entity.capital_lat,
        "capital_lon": entity.capital_lon,
        "capital_name": entity.capital_name,
        "name_variants": [
            {"name": nv.name, "lang": nv.lang} for nv in name_variants
        ],
        "ethical_notes": entity.ethical_notes,
        "status": entity.status,
    }


# ─── NE strong-strategy matcher (no fuzzy) ──────────────────────────────────


def _load_ne_by_iso() -> dict[str, dict]:
    """Load processed Natural Earth. Raises if not available."""
    if not NE_PROCESSED_JSON.exists():
        raise FileNotFoundError(
            f"Natural Earth processed file missing: {NE_PROCESSED_JSON}. "
            f"Run `python -m src.ingestion.natural_earth_import` first."
        )
    data = json.loads(NE_PROCESSED_JSON.read_text(encoding="utf-8"))
    return data


def _try_ne_strong(entity_dict: dict, ne_by_iso: dict[str, dict]):
    """Run ONLY the ISO + exact_name strategies against Natural Earth.

    Returns a MatchResult-like dict {matched, ne_iso_a3, geojson, strategy,
    confidence} or None. Explicitly skips fuzzy — ETHICS-006 prohibits it
    for approximate-recovery, which is the exact bucket where fuzzy
    previously produced 133 displaced matches.
    """
    res = _try_iso_match(entity_dict, ne_by_iso)
    if res and res.matched:
        return res

    ne_records = list(ne_by_iso.values())
    res = _try_exact_name_match(entity_dict, ne_records)
    if res and res.matched:
        return res

    return None


# ─── Confidence scoring ─────────────────────────────────────────────────────


def _ne_confidence(score: float) -> float:
    """NE strong-strategy matches: ISO = 1.0, exact_name = 0.95 → 0.80
    after discount for generic-polygon risk. Stay conservative."""
    return min(0.80, float(score) * 0.80)


def _cap_for_disputed(entity: GeoEntity, raw_conf: float, stats: RematchStats) -> float:
    """ETHICS-003: disputed entities cap at 0.70."""
    if entity.status == "disputed" and raw_conf > DISPUTED_CONFIDENCE_CAP:
        stats.confidence_capped_disputed += 1
        return DISPUTED_CONFIDENCE_CAP
    return raw_conf


# ─── Core workflow ──────────────────────────────────────────────────────────


def rematch_all(
    *, dry_run: bool = False, limit: int | None = None, write_json: bool = True
) -> RematchStats:
    """Scan all approximate_generated entities and try to upgrade them.

    Args:
        dry_run: if True, no DB writes (stats still computed).
        limit: max entities to process (useful for smoke testing).
        write_json: if True (default), propagate DB upgrades to the batch
            JSON files in data/entities/ so they survive a re-seed. Set
            False in tests that only want to validate the matcher logic.

    Returns:
        RematchStats summary. Writes are committed atomically if dry_run=False.
    """
    stats = RematchStats()
    json_upgrades: list[JsonUpgrade] = []

    try:
        ne_by_iso = _load_ne_by_iso()
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        stats.errors += 1
        return stats

    snapshots = list_snapshots()
    if not snapshots:
        logger.warning("No aourednik snapshots available — aourednik retry disabled")

    snapshot_cache: dict = {}

    session: Session = SessionLocal()
    try:
        q = session.query(GeoEntity).filter(
            (GeoEntity.boundary_source == "approximate_generated")
            | (GeoEntity.boundary_source.is_(None))
        )
        if limit is not None:
            q = q.limit(limit)
        candidates = q.all()
        stats.total_candidates = len(candidates)
        logger.info("Found %d approximate/unsourced candidates", stats.total_candidates)

        for entity in candidates:
            try:
                # Need capital to run the geographic guards in NE matcher.
                if entity.capital_lat is None or entity.capital_lon is None:
                    stats.skipped_no_capital += 1
                    continue

                variants = (
                    session.query(NameVariant)
                    .filter(NameVariant.entity_id == entity.id)
                    .all()
                )
                ent_dict = _entity_to_dict(entity, variants)

                upgraded = False

                # 1) NE strong strategies (ISO + exact_name, no fuzzy)
                ne_res = _try_ne_strong(ent_dict, ne_by_iso)
                if ne_res is not None and ne_res.geojson:
                    new_conf = _cap_for_disputed(
                        entity, _ne_confidence(ne_res.confidence), stats
                    )
                    if not dry_run:
                        entity.boundary_geojson = json.dumps(ne_res.geojson)
                        entity.boundary_source = "natural_earth"
                        entity.boundary_ne_iso_a3 = ne_res.ne_iso_a3
                        # Clear stale aourednik trace if any
                        entity.boundary_aourednik_name = None
                        entity.boundary_aourednik_year = None
                        entity.boundary_aourednik_precision = None
                        if new_conf > (entity.confidence_score or 0):
                            entity.confidence_score = new_conf
                    stats.upgraded_ne += 1
                    stats.sample_upgrades.append(
                        f"NE:{ne_res.strategy}: {entity.name_original!r} -> "
                        f"{ne_res.ne_name} ({ne_res.ne_iso_a3})"
                    )
                    json_upgrades.append(JsonUpgrade(
                        name_original=entity.name_original,
                        boundary_geojson=ne_res.geojson,
                        boundary_source="natural_earth",
                        confidence_score=new_conf,
                        boundary_ne_iso_a3=ne_res.ne_iso_a3,
                    ))
                    upgraded = True

                # 2) aourednik fallback (only if NE didn't succeed)
                if not upgraded and snapshots:
                    ao = match_entity_aourednik(
                        ent_dict, snapshots, snapshot_cache=snapshot_cache
                    )
                    # ETHICS-006 v6.2: accettiamo SOLO match nominali (exact/fuzzy name).
                    # Escludiamo capital_in_polygon/capital_near_centroid/subjecto/partof
                    # perche' assegnano poligoni del contenitore/suzerain, non
                    # dell'entita' stessa (es. Republica Ragusina -> Ottoman Empire).
                    ao_ok = (
                        ao.matched
                        and ao.geojson
                        and ao.strategy in AOUREDNIK_ACCEPTED_STRATEGIES
                    )
                    # Extra guard for fuzzy_name: il matcher upstream non fa
                    # geo-check, quindi "Hausa Bakwai" (Nigeria) puo' matchare
                    # "Maya city-states" (Mesoamerica) sul solo score lessicale.
                    # Richiediamo capital-in-polygon come in ETHICS-006 per NE fuzzy.
                    if ao_ok and ao.strategy == "fuzzy_name":
                        if not _capital_in_geojson(ent_dict, ao.geojson):
                            logger.info(
                                "Rejecting aourednik fuzzy match for %r -> %r: "
                                "capital outside matched polygon (ETHICS-006 guard)",
                                entity.name_original,
                                ao.aourednik_name,
                            )
                            ao_ok = False
                    # Tolerance guard for exact_name: accept if capital is
                    # inside polygon OR within EXACT_NAME_DISPLACEMENT_TOLERANCE_KM
                    # of its boundary. Anything further is a semantic error
                    # (see Mrauk-U -> Akan, Kerajaan Kediri -> Kingdom of Georgia).
                    if ao_ok and ao.strategy == "exact_name":
                        km = _capital_distance_to_polygon_km(ent_dict, ao.geojson)
                        if km is not None and km > EXACT_NAME_DISPLACEMENT_TOLERANCE_KM:
                            logger.info(
                                "Rejecting aourednik exact-name match for %r -> %r: "
                                "capital %.0f km outside matched polygon (>%.0f km "
                                "tolerance, ETHICS-006)",
                                entity.name_original,
                                ao.aourednik_name,
                                km,
                                EXACT_NAME_DISPLACEMENT_TOLERANCE_KM,
                            )
                            ao_ok = False
                    if ao_ok:
                        precision_conf = PRECISION_CONFIDENCE.get(
                            ao.border_precision, 0.45
                        )
                        new_conf = _cap_for_disputed(
                            entity, ao.confidence or precision_conf, stats
                        )
                        if not dry_run:
                            entity.boundary_geojson = json.dumps(ao.geojson)
                            entity.boundary_source = "aourednik"
                            entity.boundary_aourednik_name = ao.aourednik_name
                            entity.boundary_aourednik_year = ao.aourednik_year
                            entity.boundary_aourednik_precision = ao.border_precision
                            entity.boundary_ne_iso_a3 = None
                            if new_conf > (entity.confidence_score or 0):
                                entity.confidence_score = new_conf
                        stats.upgraded_aourednik += 1
                        stats.sample_upgrades.append(
                            f"AO:{ao.strategy}: {entity.name_original!r} -> "
                            f"{ao.aourednik_name} (year {ao.aourednik_year})"
                        )
                        json_upgrades.append(JsonUpgrade(
                            name_original=entity.name_original,
                            boundary_geojson=ao.geojson,
                            boundary_source="aourednik",
                            confidence_score=new_conf,
                            boundary_aourednik_name=ao.aourednik_name,
                            boundary_aourednik_year=ao.aourednik_year,
                            boundary_aourednik_precision=ao.border_precision,
                        ))
                        upgraded = True

                if not upgraded:
                    stats.unchanged_no_match += 1

            except Exception as exc:  # noqa: BLE001 — we want to keep going on per-entity errors
                logger.exception("Rematch failed for entity id=%s: %s", entity.id, exc)
                stats.errors += 1

        if dry_run:
            stats.unchanged_dry_run = stats.upgraded_ne + stats.upgraded_aourednik
            session.rollback()
            logger.info("dry-run: rolled back, no DB changes written")
        else:
            session.commit()
            logger.info("committed %d upgrades", stats.upgraded_ne + stats.upgraded_aourednik)

    finally:
        session.close()

    # JSON propagation: write DB upgrades back to data/entities/*.json so
    # they survive a re-seed. No-op if dry_run or write_json is False.
    if not dry_run and write_json and json_upgrades:
        files_written, entities_updated = _apply_upgrades_to_json(json_upgrades)
        stats.json_files_written = files_written
        stats.json_entities_updated = entities_updated
        logger.info(
            "Propagated %d upgrades to %d JSON files",
            entities_updated,
            files_written,
        )

    return stats


# ─── JSON propagation ───────────────────────────────────────────────────────


def _apply_upgrades_to_json(upgrades: list[JsonUpgrade]) -> tuple[int, int]:
    """Walk data/entities/batch_*.json and apply matching upgrades in-place.

    Keyed by name_original (unique across the dataset). Returns
    (files_written, entities_updated).
    """
    if not ENTITIES_DIR.is_dir():
        logger.warning("Entities directory not found: %s", ENTITIES_DIR)
        return 0, 0

    by_name = {u.name_original: u for u in upgrades}
    if not by_name:
        return 0, 0

    files_written = 0
    entities_updated = 0

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
        for ent in container:
            if not isinstance(ent, dict):
                continue
            name = ent.get("name_original")
            if not name or name not in by_name:
                continue
            upg = by_name[name]
            ent["boundary_geojson"] = upg.boundary_geojson
            ent["boundary_source"] = upg.boundary_source
            # Sync confidence as-is. Downgrades are legitimate after a
            # displacement reset (ETHICS-004 caps approximate_generated
            # at 0.4). Upgrades are applied when a stronger match is
            # found. In both cases DB is authoritative.
            if upg.confidence_score is not None:
                ent["confidence_score"] = upg.confidence_score
            # Source-specific trace fields.
            if upg.boundary_source == "natural_earth":
                ent["boundary_ne_iso_a3"] = upg.boundary_ne_iso_a3
                ent.pop("boundary_aourednik_name", None)
                ent.pop("boundary_aourednik_year", None)
                ent.pop("boundary_aourednik_precision", None)
            elif upg.boundary_source == "aourednik":
                ent["boundary_aourednik_name"] = upg.boundary_aourednik_name
                ent["boundary_aourednik_year"] = upg.boundary_aourednik_year
                ent["boundary_aourednik_precision"] = upg.boundary_aourednik_precision
                ent.pop("boundary_ne_iso_a3", None)
            else:
                # approximate_generated or any other non-NE/aourednik source:
                # clear ALL trace fields so stale data doesn't mislead
                # the provenance audit.
                ent.pop("boundary_ne_iso_a3", None)
                ent.pop("boundary_aourednik_name", None)
                ent.pop("boundary_aourednik_year", None)
                ent.pop("boundary_aourednik_precision", None)
            file_changed = True
            entities_updated += 1

        if file_changed:
            with open(json_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            files_written += 1
            logger.debug("Wrote upgrades into %s", json_file.name)

    return files_written, entities_updated


def sync_json_from_db() -> tuple[int, int]:
    """Walk the live DB and propagate every boundary row into the batch JSON
    files — INCLUDING rows that were reset to approximate_generated. This
    is critical: if we sync only NE/aourednik rows, any row that was reset
    (displaced match cleanup) stays stale in JSON and re-seeding re-creates
    the bad data.

    Idempotent. Used to backfill JSON after rematch runs that wrote to the
    DB only, OR after a cleanup that reset displaced matches.
    """
    session: Session = SessionLocal()
    try:
        rows = (
            session.query(GeoEntity)
            .filter(GeoEntity.boundary_source.isnot(None))
            .all()
        )
        upgrades: list[JsonUpgrade] = []
        for row in rows:
            if not row.boundary_geojson:
                continue
            try:
                geom = json.loads(row.boundary_geojson)
            except (ValueError, TypeError):
                continue
            upgrades.append(JsonUpgrade(
                name_original=row.name_original,
                boundary_geojson=geom,
                boundary_source=row.boundary_source,
                confidence_score=row.confidence_score,
                boundary_ne_iso_a3=row.boundary_ne_iso_a3,
                boundary_aourednik_name=row.boundary_aourednik_name,
                boundary_aourednik_year=row.boundary_aourednik_year,
                boundary_aourednik_precision=row.boundary_aourednik_precision,
            ))
    finally:
        session.close()

    return _apply_upgrades_to_json(upgrades)


# ─── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    # Windows default codepage (cp1252) can't encode non-Latin characters
    # that show up in entity names (Россия, Šentilj, ...). Force UTF-8.
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
    )
    parser = argparse.ArgumentParser(
        description=(
            "Conservative re-matching of approximate_generated entities. "
            "Tries NE ISO/exact-name + aourednik only; never retries NE fuzzy "
            "(ETHICS-006)."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute stats without writing to the DB.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max entities to process (useful for smoke testing).",
    )
    parser.add_argument(
        "--sync-json-from-db",
        action="store_true",
        help=(
            "Skip matching entirely; just walk the live DB and propagate "
            "natural_earth/aourednik rows to data/entities/*.json. "
            "Useful to backfill JSON after a rematch that wrote to DB only."
        ),
    )
    args = parser.parse_args()

    if args.sync_json_from_db:
        files, entities = sync_json_from_db()
        print(f"\nSynced {entities} entities into {files} JSON files.")
        return 0

    stats = rematch_all(dry_run=args.dry_run, limit=args.limit)

    print("\nRematch stats")
    for k, v in stats.as_dict().items():
        if isinstance(v, list):
            print(f"  {k}:")
            for item in v:
                print(f"    - {item}")
        else:
            print(f"  {k:<40} {v}")

    return 0 if stats.errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
