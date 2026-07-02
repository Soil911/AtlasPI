"""Backport dello `status` prod → JSON sorgente (riconciliazione ETHICS-012 cont.).

Contesto (2026-07-02): il diff completo prod↔JSON ha trovato **66 divergenze di
status** mai backportate — in gran parte le deprecazioni del merge duplicati
v6.85 (`scripts/merge_duplicate_entities.sql`, 44 secondarie → primary) e le
ricalibrazioni confirmed↔uncertain dei pass di coerenza prod. Senza backport un
fresh-seed **resuscita i duplicati** come record validi (la distorsione peggiore
— vedi ETHICS-012 sotto-decisione #2) e i test girano su fixture irrealistiche.

# ETHICS-012: prod e' la fonte di verita' per lo status (decisioni di merge e
# ricalibrazione documentate nei pass v6.85/phase-H). Precedente: backport
# v6.99.93 (stessa classe, cross-check ChatGPT SOUND-WITH-CAVEATS).
# FUORI SCOPE ESPLICITO: confidence_score (drift BIDIREZIONALE, ~299 entita' —
# richiede una policy di riconciliazione dedicata, non un backport meccanico)
# e ethical_notes (esclusione gia' accettata e documentata in ETHICS-012 §3).

Input:  data/fixes/prod_status_export_20260702.json (export read-only da prod)
Output: edit in-place dei data/entities/*.json (line-ending preservati)

Semantica dedup: il seed usa **last-wins** per name_original (batch correttivi)
— lo status va scritto sul record VINCENTE; i record ombreggiati vengono
allineati anch'essi (harmless, evita confusione futura).

Usage: PYTHONUTF8=1 python -m scripts.backport_status_to_json [--dry-run]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

EXPORT = Path("data/fixes/prod_status_export_20260702.json")
ENTITIES_DIR = Path("data/entities")


def _newline_of(path: Path) -> str:
    return "\r\n" if b"\r\n" in path.read_bytes() else "\n"


def main() -> None:
    dry = "--dry-run" in sys.argv
    prod = {e["name_original"]: e["status"] for e in json.loads(EXPORT.read_text(encoding="utf-8"))}

    changed_files: dict[Path, list] = {}
    changes: list[str] = []
    json_names: set[str] = set()
    json_deprecated_not_in_prod: list[str] = []

    files = sorted(ENTITIES_DIR.glob("*.json"))
    data_by_file = {p: json.loads(p.read_text(encoding="utf-8")) for p in files}

    for path in files:
        for ent in data_by_file[path]:
            name = ent.get("name_original", "")
            json_names.add(name)
            prod_status = prod.get(name)
            if prod_status is None:
                # entita' JSON assente in prod (rename nativo non ancora
                # sincronizzato — debito ETHICS-001, fuori scope qui)
                if ent.get("status") == "deprecated":
                    json_deprecated_not_in_prod.append(name)
                continue
            if ent.get("status") != prod_status:
                changes.append(f"{name[:45]:45} {ent.get('status'):>10} -> {prod_status:<10} ({path.name})")
                ent["status"] = prod_status
                changed_files.setdefault(path, data_by_file[path])

    print(f"Divergenze status corrette: {len(changes)} (in {len(changed_files)} file)")
    for c in changes:
        print("  ", c)

    only_prod = sorted(set(prod) - json_names)
    if only_prod:
        print(f"\nNomi solo-prod (rename nativi non sincronizzati — ETHICS-001 debt, NON toccati): {len(only_prod)}")
        for n in only_prod:
            print("   P:", n)
    if json_deprecated_not_in_prod:
        print("\nANOMALIA — deprecated in JSON ma nome assente in prod:", json_deprecated_not_in_prod)

    if dry:
        print("\n--dry-run: nessun file scritto.")
        return
    for path, data in changed_files.items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        with path.open("w", encoding="utf-8", newline=_newline_of(path)) as f:
            f.write(text)
    print(f"\nScritti {len(changed_files)} file.")


if __name__ == "__main__":
    main()
