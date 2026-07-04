"""M4 — dedup dei 30 record JSON ombreggiati.

⚠️ NON ESEGUITO in v6.99.124 — richiede una revisione (vincolo scoperto sotto).

Il seed (`src/db/seed.py`) deduplica per nome ma con semantica
FIRST-POSITION + LAST-DATA: la PRIMA occorrenza di un nome fissa la POSIZIONE
(quindi l'id auto-increment del fresh-seed), le occorrenze successive
SOVRASCRIVONO solo i DATI a quella posizione.

Conseguenza (scoperta 2026-07-04, ha rotto `tests/test_v673_boundary_cleanup.py`):
- rimuovere la copia in PRIMA posizione → il nome "scivola" alla posizione
  della copia successiva → **shift di tutti gli id seguenti** → i test che
  dipendono dall'id-order del seed (v673) falliscono.
- rimuovere una copia SUCCESSIVA → posizione invariata (id stabili) MA i dati
  del fresh-seed tornano a quelli della PRIMA copia, che spesso ha MENO fonti
  di quella successiva (es. `batch_32_confidence_boost` è un superset).

Riconciliazione CORRETTA (per una sessione dedicata):
  per ogni nome duplicato, rimuovere SOLO la/le occorrenza/e SUCCESSIVA/E e,
  se la prima copia ha dati più poveri di prod, MERGE-are nel record in prima
  posizione i dati (fonti/varianti/anni/conf) della copia rimossa (che è quella
  che il seed last-wins usava e che prod ha). Così id-order e dati restano
  entrambi allineati a prod.

Il piano `data/fixes/shadow_dedup_plan_20260704.json` va rifatto con questo
vincolo (attualmente rimuoveva alcune prime-occorrenze → NON usarlo così).

Input:  data/fixes/shadow_dedup_plan_20260704.json (DA RIFARE position-aware)
Usage:  PYTHONUTF8=1 python -m scripts.apply_shadow_dedup [--dry-run]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PLAN = Path("data/fixes/shadow_dedup_plan_20260704.json")
ENT = Path("data/entities")


def find_record_span(raw: str, name: str) -> tuple[int, int]:
    """Ritorna (start, end) dell'oggetto record che ha name_original == name.

    start = indice della '{' che apre il record; end = indice DOPO la '}' che lo chiude.
    """
    anchor = f'"name_original": "{name}"'
    ai = raw.find(anchor)
    if ai < 0:
        raise AssertionError(f"anchor non trovato: {name!r}")
    if raw.find(anchor, ai + 1) >= 0:
        raise AssertionError(f"anchor non unico: {name!r}")
    # opening brace = la '{' immediately before anchor (solo whitespace tra i due)
    j = ai - 1
    while j >= 0 and raw[j] in " \t\r\n":
        j -= 1
    assert raw[j] == "{", f"atteso {{ prima di name_original, trovato {raw[j]!r}"
    start = j
    # scan forward con depth counting, saltando stringhe
    depth = 0
    i = start
    in_str = False
    esc = False
    while i < len(raw):
        c = raw[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return start, i + 1
        i += 1
    raise AssertionError(f"chiusura non trovata per {name!r}")


def remove_record(path: Path, name: str, dry: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    start, end = find_record_span(raw, name)
    # includi una virgola adiacente (prima o dopo) + whitespace, per non rompere l'array
    a = start
    # guarda indietro fino a un ',' o '['
    k = start - 1
    while k >= 0 and raw[k] in " \t\r\n":
        k -= 1
    if raw[k] == ",":
        # rimuovi la virgola precedente + whitespace tra virgola e record
        a = k
    else:
        # è il primo elemento: rimuovi la virgola SEGUENTE + whitespace
        m = end
        while m < len(raw) and raw[m] in " \t\r\n":
            m += 1
        if m < len(raw) and raw[m] == ",":
            end = m + 1
    new = raw[:a] + raw[end:]
    # valida JSON
    arr = json.loads(new)
    assert not any(e.get("name_original") == name for e in arr) or \
        sum(1 for e in arr if e.get("name_original") == name) < \
        sum(1 for e in json.loads(raw) if e.get("name_original") == name), "rimozione non ha ridotto il conteggio"
    if not dry:
        path.write_bytes(new.encode("utf-8"))
    print(f"  {'[dry] ' if dry else ''}removed {name!r} from {path.name} (record {end-start if False else ''})")


def fix_confidence(path: Path, name: str, conf: float, dry: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    start, end = find_record_span(raw, name)
    rec = raw[start:end]
    import re
    m = re.search(r'"confidence_score":\s*[0-9.]+', rec)
    assert m, f"confidence non trovata in {name!r}"
    newrec = rec[:m.start()] + f'"confidence_score": {conf}' + rec[m.end():]
    new = raw[:start] + newrec + raw[end:]
    json.loads(new)
    if not dry:
        path.write_bytes(new.encode("utf-8"))
    print(f"  {'[dry] ' if dry else ''}fixed conf {name!r} → {conf} [{path.name}]")


def main():
    dry = "--dry-run" in sys.argv
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    removed = 0
    fixed = 0
    # prima le rimozioni, poi i fix (i fix sono su record che restano)
    for op in plan:
        if op["reason"].startswith("FIX"):
            continue
        remove_record(ENT / op["file"], op["name"], dry)
        removed += 1
    for op in plan:
        if not op["reason"].startswith("FIX"):
            continue
        conf = op["fix"][0]
        fix_confidence(ENT / op["file"], op["name"], conf, dry)
        fixed += 1
    print(f"\n{'[dry] ' if dry else ''}{removed} rimozioni, {fixed} fix confidence")


if __name__ == "__main__":
    main()
