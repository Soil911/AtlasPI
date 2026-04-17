"""v6.45: idempotent ingest di historical rulers da data/rulers/*.json.

Dedup key: (name_original, reign_start).
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path


def _apply_windows_stdout_fix():
    if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        except AttributeError:
            pass


from src.db.database import SessionLocal
from src.db.models import GeoEntity, HistoricalRuler

logger = logging.getLogger(__name__)

RULERS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "rulers"


def ingest_rulers(dry_run: bool = False) -> dict:
    if not RULERS_DIR.exists():
        return {"inserted": 0, "skipped_existing": 0, "files_processed": 0, "total_in_json": 0}

    db = SessionLocal()
    try:
        existing = set()
        for row in db.query(
            HistoricalRuler.name_original,
            HistoricalRuler.reign_start,
        ).all():
            existing.add((row.name_original, row.reign_start))

        entity_map = {
            e.name_original: e.id
            for e in db.query(GeoEntity.name_original, GeoEntity.id).all()
        }

        inserted = 0
        skipped = 0
        total = 0
        files = 0
        for json_file in sorted(RULERS_DIR.glob("*.json")):
            files += 1
            try:
                with json_file.open(encoding="utf-8") as f:
                    rulers_data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed loading %s: %s", json_file.name, e)
                continue

            if not isinstance(rulers_data, list):
                continue

            for data in rulers_data:
                total += 1
                name = data.get("name_original", "")
                if not name or not data.get("title") or not data.get("region"):
                    continue

                key = (name, data.get("reign_start"))
                if key in existing:
                    skipped += 1
                    continue

                entity_id = data.get("entity_id")
                if isinstance(entity_id, str):
                    entity_id = entity_map.get(entity_id)

                ruler = HistoricalRuler(
                    name_original=name,
                    name_original_lang=data.get("name_original_lang", "en"),
                    name_regnal=data.get("name_regnal"),
                    birth_year=data.get("birth_year"),
                    death_year=data.get("death_year"),
                    reign_start=data.get("reign_start"),
                    reign_end=data.get("reign_end"),
                    title=data["title"],
                    entity_id=entity_id,
                    entity_name_fallback=data.get("entity_name_fallback"),
                    region=data["region"],
                    description=data.get("description"),
                    dynasty=data.get("dynasty"),
                    confidence_score=data.get("confidence_score", 0.7),
                    status=data.get("status", "confirmed"),
                    ethical_notes=data.get("ethical_notes"),
                    sources=json.dumps(data["sources"], ensure_ascii=False) if data.get("sources") else None,
                    name_variants=json.dumps(data["name_variants"], ensure_ascii=False) if data.get("name_variants") else None,
                    notable_events=json.dumps(data["notable_events"], ensure_ascii=False) if data.get("notable_events") else None,
                )
                if not dry_run:
                    db.add(ruler)
                inserted += 1
                existing.add(key)

        if not dry_run:
            db.commit()

        logger.info("Rulers ingest: %d inserted, %d skipped, %d total, %d files",
                    inserted, skipped, total, files)
        return {
            "inserted": inserted,
            "skipped_existing": skipped,
            "files_processed": files,
            "total_in_json": total,
        }
    except Exception:
        db.rollback()
        logger.error("Rulers ingest failed", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    _apply_windows_stdout_fix()
    logging.basicConfig(level=logging.INFO)
    print("Rulers ingest:", ingest_rulers())
