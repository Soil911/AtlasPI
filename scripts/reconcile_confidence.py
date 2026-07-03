# -*- coding: utf-8 -*-
"""Riconciliazione confidence JSON<->prod — ADR-011 / M4 (v6.99.113).

Policy (approvata da Clirim, 2026-07-03; analisi in data/chatgpt_review +
workflow 2026-07-03):
  - prod_higher  -> JSON := prod ("backport": la confidence prod e' quella
    calibrata con fonti nelle sessioni enrichment; il JSON e' rimasto indietro).
  - json_higher, classe A (boost batch_32_confidence_boost.json mai applicato
    a prod, vince nel last-wins) -> prod := JSON.
  - json_higher con valore JSON che coincide con una spec enrichment presente
    in data/fixes/enrichment_s*.json (spec applicata al JSON ma mai deployata
    su prod) -> prod := JSON.
  - json_higher residuo -> CODA di review manuale (data/fixes/
    conf_review_queue.json): NESSUNA scrittura automatica.

Guardrail hard (per riga, sullo stato RISULTANTE — ETHICS-013 / ETHICS-003):
  - conf < 0.5 con status 'confirmed' -> riga RIFIUTATA;
  - conf > 0.70 con status 'disputed' -> riga RIFIUTATA;
  - la chirurgia JSON tocca SOLO il record effettivo (last-wins, ultima
    occorrenza nell'ultimo file) e SOLO il confidence_score a profondita' 1
    del record (mai quelli annidati in territory_changes/name_variants);
    valore atteso verificato prima della sostituzione, altrimenti riga abortita.

Uso:
    python -m scripts.reconcile_confidence --prod-dump <file>            # dry-run
    python -m scripts.reconcile_confidence --prod-dump <file> --apply

Il dump prod si genera con:
    ssh -i ~/.ssh/cra_vps root@77.81.229.242 "docker exec cra-atlaspi-db \
      psql -U atlaspi -d atlaspi -A -F'|' -t -c \"SELECT id, name_original, \
      confidence_score, status FROM geo_entities WHERE status != 'deprecated' \
      ORDER BY id\"" > prod_conf_dump.txt

Output (--apply):
  - data/entities/*.json aggiornati in place (chirurgia a stringa);
  - data/fixes/sql_conf_reconciliation_v6_99_113.sql (UPDATE prod con lock
    ottimistico + guard finale);
  - data/fixes/conf_reconciliation_audit_<data>.json (audit log completo);
  - data/fixes/conf_review_queue.json (coda manuale, sovrascritta).
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ENTITIES_DIR = REPO / "data" / "entities"
FIXES_DIR = REPO / "data" / "fixes"
SQL_OUT = FIXES_DIR / "sql_conf_reconciliation_v6_99_113.sql"
QUEUE_OUT = FIXES_DIR / "conf_review_queue.json"

EPS = 0.001


# ── caricamento ──────────────────────────────────────────────────────────────

def load_prod(dump_path: str) -> dict[str, tuple[int, float | None, str]]:
    prod: dict[str, tuple[int, float | None, str]] = {}
    with open(dump_path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("|")
            if len(parts) != 4:
                print(f"WARN riga dump malformata: {parts!r}", file=sys.stderr)
                continue
            eid, name, conf, status = parts
            prod[name] = (int(eid), float(conf) if conf else None, status)
    return prod


def load_json_effective() -> dict[str, dict]:
    """name_original -> record effettivo (last-wins), con _file e _idx."""
    effective: dict[str, dict] = {}
    for fp in sorted(ENTITIES_DIR.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            continue
        for idx, ent in enumerate(data):
            name = ent.get("name_original")
            if not name:
                continue
            ent["_file"] = fp.name
            ent["_idx"] = idx  # indice nel file (per la chirurgia)
            effective[name] = ent
    return effective


def load_enrichment_spec_values() -> dict[int, set[float]]:
    """id entita' -> set di confidence proposte dalle spec enrichment nel repo."""
    out: dict[int, set[float]] = {}
    for fp in glob.glob(str(FIXES_DIR / "enrichment_s*.json")):
        spec = json.loads(Path(fp).read_text(encoding="utf-8"))
        for e in spec.get("entities", []):
            eid = e.get("id")
            conf = e.get("confidence_score") or e.get("new_confidence")
            if eid is not None and conf is not None:
                out.setdefault(int(eid), set()).add(float(conf))
    return out


def load_batch32() -> dict[str, float]:
    fp = ENTITIES_DIR / "batch_32_confidence_boost.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    return {
        e["name_original"]: float(e["confidence_score"])
        for e in data
        if e.get("name_original") and e.get("confidence_score") is not None
    }


# ── guardrail ────────────────────────────────────────────────────────────────

def guard_violation(conf: float, status: str) -> str | None:
    # ETHICS-013: sotto 0.5 lo status DEVE essere uncertain (disputed tollerato:
    # asse diverso, ETHICS-003). ETHICS-003/012: disputed ha cap 0.70.
    if conf < 0.5 and status == "confirmed":
        return f"ETHICS-013: conf {conf} < 0.5 con status confirmed"
    if conf > 0.70 + 1e-9 and status == "disputed":
        return f"ETHICS-003: conf {conf} > 0.70 con status disputed"
    return None


# ── chirurgia JSON ───────────────────────────────────────────────────────────

def record_spans(text: str) -> list[tuple[int, int]]:
    """Span (start, end) di ogni oggetto top-level dell'array JSON."""
    decoder = json.JSONDecoder()
    spans: list[tuple[int, int]] = []
    i = text.index("[") + 1
    n = len(text)
    while i < n:
        while i < n and text[i] in " \t\r\n,":
            i += 1
        if i >= n or text[i] == "]":
            break
        obj_start = i
        _, end = decoder.raw_decode(text, i)
        spans.append((obj_start, end))
        i = end
    return spans


def depth1_conf_match(segment: str) -> re.Match | None:
    """Primo match di confidence_score a profondita' 1 dentro il record."""
    depth = 0
    in_str = False
    escape = False
    for m in re.finditer(r'"confidence_score"\s*:\s*(-?\d+(?:\.\d+)?)', segment):
        # calcola la profondita' al punto del match scandendo fino a m.start()
        depth = 0
        in_str = False
        escape = False
        for ch in segment[: m.start()]:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch in "{[":
                depth += 1
            elif ch in "}]":
                depth -= 1
        if depth == 1:
            return m
    return None


def patch_confidence(fp: Path, target_idx: int, old_val: float, new_val: float) -> str | None:
    """Sostituisce il confidence_score del record target_idx. None = ok, str = errore."""
    text = fp.read_text(encoding="utf-8")
    spans = record_spans(text)
    if target_idx >= len(spans):
        return f"indice record {target_idx} fuori range in {fp.name}"
    start, end = spans[target_idx]
    segment = text[start:end]
    m = depth1_conf_match(segment)
    if m is None:
        return f"nessun confidence_score a depth 1 nel record {target_idx} di {fp.name}"
    found = float(m.group(1))
    if abs(found - old_val) >= EPS:
        return (
            f"valore inatteso in {fp.name} record {target_idx}: "
            f"trovato {found}, atteso {old_val}"
        )
    new_num = json.dumps(new_val)
    new_segment = segment[: m.start(1)] + new_num + segment[m.end(1):]
    fp.write_text(text[:start] + new_segment + text[end:], encoding="utf-8")
    return None


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prod-dump", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    prod = load_prod(args.prod_dump)
    jsonv = load_json_effective()
    spec_values = load_enrichment_spec_values()
    b32 = load_batch32()

    backports: list[dict] = []      # JSON := prod
    prod_updates: list[dict] = []   # prod := JSON
    queue: list[dict] = []          # review manuale
    refused: list[dict] = []        # guardrail

    for name, (eid, pconf, pstatus) in sorted(prod.items(), key=lambda kv: kv[1][0]):
        je = jsonv.get(name)
        if je is None:
            continue  # rename nativi prod-only: track M4 separato
        jconf = je.get("confidence_score")
        if jconf is None or pconf is None:
            continue
        jconf = float(jconf)
        if abs(pconf - jconf) < EPS:
            continue

        row = {
            "id": eid, "name": name, "prod": pconf, "json": jconf,
            "prod_status": pstatus, "json_status": je.get("status"),
            "file": je["_file"], "idx": je["_idx"],
        }

        if pconf > jconf:
            # prod vince -> backport a JSON. Guard sul risultato JSON.
            v = guard_violation(pconf, je.get("status", "confirmed"))
            if v:
                row["guard"] = v
                refused.append(row)
            else:
                row["action"] = "json:=prod"
                backports.append(row)
        else:
            in_b32 = name in b32 and abs(b32[name] - jconf) < EPS
            from_spec = eid in spec_values and any(
                abs(sv - jconf) < EPS for sv in spec_values[eid]
            )
            if in_b32 or from_spec:
                v = guard_violation(jconf, pstatus)
                if v:
                    row["guard"] = v
                    refused.append(row)
                else:
                    row["action"] = "prod:=json"
                    row["reason"] = "batch_32_boost" if in_b32 else "spec_enrichment_non_deployata"
                    prod_updates.append(row)
            else:
                row["action"] = "review_queue"
                queue.append(row)

    print(f"divergenze: {len(backports) + len(prod_updates) + len(queue) + len(refused)}")
    print(f"  backport JSON:=prod : {len(backports)}")
    print(f"  UPDATE prod:=JSON   : {len(prod_updates)}"
          f"  ({sum(1 for r in prod_updates if r['reason']=='batch_32_boost')} batch_32, "
          f"{sum(1 for r in prod_updates if r['reason']!='batch_32_boost')} spec)")
    print(f"  coda review manuale : {len(queue)}")
    print(f"  rifiutate da guard  : {len(refused)}")
    for r in refused:
        print(f"    REFUSED id={r['id']} {r['name'][:40]!r}: {r['guard']}")
    for r in prod_updates:
        print(f"    PROD id={r['id']} {r['name'][:40]!r}: {r['prod']} -> {r['json']} ({r['reason']})")

    if not args.apply:
        print("\nDRY-RUN: nessuna modifica. Rilanciare con --apply.")
        return

    # 1. chirurgia JSON (raggruppata per file, dal fondo verso l'inizio)
    by_file: dict[str, list[dict]] = {}
    for r in backports:
        by_file.setdefault(r["file"], []).append(r)
    errors: list[str] = []
    for fname, rows in by_file.items():
        fp = ENTITIES_DIR / fname
        for r in sorted(rows, key=lambda x: -x["idx"]):
            err = patch_confidence(fp, r["idx"], r["json"], r["prod"])
            if err:
                errors.append(err)
    if errors:
        print("\nERRORI CHIRURGIA (righe saltate):")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    # verifica di rilettura: ogni backport deve ora leggere il valore prod
    reloaded = load_json_effective()
    bad = [
        r for r in backports
        if abs(float(reloaded[r["name"]]["confidence_score"]) - r["prod"]) >= EPS
    ]
    if bad:
        print(f"\nVERIFICA FALLITA su {len(bad)} righe (es. {bad[0]['name']!r})")
        sys.exit(1)

    # 2. SQL per prod
    lines = [
        "-- ADR-011 (v6.99.113): riconciliazione confidence JSON->prod",
        "-- Generato da scripts/reconcile_confidence.py — NON editare a mano.",
        "-- Eseguire DOPO backup pg_dump. ON_ERROR_STOP=1.",
        "BEGIN;",
    ]
    for r in prod_updates:
        lines.append(
            f"UPDATE geo_entities SET confidence_score = {r['json']} "
            f"WHERE id = {r['id']} AND confidence_score = {r['prod']};"
            f"  -- {r['reason']}"
        )
    lines += [
        "DO $$",
        "DECLARE n int;",
        "BEGIN",
    ]
    for r in prod_updates:
        lines.append(
            f"  SELECT count(*) INTO n FROM geo_entities WHERE id = {r['id']} "
            f"AND confidence_score = {r['json']};"
        )
        lines.append(
            f"  IF n <> 1 THEN RAISE EXCEPTION 'GUARD: id {r['id']} non aggiornato'; END IF;"
        )
    lines += ["END $$;", "COMMIT;", ""]
    SQL_OUT.write_text("\n".join(lines), encoding="utf-8")

    # 3. audit log + coda
    audit_path = FIXES_DIR / f"conf_reconciliation_audit_{date.today():%Y%m%d}.json"
    audit_path.write_text(
        json.dumps(
            {
                "date": f"{date.today():%Y-%m-%d}",
                "policy": "ADR-011",
                "backports_json_from_prod": backports,
                "prod_updates_from_json": prod_updates,
                "review_queue": queue,
                "refused_by_guard": refused,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    QUEUE_OUT.write_text(
        json.dumps(
            {
                "description": "Coda review manuale confidence (ADR-011, classe C json_higher): "
                "verificare le fonti PRIMA di alzare la conf su prod; lotti da ~10 nelle "
                "sessioni enrichment. Nessuna scrittura automatica.",
                "rows": queue,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"\nAPPLICATO: {len(backports)} backport JSON, "
          f"{len(prod_updates)} UPDATE in {SQL_OUT.name}, "
          f"audit in {audit_path.name}, coda in {QUEUE_OUT.name}")


if __name__ == "__main__":
    main()
