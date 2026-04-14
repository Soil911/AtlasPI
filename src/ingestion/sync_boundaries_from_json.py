"""Monotonic boundary reconciliation: batch JSON → running DB.

Context: the v6.1.1 boundary enrichment pipeline upgrades
`data/entities/batch_*.json` with real Natural Earth / aourednik /
academic_source polygons. The initial `seed_database()` only runs on
an empty DB, so a long-running production database will keep its
pre-enrichment boundaries even after the JSON has been upgraded.

This module closes that gap. It is a MONOTONIC upgrade:

  - For each entity in the DB, look up the same `name_original` in the
    current batch JSON index.
  - If the batch version has a strictly better boundary (more vertices,
    or a real geometry replacing a Point/null), overwrite the DB
    boundary and bump `confidence_score` to the batch value — capped
    at 0.70 for `status == 'disputed'` (ETHICS-003).
  - Never downgrade an existing DB boundary. A high-vertex DB polygon
    is kept even if the batch lists something smaller.

Designed to be idempotent: re-running produces zero changes once the DB
is in sync. Safe to call manually in production after pulling new
enrichment commits:

    python -m src.ingestion.sync_boundaries_from_json --dry-run
    python -m src.ingestion.sync_boundaries_from_json

Or invoked at container startup behind the `SYNC_BOUNDARIES_ON_START=1`
env var (see `src/main.py` lifespan).

ETHICS: the disputed-territory cap (ETHICS-003) is enforced here too —
a batch confidence of 0.85 for a disputed entity is silently lowered
to 0.70 on write, identical to the enrichment-time behaviour in
`src.ingestion.enrich_all_boundaries`.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

ENTITIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"

DISPUTED_CONFIDENCE_CAP = 0.70  # ETHICS-003


@dataclass
class SyncStats:
    """Summary of a sync run."""

    total_db: int = 0
    matched_in_batch: int = 0
    upgraded: int = 0
    skipped_no_batch_entry: int = 0
    skipped_batch_has_no_boundary: int = 0
    skipped_db_already_better: int = 0
    skipped_equal: int = 0
    confidence_capped_disputed: int = 0

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def _count_vertices(geom: dict | None) -> int:
    """Count vertices in a GeoJSON Polygon or MultiPolygon. Returns 0 for Point/None/invalid."""
    if not isinstance(geom, dict):
        return 0
    t = geom.get("type")
    coords = geom.get("coordinates") or []
    if t == "Polygon":
        return sum(len(ring) for ring in coords)
    if t == "MultiPolygon":
        return sum(sum(len(ring) for ring in poly) for poly in coords)
    return 0


def _load_batch_index() -> dict[str, dict]:
    """Read all `data/entities/batch_*.json` files into `name_original → entity_dict`.

    Silently skips files that don't parse. The caller is expected to handle
    an empty index gracefully.
    """
    index: dict[str, dict] = {}
    if not ENTITIES_DIR.exists():
        logger.warning("Entities dir not found: %s", ENTITIES_DIR)
        return index

    for json_file in sorted(ENTITIES_DIR.glob("batch_*.json")):
        try:
            with open(json_file, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping %s: %s", json_file.name, exc)
            continue

        if isinstance(data, dict) and "entities" in data:
            data = data["entities"]
        if not isinstance(data, list):
            continue

        for ent in data:
            name = ent.get("name_original")
            if not name:
                continue
            # Last one wins on collision — matches seed_database() dedup behaviour.
            index[name] = ent

    return index


def _should_upgrade(db_geom_str: str | None, batch_entity: dict) -> bool:
    """Monotonic upgrade predicate.

    Returns True iff the batch entity carries a meaningfully better boundary
    than what the DB currently stores. Conservative by design — a tie is
    treated as "do nothing".
    """
    batch_geom = batch_entity.get("boundary_geojson")
    if not isinstance(batch_geom, dict):
        return False
    batch_type = batch_geom.get("type")
    if batch_type not in ("Polygon", "MultiPolygon"):
        # A Point or unknown geometry is never an upgrade.
        return False

    batch_v = _count_vertices(batch_geom)
    if batch_v < 8:
        # Degenerate batch polygon — don't overwrite anything with it.
        return False

    # Parse current DB boundary.
    db_geom: dict | None = None
    if db_geom_str:
        try:
            db_geom = json.loads(db_geom_str)
        except (ValueError, TypeError):
            db_geom = None

    db_type = db_geom.get("type") if isinstance(db_geom, dict) else None
    db_v = _count_vertices(db_geom)

    # Empty DB geometry: any real batch polygon is an upgrade.
    if db_type not in ("Polygon", "MultiPolygon"):
        return True

    # Both real. Require the batch to be *materially* bigger (20% floor) to
    # avoid churn from trivial vertex-count differences between equivalent
    # simplifications.
    return batch_v >= db_v * 1.2


def sync_boundaries_from_json(
    dry_run: bool = False, session: Session | None = None
) -> SyncStats:
    """Reconcile DB boundaries against current batch JSON files.

    Args:
        dry_run: if True, compute what would change without writing.
        session: optional session (used by tests). Defaults to SessionLocal().

    Returns:
        SyncStats with per-category counts.
    """
    own_session = session is None
    db: Session = session if session is not None else SessionLocal()

    stats = SyncStats()
    try:
        batch_index = _load_batch_index()
        logger.info("Loaded %d entities from batch JSONs", len(batch_index))

        all_entities = db.query(GeoEntity).all()
        stats.total_db = len(all_entities)

        for entity in all_entities:
            batch_entity = batch_index.get(entity.name_original)
            if batch_entity is None:
                stats.skipped_no_batch_entry += 1
                continue
            stats.matched_in_batch += 1

            batch_geom = batch_entity.get("boundary_geojson")
            if not isinstance(batch_geom, dict) or batch_geom.get("type") not in ("Polygon", "MultiPolygon"):
                stats.skipped_batch_has_no_boundary += 1
                continue

            if not _should_upgrade(entity.boundary_geojson, batch_entity):
                # Either DB is already better, or the batch is a tie.
                if entity.boundary_geojson:
                    stats.skipped_db_already_better += 1
                else:
                    stats.skipped_equal += 1
                continue

            # Upgrade!
            new_geojson = json.dumps(batch_geom)
            new_confidence = batch_entity.get("confidence_score", entity.confidence_score)

            # ETHICS-003: disputed entities cannot exceed 0.70 regardless of source quality.
            if entity.status == "disputed" and new_confidence > DISPUTED_CONFIDENCE_CAP:
                new_confidence = DISPUTED_CONFIDENCE_CAP
                stats.confidence_capped_disputed += 1

            if not dry_run:
                entity.boundary_geojson = new_geojson
                # Only raise confidence, never lower it here — that's a
                # different operation and could mask an unrelated downgrade.
                if new_confidence > entity.confidence_score:
                    entity.confidence_score = new_confidence
                # ETHICS-005: sync provenance metadata alongside the geometry.
                # These fields are informational — they document where the
                # upgraded polygon came from, which is essential for
                # reproducibility and academic citability.
                entity.boundary_source = batch_entity.get("boundary_source")
                entity.boundary_aourednik_name = batch_entity.get("boundary_aourednik_name")
                entity.boundary_aourednik_year = batch_entity.get("boundary_aourednik_year")
                entity.boundary_aourednik_precision = batch_entity.get("boundary_aourednik_precision")
                entity.boundary_ne_iso_a3 = batch_entity.get("boundary_ne_iso_a3")

            stats.upgraded += 1

        if not dry_run and stats.upgraded > 0:
            db.commit()
            logger.info(
                "Sync committed: %d entities upgraded out of %d matched (%d total in DB)",
                stats.upgraded, stats.matched_in_batch, stats.total_db,
            )
        elif dry_run:
            logger.info(
                "DRY-RUN: would upgrade %d entities out of %d matched (%d total in DB)",
                stats.upgraded, stats.matched_in_batch, stats.total_db,
            )
            db.rollback()

    except Exception:
        db.rollback()
        logger.exception("sync_boundaries_from_json failed")
        raise
    finally:
        if own_session:
            db.close()

    return stats


def main() -> None:
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Compute changes without writing.")
    args = parser.parse_args()

    stats = sync_boundaries_from_json(dry_run=args.dry_run)
    print("\n=== Sync stats ===")
    for k, v in stats.as_dict().items():
        print(f"  {k:40s}  {v}")


if __name__ == "__main__":
    main()
