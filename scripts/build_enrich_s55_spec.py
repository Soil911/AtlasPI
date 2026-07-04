# -*- coding: utf-8 -*-
"""Costruisce data/fixes/enrichment_s55.json dal workflow enrich-s55.

Applica le correzioni del verifier avversariale:
  - scarta le fonti segnalate come fabbricate/dubbie (match per citation);
  - usa corrected_confidence del verifier se confidence_honest=False;
  - rispetta il cap ETHICS-003 (disputed <= 0.70) e ETHICS-013 (conf<0.5 -> uncertain).

Uso: PYTHONUTF8=1 python -m scripts.build_enrich_s55_spec <workflow_output.json> <enrich10_prod.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "data" / "fixes" / "enrichment_s55.json"


def main():
    wf_path, prod_path = sys.argv[1], sys.argv[2]
    wf = json.loads(Path(wf_path).read_text(encoding="utf-8"))
    recs = wf["records"] if isinstance(wf, dict) and "records" in wf else wf
    # se e' il file .output del task, estrai .result
    if isinstance(wf, dict) and "result" in wf:
        res = wf["result"]
        res = json.loads(res) if isinstance(res, str) else res
        recs = res["records"]
    prod = {e["id"]: e for e in json.loads(Path(prod_path).read_text(encoding="utf-8"))}

    entities = []
    dropped_total = 0
    for o in recs:
        if not o.get("research"):
            print(f"SKIP id={o.get('id')} (no research)")
            continue
        r = o["research"]
        v = o.get("verify") or {}
        eid = r["id"]
        p = prod[eid]
        # confidence onesta
        conf = r["new_confidence"]
        if v and not v.get("confidence_honest", True):
            conf = v.get("corrected_confidence", conf)
        conf = round(float(conf), 3)
        # scarta fonti fabbricate/dubbie
        bad = set(v.get("fabricated_or_dubious", []) or [])
        good_sources = []
        for s in r["new_sources"]:
            cit = s["citation"]
            if any(cit in b or b in cit for b in bad):
                dropped_total += 1
                continue
            good_sources.append({"citation": cit, "url": s.get("url"), "source_type": s.get("source_type", "academic")})
        # guardrail status/conf (ETHICS-003/013)
        status = r.get("status", p["status"])
        if status == "disputed" and conf > 0.70:
            conf = 0.70
        if conf < 0.5 and status == "confirmed":
            status = "uncertain"
        if not good_sources:
            print(f"SKIP id={eid} {r['label']} (0 fonti valide dopo il filtro)")
            continue
        entities.append({
            "id": eid,
            "name_original": p["name_original"],
            "label": r["label"],
            "confidence": conf,
            "status": status,
            "ethical_notes_append": r["ethical_notes_append"],
            "new_sources": good_sources,
        })
        print(f"  id={eid:>4} {r['label'][:24]:26} conf {p['conf']}->{conf} status={status} +{len(good_sources)} src"
              + ("  (verifier: fonti sospette scartate)" if bad else ""))

    spec = {"_meta": {"session": "S55", "date": "2026-07-05",
                      "note": "Enrichment ultracode: 10 polity sotto-sourced <0.6, research + refuter avversariale sulle fonti; conf calibrata onestamente (ETHICS-013).",
                      "dropped_sources": dropped_total},
            "entities": entities}
    OUT.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\nOK {OUT}: {len(entities)} entità, {dropped_total} fonti scartate dal verifier")


if __name__ == "__main__":
    main()
