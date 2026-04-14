"""Pipeline completa di arricchimento boundary per tutti i batch AtlasPI.

Per ogni entita' nei file batch_*.json:

  1. Se ha gia' un boundary_geojson di tipo Polygon/MultiPolygon REALE
     (boundary_source != 'approximate_generated'), SKIP.
  2. Se e' eligibile per Natural Earth (year_end > 1800 o year_start > 1700)
     e c'e' un match valido, usa quello (boundary_source = 'natural_earth').
  3. Altrimenti, genera un boundary approssimativo via name_seeded_boundary
     (boundary_source = 'approximate_generated', confidence_score = 0.4).

ETHICS:
  - Idempotente: rieseguire lo script non corrompe nulla. I boundary
    'historical_map'/'natural_earth'/'academic_source' sono intoccabili.
  - Solo i boundary 'approximate_generated' possono essere upgradati a
    'natural_earth' se viene trovato un match valido (questo migliora
    la qualita' del dato).
  - Boundary mancanti o di tipo Point sono sempre rigenerati.
  - I file batch vengono backuppati in .bak prima di ogni modifica.
  - Vedi ETHICS-004 e ETHICS-005.

Uso:
    python -m src.ingestion.enrich_all_boundaries --dry-run
    python -m src.ingestion.enrich_all_boundaries
    python -m src.ingestion.enrich_all_boundaries --skip-natural-earth
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

from src.ingestion.boundary_generator import name_seeded_boundary
from src.ingestion.boundary_match import (
    MatchResult,
    entity_key,
    match_entity,
)
from src.ingestion.natural_earth_import import (
    OUTPUT_JSON as NE_PROCESSED_JSON,
    import_natural_earth,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BATCHES_DIR = ROOT_DIR / "data" / "entities"

# Sorgenti boundary considerate "reali" (non generate)
REAL_SOURCES = {"historical_map", "natural_earth", "academic_source"}


# ─── Helpers ────────────────────────────────────────────────────────────────


def _is_real_polygon(entity: dict) -> bool:
    """L'entita' ha gia' un poligono REALE che non va sostituito."""
    bg = entity.get("boundary_geojson")
    if not isinstance(bg, dict):
        return False
    if bg.get("type") not in ("Polygon", "MultiPolygon"):
        return False
    bs = entity.get("boundary_source")
    # Polygon presente ma SENZA boundary_source: lo trattiamo come reale
    # e gli aggiungiamo il tag 'historical_map' per retro-compatibilita'.
    if bs is None:
        return True
    return bs in REAL_SOURCES


def _is_generated_polygon(entity: dict) -> bool:
    """L'entita' ha un poligono generato — eligibile per upgrade a NE."""
    bg = entity.get("boundary_geojson")
    if not isinstance(bg, dict):
        return False
    if bg.get("type") not in ("Polygon", "MultiPolygon"):
        return False
    return entity.get("boundary_source") == "approximate_generated"


def _is_missing_or_point(entity: dict) -> bool:
    """L'entita' non ha boundary o ha solo un Point."""
    bg = entity.get("boundary_geojson")
    if bg is None:
        return True
    if isinstance(bg, dict) and bg.get("type") == "Point":
        return True
    return False


def _has_valid_capital(entity: dict) -> bool:
    lat = entity.get("capital_lat")
    lon = entity.get("capital_lon")
    return (
        lat is not None and lon is not None
        and isinstance(lat, (int, float))
        and isinstance(lon, (int, float))
        and -90 <= lat <= 90 and -180 <= lon <= 180
    )


def _build_disputed_note(match: MatchResult) -> str:
    """Costruisce una nota etica per i match su territori contestati."""
    return (
        f"ETHICS-005: boundary da Natural Earth (ISO {match.ne_iso_a3}, "
        f"{match.ne_name}). Territorio contestato — vedi ETHICS-005-boundary-"
        f"natural-earth.md per la metodologia. Status dell'entita' AtlasPI "
        f"resta 'disputed' se applicabile."
    )


# ─── Core pipeline per file ─────────────────────────────────────────────────


def _backup_file(filepath: Path) -> Path:
    """Crea un backup .bak del file. Idempotente: sovrascrive backup esistente."""
    backup = filepath.with_suffix(filepath.suffix + ".bak")
    shutil.copy2(filepath, backup)
    return backup


def _apply_natural_earth_match(entity: dict, match: MatchResult) -> None:
    """Applica un match Natural Earth all'entita' (mutazione in-place)."""
    entity["boundary_geojson"] = match.geojson
    entity["boundary_source"] = "natural_earth"
    if match.ne_iso_a3:
        # Memorizziamo l'ISO usato per audit
        entity["boundary_ne_iso_a3"] = match.ne_iso_a3
    # Confidence: alta se ISO/exact, media se fuzzy/capital
    if match.strategy in ("iso_a3", "exact_name"):
        entity["confidence_score"] = max(
            entity.get("confidence_score", 0.5), 0.85
        )
    elif match.strategy == "fuzzy":
        # Boost modesto, capped
        entity["confidence_score"] = max(
            entity.get("confidence_score", 0.5),
            min(0.85, 0.6 + 0.25 * match.confidence),
        )
    else:  # capital_in_polygon
        entity["confidence_score"] = max(
            entity.get("confidence_score", 0.5), 0.6
        )

    # ETHICS: nota per territori contestati
    if match.is_disputed:
        existing_note = entity.get("ethical_notes", "") or ""
        disputed_note = _build_disputed_note(match)
        if disputed_note not in existing_note:
            entity["ethical_notes"] = (
                f"{existing_note} {disputed_note}".strip()
            )


def _apply_generated_boundary(entity: dict) -> None:
    """Genera un boundary approssimativo e lo applica (mutazione in-place)."""
    boundary = name_seeded_boundary(
        name=entity.get("name_original", "unknown"),
        lat=entity["capital_lat"],
        lon=entity["capital_lon"],
        entity_type=entity.get("entity_type", "kingdom"),
        num_vertices=12,
    )
    entity["boundary_geojson"] = boundary
    entity["boundary_source"] = "approximate_generated"
    # ETHICS: confidence basso per riflettere l'incertezza
    entity["confidence_score"] = round(
        min(0.4, entity.get("confidence_score", 0.5)), 2
    )


def _tag_existing_real_polygon(entity: dict) -> bool:
    """Se l'entita' ha un poligono reale ma senza boundary_source, taggalo.

    Returns: True se ha modificato l'entita'.
    """
    bg = entity.get("boundary_geojson")
    if isinstance(bg, dict) and bg.get("type") in ("Polygon", "MultiPolygon"):
        if entity.get("boundary_source") is None:
            entity["boundary_source"] = "historical_map"
            return True
    return False


# ─── File processing ────────────────────────────────────────────────────────


def process_file(
    filepath: Path,
    ne_by_iso: dict[str, dict],
    dry_run: bool = False,
    skip_natural_earth: bool = False,
) -> dict:
    """Processa un singolo file batch.

    Returns:
        Statistiche del processing per questo file.
    """
    entities = json.loads(filepath.read_text(encoding="utf-8"))
    stats = {
        "total": len(entities),
        "skipped_real": 0,
        "ne_matched_new": 0,        # Point/None -> NE
        "ne_matched_upgrade": 0,    # generated -> NE
        "generated_new": 0,         # Point/None -> generated
        "generated_kept": 0,        # generated rimasto generated
        "missing_capital": 0,
        "tagged_existing": 0,
        "by_strategy": Counter(),
        "by_type_enriched": Counter(),
        "disputed_matches": 0,
    }

    modified = False

    for entity in entities:
        # 1. Boundary reale presente: skip (e tagga se manca boundary_source)
        if _is_real_polygon(entity):
            if _tag_existing_real_polygon(entity):
                stats["tagged_existing"] += 1
                modified = True
            stats["skipped_real"] += 1
            continue

        # 2. Tenta Natural Earth (per generated-upgrade o per missing/point)
        match: Optional[MatchResult] = None
        if not skip_natural_earth and ne_by_iso:
            match = match_entity(entity, ne_by_iso)

        if match and match.matched:
            was_generated = _is_generated_polygon(entity)
            _apply_natural_earth_match(entity, match)
            modified = True
            if was_generated:
                stats["ne_matched_upgrade"] += 1
            else:
                stats["ne_matched_new"] += 1
            stats["by_strategy"][match.strategy] += 1
            stats["by_type_enriched"][entity.get("entity_type", "?")] += 1
            if match.is_disputed:
                stats["disputed_matches"] += 1
            continue

        # 3. Nessun NE match: genera approssimativo (solo se ha capitale)
        if _is_missing_or_point(entity):
            if not _has_valid_capital(entity):
                stats["missing_capital"] += 1
                logger.warning(
                    "%s: %s — manca capitale, skip",
                    filepath.name,
                    entity.get("name_original", "?"),
                )
                continue
            _apply_generated_boundary(entity)
            modified = True
            stats["generated_new"] += 1
            stats["by_strategy"]["generated"] += 1
            stats["by_type_enriched"][entity.get("entity_type", "?")] += 1
        else:
            # Era gia' un poligono generato e non c'e' match NE: lascio com'e'
            stats["generated_kept"] += 1

    # Scrivi (se non dry-run e qualcosa e' cambiato)
    if modified and not dry_run:
        backup = _backup_file(filepath)
        logger.info("Backup creato: %s", backup.name)
        filepath.write_text(
            json.dumps(entities, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Scritto: %s", filepath.name)
    elif modified and dry_run:
        logger.info("[DRY RUN] %s sarebbe stato modificato", filepath.name)

    return stats


def process_all(
    dry_run: bool = False,
    skip_natural_earth: bool = False,
    ne_processed_path: Path = NE_PROCESSED_JSON,
) -> dict:
    """Processa tutti i file batch in data/entities/.

    Returns: aggregato di tutte le statistiche per file.
    """
    batch_files = sorted(BATCHES_DIR.glob("batch_*.json"))
    if not batch_files:
        logger.error("Nessun file batch trovato in %s", BATCHES_DIR)
        return {}

    # Carica Natural Earth (preferenza: file processato; fallback: import on-the-fly)
    ne_by_iso: dict[str, dict] = {}
    if not skip_natural_earth:
        if ne_processed_path.exists():
            logger.info("Carico Natural Earth processato: %s", ne_processed_path)
            ne_by_iso = json.loads(ne_processed_path.read_text(encoding="utf-8"))
        else:
            logger.info(
                "File processato Natural Earth non trovato (%s) — eseguo import on-the-fly",
                ne_processed_path,
            )
            try:
                ne_by_iso = import_natural_earth(dry_run=dry_run)
            except Exception:
                logger.exception("Import Natural Earth fallito — proseguo senza")
                ne_by_iso = {}
        logger.info("Caricate %d entita' Natural Earth", len(ne_by_iso))

    print()
    print("=" * 78)
    print(f"  AtlasPI — Boundary Enrichment Pipeline {'[DRY RUN]' if dry_run else ''}")
    if skip_natural_earth:
        print("  Modalita': solo generazione (Natural Earth disabilitato)")
    print("=" * 78)
    print()

    aggregate = {
        "total": 0,
        "skipped_real": 0,
        "ne_matched_new": 0,
        "ne_matched_upgrade": 0,
        "generated_new": 0,
        "generated_kept": 0,
        "missing_capital": 0,
        "tagged_existing": 0,
        "by_strategy": Counter(),
        "by_type_enriched": Counter(),
        "disputed_matches": 0,
        "files_processed": 0,
    }

    for filepath in batch_files:
        stats = process_file(
            filepath, ne_by_iso, dry_run=dry_run, skip_natural_earth=skip_natural_earth
        )
        for k in (
            "total","skipped_real","ne_matched_new","ne_matched_upgrade",
            "generated_new","generated_kept","missing_capital","tagged_existing",
            "disputed_matches",
        ):
            aggregate[k] += stats[k]
        aggregate["by_strategy"] += stats["by_strategy"]
        aggregate["by_type_enriched"] += stats["by_type_enriched"]
        aggregate["files_processed"] += 1

        print(
            f"  {filepath.name:35s} "
            f"total={stats['total']:>3} "
            f"skip_real={stats['skipped_real']:>3} "
            f"ne_new={stats['ne_matched_new']:>3} "
            f"ne_upg={stats['ne_matched_upgrade']:>3} "
            f"gen_new={stats['generated_new']:>3} "
            f"gen_kept={stats['generated_kept']:>3}"
        )

    print()
    print("=" * 78)
    print("  AGGREGATE SUMMARY")
    print("=" * 78)
    print(f"  Files processed:           {aggregate['files_processed']}")
    print(f"  Total entities:            {aggregate['total']}")
    print(f"  Skipped (real polygon):    {aggregate['skipped_real']}")
    print(f"  Tagged-only (legacy real): {aggregate['tagged_existing']}")
    print(f"  NE matched (new boundary): {aggregate['ne_matched_new']}")
    print(f"  NE matched (upgrade gen):  {aggregate['ne_matched_upgrade']}")
    print(f"  Generated (new boundary):  {aggregate['generated_new']}")
    print(f"  Generated (kept as-is):    {aggregate['generated_kept']}")
    print(f"  Missing capital (skip):    {aggregate['missing_capital']}")
    print(f"  Disputed matches (ETHICS): {aggregate['disputed_matches']}")
    print()
    print("  By strategy (this run):")
    for strat, n in aggregate["by_strategy"].most_common():
        print(f"    {strat:25s} {n}")
    print()
    print("  By entity type (enriched/upgraded):")
    for et, n in aggregate["by_type_enriched"].most_common():
        print(f"    {et:25s} {n}")
    print()

    # Coverage projection
    real_total = aggregate["skipped_real"] + aggregate["ne_matched_new"] + aggregate["ne_matched_upgrade"]
    gen_total = aggregate["generated_new"] + aggregate["generated_kept"]
    if aggregate["total"] > 0:
        real_pct = real_total / aggregate["total"] * 100
        gen_pct = gen_total / aggregate["total"] * 100
        none_pct = aggregate["missing_capital"] / aggregate["total"] * 100
        print(f"  COVERAGE (after this run):")
        print(f"    Real boundaries:         {real_total} ({real_pct:.1f}%)")
        print(f"    Generated boundaries:    {gen_total} ({gen_pct:.1f}%)")
        print(f"    No boundary (no capital): {aggregate['missing_capital']} ({none_pct:.1f}%)")
    print("=" * 78)

    if dry_run:
        print("  DRY RUN — nessun file modificato")
    else:
        print("  Done. Backup .bak per ogni file modificato.")
    print("=" * 78)
    print()

    return aggregate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stampa cosa sarebbe modificato senza scrivere file.",
    )
    parser.add_argument(
        "--skip-natural-earth",
        action="store_true",
        help="Non usa Natural Earth (solo generated).",
    )
    parser.add_argument(
        "--ne-processed",
        type=Path,
        default=NE_PROCESSED_JSON,
        help=f"Path del file Natural Earth processato (default: {NE_PROCESSED_JSON})",
    )
    args = parser.parse_args()

    try:
        process_all(
            dry_run=args.dry_run,
            skip_natural_earth=args.skip_natural_earth,
            ne_processed_path=args.ne_processed,
        )
    except Exception:
        logger.exception("Errore nella pipeline di arricchimento boundary")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
