"""Arricchimento batch: aggiunge confini approssimativi alle entità senza boundary_geojson.

Questo script:
1. Carica tutti i file JSON batch
2. Per ogni entità con boundary_geojson == null (o Point) E coordinate capitale:
   - Genera un poligono approssimativo
   - Riduce il confidence_score di 0.1
   - Aggiunge boundary_source = "approximate_generated"
3. Salva i file aggiornati
4. Stampa un riepilogo

ETHICS: I confini generati sono approssimazioni computazionali.
Ogni entità arricchita viene marcata con boundary_source = "approximate_generated"
per distinguerla dai dati storici verificati.
Vedi ETHICS-004-confini-generati-approssimativi.md

Uso:
    python -m src.ingestion.enrich_boundaries [--dry-run]
"""

import json
import logging
import sys
from collections import Counter
from pathlib import Path

from src.ingestion.boundary_generator import (
    estimate_polygon_area_km2,
    generate_approximate_boundary,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "entities"


def _needs_boundary(entity: dict) -> bool:
    """Verifica se un'entità necessita di un confine generato.

    ETHICS: non sovrascrivere confini reali esistenti (Polygon con coordinate reali).
    Solo entità con boundary_geojson == null o di tipo Point vengono arricchite.
    """
    bg = entity.get("boundary_geojson")
    if bg is None:
        return True
    if isinstance(bg, dict) and bg.get("type") == "Point":
        return True
    return False


def _has_capital_coords(entity: dict) -> bool:
    """Verifica se l'entità ha coordinate capitale valide."""
    lat = entity.get("capital_lat")
    lon = entity.get("capital_lon")
    return (
        lat is not None
        and lon is not None
        and isinstance(lat, (int, float))
        and isinstance(lon, (int, float))
        and -90 <= lat <= 90
        and -180 <= lon <= 180
    )


def _add_boundary_source_to_existing(entity: dict) -> None:
    """Aggiunge boundary_source alle entità che hanno già confini reali.

    ETHICS: entità con confini esistenti vengono marcate come 'historical_map'
    per distinguerle dai confini generati. Questo è critico per la trasparenza.
    """
    bg = entity.get("boundary_geojson")
    if bg and isinstance(bg, dict) and bg.get("type") == "Polygon":
        if "boundary_source" not in entity:
            entity["boundary_source"] = "historical_map"


def enrich_file(filepath: Path, dry_run: bool = False) -> dict:
    """Arricchisce un singolo file batch con confini approssimativi.

    Returns:
        Dizionario con statistiche: enriched, skipped_no_coords, already_has,
        total, by_type.
    """
    with open(filepath, encoding="utf-8") as f:
        entities = json.load(f)

    stats = {
        "enriched": 0,
        "skipped_no_coords": 0,
        "already_has_polygon": 0,
        "point_upgraded": 0,
        "total": len(entities),
        "by_type": Counter(),
        "source_tagged": 0,
    }

    for entity in entities:
        # Tag existing real boundaries with boundary_source
        if not _needs_boundary(entity):
            _add_boundary_source_to_existing(entity)
            stats["already_has_polygon"] += 1
            stats["source_tagged"] += 1
            continue

        if not _has_capital_coords(entity):
            stats["skipped_no_coords"] += 1
            logger.warning(
                "Skipped '%s' — no valid capital coordinates",
                entity.get("name_original", "?"),
            )
            continue

        was_point = (
            isinstance(entity.get("boundary_geojson"), dict)
            and entity["boundary_geojson"].get("type") == "Point"
        )

        # Generate approximate boundary
        boundary = generate_approximate_boundary(
            lat=entity["capital_lat"],
            lon=entity["capital_lon"],
            entity_type=entity.get("entity_type", "kingdom"),
            year_start=entity.get("year_start", 0),
            year_end=entity.get("year_end"),
            num_vertices=12,
        )

        entity["boundary_geojson"] = boundary

        # ETHICS: mark as approximate — users must know this is not real cartographic data
        entity["boundary_source"] = "approximate_generated"

        # Reduce confidence to reflect the approximation
        current_score = entity.get("confidence_score", 0.5)
        entity["confidence_score"] = round(max(0.1, current_score - 0.1), 2)

        # Log area for sanity check
        area_km2 = estimate_polygon_area_km2(boundary)
        entity_type = entity.get("entity_type", "unknown")

        stats["enriched"] += 1
        stats["by_type"][entity_type] += 1
        if was_point:
            stats["point_upgraded"] += 1

        logger.debug(
            "Enriched '%s' (%s): ~%.0f km^2",
            entity.get("name_original", "?"),
            entity_type,
            area_km2,
        )

    needs_save = stats["enriched"] > 0 or stats["source_tagged"] > 0
    if not dry_run and needs_save:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)
        logger.info(
            "Saved %s — %d enriched, %d source-tagged",
            filepath.name,
            stats["enriched"],
            stats["source_tagged"],
        )

    return stats


def enrich_all(dry_run: bool = False) -> None:
    """Arricchisce tutti i file batch nella directory data/entities/.

    ETHICS: non modifica mai entità con confini Polygon esistenti.
    """
    batch_files = sorted(DATA_DIR.glob("batch_*.json"))

    if not batch_files:
        logger.error("No batch files found in %s", DATA_DIR)
        return

    total_stats = {
        "enriched": 0,
        "skipped_no_coords": 0,
        "already_has_polygon": 0,
        "point_upgraded": 0,
        "total": 0,
        "by_type": Counter(),
        "source_tagged": 0,
        "files_modified": 0,
    }

    print(f"\n{'='*70}")
    print(f"  AtlasPI Boundary Enrichment {'(DRY RUN)' if dry_run else ''}")
    print(f"{'='*70}\n")

    for filepath in batch_files:
        stats = enrich_file(filepath, dry_run=dry_run)

        total_stats["enriched"] += stats["enriched"]
        total_stats["skipped_no_coords"] += stats["skipped_no_coords"]
        total_stats["already_has_polygon"] += stats["already_has_polygon"]
        total_stats["point_upgraded"] += stats["point_upgraded"]
        total_stats["total"] += stats["total"]
        total_stats["by_type"] += stats["by_type"]
        total_stats["source_tagged"] += stats["source_tagged"]

        if stats["enriched"] > 0:
            total_stats["files_modified"] += 1

        status = (
            f"  {filepath.name}: "
            f"{stats['total']} total, "
            f"{stats['enriched']} enriched, "
            f"{stats['already_has_polygon']} already had polygon, "
            f"{stats['skipped_no_coords']} skipped (no coords)"
        )
        print(status)

    # Summary
    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total entities:              {total_stats['total']}")
    print(f"  Already had polygon:         {total_stats['already_has_polygon']}")
    print(f"  Enriched with approx:        {total_stats['enriched']}")
    print(f"    - Upgraded from Point:     {total_stats['point_upgraded']}")
    print(f"  Skipped (no coordinates):    {total_stats['skipped_no_coords']}")
    print(f"  Source-tagged (existing):    {total_stats['source_tagged']}")
    print(f"  Files modified:              {total_stats['files_modified']}")
    print(f"\n  Enriched by entity type:")
    for etype, count in total_stats["by_type"].most_common():
        print(f"    {etype:25s} {count}")
    print(f"\n{'='*70}")
    if dry_run:
        print("  DRY RUN — no files were modified")
    else:
        print("  Done. All files saved.")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    enrich_all(dry_run=dry)
