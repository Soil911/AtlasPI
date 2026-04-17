"""v6.37.1: idempotent ingest di archaeological sites da data/sites/*.json.

Caricato dalla lifespan app dopo seed_database / seed_events_database.
Dedup per (name_original, latitude, longitude) — un sito e' univoco per
nome originale + posizione geografica.

ETHICS-009: rinominazioni coloniali preservate in name_variants con
context esplicito. name_original resta nella lingua/cultura originale.
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path


def _apply_windows_stdout_fix():
    """Windows cp1252 stdout fix — only when run as __main__ (not imported)."""
    if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        except AttributeError:
            pass

from src.db.database import SessionLocal
from src.db.models import ArchaeologicalSite, GeoEntity

logger = logging.getLogger(__name__)

SITES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sites"


def ingest_sites(dry_run: bool = False) -> dict:
    """Ingest archaeological sites idempotently.

    Dedup key: (name_original, latitude, longitude) tupla.

    Args:
        dry_run: se True, non scrive su DB (utile per testing).

    Returns:
        dict con {inserted, skipped_existing, files_processed, total_in_json}.
    """
    if not SITES_DIR.exists():
        logger.warning("Sites directory missing: %s", SITES_DIR)
        return {"inserted": 0, "skipped_existing": 0, "files_processed": 0, "total_in_json": 0}

    db = SessionLocal()
    try:
        # Build dedup set from DB.
        existing = set()
        for row in db.query(
            ArchaeologicalSite.name_original,
            ArchaeologicalSite.latitude,
            ArchaeologicalSite.longitude,
        ).all():
            existing.add((row.name_original, round(row.latitude, 4), round(row.longitude, 4)))

        # Entity map for optional entity_id resolution by name.
        entity_map: dict[str, int] = {
            e.name_original: e.id for e in db.query(GeoEntity.name_original, GeoEntity.id).all()
        }

        inserted = 0
        skipped = 0
        total = 0
        files = 0
        for json_file in sorted(SITES_DIR.glob("*.json")):
            files += 1
            try:
                with json_file.open(encoding="utf-8") as f:
                    sites_data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed loading %s: %s", json_file.name, e)
                continue

            if not isinstance(sites_data, list):
                logger.warning("Expected list in %s, got %s", json_file.name, type(sites_data).__name__)
                continue

            for data in sites_data:
                total += 1
                name = data.get("name_original", "")
                lat = data.get("latitude")
                lon = data.get("longitude")
                if not name or lat is None or lon is None:
                    logger.warning("Skipping malformed site: %s", data)
                    continue

                key = (name, round(lat, 4), round(lon, 4))
                if key in existing:
                    skipped += 1
                    continue

                # Resolve entity_id from name if provided but not numeric.
                entity_id = data.get("entity_id")
                if isinstance(entity_id, str):
                    entity_id = entity_map.get(entity_id)

                site = ArchaeologicalSite(
                    name_original=name,
                    name_original_lang=data.get("name_original_lang", "en"),
                    latitude=float(lat),
                    longitude=float(lon),
                    date_start=data.get("date_start"),
                    date_end=data.get("date_end"),
                    site_type=data.get("site_type", "ruins"),
                    description=data.get("description"),
                    unesco_id=data.get("unesco_id"),
                    unesco_year=data.get("unesco_year"),
                    entity_id=entity_id,
                    confidence_score=data.get("confidence_score", 0.7),
                    status=data.get("status", "confirmed"),
                    ethical_notes=data.get("ethical_notes"),
                    sources=json.dumps(data["sources"], ensure_ascii=False) if data.get("sources") else None,
                    name_variants=json.dumps(data["name_variants"], ensure_ascii=False) if data.get("name_variants") else None,
                )
                if not dry_run:
                    db.add(site)
                inserted += 1
                existing.add(key)

        if not dry_run:
            db.commit()

        logger.info(
            "Sites ingest: %d inserted, %d skipped (already present), %d total, %d files processed",
            inserted, skipped, total, files,
        )
        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "files_processed": files,
            "total_in_json": total,
        }
    except Exception:
        db.rollback()
        logger.error("Sites ingest failed", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    _apply_windows_stdout_fix()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    stats = ingest_sites()
    print("\nSites ingest stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
