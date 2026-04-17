"""v6.44: idempotent ingest di historical languages da data/languages/*.json.

Dedup key: (name_original, iso_code or None, center_lat, center_lon).
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
from src.db.models import HistoricalLanguage

logger = logging.getLogger(__name__)

LANGS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "languages"


def ingest_languages(dry_run: bool = False) -> dict:
    if not LANGS_DIR.exists():
        logger.warning("Languages directory missing: %s", LANGS_DIR)
        return {"inserted": 0, "skipped_existing": 0, "files_processed": 0, "total_in_json": 0}

    db = SessionLocal()
    try:
        existing = set()
        for row in db.query(
            HistoricalLanguage.name_original,
            HistoricalLanguage.iso_code,
        ).all():
            existing.add((row.name_original, row.iso_code))

        inserted = 0
        skipped = 0
        total = 0
        files = 0
        for json_file in sorted(LANGS_DIR.glob("*.json")):
            files += 1
            try:
                with json_file.open(encoding="utf-8") as f:
                    langs_data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed loading %s: %s", json_file.name, e)
                continue

            if not isinstance(langs_data, list):
                continue

            for data in langs_data:
                total += 1
                name = data.get("name_original", "")
                iso = data.get("iso_code")
                if not name or not data.get("region_name"):
                    continue

                key = (name, iso)
                if key in existing:
                    skipped += 1
                    continue

                lang = HistoricalLanguage(
                    name_original=name,
                    name_original_lang=data.get("name_original_lang", "en"),
                    iso_code=iso,
                    family=data.get("family"),
                    script=data.get("script"),
                    center_lat=data.get("center_lat"),
                    center_lon=data.get("center_lon"),
                    region_name=data["region_name"],
                    period_start=data.get("period_start"),
                    period_end=data.get("period_end"),
                    vitality_status=data.get("vitality_status", "extinct"),
                    description=data.get("description"),
                    confidence_score=data.get("confidence_score", 0.7),
                    status=data.get("status", "confirmed"),
                    ethical_notes=data.get("ethical_notes"),
                    sources=json.dumps(data["sources"], ensure_ascii=False) if data.get("sources") else None,
                    name_variants=json.dumps(data["name_variants"], ensure_ascii=False) if data.get("name_variants") else None,
                )
                if not dry_run:
                    db.add(lang)
                inserted += 1
                existing.add(key)

        if not dry_run:
            db.commit()

        logger.info(
            "Languages ingest: %d inserted, %d skipped, %d total, %d files",
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
        logger.error("Languages ingest failed", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    _apply_windows_stdout_fix()
    logging.basicConfig(level=logging.INFO)
    print("Languages ingest:", ingest_languages())
