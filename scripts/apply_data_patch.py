"""v6.55: unified data patch applier for audit fix pipeline.

Reads a JSON patch file with corrections and applies them to the DB.
Supports all major resource types (entity, event, site, ruler, language).

## Patch JSON format

```json
[
  {
    "resource": "entity",
    "id": 42,
    "field": "year_end",
    "new_value": 907,
    "rationale": "Tang ended 907 CE per Cambridge History Vol 3",
    "source": "Twitchett (1979)",
    "audit_ref": "report_05_historical_accuracy.md#2"
  },
  ...
]
```

## Usage

```bash
# Dry run (no write)
python -m scripts.apply_data_patch research_output/audit/01_fixes.json --dry-run

# Apply for real
python -m scripts.apply_data_patch research_output/audit/01_fixes.json

# On VPS (prod)
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi python -m scripts.apply_data_patch /opt/cra/patches/01_fixes.json"
```

## Audit trail

Every patch writes an audit row to `data_patch_audit.log` (plain text append-only):
```
2026-04-18T00:12:34Z | entity/42 | year_end: 960 -> 907 | rationale: ... | applied_by: cli
```

## Safety

- Dry-run mode prints changes without writing
- Transaction: all or nothing (rollback on any error)
- Skips patches with missing fields
- Skips if current value already matches new_value (idempotent)
"""

from __future__ import annotations

import argparse
import datetime
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
from src.db.models import (
    ArchaeologicalSite,
    GeoEntity,
    HistoricalEvent,
    HistoricalLanguage,
    HistoricalRuler,
)

logger = logging.getLogger(__name__)

AUDIT_LOG = Path(__file__).resolve().parent.parent / "data_patch_audit.log"

# Map resource string → model class
RESOURCE_MAP = {
    "entity": GeoEntity,
    "event": HistoricalEvent,
    "site": ArchaeologicalSite,
    "ruler": HistoricalRuler,
    "language": HistoricalLanguage,
}

# Whitelist of fields we allow to patch via this script.
# Prevents accidental mutation of id, relations, or structural data.
PATCHABLE_FIELDS = {
    "entity": {
        "name_original", "name_original_lang",
        "entity_type", "year_start", "year_end",
        "capital_name", "capital_lat", "capital_lon",
        "confidence_score", "status", "ethical_notes",
        "boundary_source", "boundary_aourednik_year", "boundary_aourednik_precision",
    },
    "event": {
        "name_original", "name_original_lang",
        "event_type", "year", "year_end",
        "month", "day", "date_precision", "iso_date", "calendar_note",
        "location_name", "location_lat", "location_lon",
        "main_actor", "description",
        "casualties_low", "casualties_high", "casualties_source",
        "confidence_score", "status",
        "known_silence", "silence_reason", "ethical_notes",
    },
    "site": {
        "name_original", "name_original_lang",
        "latitude", "longitude",
        "date_start", "date_end", "site_type",
        "description", "unesco_id", "unesco_year",
        "entity_id", "confidence_score", "status", "ethical_notes",
    },
    "ruler": {
        "name_original", "name_original_lang", "name_regnal",
        "birth_year", "death_year", "reign_start", "reign_end",
        "title", "entity_id", "entity_name_fallback",
        "region", "description", "dynasty",
        "confidence_score", "status", "ethical_notes",
    },
    "language": {
        "name_original", "name_original_lang",
        "iso_code", "family", "script",
        "center_lat", "center_lon", "region_name",
        "period_start", "period_end",
        "vitality_status", "description",
        "confidence_score", "status", "ethical_notes",
    },
}


def _audit_log(entries: list[str]):
    """Append audit entries to the log file."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        for entry in entries:
            f.write(entry + "\n")


def apply_patches(patches: list[dict], dry_run: bool = False) -> dict:
    """Apply patch list to DB. Returns summary stats."""
    db = SessionLocal()
    stats = {
        "total": len(patches),
        "applied": 0,
        "skipped_unchanged": 0,
        "skipped_missing": 0,
        "skipped_invalid_field": 0,
        "errors": 0,
    }
    audit_entries: list[str] = []
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        for i, patch in enumerate(patches):
            resource = patch.get("resource")
            res_id = patch.get("id")
            field = patch.get("field")
            new_value = patch.get("new_value")
            rationale = patch.get("rationale", "")

            if resource not in RESOURCE_MAP:
                logger.warning("Patch %d: unknown resource %r, skip", i, resource)
                stats["skipped_invalid_field"] += 1
                continue
            if field not in PATCHABLE_FIELDS.get(resource, set()):
                logger.warning("Patch %d: field %r not patchable for %s, skip", i, field, resource)
                stats["skipped_invalid_field"] += 1
                continue

            Model = RESOURCE_MAP[resource]
            obj = db.query(Model).filter(Model.id == res_id).first()
            if obj is None:
                logger.warning("Patch %d: %s id=%d not found, skip", i, resource, res_id)
                stats["skipped_missing"] += 1
                continue

            current = getattr(obj, field)
            if current == new_value:
                stats["skipped_unchanged"] += 1
                continue

            # Apply
            if not dry_run:
                setattr(obj, field, new_value)

            entry = (
                f"{now} | {resource}/{res_id} | {field}: "
                f"{current!r} -> {new_value!r} | rationale: {rationale} | "
                f"applied_by: {'dry-run' if dry_run else 'cli'}"
            )
            audit_entries.append(entry)
            stats["applied"] += 1
            logger.info(entry)

        if not dry_run:
            db.commit()
            _audit_log(audit_entries)

        return stats
    except Exception:
        db.rollback()
        logger.error("Patch application failed, rollback.", exc_info=True)
        stats["errors"] += 1
        raise
    finally:
        db.close()


def main():
    _apply_windows_stdout_fix()
    parser = argparse.ArgumentParser(description="Apply a JSON data patch")
    parser.add_argument("patch_file", help="Path to JSON patch file")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )

    patch_path = Path(args.patch_file)
    if not patch_path.exists():
        logger.error("Patch file not found: %s", patch_path)
        sys.exit(1)

    with patch_path.open(encoding="utf-8") as f:
        patches = json.load(f)

    if not isinstance(patches, list):
        logger.error("Patch file must contain a JSON array")
        sys.exit(1)

    stats = apply_patches(patches, dry_run=args.dry_run)

    print("\n=== Patch stats ===")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    if args.dry_run:
        print("\n(DRY RUN — no changes written)")
    else:
        print(f"\nAudit log: {AUDIT_LOG}")


if __name__ == "__main__":
    main()
