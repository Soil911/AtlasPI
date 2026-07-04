# -*- coding: utf-8 -*-
"""Applica le decisioni della review confidence (Task 1 ultracode, ADR-011).

Consuma il JSON di decisioni prodotto dal workflow `conf-review-queue`
(1 verify-agent per entità + refuter avversariale su ogni raise) e chiude la
coda `data/fixes/conf_review_queue.json` in dual-write:

  - decision "raise_prod"  -> prod := json  (UPDATE prod; JSON già al valore alto)
  - decision "lower_json"  -> json := prod  (chirurgia JSON; prod già al valore basso)

Ogni id della coda viene deciso: se manca dalle decisioni (agente droppato) →
default conservativo "lower_json" (ETHICS-013: non alzare senza fonti).

Guardrail (ETHICS-013 / ETHICS-003), sullo stato risultante:
  - raise che porterebbe conf>0.70 su status 'disputed' -> RIFIUTATO (declassato a lower_json).
  - (i lower non possono violare: abbassano, e gli status uncertain/disputed restano coerenti.)

Riusa la chirurgia byte-preserving di scripts.reconcile_confidence (patch del solo
confidence_score a profondità 1 del record effettivo last-wins, valore atteso
verificato prima e rilettura dopo).

Uso:
    python -m scripts.apply_conf_review_batch3 --decisions <file.json>            # dry-run
    python -m scripts.apply_conf_review_batch3 --decisions <file.json> --apply
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from scripts.reconcile_confidence import ENTITIES_DIR, patch_confidence, load_json_effective

REPO = Path(__file__).resolve().parent.parent
FIXES_DIR = REPO / "data" / "fixes"
QUEUE = FIXES_DIR / "conf_review_queue.json"
SQL_OUT = REPO / "scripts" / "sql_conf_review_batch3.sql"
EPS = 0.001


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    rows = queue["rows"]
    qmap = {r["id"]: r for r in rows}

    dec_raw = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    # accetta sia {decisions:[...]} sia [...]
    decisions = dec_raw["decisions"] if isinstance(dec_raw, dict) else dec_raw
    dmap = {d["id"]: d for d in decisions if isinstance(d, dict) and "id" in d}

    # Vista JSON EFFETTIVA corrente (last-wins). NON fidarsi degli idx della coda:
    # il file può essere cambiato dopo la generazione della coda (es. #1008 shift
    # 36->35). Ri-derivo per NOME; fallback alla coda solo se il nome non matcha
    # (nomi con zero-width space, es. #600).
    eff = load_json_effective()

    raises: list[dict] = []      # prod := json_now
    lowers: list[dict] = []      # json := prod (chirurgia)
    refused: list[dict] = []     # guardrail -> declassati a lower
    missing: list[int] = []      # id in coda ma non nelle decisioni
    converged: list[dict] = []   # json_eff già == prod: nulla da fare

    for eid, row in qmap.items():
        d = dmap.get(eid)
        if d is None:
            missing.append(eid)
            decision = "lower_json"
            rationale = "MISSING dalle decisioni: default conservativo ETHICS-013"
        else:
            decision = d.get("decision", "lower_json")
            rationale = d.get("rationale", "")

        prod, status = row["prod"], row.get("prod_status")
        je = eff.get(row["name"])
        if je is not None and je.get("confidence_score") is not None:
            json_now = float(je["confidence_score"])
            jfile, jidx = je["_file"], je["_idx"]
        else:
            json_now = row["json"]  # fallback (nome non matchabile)
            jfile, jidx = row["file"], row["idx"]

        entry = {"id": eid, "name": row["name"], "prod": prod, "json": json_now,
                 "queue_json": row["json"], "status": status, "file": jfile, "idx": jidx,
                 "decision": decision, "rationale": rationale}

        if abs(json_now - prod) < EPS:
            entry["note"] = "already_converged (json_eff==prod)"
            converged.append(entry)
            continue

        if decision == "raise_prod":
            if status == "disputed" and json_now > 0.70 + 1e-9:
                entry["guard"] = f"ETHICS-003: raise a {json_now} su disputed (>0.70)"
                refused.append(entry)
                lowers.append(entry)  # declassato
            else:
                raises.append(entry)
        else:
            lowers.append(entry)

    print(f"coda: {len(rows)} righe")
    print(f"  raise_prod (prod:=json): {len(raises)}")
    print(f"  lower_json (json:=prod): {len(lowers)}")
    print(f"  già convergenti (skip):  {len(converged)} {[c['id'] for c in converged]}")
    print(f"  rifiutati da guard (declassati): {len(refused)}")
    print(f"  mancanti dalle decisioni (default lower): {len(missing)} {missing}")
    for r in refused:
        print(f"    REFUSED id={r['id']} {r['name'][:36]!r}: {r['guard']}")

    if not args.apply:
        print("\nDRY-RUN. Rilancia con --apply.")
        # dump un preview raggruppato per ispezione
        for r in raises:
            print(f"  RAISE  id={r['id']:>4} {r['prod']}->{r['json']}  {r['name'][:34]}")
        return

    # 1. chirurgia JSON per i lower (dal fondo del file verso l'inizio)
    by_file: dict[str, list[dict]] = {}
    for r in lowers:
        by_file.setdefault(r["file"], []).append(r)
    errors: list[str] = []
    for fname, frows in by_file.items():
        fp = ENTITIES_DIR / fname
        for r in sorted(frows, key=lambda x: -x["idx"]):
            if abs(r["json"] - r["prod"]) < EPS:
                continue  # già uguali (nessuna divergenza da chiudere sul JSON)
            err = patch_confidence(fp, r["idx"], r["json"], r["prod"])
            if err:
                errors.append(err)
    if errors:
        print("\nERRORI CHIRURGIA:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    # rilettura di verifica: ogni lower deve ora leggere il valore prod
    reloaded = load_json_effective()
    bad = [r for r in lowers
           if r["name"] in reloaded
           and abs(float(reloaded[r["name"]]["confidence_score"]) - r["prod"]) >= EPS]
    if bad:
        print(f"\nVERIFICA JSON FALLITA su {len(bad)} righe (es. id={bad[0]['id']} {bad[0]['name']!r})")
        sys.exit(1)

    # 2. SQL prod per i raise (idempotente, lock ottimistico + guard finale)
    lines = [
        "-- v6.99.127 (Task 1 ultracode / ADR-011) — batch 3 review confidence.",
        "-- Chiude la coda conf_review_queue.json: alza prod al valore JSON dove le",
        "-- fonti + la precisione di datazione lo giustificano (verify-agent + refuter",
        "-- avversariale). Gli altri sono stati abbassati nel JSON (json:=prod).",
        "-- Idempotente. Eseguire DOPO backup pg_dump. psql -v ON_ERROR_STOP=1.",
        "BEGIN;",
    ]
    for r in raises:
        lines.append(
            f"UPDATE geo_entities SET confidence_score = {r['json']} "
            f"WHERE id = {r['id']} AND confidence_score = {r['prod']};"
            f"  -- {r['name'][:40]}"
        )
    if raises:
        lines += ["DO $$", "DECLARE bad int;", "BEGIN"]
        tuples = ",".join(f"({r['id']},{r['json']})" for r in raises)
        lines += [
            f"  SELECT count(*) INTO bad FROM (VALUES {tuples}) v(eid,c)",
            "    WHERE NOT EXISTS (SELECT 1 FROM geo_entities g WHERE g.id=v.eid AND g.confidence_score=v.c);",
            "  IF bad <> 0 THEN RAISE EXCEPTION '% confidence raise non applicate', bad; END IF;",
            f"  RAISE NOTICE 'conf batch 3 OK: {len(raises)} confidence alzate';",
            "END $$;",
        ]
    lines += ["COMMIT;", ""]
    SQL_OUT.write_text("\n".join(lines), encoding="utf-8")

    # 3. audit + svuota la coda
    audit = FIXES_DIR / f"conf_review_batch3_audit_{date.today():%Y%m%d}.json"
    audit.write_text(json.dumps(
        {"date": f"{date.today():%Y-%m-%d}", "policy": "ADR-011 / Task1-ultracode",
         "raises_prod_from_json": raises, "lowers_json_from_prod": lowers,
         "already_converged": converged,
         "refused_by_guard": refused, "missing_defaulted_lower": missing},
        ensure_ascii=False, indent=1), encoding="utf-8")

    queue["rows"] = []
    queue["description"] = (
        queue["description"].split(" [")[0]
        + f" [v6.99.127: CODA CHIUSA — {len(raises)} raise prod:=json (fonti+datazione ok),"
        f" {len(lowers)} lower json:=prod (ETHICS-013), {len(converged)} già convergenti."
        f" Audit: {audit.name}.]"
    )
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\nAPPLICATO: {len(raises)} UPDATE in {SQL_OUT.name}, "
          f"{len(lowers)} lower JSON, {len(converged)} convergenti, coda svuotata, audit {audit.name}.")


if __name__ == "__main__":
    main()
