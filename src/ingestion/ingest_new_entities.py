"""Idempotent ingestion of new entities from data/entities/batch_*.json.

Purpose:
    Insert entities from JSON files whose ``name_original`` is NOT yet
    in the database, skipping any that already exist. Unlike the seed
    loader (which skips entirely if the DB is non-empty), this utility
    is safe to run on a populated production database to add new
    expansion batches without touching existing rows.

Usage:
    python -m src.ingestion.ingest_new_entities

ETHICS considerations:
    * Existing rows are NEVER updated here. Use sync_boundaries_from_json
      for boundary amendments — this tool only INSERTs missing entities.
    * Same ETHICS-001/002/003/004/005 guarantees as seed_database():
      name_original primary, name_variants preserved, territory_changes
      preserved, sources preserved, boundary_source provenance preserved.
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path

# Windows cp1252 stdout fix for non-latin entity names
if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except AttributeError:
        pass

from src.db.database import SessionLocal
from src.db.models import GeoEntity, NameVariant, Source, TerritoryChange
from src.db.seed import load_all_entities

logger = logging.getLogger(__name__)


def ingest_missing_entities() -> dict:
    """Insert entities whose name_original is not in the DB yet.

    Returns:
        dict with keys {inserted, skipped_existing, missing_batch_files}.
    """
    db = SessionLocal()
    try:
        existing = {row.name_original for row in db.query(GeoEntity.name_original).all()}
        logger.info("Entità esistenti in DB: %d", len(existing))

        all_entities = load_all_entities()
        logger.info("Entità nei JSON: %d", len(all_entities))

        inserted = 0
        skipped = 0
        for data in all_entities:
            name = data.get("name_original", "")
            if not name:
                continue
            if name in existing:
                skipped += 1
                continue

            entity = GeoEntity(
                name_original=data["name_original"],
                name_original_lang=data["name_original_lang"],
                entity_type=data["entity_type"],
                year_start=data["year_start"],
                year_end=data.get("year_end"),
                capital_name=data.get("capital_name"),
                capital_lat=data.get("capital_lat"),
                capital_lon=data.get("capital_lon"),
                boundary_geojson=(
                    json.dumps(data["boundary_geojson"])
                    if data.get("boundary_geojson")
                    else None
                ),
                boundary_source=data.get("boundary_source"),
                boundary_aourednik_name=data.get("boundary_aourednik_name"),
                boundary_aourednik_year=data.get("boundary_aourednik_year"),
                boundary_aourednik_precision=data.get("boundary_aourednik_precision"),
                boundary_ne_iso_a3=data.get("boundary_ne_iso_a3"),
                confidence_score=data.get("confidence_score", 0.5),
                status=data.get("status", "confirmed"),
                ethical_notes=data.get("ethical_notes"),
            )

            for nv in data.get("name_variants", []):
                entity.name_variants.append(NameVariant(**nv))

            for tc in data.get("territory_changes", []):
                tc_data = dict(tc)
                pa = tc_data.get("population_affected")
                if pa is not None and not isinstance(pa, int):
                    try:
                        tc_data["population_affected"] = int(pa)
                    except (ValueError, TypeError):
                        tc_data["population_affected"] = None
                entity.territory_changes.append(TerritoryChange(**tc_data))

            for src in data.get("sources", []):
                entity.sources.append(Source(**src))

            db.add(entity)
            inserted += 1

        db.commit()
        logger.info("Ingest completato: %d inseriti, %d già esistenti saltati.", inserted, skipped)
        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "total_in_json": len(all_entities),
        }

    except Exception:
        db.rollback()
        logger.error("Errore durante ingest", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    stats = ingest_missing_entities()
    print(f"\nIngest stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
