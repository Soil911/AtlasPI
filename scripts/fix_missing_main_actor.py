"""Fill main_actor for natural-disaster events where it's missing.

Natural disasters (volcanic eruptions, earthquakes, epidemics, famines,
tsunamis, climate collapses) don't have a human 'main_actor' in the
traditional sense — but the field should document the natural force +
affected populations so the data is complete and meaningful.

Run:
    python -m scripts.fix_missing_main_actor           # apply
    python -m scripts.fix_missing_main_actor --dry-run # preview
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

# Mapping: event name (or part of it) → main_actor text
# Descriptions combine the natural force + affected populations/context.
MAIN_ACTOR_FILLS = {
    "Eruptio Vesuvii": (
        "Mount Vesuvius Plinian eruption (VEI 5); affected populations "
        "of Pompeii, Herculaneum, Stabiae, and Oplontis (Roman Campania)"
    ),
    "Pestis Antonina": (
        "Antonine Plague pathogen (likely smallpox or measles); affected "
        "populations of the Roman Empire during Marcus Aurelius's reign, "
        "brought from Mesopotamia by returning legions"
    ),
    "K'atun terminal Classic Maya collapse": (
        "Compound climate stress, endemic warfare, and political fragmentation; "
        "affected Classic Maya city-states (Tikal, Calakmul, Copán, Palenque) "
        "and their populations across southern lowlands"
    ),
    "大津波 Jōgan 貞観地震": (
        "Tectonic subduction earthquake (estimated M8.6) and tsunami off "
        "Sanriku coast; affected populations of Mutsu Province (Heian Japan) "
        "during the Jōgan era"
    ),
    "Samalas ᬲᬫᬮᬲ᭄": (
        "Mount Samalas supervolcanic eruption (VEI 7), Lombok; triggered "
        "global atmospheric cooling 1257-1258, affected North Atlantic, "
        "European, and Asian climates — one of the largest eruptions of the "
        "last 2000 years"
    ),
    "明末大饑饉": (
        "Late Ming dynasty famine during state collapse; combination of "
        "Little Ice Age climate deterioration, fiscal breakdown, and Li "
        "Zicheng's rebellion. Affected peasant populations of Shaanxi, Henan, "
        "and North China (estimated millions of deaths 1627-1644)"
    ),
    "Terremoto di Lisbona": (
        "Tectonic megathrust earthquake (M8.5-9.0) offshore Iberian Peninsula "
        "followed by tsunami and city-wide fires; affected populations of "
        "Lisbon, Algarve coast, and western Morocco (Kingdom of Portugal and "
        "Moroccan Alaouite Sultanate)"
    ),
    "Tambora 1815": (
        "Mount Tambora VEI-7 supereruption on Sumbawa, Dutch East Indies; "
        "triggered 'Year Without a Summer' (1816) globally, affecting "
        "agricultural populations across North America, Europe, and East Asia"
    ),
    "Krakatau": (
        "Mount Krakatau VEI-6 cataclysmic eruption, Sunda Strait; affected "
        "coastal populations of Java and Sumatra (Dutch East Indies) plus "
        "global atmospheric and climatic impact (2-year cooling)"
    ),
    "2004 Indian Ocean tsunami": (
        "Sumatra-Andaman undersea megathrust earthquake (M9.1-9.3); affected "
        "populations in 14 Indian Ocean countries — primarily Indonesia (Aceh), "
        "Sri Lanka, India (Tamil Nadu), Thailand, and Somalia"
    ),
}


def fix_file(filepath: Path, dry_run: bool = False) -> tuple[int, int]:
    """Apply main_actor fills. Returns (changed, total)."""
    with filepath.open(encoding="utf-8") as f:
        events = json.load(f)

    changed = 0
    for e in events:
        name = e.get("name_original", "")
        if e.get("main_actor"):
            continue
        # Match name against fill keys
        fill_text = None
        for key, text in MAIN_ACTOR_FILLS.items():
            if key == name or key in name:
                fill_text = text
                break
        if fill_text:
            e["main_actor"] = fill_text
            changed += 1

    if changed > 0 and not dry_run:
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

    return (changed, len(events))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Filling missing main_actor on natural-disaster events in {EVENTS_DIR}...")
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
