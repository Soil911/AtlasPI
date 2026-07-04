# -*- coding: utf-8 -*-
"""Task 2a (v6.99.128) — Egitto/Nubia: ripristino Meroe #552 + Terzo Periodo
Intermedio + Periodo Tardo, con estensione delle catene 137 (Regni faraonici)
e 99 (Nilotica/Kush). Follow-up ETHICS-022 (split Kemet) — ETHICS-023.

Dual-write:
  - data/entities/batch_40_egypt_periods.json  (TIP + Late Period, NUOVE)
  - data/entities/batch_16_africa_kingdoms.json (Meroe #552: un-deprecate + note)
  - data/chains/batch_39_kemet_split.json       (catena 137 + 2 link)
  - data/chains/batch_21_nile_valley_ethiopia.json (catena 99 + link Meroe)
  - scripts/sql_task2a_egypt.sql                (prod: INSERT + UPDATE + chain_links)

Fonti + note verificate dal workflow task2-research (research + refuter avversariale),
provenance in data/enrichment/task2_research_20260705.json. Correzioni applicate qui:
  - name_original normalizzato alla convenzione dei fratelli 'tꜣ.wy (X)' (ETHICS-001);
    il nome inglese di periodizzazione diventa variante.
Confini INHERITATI da vicini reali (ETHICS-005, boundary_source documentato):
  TIP <- #1058 (New Kingdom, Egitto+Nubia, coerente col dominio kushita 25a din.);
  Late <- #1057 (Middle Kingdom, core egizio, coerente con l'Egitto saitico).

Uso: PYTHONUTF8=1 python -m scripts.apply_task2a_egypt
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESEARCH = REPO / "data" / "enrichment" / "task2_research_20260705.json"
BOUNDARY_DIR = Path(
    r"C:/Users/cliri/AppData/Local/Temp/claude/"
    r"C--Users-cliri-Documents-AtlasPI/f407f556-bf8a-4600-bf5a-843726a309af/scratchpad"
)
ENT_OUT = REPO / "data" / "entities" / "batch_40_egypt_periods.json"
BATCH16 = REPO / "data" / "entities" / "batch_16_africa_kingdoms.json"
CHAIN39 = REPO / "data" / "chains" / "batch_39_kemet_split.json"
CHAIN21 = REPO / "data" / "chains" / "batch_21_nile_valley_ethiopia.json"
SQL_OUT = REPO / "scripts" / "sql_task2a_egypt.sql"


def q(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"


def qn(v):
    return "NULL" if v is None else str(v)


def load_research():
    data = json.loads(RESEARCH.read_text(encoding="utf-8"))
    return {o["key"]: o["record"] for o in data}


def load_boundary(entity_id: int) -> dict:
    g = json.loads((BOUNDARY_DIR / f"boundary_{entity_id}.json").read_text(encoding="utf-8"))
    # antimeridian guard (CLAUDE.md geometric check)
    from shapely.geometry import shape
    shp = shape(g)
    b = shp.bounds
    assert shp.is_valid and (b[2] - b[0]) < 180, f"boundary {entity_id} invalida/antimeridiana"
    return g


def _fix_tip_tc(tcs):
    """Correzione cross-check ChatGPT: il sacco di Tebe da parte di Assurbanipal
    è datato 663 a.C. (non 664, che è il confine convenzionale del Periodo Tardo)."""
    out = []
    for tc in tcs:
        tc = dict(tc)
        if "sacks Thebes" in tc.get("description", ""):
            tc["description"] = tc["description"].replace(
                "sacks Thebes and expels the Kushite Tantamani",
                "sacks Thebes in 663 BCE and expels the Kushite Tantamani",
            )
        out.append(tc)
    return out


# ── record corretti (name-normalized) ────────────────────────────────────────
def build_tip(recs) -> dict:
    r = recs["egypt_third_intermediate"]
    nv = list(r["name_variants"])
    nv.append({"name": "Third Intermediate Period of Egypt", "lang": "en",
               "context": "Standard Egyptological periodization label (21st-25th dynasties, c. 1069-664 BCE); era il name_original inglese, normalizzato alla convenzione tꜣ.wy (X) come i fratelli di catena.",
               "source": "Metropolitan Museum of Art, Heilbrunn Timeline of Art History"})
    return {
        "name_original": "tꜣ.wy (Third Intermediate Period)",
        "name_original_lang": "egy",
        "entity_type": "period",
        "year_start": -1069, "year_end": -664,
        "capital_name": "Tanis (Djanet)", "capital_lat": 30.9758, "capital_lon": 31.8804,
        "confidence_score": 0.62, "status": "confirmed",
        "boundary_geojson": load_boundary(1058),  # DICT (il seed fa json.dumps)
        "boundary_source": "historical_approximation",
        "ethical_notes": r["ethical_notes"],
        "wikidata_qid": "Q212728",
        "name_variants": nv,
        "territory_changes": _fix_tip_tc(r["territory_changes"]),
        "sources": r["sources"],
        "_boundary_from": 1058,
    }


def build_late(recs) -> dict:
    r = recs["egypt_late_period"]
    return {
        "name_original": "tꜣ.wy (Late Period)",
        "name_original_lang": "egy",
        "entity_type": "period",
        "year_start": -664, "year_end": -332,
        "capital_name": "Sais (Zau)", "capital_lat": 30.9666, "capital_lon": 30.7693,
        "confidence_score": 0.82, "status": "confirmed",
        "boundary_geojson": load_boundary(1057),  # DICT (il seed fa json.dumps)
        "boundary_source": "historical_approximation",
        "ethical_notes": r["ethical_notes"],
        "wikidata_qid": "Q621917",
        "name_variants": r["name_variants"],
        "territory_changes": r["territory_changes"],
        "sources": r["sources"],
        "_boundary_from": 1057,
    }


MEROE_RESTORE_NOTE = (
    " [RESTORED v6.99.128] This entity was deprecated in the v6.85 merge as a supposed "
    "duplicate of Kush #52 (they were assumed to share Wikidata Q241790); it is in fact the "
    "distinct MEROITIC PHASE of the Kingdom of Kush and is here restored as a phase-entity "
    "(ETHICS-015/023, like the tꜣ.wy phases of the pharaonic kingdoms) and re-linked into the "
    "Nile Valley / Kush chain #99 after Napata. The wikidata_qid is left null because Q241790 "
    "designates the whole Kingdom of Kush (held by #52); Meroe is its southern-capital phase, "
    "not a separate polity."
)


def entity_json(rec: dict) -> dict:
    conf = rec["confidence_score"]
    return {
        "name_original": rec["name_original"],
        "name_original_lang": rec["name_original_lang"],
        "entity_type": rec["entity_type"],
        "year_start": rec["year_start"], "year_end": rec["year_end"],
        "capital_name": rec["capital_name"], "capital_lat": rec["capital_lat"], "capital_lon": rec["capital_lon"],
        "boundary_geojson": rec["boundary_geojson"], "boundary_source": rec["boundary_source"],
        "confidence_score": conf, "status": rec["status"],
        "ethical_notes": rec["ethical_notes"], "wikidata_qid": rec["wikidata_qid"],
        "name_variants": rec["name_variants"],
        "territory_changes": [
            {"year": tc["year"], "region": tc["region"], "change_type": tc["change_type"],
             "description": tc["description"], "population_affected": tc.get("population_affected"),
             "confidence_score": conf}
            for tc in rec["territory_changes"]
        ],
        "sources": rec["sources"],
    }


# ── chain link builders ───────────────────────────────────────────────────────
TIP_LINK = {
    "entity_name": "tꜣ.wy (Third Intermediate Period)", "transition_year": -1069,
    "transition_type": "DISSOLUTION", "is_violent": False,
    "description": "The death of Ramesses XI and accession of Smendes I at Tanis (c. 1069 BCE) ended the New Kingdom and opened four centuries of political fragmentation: Tanite pharaohs of the 21st Dynasty in the north shared power with the Theban High Priests of Amun, and Libyan-descended (Meshwesh) dynasties (22nd-24th) later ruled competing seats.",
    "ethical_notes": "Modelling ~400 years of a divided Egypt (21st-25th dynasties) as one chain node is a periodization convenience; the entity record documents the fragmentation and the Kushite 25th Dynasty's reversal of the New Kingdom's earlier domination of Nubia.",
}
LATE_LINK = {
    "entity_name": "tꜣ.wy (Late Period)", "transition_year": -664,
    "transition_type": "RESTORATION", "is_violent": True,
    "description": "After the Neo-Assyrian sack of Thebes (663 BCE) under Ashurbanipal, Psamtik I of Sais opened the Late Period (26th Saite Dynasty, native Egyptianized Libyan-descended), consolidating an independent reunified Egypt by c. 656 BCE; it ended with the Achaemenid (525, 343 BCE) and Macedonian (332 BCE) conquests.",
    "ethical_notes": "is_violent=true: the reunification followed the Assyrian sack of Thebes; historiographies differ on whether the Saite dynasty was an indigenous restoration or an Assyrian client that later won independence — both readings are recorded on the entity.",
}
MEROE_LINK = {
    "entity_name": "Meroe", "transition_year": -300,
    "transition_type": "REFORM", "is_violent": False,
    "description": "The Kushite kingdom's primary royal, political and burial focus shifted south toward Meroe (Begrawiya) by c. 300 BCE (Meroe was already significant earlier, and Napata retained religious weight); the Meroitic period developed its own script, large-scale iron industry and the ruling Kandake (Candace) queens, and the kingdom endured until its conquest by Aksum c. 350 CE.",
    "ethical_notes": "Restored as a distinct Meroitic phase-entity (ETHICS-015/023) after being wrongly deprecated as a duplicate of Kush in v6.85; the earlier merge conflated the Meroitic phase with the umbrella Kingdom of Kush (#52, Q241790).",
}


def edit_json_files(tip, late):
    # 1. batch_40 (new)
    ENT_OUT.write_text(json.dumps([entity_json(tip), entity_json(late)], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT.name}: 2 entità (TIP, Late Period)")

    # 2. Meroe restore in batch_16
    d16 = json.loads(BATCH16.read_text(encoding="utf-8"))
    meroe = next(e for e in d16 if e.get("name_original") == "Meroe")
    assert meroe["status"] == "deprecated", "Meroe non è deprecated in batch_16 — già ripristinato?"
    base = meroe["ethical_notes"].rstrip()
    meroe["status"] = "confirmed"
    meroe["ethical_notes"] = base + MEROE_RESTORE_NOTE
    BATCH16.write_text(json.dumps(d16, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {BATCH16.name}: Meroe un-deprecated + restore note")

    # 3. chain 137 (batch_39): append TIP, Late
    d39 = json.loads(CHAIN39.read_text(encoding="utf-8"))
    ch137 = next(c for c in d39 if c.get("name", "").startswith("Egyptian pharaonic kingdoms"))
    existing = {l["entity_name"] for l in ch137["links"]}
    assert TIP_LINK["entity_name"] not in existing, "TIP già in catena 137"
    ch137["links"].append(dict(TIP_LINK))
    ch137["links"].append(dict(LATE_LINK))
    ch137["name"] = "Egyptian pharaonic kingdoms: tꜣ.wy (Old) → (Middle) → (New) → (Third Intermediate) → (Late Period)"
    CHAIN39.write_text(json.dumps(d39, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAIN39.name}: catena 137 +2 link (TIP, Late)")

    # 4. chain 99 (batch_21): append Meroe
    d21 = json.loads(CHAIN21.read_text(encoding="utf-8"))
    ch99 = next(c for c in d21 if "Kerma" in c.get("name", "") and "Kush" in c.get("name", ""))
    assert "Meroe" not in {l["entity_name"] for l in ch99["links"]}, "Meroe già in catena 99"
    ch99["links"].append(dict(MEROE_LINK))
    ch99["name"] = "Nile Valley / Kush dynastic trunk: Kerma → Kush → Napata → Meroe"
    CHAIN21.write_text(json.dumps(d21, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAIN21.name}: catena 99 +1 link (Meroe)")

    return base + MEROE_RESTORE_NOTE  # converged Meroe notes for prod SQL


def gen_sql(tip, late, meroe_notes):
    out = []
    w = out.append
    w("-- v6.99.128 (Task 2a / ETHICS-023) — Egitto/Nubia: TIP + Late Period + restore Meroe #552.")
    w("-- Dual-write: data/entities/batch_40 + batch_16 (Meroe) + data/chains/batch_39,21.")
    w("-- Backup pg_dump PRIMA. psql -v ON_ERROR_STOP=1. Confini INHERITATI (#1058/#1057).")
    w("BEGIN;")
    w("")
    w("-- guard: le entità nuove non esistono")
    w("DO $$ BEGIN")
    w("  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN ("
      + q(tip["name_original"]) + ", " + q(late["name_original"]) + ")) THEN")
    w("    RAISE EXCEPTION 'TIP/Late già presenti — script già applicato?'; END IF;")
    w("  IF NOT EXISTS (SELECT 1 FROM geo_entities WHERE id=552 AND status='deprecated') THEN")
    w("    RAISE EXCEPTION 'Meroe #552 non è deprecated — restore già applicato?'; END IF;")
    w("END $$;")
    w("")
    for rec in (tip, late):
        gj = json.dumps(rec["boundary_geojson"], ensure_ascii=False)  # dict -> stringa per Text/PostGIS
        w(f"-- ── {rec['name_original']} (confine inherited da #{rec['_boundary_from']}) ──")
        w("INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,")
        w("  capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,")
        w("  confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)")
        w(f"VALUES ({q(rec['name_original'])}, {q(rec['name_original_lang'])}, {q(rec['entity_type'])}, {rec['year_start']}, {qn(rec['year_end'])},")
        w(f"  {q(rec['capital_name'])}, {rec['capital_lat']}, {rec['capital_lon']}, {q(gj)}, {q(rec['boundary_source'])},")
        w(f"  {rec['confidence_score']}, 'confirmed', {q(rec['ethical_notes'])}, {q(rec['wikidata_qid'])},")
        w(f"  ST_Multi(ST_GeomFromGeoJSON({q(gj)})));")
        ref = f"(SELECT id FROM geo_entities WHERE name_original = {q(rec['name_original'])})"
        for v in rec["name_variants"]:
            w("INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES")
            w(f"  ({ref}, {q(v['name'])}, {q(v['lang'])}, {qn(v.get('period_start'))}, {qn(v.get('period_end'))}, {q(v.get('context'))}, {q(v.get('source'))});")
        for tc in rec["territory_changes"]:
            w("INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES")
            w(f"  ({ref}, {tc['year']}, {q(tc['region'])}, {q(tc['change_type'])}, {q(tc['description'])}, {qn(tc.get('population_affected'))}, {rec['confidence_score']});")
        for s in rec["sources"]:
            w("INSERT INTO sources (entity_id, citation, url, source_type) VALUES")
            w(f"  ({ref}, {q(s['citation'])}, {q(s.get('url'))}, {q(s['source_type'])});")
        w("")

    w("-- ── restore Meroe #552 (un-deprecate + note convergenti JSON=prod) ──")
    w(f"UPDATE geo_entities SET status='confirmed', ethical_notes={q(meroe_notes)} WHERE id=552;")
    w("")

    w("-- ── catena 137 (Regni faraonici): +TIP (seq 3) +Late (seq 4) ──")
    for seq, ln in ((3, TIP_LINK), (4, LATE_LINK)):
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES (137, (SELECT id FROM geo_entities WHERE name_original={q(ln['entity_name'])}), {seq}, {qn(ln['transition_year'])}, {q(ln['transition_type'])}, {'true' if ln['is_violent'] else 'false'}, {q(ln['description'])}, {q(ln['ethical_notes'])});")
    w("UPDATE dynasty_chains SET name='Egyptian pharaonic kingdoms: tꜣ.wy (Old) → (Middle) → (New) → (Third Intermediate) → (Late Period)' WHERE id=137;")
    w("")
    w("-- ── catena 99 (Nilotica/Kush): +Meroe (seq 3) ──")
    w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
    w(f"VALUES (99, 552, 3, {qn(MEROE_LINK['transition_year'])}, {q(MEROE_LINK['transition_type'])}, false, {q(MEROE_LINK['description'])}, {q(MEROE_LINK['ethical_notes'])});")
    w("UPDATE dynasty_chains SET name='Nile Valley / Kush dynastic trunk: Kerma → Kush → Napata → Meroe' WHERE id=99;")
    w("")

    w("-- ── validazione finale ──")
    w("DO $$")
    w("DECLARE n int; bad int;")
    w("BEGIN")
    w(f"  SELECT count(*) INTO n FROM geo_entities WHERE name_original IN ({q(tip['name_original'])}, {q(late['name_original'])}) AND status='confirmed';")
    w("  IF n <> 2 THEN RAISE EXCEPTION 'attese 2 entità nuove confirmed, trovate %', n; END IF;")
    w("  IF EXISTS (SELECT 1 FROM geo_entities WHERE id=552 AND status<>'confirmed') THEN RAISE EXCEPTION 'Meroe non ripristinata'; END IF;")
    w("  -- contiguità sequence_order catene 99/137")
    w("  SELECT count(*) INTO bad FROM (SELECT chain_id FROM chain_links WHERE chain_id IN (99,137) GROUP BY chain_id HAVING count(*) <> max(sequence_order)+1 OR min(sequence_order)<>0) t;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION 'sequence_order non contigui su % catene', bad; END IF;")
    w("  -- antimeridian guard sui confini nuovi")
    w(f"  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN ({q(tip['name_original'])}, {q(late['name_original'])}) AND (ST_XMax(boundary_geom)-ST_XMin(boundary_geom)) >= 180;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% confini attraversano l''antimeridiano', bad; END IF;")
    w("  RAISE NOTICE 'Task 2a OK: TIP + Late Period + Meroe restore + catene 99/137';")
    w("END $$;")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main():
    recs = load_research()
    tip, late = build_tip(recs), build_late(recs)
    meroe_notes = edit_json_files(tip, late)
    SQL_OUT.write_text(gen_sql(tip, late, meroe_notes), encoding="utf-8")
    print(f"OK {SQL_OUT.name}")
    # sanity: tutti i file JSON toccati parsano
    for f in (ENT_OUT, BATCH16, CHAIN39, CHAIN21):
        json.loads(f.read_text(encoding="utf-8"))
    print("OK tutti i JSON parsano")


if __name__ == "__main__":
    main()
