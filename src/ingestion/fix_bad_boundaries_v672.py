"""Second targeted boundary fix batch (v6.7.2).

Context: after v6.7.1 cleaned up shared-polygon clusters and placeholder
rectangles, a deeper audit run (capital-to-centroid displacement >500 km
on confirmed entities + area sanity checks by entity_type) surfaced a new
class of single-entity defects:

  - **Wrong-polygon matches** where a small kingdom inherited a
    continent-scale polygon via a fuzzy-name collision with a much
    bigger entity at ingest time (e.g. Commagene matched to a polygon
    spanning 20M km², Oceti Sakowin inheriting full USA polygon,
    Transylvania principality mapped to 25M km²).

  - **Vassal-inclusion bloat** where aourednik polygons encoded the
    maximum nominal sovereignty (incl. vassals/client regions) rather
    than the polity's effective territory (Normandy duchy carrying a
    1.5M km² polygon that likely encodes Plantagenet holdings;
    Brittany similar).

All fixes replace the bad polygon with a `name_seeded_boundary` of
realistic radius, keeping the entity's capital as anchor. Provenance
fields (boundary_aourednik_*, boundary_ne_iso_a3) are cleared and
`boundary_source` becomes `approximate_generated`. `confidence_score`
capped to APPROX_CONFIDENCE (0.4) per ETHICS-004.

Radii chosen from historical-geography sources (rough peak extents):

  | Entity                        | Peak ~km² | Radius km |
  |-------------------------------|-----------|-----------|
  | Commagene                     | 15 000    | 70        |
  | Misiones Guaraníes            | 200 000   | 250       |
  | Oceti Sakowin (Great Plains)  | 1 500 000 | 700       |
  | Lanfang Gongheguo (Borneo)    | 50 000    | 125       |
  | Nanzhao                       | 500 000   | 400       |
  | Transylvania principality     | 60 000    | 140       |
  | Polatsk principality          | 100 000   | 180       |
  | Normandy duchy                | 30 000    | 100       |
  | Brittany duchy                | 30 000    | 100       |
  | Finland Grand Duchy           | 390 000   | 350       |
  | Grand Duchy of Lithuania      | 900 000   | 500       |

Idempotent. Usage:
    python -m src.ingestion.fix_bad_boundaries_v672 --dry-run
    python -m src.ingestion.fix_bad_boundaries_v672 --apply
"""

from __future__ import annotations

import argparse
import io
import logging
import sys

from src.ingestion.fix_bad_boundaries_v671 import (
    EntityFix,
    run_fixes as _run_fixes_with_custom,
)

logger = logging.getLogger(__name__)

# Shared with v671 (import avoids duplication)
APPROX_CONFIDENCE = 0.4

# Note explaining the v6.7.2 repair class — appended once per entity.
V672_NOTE = (
    "[v6.7.2] boundary precedente era un mismatch geografico "
    "(polygon >10x l'estensione storica attesa). Sostituito con "
    "name_seeded_boundary ancorato alla capital. Vedi ETHICS-006."
)


FIXES_V672: list[EntityFix] = [
    # Commagene: small Hellenistic kingdom in SE Anatolia (cap. Samosata).
    # Actual extent ~15k km²; previous aourednik polygon was ~20M km².
    EntityFix(
        entity_id=282,
        reason="Commagene kingdom: previous polygon 20M km² (wrong match); restoring ~15k km² kingdom scale",
        regenerate_with_radius_km=70.0,
        append_note=V672_NOTE,
    ),
    # Misiones Guaraníes: Jesuit reductions between Paraná and Uruguay.
    # Actual extent ~200k km²; previous polygon 20.6M km² is continental.
    EntityFix(
        entity_id=227,
        reason="Misiones Guaraníes: previous polygon 20M km² (continental); restoring ~200k km² mission-belt scale",
        regenerate_with_radius_km=250.0,
        append_note=V672_NOTE,
    ),
    # Oceti Sakowin: Seven Council Fires, Great Plains confederation.
    # Actual range ~1.5M km²; previous NE polygon was entire USA (232M km²).
    EntityFix(
        entity_id=727,
        reason="Oceti Sakowin: previous polygon was entire USA (232M km²); restoring ~1.5M km² Great Plains range",
        regenerate_with_radius_km=700.0,
        append_note=V672_NOTE,
    ),
    # Lanfang Gongheguo: West Kalimantan Chinese republic.
    # Actual extent ~50k km²; previous NE polygon 9.5M km² (wrong country).
    EntityFix(
        entity_id=705,
        reason="Lanfang: previous polygon 9.5M km² (wrong country match); restoring ~50k km² West Kalimantan scale",
        regenerate_with_radius_km=125.0,
        append_note=V672_NOTE,
    ),
    # Nanzhao: Tibeto-Burman kingdom in Yunnan.
    # Actual extent ~500k km²; previous polygon 7.8M km² likely Ming-era Yunnan+vassals.
    EntityFix(
        entity_id=454,
        reason="Nanzhao: previous polygon 7.8M km² (likely later-era Yunnan projection); restoring ~500k km²",
        regenerate_with_radius_km=400.0,
        append_note=V672_NOTE,
    ),
    # Principality of Transylvania (Ottoman vassal).
    # Actual extent ~60k km²; previous aourednik polygon 25M km² — continental mismatch.
    EntityFix(
        entity_id=575,
        reason="Transylvania principality: previous polygon 25M km² (continental); restoring ~60k km²",
        regenerate_with_radius_km=140.0,
        append_note=V672_NOTE,
    ),
    # Polatsk Principality (Kievan Rus' era).
    # Actual extent ~100k km²; previous polygon 1.5M km² (likely all-Rus scope).
    EntityFix(
        entity_id=679,
        reason="Polatsk principality: previous polygon 1.5M km² (likely all-Rus scope); restoring ~100k km²",
        regenerate_with_radius_km=180.0,
        append_note=V672_NOTE,
    ),
    # Duchy of Normandy.
    # Actual extent ~30k km²; previous polygon 1.5M km² (likely Plantagenet empire scope).
    EntityFix(
        entity_id=651,
        reason="Normandy duchy: previous polygon 1.5M km² (Plantagenet scope); restoring ~30k km²",
        regenerate_with_radius_km=100.0,
        append_note=V672_NOTE,
    ),
    # Duchy of Brittany.
    # Actual extent ~30k km²; previous polygon 1.3M km² (likely wrong match).
    EntityFix(
        entity_id=566,
        reason="Brittany duchy: previous polygon 1.3M km² (continental mismatch); restoring ~30k km²",
        regenerate_with_radius_km=100.0,
        append_note=V672_NOTE,
    ),
    # Finland Grand Duchy (Russian autonomy 1809-1917).
    # Actual extent ~390k km²; previous polygon 1.4M km² (probably included Russian Karelia).
    EntityFix(
        entity_id=427,
        reason="Finland Grand Duchy: previous polygon 1.4M km² (included Russian territories); restoring ~390k km²",
        regenerate_with_radius_km=350.0,
        append_note=V672_NOTE,
    ),
    # Grand Duchy of Lithuania (peak pre-Union of Lublin).
    # Actual extent at peak ~900k km² (included Ruthenian lands); previous polygon 3M km².
    EntityFix(
        entity_id=653,
        reason="Grand Duchy of Lithuania: previous polygon 3M km² (oversized even at peak); restoring ~900k km²",
        regenerate_with_radius_km=500.0,
        append_note=V672_NOTE,
    ),
]


def run_v672_fixes(*, dry_run: bool = True) -> dict:
    """Apply FIXES_V672 using the v671 engine."""
    # Monkey-swap: the engine consumes a module-level FIXES list.
    # Simplest: import engine's module and swap its FIXES temporarily.
    from src.ingestion import fix_bad_boundaries_v671 as engine

    original = engine.FIXES
    engine.FIXES = FIXES_V672
    try:
        return engine.run_fixes(dry_run=dry_run)
    finally:
        engine.FIXES = original


def main() -> int:
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true",
                       help="Compute without writing (default).")
    group.add_argument("--apply", action="store_true",
                       help="Perform mutations.")
    args = parser.parse_args()

    dry_run = not args.apply

    result = run_v672_fixes(dry_run=dry_run)

    print(f"\n=== fix_bad_boundaries_v672 (dry_run={dry_run}) ===\n")
    for k, v in result.items():
        print(f"  {k:<25} {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
