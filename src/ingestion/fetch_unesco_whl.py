"""v6.56: fetch all 1248 UNESCO World Heritage sites via UNESCO DataHub API.

Saves as JSON batch in `data/sites/batch_01_unesco_whl_full.json` ready for
ingest via `ingest_sites.py`.

API: https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/records
License: UNESCO open data (attribution required — see NOTICE file).

Usage:
    python -m src.ingestion.fetch_unesco_whl

Mapping UNESCO → ArchaeologicalSite:
- id_no → unesco_id
- name_en → name_original (fallback; UNESCO records primarily in English)
- coordinates.{lat,lon} → latitude, longitude
- date_inscribed → unesco_year
- category (Cultural/Natural/Mixed) → site_type
- short_description_en → description
- name_{fr,es,ar,ru,zh} → name_variants (JSON)

ETHICS-009 note: UNESCO uses English as primary name. For sites we already
have curated with native scripts (e.g. "Pompeii", "Ἀκρόπολις"), dedup by
unesco_id prevents override. UNESCO batch only adds new sites not in DB.
"""

from __future__ import annotations

import io
import json
import logging
import sys
from pathlib import Path

import httpx


def _apply_windows_stdout_fix():
    if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        except AttributeError:
            pass


logger = logging.getLogger(__name__)

API_BASE = "https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/records"
OUTPUT_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "sites" / "batch_01_unesco_whl_full.json"


# Category → site_type mapping
_CATEGORY_TO_SITE_TYPE = {
    "Cultural": "archaeological_zone",
    "Natural": "other",
    "Mixed": "archaeological_zone",
}


def fetch_unesco_records(max_records: int = 1300, batch_size: int = 100) -> list[dict]:
    """Fetch all UNESCO WHL records in batches."""
    all_records: list[dict] = []
    offset = 0
    with httpx.Client(timeout=60.0) as client:
        while offset < max_records:
            logger.info("Fetching UNESCO offset=%d...", offset)
            r = client.get(API_BASE, params={"limit": batch_size, "offset": offset})
            r.raise_for_status()
            data = r.json()
            records = data.get("results", [])
            if not records:
                break
            all_records.extend(records)
            total = data.get("total_count", 0)
            logger.info("  got %d records (running total %d / %d)", len(records), len(all_records), total)
            if len(records) < batch_size or len(all_records) >= total:
                break
            offset += batch_size
    return all_records


def transform_to_site_schema(records: list[dict]) -> list[dict]:
    """Convert UNESCO records to AtlasPI ArchaeologicalSite JSON schema."""
    sites: list[dict] = []
    skipped = 0

    for r in records:
        # Required fields
        unesco_id = str(r.get("id_no") or "").strip()
        name_en = (r.get("name_en") or "").strip()
        coords = r.get("coordinates") or {}
        lat = coords.get("lat")
        lon = coords.get("lon")

        if not unesco_id or not name_en or lat is None or lon is None:
            skipped += 1
            continue

        # site_type from category
        category = (r.get("category") or "").strip()
        site_type = _CATEGORY_TO_SITE_TYPE.get(category, "other")

        # name_variants from multilingual fields
        variants = []
        lang_map = {
            "fr": r.get("name_fr"),
            "es": r.get("name_es"),
            "ar": r.get("name_ar"),
            "zh": r.get("name_zh"),
            "ru": r.get("name_ru"),
        }
        for lang, v in lang_map.items():
            if v and v != name_en:
                variants.append({"name": v.strip(), "lang": lang, "context": "UNESCO official"})

        # Sources: UNESCO record itself
        sources = [{
            "citation": f"UNESCO World Heritage List, site #{unesco_id}: {name_en}. "
                        f"Inscribed {r.get('date_inscribed') or '?'}.",
            "source_type": "primary",
            "url": f"https://whc.unesco.org/en/list/{unesco_id}/",
        }]

        # Description: short_description_en (may be truncated, but useful)
        description = r.get("short_description_en") or None
        if description and len(description) > 2000:
            description = description[:1997] + "..."

        # date_inscribed → unesco_year
        unesco_year = r.get("date_inscribed")
        try:
            unesco_year = int(unesco_year) if unesco_year else None
        except (ValueError, TypeError):
            unesco_year = None

        # danger_list → ethical_notes mention
        danger = r.get("danger_list") or r.get("danger")
        ethical_notes = None
        if danger:
            ethical_notes = f"UNESCO In-Danger List: {danger}. Site is under threat (conflict, climate, urbanization, or other)."

        site = {
            "name_original": name_en,
            "name_original_lang": "en",  # UNESCO API primary lang
            "latitude": float(lat),
            "longitude": float(lon),
            # UNESCO doesn't provide date_start/date_end for sites (it's the inscription year, not the site age)
            "date_start": None,
            "date_end": None,
            "site_type": site_type,
            "description": description,
            "unesco_id": unesco_id,
            "unesco_year": unesco_year,
            "entity_id": None,  # No auto-link to entity
            "confidence_score": 0.95,  # UNESCO is authoritative
            "status": "confirmed",
            "ethical_notes": ethical_notes,
            "sources": sources,
            "name_variants": variants,
        }
        sites.append(site)

    logger.info("Transformed %d sites (skipped %d missing required fields)", len(sites), skipped)
    return sites


def main():
    _apply_windows_stdout_fix()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    logger.info("Fetching UNESCO World Heritage List from DataHub API...")
    records = fetch_unesco_records()
    logger.info("Total UNESCO records fetched: %d", len(records))

    sites = transform_to_site_schema(records)
    logger.info("Sites ready for ingest: %d", len(sites))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(sites, f, ensure_ascii=False, indent=2)

    logger.info("Wrote %s (%.1f KB)", OUTPUT_FILE, OUTPUT_FILE.stat().st_size / 1024)
    print(f"\nDone. {len(sites)} sites in {OUTPUT_FILE.name}")


if __name__ == "__main__":
    main()
