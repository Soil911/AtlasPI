# -*- coding: utf-8 -*-
"""Task 2b (v6.99.129) — Cambogia: PRK + Stato di Cambogia + estensione avanti
della catena 126 con la sequenza dei regimi 1970-1993. Follow-up ETHICS-020 — ETHICS-024.

Dual-write:
  - data/entities/batch_41_cambodia_modern.json (PRK + State of Cambodia, NUOVE)
  - data/chains/batch_35_class1_asia_pacific.json (catena 126: +4 link, chirurgia
    a stringa — il file NON round-trippa a indent=2)
  - scripts/sql_task2b_cambodia.sql (prod: INSERT + chain_links + rename)

Modellazione (cross-check ChatGPT, log 20260705): la catena 126 termina a Kingdom
of Cambodia #256 (1953-present, monarchia RESTAURATA nel 1993). Si estende avanti coi
regimi de-facto (Khmer Republic → Democratic Kampuchea → PRK → State of Cambodia);
il ritorno del 1993 al #256 è documentato nelle note (convenzione linea+note,
ETHICS-017), NON come back-link letterale. ChatGPT preferiva SPLITTARE #256 in
(1953-70)+(1993-): rinviato come operazione separata (Sihanouk regnò in entrambi i
periodi → re-home complesso), interruzione resa esplicita nelle note.

Confini INHERITATI da #256 (Cambogia moderna). Uso: PYTHONUTF8=1 python -m scripts.apply_task2b_cambodia
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
ENT_OUT = REPO / "data" / "entities" / "batch_41_cambodia_modern.json"
CHAIN35 = REPO / "data" / "chains" / "batch_35_class1_asia_pacific.json"
SQL_OUT = REPO / "scripts" / "sql_task2b_cambodia.sql"

# id prod noti (le entità esistenti referenziate nei chain_links)
KINGDOM = "ព្រះរាជាណាចក្រកម្ពុជា"   # #256
KHMER_REPUBLIC = "សាធារណរដ្ឋខ្មែរ"   # #1044
DEM_KAMPUCHEA = "កម្ពុជាប្រជាធិបតេយ្យ"  # #240
PROD_IDS = {KINGDOM: 256, KHMER_REPUBLIC: 1044, DEM_KAMPUCHEA: 240}


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def qn(v):
    return "NULL" if v is None else str(v)


def load_boundary(entity_id: int) -> dict:
    g = json.loads((BOUNDARY_DIR / f"boundary_{entity_id}.json").read_text(encoding="utf-8"))
    from shapely.geometry import shape
    shp = shape(g)
    assert shp.is_valid and (shp.bounds[2] - shp.bounds[0]) < 180, f"boundary {entity_id} invalida"
    return g


def entity_json(rec: dict, boundary: dict) -> dict:
    conf = rec["confidence_score"]
    return {
        "name_original": rec["name_original"], "name_original_lang": rec["name_original_lang"],
        "entity_type": rec["entity_type"], "year_start": rec["year_start"], "year_end": rec["year_end"],
        "capital_name": rec["capital_name"], "capital_lat": rec["capital_lat"], "capital_lon": rec["capital_lon"],
        "boundary_geojson": boundary, "boundary_source": "historical_approximation",
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


# ── 4 link nuovi per la catena 126 (ordine 4..7) ─────────────────────────────
def build_links(prk_name, soc_name):
    return [
        {"entity_name": KHMER_REPUBLIC, "transition_year": 1970, "transition_type": "REVOLUTION", "is_violent": False,
         "description": "The Lon Nol / Sirik Matak coup of 18 March 1970 deposed Prince Norodom Sihanouk while he was abroad and abolished the monarchy; the Khmer Republic was proclaimed on 9 October 1970.",
         "ethical_notes": "The coup itself was bloodless, but it pulled Cambodia openly into the Vietnam War and triggered the 1970-1975 civil war; the monarchy it abolished was restored only in 1993 (see chain-level note)."},
        {"entity_name": DEM_KAMPUCHEA, "transition_year": 1975, "transition_type": "CONQUEST", "is_violent": True,
         "description": "The Khmer Rouge captured Phnom Penh on 17 April 1975, ending the Khmer Republic and establishing Democratic Kampuchea under Pol Pot.",
         "ethical_notes": "Perpetrator named: the Communist Party of Kampuchea (Khmer Rouge) under Pol Pot. Democratic Kampuchea carried out the Cambodian genocide (c. 1.5-2 million dead, ~20-25% of the population, 1975-79)."},
        {"entity_name": prk_name, "transition_year": 1979, "transition_type": "CONQUEST", "is_violent": True,
         "description": "Vietnam invaded (25 December 1978), captured Phnom Penh on 7 January 1979 and routed the Khmer Rouge, installing the People's Republic of Kampuchea (proclaimed 8-10 January 1979) under Heng Samrin and Hun Sen.",
         "ethical_notes": "Both readings recorded without arbitration (ETHICS-002/no-single-version): the invasion ENDED the Khmer Rouge genocide, AND it was a Vietnamese military occupation (troops until Sept 1989) installing a client state. The ousted Democratic Kampuchea kept Cambodia's UN seat with Chinese, US and ASEAN backing."},
        {"entity_name": soc_name, "transition_year": 1989, "transition_type": "REFORM", "is_violent": False,
         "description": "At the April 1989 National Assembly (chaired by Hun Sen) the PRK adopted a revised constitution renaming the state the State of Cambodia and reintroducing market reforms as Vietnam withdrew; it ended with the 1991 Paris Peace Accords, the UNTAC transition, and the 1993 restoration of the monarchy.",
         "ethical_notes": "The 1993 restoration returned governance to the Kingdom of Cambodia (#256), which this chain departs from at 1970 — the interruption (1970-1993) and restoration are documented here rather than as a literal back-link (linear-chain convention). A full split of #256 into 1953-70 and 1993- entities was considered (ChatGPT cross-check) but deferred: King Sihanouk reigned in both periods."},
    ]


NEW_NAME_126 = ("Cambodian state: អាណាចក្រខ្មែរ → កម្ពុជា (Longvek-Oudong) → Indochine française → "
                "Kingdom of Cambodia → Khmer Republic → Democratic Kampuchea → PRK → State of Cambodia")
OLD_NAME_126 = ("Cambodian state: អាណាចក្រខ្មែរ → កម្ពុជា (Longvek-Oudong) → Indochine française → "
                "Kingdom of Cambodia")
NOTE_ANCHOR = "1975-1979 years.)"
NOTE_APPEND = (" [v6.99.129/ETHICS-024] The 1970-1993 upheavals are now modelled as explicit chain "
               "nodes (Khmer Republic, Democratic Kampuchea, PRK, State of Cambodia) rather than only "
               "flagged as internal to #256's span; the 1993 monarchy restoration returns to #256 and "
               "is documented on the State-of-Cambodia link (no literal back-link — a split of #256 was "
               "considered but deferred).")


def chain_surgery(links):
    raw = CHAIN35.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in raw else "\n"  # newline-agnostic (git autocrlf materializza CRLF)
    # 1. append i 4 link dopo il link seq3 (chiude a `see chain-level notes."}` + newline + `    ]`)
    link_anchor = 'see chain-level notes."}' + nl + '    ]'
    assert raw.count(link_anchor) == 1, f"link_anchor occorrenze={raw.count(link_anchor)}"
    links_txt = ("," + nl + "      ").join(json.dumps(l, ensure_ascii=False) for l in links)
    raw = raw.replace(link_anchor, 'see chain-level notes."},' + nl + '      ' + links_txt + nl + '    ]')
    # 2. rename catena
    assert raw.count('"' + OLD_NAME_126 + '"') == 1, "OLD_NAME_126 non unico"
    raw = raw.replace('"' + OLD_NAME_126 + '"', '"' + NEW_NAME_126 + '"')
    # 3. append nota chain-level
    assert raw.count(NOTE_ANCHOR) == 1, f"NOTE_ANCHOR occorrenze={raw.count(NOTE_ANCHOR)}"
    raw = raw.replace(NOTE_ANCHOR, NOTE_ANCHOR + NOTE_APPEND, 1)
    CHAIN35.write_bytes(raw.encode("utf-8"))
    json.loads(raw)  # deve ancora parsare
    print(f"OK {CHAIN35.name}: catena 126 +4 link + rename + nota")


def gen_sql(prk, soc, links):
    out = []
    w = out.append
    w("-- v6.99.129 (Task 2b / ETHICS-024) — Cambogia: PRK + State of Cambodia + catena 126 avanti.")
    w("-- Dual-write: data/entities/batch_41 + data/chains/batch_35. Backup PRIMA. ON_ERROR_STOP=1.")
    w("BEGIN;")
    w("DO $$ BEGIN")
    w(f"  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN ({q(prk['name_original'])}, {q(soc['name_original'])})) THEN")
    w("    RAISE EXCEPTION 'PRK/SoC già presenti'; END IF;")
    w("END $$;")
    w("")
    for rec, bid in ((prk, 256), (soc, 256)):
        gj = json.dumps(rec["_boundary"], ensure_ascii=False)
        w(f"-- ── {rec['name_original']} (confine inherited da #{bid}) ──")
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

    def eref(name):
        return str(PROD_IDS[name]) if name in PROD_IDS else f"(SELECT id FROM geo_entities WHERE name_original = {q(name)})"

    w("-- ── catena 126: +4 link (seq 4..7) ──")
    for seq, ln in zip(range(4, 8), links):
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES (126, {eref(ln['entity_name'])}, {seq}, {qn(ln['transition_year'])}, {q(ln['transition_type'])}, {'true' if ln['is_violent'] else 'false'}, {q(ln['description'])}, {q(ln['ethical_notes'])});")
    w(f"UPDATE dynasty_chains SET name={q(NEW_NAME_126)} WHERE id=126;")
    w("")
    w("-- ── validazione ──")
    w("DO $$ DECLARE n int; bad int;")
    w("BEGIN")
    w(f"  SELECT count(*) INTO n FROM geo_entities WHERE name_original IN ({q(prk['name_original'])}, {q(soc['name_original'])}) AND status='confirmed';")
    w("  IF n <> 2 THEN RAISE EXCEPTION 'attese 2 entità nuove, trovate %', n; END IF;")
    w("  SELECT count(*) INTO bad FROM (SELECT chain_id FROM chain_links WHERE chain_id=126 GROUP BY chain_id HAVING count(*)<>max(sequence_order)+1 OR min(sequence_order)<>0) t;")
    w("  IF bad<>0 THEN RAISE EXCEPTION 'catena 126 sequence_order non contigui'; END IF;")
    w(f"  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN ({q(prk['name_original'])}, {q(soc['name_original'])}) AND (ST_XMax(boundary_geom)-ST_XMin(boundary_geom))>=180;")
    w("  IF bad<>0 THEN RAISE EXCEPTION '% confini antimeridiano', bad; END IF;")
    w("  RAISE NOTICE 'Task 2b OK: PRK + State of Cambodia + catena 126 (8 link)';")
    w("END $$;")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main():
    recs = {o["key"]: o["record"] for o in json.loads(RESEARCH.read_text(encoding="utf-8"))}
    prk, soc = recs["prk"], recs["state_of_cambodia"]
    b256 = load_boundary(256)
    prk["_boundary"] = b256
    soc["_boundary"] = b256
    ENT_OUT.write_text(json.dumps([entity_json(prk, b256), entity_json(soc, b256)], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT.name}: 2 entità (PRK, State of Cambodia)")
    links = build_links(prk["name_original"], soc["name_original"])
    chain_surgery(links)
    SQL_OUT.write_text(gen_sql(prk, soc, links), encoding="utf-8")
    print(f"OK {SQL_OUT.name}")
    json.loads(ENT_OUT.read_text(encoding="utf-8"))
    print("OK JSON parsano")


if __name__ == "__main__":
    main()
