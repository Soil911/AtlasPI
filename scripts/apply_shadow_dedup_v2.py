"""M4 — dedup position-aware dei 30 record JSON ombreggiati (v6.99.126).

Vincolo (scoperto v6.99.125): il seed deduplica FIRST-POSITION + LAST-DATA →
rimuovere una PRIMA-occorrenza shifta gli id auto-increment del fresh-seed
(rompe test_v673). Quindi:
  - il record sopravvissuto DEVE stare alla posizione della PRIMA occorrenza
    (nel file che viene per primo in ordine glob) → id-order preservato;
  - con i DATI del record canonico (quello che matcha prod: stessi anni, più
    fonti = superset che prod ha per last-wins), con conf/status forzati a prod.

Algoritmo per nome (tutti i 30 pair sono 2 copie in file DIVERSI):
  1. target = copia che matcha gli anni di prod; a parità, quella con più fonti.
     Forza conf/status del target ai valori prod.
  2. Se il contenuto del target ≠ prima copia: sostituisci l'oggetto della PRIMA
     copia col target (byte dell'oggetto, conf/status aggiustati).
  3. Rimuovi la copia SUCCESSIVA.

Sorgente-only (prod già corretta). Idempotente-ish (fallisce pulito se già fatto).
Usage: PYTHONUTF8=1 python -m scripts.apply_shadow_dedup_v2 [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ENT = Path("data/entities")
PROD_PSV = Path(r"C:\Users\cliri\AppData\Local\Temp\claude\C--Users-cliri-Documents-AtlasPI\ee41be87-6c8d-4d66-bd90-9335c30819d4\scratchpad\prod_full.psv")


def find_record_span(raw: str, name: str, occurrence: int = 0) -> tuple[int, int]:
    anchor = f'"name_original": "{name}"'
    ai = -1
    for _ in range(occurrence + 1):
        ai = raw.find(anchor, ai + 1)
        if ai < 0:
            raise AssertionError(f"anchor #{occurrence} non trovato: {name!r}")
    j = ai - 1
    while j >= 0 and raw[j] in " \t\r\n":
        j -= 1
    assert raw[j] == "{", f"atteso {{ prima di name_original ({name!r})"
    start = j
    depth = 0; i = start; in_str = False; esc = False
    while i < len(raw):
        c = raw[i]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return start, i + 1
        i += 1
    raise AssertionError(f"chiusura non trovata: {name!r}")


def remove_object(raw: str, start: int, end: int) -> str:
    """Rimuove l'oggetto [start,end) + una virgola adiacente."""
    a = start
    k = start - 1
    while k >= 0 and raw[k] in " \t\r\n":
        k -= 1
    if raw[k] == ",":
        a = k
    else:
        m = end
        while m < len(raw) and raw[m] in " \t\r\n":
            m += 1
        if m < len(raw) and raw[m] == ",":
            end = m + 1
    return raw[:a] + raw[end:]


def adjust(obj: str, conf: float, status: str) -> str:
    obj = re.sub(r'"confidence_score":\s*[0-9.]+', f'"confidence_score": {conf}', obj, count=1)
    obj = re.sub(r'"status":\s*"[^"]*"', f'"status": "{status}"', obj, count=1)
    return obj


def load_prod() -> dict[str, tuple]:
    # formato PSV: name~year_start~year_end(o NULL)~confidence~status
    prod = {}
    for line in PROD_PSV.read_text(encoding="utf-8").splitlines():
        p = line.split("~")
        if len(p) < 5:
            continue
        prod[p[0]] = (int(p[1]), None if p[2] == "NULL" else int(p[2]), float(p[3]), p[4])
    return prod


def main():
    dry = "--dry-run" in sys.argv
    prod = load_prod()

    # mappa nome → [(file, year_start, year_end, conf, status, nsrc)] in ordine glob
    by_name = defaultdict(list)
    files = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(ENT.glob("*.json"))}
    for fname in sorted(files):
        for e in files[fname]:
            n = e.get("name_original")
            if n:
                by_name[n].append((fname, e.get("year_start"), e.get("year_end"),
                                   e.get("confidence_score"), e.get("status", "confirmed"),
                                   len(e.get("sources", []))))
    shadow = {n: v for n, v in by_name.items() if len(v) > 1}
    print(f"pair ombreggiati: {len(shadow)}")

    done = 0
    for name, occ in sorted(shadow.items()):
        pr = prod.get(name)
        if not pr:
            print(f"  SKIP {name!r}: non in prod"); continue
        assert len(occ) == 2, f"{name}: {len(occ)} copie (atteso 2)"
        first, later = occ[0], occ[1]  # ordine glob
        # target = copia che matcha gli anni prod; a parità, più fonti
        def yrs(o): return o[1] == pr[0] and o[2] == pr[1]
        cands = [o for o in occ if yrs(o)] or list(occ)
        target = max(cands, key=lambda o: o[5])  # più fonti
        # estrai i byte dell'oggetto target dal suo file
        tfile = target[0]
        traw = (ENT / tfile).read_bytes().decode("utf-8")
        # trova l'occorrenza giusta del target nel suo file
        # (nel file può esserci una sola occorrenza del nome — è un pair cross-file)
        tstart, tend = find_record_span(traw, name, 0)
        tobj = adjust(traw[tstart:tend], pr[2], pr[3])

        # 1) sostituisci l'oggetto della PRIMA copia col target (se diverso)
        fraw = (ENT / first[0]).read_bytes().decode("utf-8")
        fstart, fend = find_record_span(fraw, name, 0)
        if fraw[fstart:fend] != tobj:
            fraw = fraw[:fstart] + tobj + fraw[fend:]
            if not dry:
                (ENT / first[0]).write_bytes(fraw.encode("utf-8"))
            json.loads(fraw)
        # 2) rimuovi la copia SUCCESSIVA (nel suo file, diverso dal primo)
        lraw = (ENT / later[0]).read_bytes().decode("utf-8")
        lstart, lend = find_record_span(lraw, name, 0)
        lraw = remove_object(lraw, lstart, lend)
        if not dry:
            (ENT / later[0]).write_bytes(lraw.encode("utf-8"))
        json.loads(lraw)
        done += 1
        tag = "=first" if target[0] == first[0] else "=later→moved"
        print(f"  {'[dry] ' if dry else ''}{name!r}: keep@{first[0]} (target {target[0]}{tag}, conf→{pr[2]}), remove {later[0]}")

    print(f"\n{'[dry] ' if dry else ''}{done} pair deduplicati")


if __name__ == "__main__":
    main()
