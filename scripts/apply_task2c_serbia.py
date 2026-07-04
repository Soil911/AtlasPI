# -*- coding: utf-8 -*-
"""Task 2c (v6.99.130) — Serbia moderna: coda della catena 34.
Crea FR Jugoslavia + Serbia e Montenegro + Repubblica di Serbia, incatena dopo
la SFRJ #231. Follow-up ETHICS-020 — ETHICS-025.

Correzioni applicate (cross-check verifier + ChatGPT gpt-5.5, log 20260705):
  - FRY: wikidata_qid Q37024 → **Q838261** (Q37024 è Serbia and Montenegro; il
    verifier ha colto lo scambio); name_variants[3] corrotta ripulita.
  - Republic of Serbia: status disputed → **confirmed**, conf 0.7 → **0.9**
    (ChatGPT P1: lo Stato serbo NON è in dubbio; il cap ETHICS-003 va riservato al
    TERRITORIO contestato = Kosovo, localizzato come territory_change + note); +
    nel ethical_notes va NOMINATO il conflitto del Kosovo 1998-99 e la pulizia
    etnica dell'era Milošević (ChatGPT P2, ETHICS-002) — prima della disputa 2008.

Confini APPROSSIMATIVI generati (nessun vicino da ereditare per gli stati moderni),
boundary_source=approximate_generated (ETHICS-005). Catena 34 = strutturale (batch_20
round-trippa). Uso: PYTHONUTF8=1 python -m scripts.apply_task2c_serbia
"""
from __future__ import annotations

import json
from pathlib import Path

from src.ingestion.boundary_generator import generate_approximate_boundary

REPO = Path(__file__).resolve().parent.parent
RESEARCH = REPO / "data" / "enrichment" / "task2_research_20260705.json"
ENT_OUT = REPO / "data" / "entities" / "batch_42_serbia_modern.json"
CHAIN20 = REPO / "data" / "chains" / "batch_20_balkan.json"
SQL_OUT = REPO / "scripts" / "sql_task2c_serbia.sql"

SFRJ = "Социјалистичка Федеративна Република Југославија"  # #231
PROD_IDS = {SFRJ: 231}

KOSOVO_PREPEND = (
    "Il conflitto del Kosovo del 1998-1999 va nominato per primo (ETHICS-002): le forze "
    "serbo-jugoslave dell'era di Slobodan Milošević condussero una pulizia etnica su larga "
    "scala (circa 850.000 albanesi kosovari espulsi e migliaia di uccisi), che innescò "
    "l'intervento aereo NATO (marzo-giugno 1999) e l'amministrazione ONU del Kosovo (UNMIK, "
    "Ris. CdS 1244). Su questo sfondo si colloca la disputa successiva sullo status. "
)


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def qn(v):
    return "NULL" if v is None else str(v)


def apply_corrections(recs):
    fry = recs["fr_yugoslavia"]
    fry["wikidata_qid"] = "Q838261"
    for nv in fry["name_variants"]:
        if "Tr>eća" in nv["name"] or "Републичка Југославија" in nv["name"]:
            nv["name"] = "Трећа Југославија (Treća Jugoslavija)"
            nv["context"] = "Denominazione informale 'Terza Jugoslavia' (dopo il Regno e la SFRJ); lang sr."
    rs = recs["republic_of_serbia"]
    rs["status"] = "confirmed"
    rs["confidence_score"] = 0.9
    assert not rs["ethical_notes"].startswith("Il conflitto del Kosovo del 1998")
    rs["ethical_notes"] = KOSOVO_PREPEND + rs["ethical_notes"]


def gen_boundary(seed: int, y0: int, y1):
    # entity_type='country' → raggio ~Serbia (federation sovradimensiona a 11°)
    return generate_approximate_boundary(lat=44.8125, lon=20.4612, entity_type="country",
                                         year_start=y0, year_end=y1, seed=seed)


def entity_json(rec, boundary):
    conf = rec["confidence_score"]
    return {
        "name_original": rec["name_original"], "name_original_lang": rec["name_original_lang"],
        "entity_type": rec["entity_type"], "year_start": rec["year_start"], "year_end": rec["year_end"],
        "capital_name": rec["capital_name"], "capital_lat": rec["capital_lat"], "capital_lon": rec["capital_lon"],
        "boundary_geojson": boundary, "boundary_source": "approximate_generated",
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


def build_links(fry, sm, rs):
    return [
        {"entity_name": fry["name_original"], "transition_year": 1992, "transition_type": "DISSOLUTION", "is_violent": True,
         "description": "As the SFR Yugoslavia broke up in the 1991-1995 wars (Slovenia, Croatia, Bosnia, Macedonia seceding), Serbia and Montenegro proclaimed the Federal Republic of Yugoslavia on 27 April 1992 as the rump/claimed-continuator state.",
         "ethical_notes": "is_violent=true: the FRY was born from the violent dissolution of the SFRY (Yugoslav wars, including the Srebrenica genocide of 1995 by Bosnian Serb forces, and the 1998-99 Kosovo war and NATO intervention involving FRY forces). Milošević-era Serbia was a principal party; perpetrator roles are named on the relevant entities."},
        {"entity_name": sm["name_original"], "transition_year": 2003, "transition_type": "REFORM", "is_violent": False,
         "description": "The Constitutional Charter of 4 February 2003 restructured the FRY into the loose State Union of Serbia and Montenegro, retiring the name 'Yugoslavia' after 74 years (EU-mediated, the 'Solania' arrangement).",
         "ethical_notes": "A constitutional restructuring/renaming, not a violent transition. Kosovo remained de iure part of Serbia but under UN administration (UNMIK, UNSC Res 1244)."},
        {"entity_name": rs["name_original"], "transition_year": 2006, "transition_type": "SECESSION", "is_violent": False,
         "description": "Montenegro's independence referendum of 21 May 2006 (55.5% vs the EU-set 55% threshold) led to Montenegro's declaration of independence on 3 June 2006; Serbia's National Assembly declared the Republic of Serbia the successor state on 5 June 2006.",
         "ethical_notes": "Peaceful secession by referendum. Both historiographies on the 55% threshold and the union are recorded on the Serbia-and-Montenegro entity; the unresolved Kosovo dispute (2008 UDI) is recorded on the Republic of Serbia entity, not arbitrated."},
    ]


OLD_NAME_34 = "Serbian state trunk: Raska → Srpsko Carstvo → Српска деспотовина → Ottoman → Кнежевина Србија → Југославија (СХС → СФРЈ)"
NEW_NAME_34 = "Serbian state trunk: Raska → Srpsko Carstvo → Српска деспотовина → Ottoman → Кнежевина Србија → Југославија (СХС → СФРЈ → СРЈ → СЦГ) → Република Србија"


def chain_edit(links):
    d = json.loads(CHAIN20.read_text(encoding="utf-8"))
    ch = next(c for c in d if c.get("name") == OLD_NAME_34)
    existing = {l["entity_name"] for l in ch["links"]}
    for ln in links:
        assert ln["entity_name"] not in existing, f"{ln['entity_name']} già in catena 34"
    ch["links"].extend(dict(l) for l in links)
    ch["name"] = NEW_NAME_34
    CHAIN20.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAIN20.name}: catena 34 +3 link + rename")


def gen_sql(entities, links):
    out = []
    w = out.append
    w("-- v6.99.130 (Task 2c / ETHICS-025) — Serbia moderna: FRY + S&M + Republic of Serbia + catena 34.")
    w("-- Backup PRIMA. ON_ERROR_STOP=1. Confini approximate_generated.")
    w("BEGIN;")
    names = [e["name_original"] for e in entities]
    w("DO $$ BEGIN")
    w("  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN (" + ", ".join(q(n) for n in names) + ")) THEN")
    w("    RAISE EXCEPTION 'entità Serbia moderna già presenti'; END IF;")
    w("END $$;")
    w("")
    for rec in entities:
        gj = json.dumps(rec["boundary_geojson"], ensure_ascii=False)
        w(f"-- ── {rec['name_original']} ──")
        w("INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,")
        w("  capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,")
        w("  confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)")
        w(f"VALUES ({q(rec['name_original'])}, {q(rec['name_original_lang'])}, {q(rec['entity_type'])}, {rec['year_start']}, {qn(rec['year_end'])},")
        w(f"  {q(rec['capital_name'])}, {rec['capital_lat']}, {rec['capital_lon']}, {q(gj)}, {q(rec['boundary_source'])},")
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

    def eref(name):
        return str(PROD_IDS[name]) if name in PROD_IDS else f"(SELECT id FROM geo_entities WHERE name_original = {q(name)})"

    w("-- ── catena 34: +3 link (seq 7..9) ──")
    for seq, ln in zip(range(7, 10), links):
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES (34, {eref(ln['entity_name'])}, {seq}, {qn(ln['transition_year'])}, {q(ln['transition_type'])}, {'true' if ln['is_violent'] else 'false'}, {q(ln['description'])}, {q(ln['ethical_notes'])});")
    w(f"UPDATE dynasty_chains SET name={q(NEW_NAME_34)} WHERE id=34;")
    w("")
    w("DO $$ DECLARE n int; bad int;")
    w("BEGIN")
    w("  SELECT count(*) INTO n FROM geo_entities WHERE name_original IN (" + ", ".join(q(n) for n in names) + ");")
    w("  IF n <> 3 THEN RAISE EXCEPTION 'attese 3 entità, trovate %', n; END IF;")
    w("  SELECT count(*) INTO bad FROM (SELECT chain_id FROM chain_links WHERE chain_id=34 GROUP BY chain_id HAVING count(*)<>max(sequence_order)+1 OR min(sequence_order)<>0) t;")
    w("  IF bad<>0 THEN RAISE EXCEPTION 'catena 34 sequence non contigua'; END IF;")
    w("  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN (" + ", ".join(q(n) for n in names) + ") AND (ST_XMax(boundary_geom)-ST_XMin(boundary_geom))>=180;")
    w("  IF bad<>0 THEN RAISE EXCEPTION '% confini antimeridiano', bad; END IF;")
    w("  -- ETHICS-003: nessun disputed sopra 0.70 tra i nuovi")
    w("  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN (" + ", ".join(q(n) for n in names) + ") AND status='disputed' AND confidence_score>0.70;")
    w("  IF bad<>0 THEN RAISE EXCEPTION '% disputed sopra cap 0.70', bad; END IF;")
    w("  RAISE NOTICE 'Task 2c OK: FRY + S&M + Republic of Serbia + catena 34 (10 link)';")
    w("END $$;")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main():
    recs = {o["key"]: o["record"] for o in json.loads(RESEARCH.read_text(encoding="utf-8"))}
    apply_corrections(recs)
    fry, sm, rs = recs["fr_yugoslavia"], recs["serbia_montenegro"], recs["republic_of_serbia"]
    from shapely.geometry import shape
    entities = []
    for i, rec in enumerate((fry, sm, rs)):
        b = gen_boundary(seed=101 + i, y0=rec["year_start"], y1=rec["year_end"])
        assert shape(b).is_valid
        entities.append(entity_json(rec, b))
    ENT_OUT.write_text(json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT.name}: 3 entità (FRY, S&M, Republic of Serbia)")
    links = build_links(fry, sm, rs)
    chain_edit(links)
    SQL_OUT.write_text(gen_sql(entities, links), encoding="utf-8")
    print(f"OK {SQL_OUT.name}")
    json.loads(ENT_OUT.read_text(encoding="utf-8"))
    json.loads(CHAIN20.read_text(encoding="utf-8"))
    print("OK JSON parsano")


if __name__ == "__main__":
    main()
