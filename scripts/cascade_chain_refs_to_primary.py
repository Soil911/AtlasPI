"""Cascata JSON dei chain-ref → primary del merge v6.85 (ETHICS-001/ADR-005).

Il merge duplicati v6.85 ridiresse le FK di prod (Pass 4 di
``scripts/merge_duplicate_entities.sql``) ma NON cascadò i riferimenti
per-nome nei ``data/chains/*.json``. Finché i duplicati risultavano
'confirmed' nel JSON il fresh-seed li ri-linkava (silenziosamente); col
backport-status v6.99.107 quei nomi sono deprecati anche nel JSON e il
fence ``tests/test_chain_deprecated_json_audit.py`` li ha esposti tutti.

# ETHICS-001: ogni primary ha il nome nella lingua/scrittura locale
# (Xšāça, ዛግዌ, ᏣᎳᎩ, Mvskoke, ...) — la cascata sostituisce forme latine
# o duplicate con la forma locale primaria.
# Prod NON va toccata: le sue chain_links puntano già alle primary.

Mappa derivata da merge_duplicate_entities.sql + export prod 2026-07-02.
Usage: PYTHONUTF8=1 python -m scripts.cascade_chain_refs_to_primary
(idempotente: alla seconda esecuzione non trova più nulla da sostituire)
"""

from __future__ import annotations

import json
from pathlib import Path

CHAINS_DIR = Path("data/chains")

# nome deprecato (secondary) → nome primary (native, verificato su prod)
CASCADE = {
    "Virreinato del Peru": "Virreinato del Perú",          # 709 → 206
    "هخامنشیان": "Xšāça",                                   # 847 → 27
    "سلطنت دہلی": "دلّی سلطنت",                             # 848 → 112
    "سلطنت مغلیہ": "مغلیہ سلطنت",                           # 849 → 12
    "Zagwe": "ዛግዌ",                                         # 854 → 491
    "Mengist Ityop'p'ya": "የኢትዮጵያ ንጉሠ ነገሥት መንግሥት",      # 855 → 24
    "المرينيون": "الدولة المرينية",                          # 482 → 187
    "Oyo": "Ọyọ́",                                           # 851 → 151
    "Daular Usmaniyya ta Sakkwato": "خلافة سكتو",           # 852 → 150
    "آل بويه": "آل بویه",                                    # 494 → 475
    "Tsalagi": "ᏣᎳᎩ",                                       # 859 → 218
    "Muscogee": "Mvskoke",                                  # 726 → 219
}


def main() -> None:
    # Chirurgia a stringa (byte-preserving): molti file catene sono in
    # formato compatto e una ri-serializzazione JSON li riformatterebbe
    # per intero, inquinando diff e blame.
    total = 0
    for path in sorted(CHAINS_DIR.glob("*.json")):
        raw = path.read_bytes().decode("utf-8")
        new = raw
        touched = 0
        for old_name, new_name in CASCADE.items():
            # entrambe le forme di serializzazione: UTF-8 raw e \uXXXX-escaped
            for old_ser, new_ser in (
                (json.dumps(old_name, ensure_ascii=False), json.dumps(new_name, ensure_ascii=False)),
                (json.dumps(old_name, ensure_ascii=True), json.dumps(new_name, ensure_ascii=True)),
            ):
                needle = f'"entity_name": {old_ser}'
                n = new.count(needle)
                if n:
                    new = new.replace(needle, f'"entity_name": {new_ser}')
                    touched += n
        if touched:
            json.loads(new)  # sanity: il risultato resta JSON valido
            path.write_bytes(new.encode("utf-8"))
            print(f"{path.name}: {touched} ref cascadati")
            total += touched
    print(f"Totale: {total} riferimenti cascadati alle primary.")


if __name__ == "__main__":
    main()
