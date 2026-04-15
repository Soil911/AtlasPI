"""Third targeted boundary fix batch (v6.7.3).

Context: after v6.7.2 scaled down 11 polygons using bounding-box area as
trigger, a follow-up audit using real geodesic polygon areas (via
shapely + pyproj.Geod) surfaced 4 remaining polities whose *actual*
polygon area (not bbox) is still >2x historical peak extent:

  | ID  | Entity                   | Post-v672 real area | Historical peak |
  |-----|--------------------------|--------------------:|----------------:|
  | 604 | Kalmyk/Hajar Khanate     | 13.3 M km²          | ~1 M km²        |
  | 343 | هوتکیان Hotaki dynasty   | 2.5 M km²           | ~1.5 M km²      |
  | 350 | Βακτριανή Bactria        | 2.8 M km²           | ~1 M km²        |
  | 330 | Казан ханлыгы (Kazan)    | 1.2 M km²           | ~700 k km²      |

All four carry aourednik polygons that encode "empire at nominal
maximum" rather than effective administration. We replace with
`name_seeded_boundary` anchored to the known capital, using a radius
calibrated to 1.2x-1.5x historical peak (conservative — visible as
approximation rather than over-claim).

Entity 604 deserves a note: its `name_original` is in Mongolian script
but `capital_name="Sarai-on-the-Volga (nomadic, near Astrakhan)"` and
year range 1634-1771 identify it as the **Kalmyk Khanate**, not the
earlier Khazar Khaganate (650-969). The polygon was matched to a label
encoding the composite steppe region which is much larger than the
effective Kalmyk territory.

Idempotent. Usage:
    python -m src.ingestion.fix_bad_boundaries_v673 --dry-run
    python -m src.ingestion.fix_bad_boundaries_v673 --apply
"""

from __future__ import annotations

import argparse
import io
import logging
import sys

from src.ingestion.fix_bad_boundaries_v671 import EntityFix

logger = logging.getLogger(__name__)

APPROX_CONFIDENCE = 0.4

V673_NOTE = (
    "[v6.7.3] aourednik polygon codificava estensione nominale composita "
    "(o dinastia successiva), >2x l'area effettiva storica. Sostituito con "
    "name_seeded_boundary ancorato al capital, radius calibrato al 1.2-1.5x "
    "del picco storico. Vedi ETHICS-006."
)

FIXES_V673: list[EntityFix] = [
    # Kalmyk Khanate: Caspian steppe, capital Sarai-on-Volga near Astrakhan.
    # Historical peak ~1M km²; post-v672 had 13.3M.
    EntityFix(
        entity_id=604,
        reason="Kalmyk Khanate (labeled Mongolian Hajar): 13.3M km² real area; restoring ~1.2M km² steppe",
        regenerate_with_radius_km=600.0,
        append_note=V673_NOTE,
    ),
    # Hotaki dynasty: Kandahar-based Afghan/Persian dynasty 1709-1738.
    # Peak extent during Mahmud's Isfahan campaign ~1.5M km².
    EntityFix(
        entity_id=343,
        reason="Hotaki dynasty: 2.5M km² real area; restoring ~1.5M km² Afghan-Persian",
        regenerate_with_radius_km=700.0,
        append_note=V673_NOTE,
    ),
    # Greco-Bactrian kingdom: Bactra (Balkh), Hellenistic Afghanistan 250 BCE - 125 CE.
    # Peak extent ~1M km² (Oxus basin + Indus).
    EntityFix(
        entity_id=350,
        reason="Bactria: 2.8M km² real area; restoring ~1M km² Greco-Bactrian",
        regenerate_with_radius_km=550.0,
        append_note=V673_NOTE,
    ),
    # Kazan Khanate: successor of Golden Horde, Kazan 1438-1552.
    # Peak extent ~700k km² (Middle Volga).
    EntityFix(
        entity_id=330,
        reason="Kazan Khanate: 1.2M km² real area; restoring ~700k km² Middle Volga",
        regenerate_with_radius_km=500.0,
        append_note=V673_NOTE,
    ),
]


def run_v673_fixes(*, dry_run: bool = True) -> dict:
    """Apply FIXES_V673 using the v671 engine."""
    from src.ingestion import fix_bad_boundaries_v671 as engine

    original = engine.FIXES
    engine.FIXES = FIXES_V673
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
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    dry_run = not args.apply
    result = run_v673_fixes(dry_run=dry_run)

    print(f"\n=== fix_bad_boundaries_v673 (dry_run={dry_run}) ===\n")
    for k, v in result.items():
        print(f"  {k:<25} {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
