# -*- coding: utf-8 -*-
"""Task 2d (v6.99.131) — Eritrea: Colonia Eritrea + catena Medri Bahri #658.
Follow-up ETHICS-020 — ETHICS-026.

Crea Colonia Eritrea (1890-1941) e una NUOVA catena COLONIAL Medri Bahri → Colonia
Eritrea. Correzione applicata (verifier): la legge del 1933 regolava lo status dei
figli meticci; il divieto delle unioni (madamato) è del 1937, non "matrimoni misti
banditi nel 1933".

Confine INHERITATO da #658 (altopiano eritreo, ETHICS-005). Catena NUOVA creata via
SQL (come apply_m1_unlock) + JSON per il fresh-seed; l'ingest al boot la salta perché
già presente per nome. Uso: PYTHONUTF8=1 python -m scripts.apply_task2d_eritrea
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
ENT_OUT = REPO / "data" / "entities" / "batch_43_eritrea.json"
CHAIN_OUT = REPO / "data" / "chains" / "batch_43_eritrea.json"
SQL_OUT = REPO / "scripts" / "sql_task2d_eritrea.sql"

MEDRI_BAHRI_JSON = "ምድረ ባሕሪ"   # nome effettivo JSON-land (= prod #658)
MEDRI_BAHRI_ID = 658


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def qn(v):
    return "NULL" if v is None else str(v)


def load_boundary(entity_id: int) -> dict:
    g = json.loads((BOUNDARY_DIR / f"boundary_{entity_id}.json").read_text(encoding="utf-8"))
    from shapely.geometry import shape
    shp = shape(g)
    assert shp.is_valid and (shp.bounds[2] - shp.bounds[0]) < 180
    return g


def build_eritrea(recs):
    r = recs["italian_eritrea"]
    # correzione verifier: legge 1933 = status figli meticci; divieto unioni = 1937
    old = "mixed marriages were banned in 1933, and"
    assert r["ethical_notes"].count(old) == 1, "clausola 1933 non trovata"
    r["ethical_notes"] = r["ethical_notes"].replace(
        old,
        "the 1933 legislation regulated the legal status of mixed-race (meticci) children, and",
    )
    # correzione minore: fonte della variante 'Erythrea' (alias Wikidata, non official-name)
    for nv in r["name_variants"]:
        if nv.get("name") == "Erythrea":
            nv["context"] = "Latinate form (from Greek Erythra Thalassa, 'Red Sea'); alias su Wikidata Q1232988"
    r["_boundary"] = load_boundary(MEDRI_BAHRI_ID)
    return r


def entity_json(rec):
    conf = rec["confidence_score"]
    return {
        "name_original": rec["name_original"], "name_original_lang": rec["name_original_lang"],
        "entity_type": rec["entity_type"], "year_start": rec["year_start"], "year_end": rec["year_end"],
        "capital_name": rec["capital_name"], "capital_lat": rec["capital_lat"], "capital_lon": rec["capital_lon"],
        "boundary_geojson": rec["_boundary"], "boundary_source": "historical_approximation",
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


CHAIN_NAME = "Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea"


def build_chain(eritrea_name):
    return {
        "name": CHAIN_NAME, "name_lang": "en", "chain_type": "COLONIAL",
        "region": "Horn of Africa / Eritrean highlands and Red Sea coast",
        "description": "The Eritrean highland state from the Medri Bahri kingdom of the Bahr Negash (c. 1137-1879) to its incorporation into Italy's Colonia Eritrea (1890-1941). A deliberately short two-link chain (ETHICS-017): between Medri Bahri's end and the Italian colony the highlands were briefly contested by Egypt (1870s) and Ethiopia (Yohannes IV) before Italy consolidated the colony from Massawa (1885) and proclaimed it on 1 January 1890.",
        "confidence_score": 0.7,
        "ethical_notes": "COLONIAL chain (ETHICS-002: colonial oppression is a first-class datum). Colonia Eritrea was an occupation regime of the Kingdom of Italy, intensified under Fascism and used as the springboard for the 1935-36 invasion of Ethiopia, imposing racial segregation and criminalising Italian-Eritrean unions (madamato, 1937). The chain does NOT end the Eritrean story at colonization: after the Italian defeat (1941) came the British Military Administration (1941-52), the UN-imposed federation with then annexation by Ethiopia (1952/1962), the 30-year Eritrean War of Independence (1961-1991, EPLF) and independence by referendum in 1993. The independent State of Eritrea (1993-) and the British/Ethiopian interregnum are not yet entities in this dataset (queued extension).",
        "sources": [
            {"citation": "Negash, Tekeste. Italian Colonialism in Eritrea, 1882-1941. Uppsala: Studia Historica Upsaliensia 148, 1987.", "url": None, "source_type": "academic"},
            {"citation": "Iyob, Ruth. The Eritrean Struggle for Independence. Cambridge University Press, 1995.", "url": None, "source_type": "academic"},
        ],
        "links": [
            {"entity_name": MEDRI_BAHRI_JSON, "transition_year": None, "transition_type": None, "is_violent": False,
             "description": "Medri Bahri (c. 1137-1879), the Christian highland kingdom of the Bahr Negash ('lord of the sea'), centred on Debarwa, spanning the Eritrean plateau between the Mereb river and the Red Sea escarpment.",
             "ethical_notes": None},
            {"entity_name": eritrea_name, "transition_year": 1890, "transition_type": "CONQUEST", "is_violent": True,
             "description": "Italy consolidated the Red Sea coast (Assab 1882, Massawa 1885) and the highlands by military conquest, proclaiming the unified Colonia Eritrea on 1 January 1890; the 1896 Battle of Adwa (Ethiopian victory over Italy) halted Italian expansion inland but Eritrea remained an Italian colony until 1941.",
             "ethical_notes": "Colonial conquest, perpetrator named (Kingdom of Italy). Between Medri Bahri's end (1879) and the colony, the highlands had been contested by Egypt and by Ethiopia (Yohannes IV)."},
        ],
    }


def gen_sql(rec, chain):
    out = []
    w = out.append
    w("-- v6.99.131 (Task 2d / ETHICS-026) — Eritrea: Colonia Eritrea + catena Medri Bahri.")
    w("-- Backup PRIMA. ON_ERROR_STOP=1. Confine inherited da #658. Catena NUOVA via SQL.")
    w("BEGIN;")
    w("DO $$ BEGIN")
    w(f"  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original = {q(rec['name_original'])}) THEN")
    w("    RAISE EXCEPTION 'Colonia Eritrea già presente'; END IF;")
    w(f"  IF EXISTS (SELECT 1 FROM dynasty_chains WHERE name = {q(chain['name'])}) THEN")
    w("    RAISE EXCEPTION 'catena eritrea già presente'; END IF;")
    w("END $$;")
    w("")
    gj = json.dumps(rec["_boundary"], ensure_ascii=False)
    w(f"-- ── {rec['name_original']} (confine inherited da #{MEDRI_BAHRI_ID}) ──")
    w("INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,")
    w("  capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,")
    w("  confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)")
    w(f"VALUES ({q(rec['name_original'])}, {q(rec['name_original_lang'])}, {q(rec['entity_type'])}, {rec['year_start']}, {qn(rec['year_end'])},")
    w(f"  {q(rec['capital_name'])}, {rec['capital_lat']}, {rec['capital_lon']}, {q(gj)}, 'historical_approximation',")
    w(f"  {rec['confidence_score']}, {q(rec['status'])}, {q(rec['ethical_notes'])}, {q(rec['wikidata_qid'])},")
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
    w("-- ── catena NUOVA (COLONIAL) + 2 link ──")
    w("INSERT INTO dynasty_chains (name, name_lang, chain_type, region, description, confidence_score, status, ethical_notes, sources)")
    w(f"VALUES ({q(chain['name'])}, 'en', {q(chain['chain_type'])}, {q(chain['region'])}, {q(chain['description'])}, {chain['confidence_score']}, 'confirmed', {q(chain['ethical_notes'])}, {q(json.dumps(chain['sources'], ensure_ascii=False))});")
    cref = f"(SELECT id FROM dynasty_chains WHERE name = {q(chain['name'])})"
    for i, ln in enumerate(chain["links"]):
        eref = str(MEDRI_BAHRI_ID) if ln["entity_name"] == MEDRI_BAHRI_JSON else f"(SELECT id FROM geo_entities WHERE name_original = {q(ln['entity_name'])})"
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES ({cref}, {eref}, {i}, {qn(ln['transition_year'])}, {q(ln['transition_type'])}, {'true' if ln['is_violent'] else 'false'}, {q(ln['description'])}, {q(ln['ethical_notes'])});")
    w("")
    w("DO $$ DECLARE bad int;")
    w("BEGIN")
    w(f"  IF NOT EXISTS (SELECT 1 FROM geo_entities WHERE name_original={q(rec['name_original'])} AND status='confirmed') THEN RAISE EXCEPTION 'entità non creata'; END IF;")
    w(f"  SELECT count(*) INTO bad FROM chain_links WHERE chain_id={cref};")
    w("  IF bad<>2 THEN RAISE EXCEPTION 'catena eritrea attesi 2 link, trovati %', bad; END IF;")
    w(f"  SELECT count(*) INTO bad FROM geo_entities WHERE name_original={q(rec['name_original'])} AND (ST_XMax(boundary_geom)-ST_XMin(boundary_geom))>=180;")
    w("  IF bad<>0 THEN RAISE EXCEPTION 'confine antimeridiano'; END IF;")
    w("  RAISE NOTICE 'Task 2d OK: Colonia Eritrea + catena Medri Bahri (2 link)';")
    w("END $$;")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main():
    recs = {o["key"]: o["record"] for o in json.loads(RESEARCH.read_text(encoding="utf-8"))}
    rec = build_eritrea(recs)
    ENT_OUT.write_text(json.dumps([entity_json(rec)], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT.name}: 1 entità (Colonia Eritrea)")
    chain = build_chain(rec["name_original"])
    CHAIN_OUT.write_text(json.dumps([chain], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAIN_OUT.name}: 1 catena COLONIAL (2 link)")
    SQL_OUT.write_text(gen_sql(rec, chain), encoding="utf-8")
    print(f"OK {SQL_OUT.name}")
    for f in (ENT_OUT, CHAIN_OUT):
        json.loads(f.read_text(encoding="utf-8"))
    print("OK JSON parsano")


if __name__ == "__main__":
    main()
