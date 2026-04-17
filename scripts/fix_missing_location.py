"""Assign representative locations to multi-region events missing lat/lon.

These 11 events are legitimately multi-region (pandemics, genocides
across empires, global treaties), but lack of lat/lon makes them
invisible on the map. We assign a symbolic center point representing
the core historical locus while preserving the full scope in
location_name.

Convention:
  - Perpetrator-centric for state-organized atrocities (Tokyo for
    Japanese comfort women system, London for Operation Legacy)
  - Peak/most-affected-location for epidemics/famines (Paris for Black
    Death's European peak, Kyiv for Holodomor, Auschwitz for the Shoah)
  - Origin/declaration point for other declared events

Run:
    python -m scripts.fix_missing_location           # apply
    python -m scripts.fix_missing_location --dry-run # preview
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

EVENTS_DIR = _PROJECT_ROOT / "data" / "events"

# name_original → (lat, lon, explanation_for_ethical_notes)
LOCATION_FILLS = {
    "Damnatio memoriae Getae": (
        41.9028, 12.4964,
        "Rome as empire-wide decree origin; the damnatio affected inscriptions throughout the Empire",
    ),
    "Mors Nigra": (
        48.8566, 2.3522,
        "Paris representing European peak of Black Death (1348-1350); pandemic spanned Eurasia + North Africa",
    ),
    "Révolution haïtienne et abolition dans les empires européens": (
        18.5944, -72.3074,
        "Port-au-Prince as origin of Haitian Revolution (1791-1804); abolition cascade spanned Atlantic empires",
    ),
    "Scramble for Africa / Partage de l'Afrique": (
        52.5200, 13.4050,
        "Berlin Conference (1884-85) as colonial partition venue; actual violence spanned entire African continent",
    ),
    "Հայոց ցեղասպանություն": (
        39.9264, 41.1025,
        "Erzurum (eastern Anatolia) as representative epicenter of Armenian Genocide; deportations to Syrian deserts",
    ),
    "1918 Influenza Pandemic": (
        39.0458, -97.3714,
        "Fort Riley, Kansas as likely origin point of 1918 H1N1 pandemic; spread globally in <12 months",
    ),
    "日本軍慰安婦制度": (
        35.6762, 139.6503,
        "Tokyo as organizer of the system; victims were drawn from occupied Korea, China, Philippines, Indonesia, Taiwan, Burma, Pacific",
    ),
    "Голодомор": (
        50.4501, 30.5234,
        "Kyiv as Ukrainian center; famine also affected Kuban (North Caucasus)",
    ),
    "השואה": (
        50.0355, 19.1783,
        "Auschwitz-Birkenau as symbol of industrialized genocide; Shoah spanned Nazi Germany and occupied Europe",
    ),
    "Partition of India / ਭਾਰਤ ਦੀ ਵੰਡ / भारत का विभाजन": (
        30.0668, 76.4792,
        "Radcliffe Line across Punjab; partition violence also affected Bengal (east) with millions displaced and killed",
    ),
    "Operation Legacy": (
        51.5074, -0.1278,
        "London as origin of the UK Colonial Office's systematic destruction of colonial records; operation spanned decolonizing UK colonies globally",
    ),
}


def fix_file(filepath: Path, dry_run: bool = False) -> tuple[int, int]:
    """Apply location fills. Returns (changed, total)."""
    with filepath.open(encoding="utf-8") as f:
        events = json.load(f)

    changed = 0
    for e in events:
        if e.get("location_lat") is not None:
            continue
        name = e.get("name_original", "")
        fill = LOCATION_FILLS.get(name)
        if fill is None:
            # Try substring match
            for key, value in LOCATION_FILLS.items():
                if key in name or name in key:
                    fill = value
                    break
        if fill:
            lat, lon, explanation = fill
            e["location_lat"] = lat
            e["location_lon"] = lon
            # Append to ethical_notes
            note_marker = "[v6.30-representative-location]"
            loc_note = (
                f"{note_marker} location_lat/lon represent a symbolic center; "
                f"actual event scope was broader. {explanation}."
            )
            existing = e.get("ethical_notes") or ""
            if note_marker not in existing:
                e["ethical_notes"] = (existing + "\n\n" if existing else "") + loc_note
            changed += 1

    if changed > 0 and not dry_run:
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

    return (changed, len(events))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Filling representative location for multi-region events in {EVENTS_DIR}...")
    total_changed = 0
    for fp in sorted(EVENTS_DIR.glob("batch_*.json")):
        if fp.name.endswith(".bak"):
            continue
        changed, total = fix_file(fp, dry_run=args.dry_run)
        if changed > 0:
            print(f"  {fp.name}: fixed {changed}/{total}")
            total_changed += changed

    print(f"\nTotal: {total_changed} events updated")
    if args.dry_run:
        print("(dry-run — no files written)")


if __name__ == "__main__":
    main()
