"""Split Sri Lanka (v6.99.121, ETHICS-021).

Re-scope #142 (nome di re → Anuradhapura) e #600 (script khmer → Dambadeniya),
deprecazione #386 (nome di re) + re-home siti/tc, creazione Gampola + Kotte,
catena "Sinhalese kingdom trunk".

Input:  research_output/split_period_entities.json (Gampola/Kotte verificati)
Output: data/entities/batch_38_sri_lanka_split.json (2 nuove)
        data/chains/batch_38_sri_lanka_split.json (1 catena)
        chirurgia batch_02 (#142), batch_10 (#386), batch_18 (#600)
        scripts/sql_sri_lanka_split.sql (prod, transazionale)

Dual-write: JSON allinea il fresh-seed, SQL allinea la prod live.
Usage: PYTHONUTF8=1 python -m scripts.apply_sri_lanka_split
"""
from __future__ import annotations

import json
from pathlib import Path

RESEARCH = Path("research_output/split_period_entities.json")
ENT_OUT = Path("data/entities/batch_38_sri_lanka_split.json")
CHAINS_OUT = Path("data/chains/batch_38_sri_lanka_split.json")
SQL_OUT = Path("scripts/sql_sri_lanka_split.sql")

# id prod delle entità esistenti referenziate nella catena
PROD = {
    "anuradhapura": 142, "polonnaruwa": 387, "chola": 110,
    "dambadeniya": 600, "kandy": 388, "jaffna": 601, "gajabahu": 386,
}
CHOLA_NAME = "சோழ நாடு"
ANU_NAME = "අනුරාධපුර රාජධානිය"
POL_NAME = "පොළොන්නරුව"
DAM_NAME = "දඹදෙණිය රාජධානිය"


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def qn(v):
    return "NULL" if v is None else str(v)


def load():
    data = json.loads(RESEARCH.read_text(encoding="utf-8"))
    return {i["key"]: i["record"] for i in data}


def replace_once(raw: str, old: str, new: str, tag: str) -> str:
    lf_old = old.replace("\r\n", "\n")
    cands = [old, lf_old, lf_old.replace("\n", "\r\n")]
    for o in cands:
        if raw.count(o) == 1:
            return raw.replace(o, new if o == old else (new.replace("\r\n", "\n") if o == lf_old else new.replace("\r\n", "\n").replace("\n", "\r\n")))
    raise AssertionError(f"{tag}: occorrenze {[raw.count(o) for o in cands]} (attesa 1)")


# ── nuove entità Gampola + Kotte ─────────────────────────────────────
NEW_KEYS = ["gampola", "kotte"]


def build_entity(rec: dict) -> dict:
    return {
        "name_original": rec["name_original"],
        "name_original_lang": rec["name_original_lang"],
        "entity_type": rec["entity_type"],
        "year_start": rec["year_start"],
        "year_end": rec.get("year_end"),
        "capital_name": rec["capital_name"],
        "capital_lat": rec["capital_lat"],
        "capital_lon": rec["capital_lon"],
        "confidence_score": rec["confidence_score"],
        "status": "confirmed",
        "boundary_geojson": rec["boundary_geojson"],
        "boundary_source": "historical_approximation",
        "ethical_notes": rec["ethical_notes"],
        "wikidata_qid": rec.get("wikidata_qid"),
        "name_variants": rec["name_variants"],
        "territory_changes": [
            {k: tc.get(k) for k in ("year", "region", "change_type", "description", "population_affected", "confidence_score")}
            for tc in rec["territory_changes"]
        ],
        "sources": rec["sources"],
    }


# ── nuova catena ─────────────────────────────────────────────────────
def build_chain() -> dict:
    return {
        "name": "Sinhalese kingdom trunk: අනුරාධපුර → පොළොන්නරුව → දඹදෙණිය → ගම්පොල → කෝට්ටේ",
        "name_lang": "en",
        "chain_type": "SUCCESSION",
        "region": "South Asia / Sri Lanka (Sinhalese heartland)",
        "description": "The Sinhalese Buddhist monarchy from the Anuradhapura kingdom (from the 5th c. BCE) through its drifting-capital successors to the Kingdom of Kotte, absorbed by Portugal in 1597. The Kandyan kingdom (a branch from 1469) carried the line to 1815.",
        "confidence_score": 0.75,
        "ethical_notes": "This is the SINHALESE line only. ETHICS (no false linearity): the northern Tamil Jaffna kingdom (#601) is a PARALLEL polity with its own chain, NOT a subordinate node here; the 1017-1070 occupation of Rajarata is modelled as a FOREIGN Tamil Chola conquest (a node through the existing Chola entity #110), not a Sinhalese succession; the Kandyan kingdom (#388) is a branch, not the trunk terminus. Kalinga Magha's invasion (1215) preceded the Dambadeniya consolidation (1232). The 1597 Portuguese absorption was a coerced client-state annexation at Dharmapala's death, not a voluntary bequest.",
        "sources": [
            {"citation": "K.M. de Silva, A History of Sri Lanka, University of California Press, 1981", "url": None, "source_type": "academic"},
            {"citation": "R.A.L.H. Gunawardana, Robe and Plough: Monasticism and Economic Interest in Early Medieval Sri Lanka, University of Arizona Press, 1979", "url": None, "source_type": "academic"},
        ],
        "links": [
            {"entity_name": ANU_NAME, "transition_year": None, "transition_type": None, "is_violent": False,
             "description": "The Anuradhapura kingdom (c. 437 BCE - 1017 CE), the long first phase of the Sinhalese state, centred on the dry-zone irrigation civilisation of Rajarata.",
             "ethical_notes": None},
            {"entity_name": CHOLA_NAME, "transition_year": 1017, "transition_type": "CONQUEST", "is_violent": True,
             "description": "FOREIGN Tamil Chola conquest: Rajaraja I sacked Anuradhapura (993) and Rajendra I annexed the whole of Rajarata by 1017, administering it as the province Mummudi-sola-mandalam from Polonnaruwa (renamed Jananathamangalam). King Mahinda V was captured and died in exile in India (1029).",
             "ethical_notes": "This link is a FOREIGN occupation, NOT a Sinhalese succession: the Chola entity #110 is a South Indian Tamil empire. Recorded here to represent the 1017-1070 interruption honestly, per the no-false-linearity principle."},
            {"entity_name": POL_NAME, "transition_year": 1070, "transition_type": "RESTORATION", "is_violent": True,
             "description": "Vijayabahu I expelled the Cholas by war (from Ruhuna in the south) and was crowned at Polonnaruwa (1070; formal consecration 1076-77), restoring Sinhalese sovereignty over Rajarata. Polonnaruwa became the new capital.",
             "ethical_notes": "The 1055/56-1070 overlap is real: Vijayabahu I ruled from Ruhuna while the Cholas still held Rajarata."},
            {"entity_name": DAM_NAME, "transition_year": 1215, "transition_type": "CONQUEST", "is_violent": True,
             "description": "Kalinga Magha's invasion (1215) with a brutal occupation of Rajarata forced the Sinhalese polity to relocate to the southwestern wet zone; Vijayabahu III established the kingdom at Dambadeniya (1232), securing the Tooth Relic and re-founding Buddhist kingship.",
             "ethical_notes": "The trigger is the 1215 invasion; 1232 is the Dambadeniya consolidation. The dry-zone irrigation civilisation of Rajarata was permanently abandoned after this."},
            {"entity_name": None, "transition_year": 1341, "transition_type": "SUCCESSION", "is_violent": False,
             "description": "Peaceful dynastic capital shift to Gampola (Gangasiripura) under Bhuvanaikabahu IV.",
             "ethical_notes": None, "_new": "gampola"},
            {"entity_name": None, "transition_year": 1412, "transition_type": "SUCCESSION", "is_violent": True,
             "description": "Parakramabahu VI acceded (1412) and moved the capital to Kotte, reunifying most of the island by 1450. The transition followed the 1410-11 Ming intervention that captured and deported the previous king Vira Alakesvara.",
             "ethical_notes": "Ming China's armed intervention (1411) is documented on the Gampola entity; the Ming and Sinhala accounts of the 1412 accession (installation vs indigenous restoration) are both recorded, not arbitrated.", "_new": "kotte"},
        ],
    }


# ── chirurgia JSON entità esistenti ──────────────────────────────────
def entity_surgery():
    # #142 batch_02: rename + re-scope + variant/tc cleanup
    p142 = Path("data/entities/batch_02_asia.json")
    raw = p142.read_bytes().decode("utf-8")
    old_head = ('"name_original": "මහා විජයබාහු",\r\n    "name_original_lang": "si",\r\n    "entity_type": "kingdom",\r\n'
                '    "year_start": -543,\r\n    "year_end": 1815,\r\n    "capital_name": "අනුරාධපුරය",\r\n'
                '    "capital_lat": 8.3114,\r\n    "capital_lon": 80.4037,\r\n    "confidence_score": 0.4,\r\n    "status": "uncertain",')
    new_head = ('"name_original": "අනුරාධපුර රාජධානිය",\r\n    "name_original_lang": "si",\r\n    "entity_type": "kingdom",\r\n'
                '    "year_start": -437,\r\n    "year_end": 1017,\r\n    "capital_name": "අනුරාධපුරය",\r\n'
                '    "capital_lat": 8.3114,\r\n    "capital_lon": 80.4037,\r\n    "confidence_score": 0.7,\r\n    "status": "confirmed",')
    raw = replace_once(raw, old_head, new_head, "#142 head")
    old_vt = ('"name_variants": [\r\n      {\r\n        "name": "Sinhalese Kingdom",\r\n        "lang": "en",\r\n        "period_start": -543,\r\n        "period_end": 1815,\r\n        "context": "denominazione inglese generica (multiple dinastie e capitali)",\r\n        "source": "De Silva, A History of Sri Lanka (1981)"\r\n      },\r\n      {\r\n        "name": "Anuradhapura Kingdom",\r\n        "lang": "en",\r\n        "period_start": -377,\r\n        "period_end": 1017,\r\n        "context": "periodo della capitale Anuradhapura",\r\n        "source": "De Silva, A History of Sri Lanka (1981)"\r\n      },\r\n      {\r\n        "name": "Kingdom of Kandy",\r\n        "lang": "en",\r\n        "period_start": 1469,\r\n        "period_end": 1815,\r\n        "context": "ultimo regno singalese indipendente",\r\n        "source": "Dewaraja, The Kandyan Kingdom of Sri Lanka (1988)"\r\n      },\r\n      {\r\n        "name": "Regno Singalese",\r\n        "lang": "it",\r\n        "period_start": -543,\r\n        "period_end": 1815,\r\n        "context": "denominazione italiana generica",\r\n        "source": "Enciclopedia Treccani"\r\n      }\r\n    ],\r\n    "territory_changes": [\r\n      {\r\n        "year": -543,\r\n        "region": "Sri Lanka",\r\n        "change_type": "INDEPENDENCE",\r\n        "description": "Data tradizionale dell\'arrivo del principe Vijaya dall\'India secondo il Mahavamsa. La fondazione mitologica non e\' confermata archeologicamente.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.25\r\n      },\r\n      {\r\n        "year": 993,\r\n        "region": "Sri Lanka settentrionale",\r\n        "change_type": "CONQUEST_MILITARY",\r\n        "description": "I Chola invadono Sri Lanka e conquistano Anuradhapura. Il re singalese fugge a sud. I Chola governano il nord per oltre 75 anni.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.7\r\n      },\r\n      {\r\n        "year": 1815,\r\n        "region": "Kandy",\r\n        "change_type": "COLONIZATION",\r\n        "description": "Convenzione di Kandy: i Britannici annettono l\'ultimo regno singalese indipendente. Fine di circa 2300 anni (tradizionali) di monarchia singalese.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.85\r\n      }\r\n    ],')
    new_vt = ('"name_variants": [\r\n      {\r\n        "name": "Anuradhapura Kingdom",\r\n        "lang": "en",\r\n        "period_start": -437,\r\n        "period_end": 1017,\r\n        "context": "standard English name of the polity (ETHICS-021: #142 was mislabelled with a king\'s name, මහා විජයබාහු, spanning -543..1815)",\r\n        "source": "De Silva, A History of Sri Lanka (1981)"\r\n      },\r\n      {\r\n        "name": "Rajarata",\r\n        "lang": "si",\r\n        "period_start": -437,\r\n        "period_end": 1017,\r\n        "context": "the dry-zone \'king\'s country\' core of the Anuradhapura state",\r\n        "source": "Gunawardana, Robe and Plough (1979)"\r\n      },\r\n      {\r\n        "name": "Regno di Anuradhapura",\r\n        "lang": "it",\r\n        "period_start": -437,\r\n        "period_end": 1017,\r\n        "context": "denominazione italiana",\r\n        "source": null\r\n      }\r\n    ],\r\n    "territory_changes": [\r\n      {\r\n        "year": -437,\r\n        "region": "Rajarata (Sri Lanka settentrionale)",\r\n        "change_type": "INDEPENDENCE",\r\n        "description": "Convenzione mainstream: Pandukabhaya stabilisce la capitale ad Anuradhapura (~437 a.C.; cronologia corta si.wiki: 377 a.C. — dato conteso, non risolto). L\'arrivo del principe Vijaya (Tambapanni, ~543 a.C. secondo il Mahavamsa) e\' TRADIZIONE fondativa, non confermata archeologicamente.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.5\r\n      },\r\n      {\r\n        "year": 993,\r\n        "region": "Sri Lanka settentrionale",\r\n        "change_type": "CONQUEST_MILITARY",\r\n        "description": "I Chola (Rajaraja I) invadono e saccheggiano Anuradhapura; Rajendra I annette l\'intera Rajarata entro il 1017, amministrata come provincia Mummudi-sola-mandalam. Il re Mahinda V catturato, morto in esilio in India (1029).",\r\n        "population_affected": null,\r\n        "confidence_score": 0.75\r\n      }\r\n    ],')
    raw = replace_once(raw, old_vt, new_vt, "#142 variants+tc")
    p142.write_bytes(raw.encode("utf-8"))
    json.loads(raw)
    print("OK #142 re-scope (batch_02)")

    # #386 batch_10: deprecate (flip del campo status esistente, anchor sul record)
    p386 = Path("data/entities/batch_10_indian_subcontinent.json")
    raw = p386.read_bytes().decode("utf-8")
    old386 = ('"ගජබාහු",\r\n    "name_original_lang": "si",\r\n    "entity_type": "kingdom",\r\n'
              '    "year_start": 113,\r\n    "year_end": 236,\r\n    "capital_name": "Anuradhapura (අනුරාධපුර)",\r\n'
              '    "capital_lat": 8.35,\r\n    "capital_lon": 80.4,\r\n    "confidence_score": 0.5,\r\n    "status": "uncertain",')
    new386 = old386.replace('"status": "uncertain",', '"status": "deprecated",')
    raw = replace_once(raw, old386, new386, "#386 deprecate")
    p386.write_bytes(raw.encode("utf-8"))
    json.loads(raw)
    print("OK #386 deprecate (batch_10)")

    # #600 batch_18: rename + year_end + variant/tc cleanup
    p600 = Path("data/entities/batch_18_south_central_asia.json")
    raw = p600.read_bytes().decode("utf-8")
    raw = replace_once(raw, '"name_original": "ការ្យ​ ​សីលេន",', '"name_original": "දඹදෙණිය රාජධානිය",', "#600 name")
    raw = replace_once(raw,
        '"year_start": 1232,\r\n    "year_end": 1597,\r\n    "capital_name": "Dambadeniya",',
        '"year_start": 1232,\r\n    "year_end": 1341,\r\n    "capital_name": "Dambadeniya",', "#600 year")
    old600vt = ('"name_variants": [\r\n      {\r\n        "name": "Kingdom of Dambadeniya",\r\n        "lang": "en",\r\n        "context": "Capital-based designation for the first phase of post-Polonnaruwa Sinhalese kingdoms",\r\n        "period_start": 1232,\r\n        "period_end": 1341\r\n      },\r\n      {\r\n        "name": "දඹදෙණිය රාජධානිය",\r\n        "lang": "si",\r\n        "context": "Sinhalese name for the kingdom during the Dambadeniya capital period",\r\n        "period_start": 1232,\r\n        "period_end": 1341\r\n      },\r\n      {\r\n        "name": "Kingdom of Kotte",\r\n        "lang": "en",\r\n        "context": "Designation for the later phase when the capital moved to Kotte near modern Colombo",\r\n        "period_start": 1412,\r\n        "period_end": 1597\r\n      }\r\n    ],\r\n    "territory_changes": [\r\n      {\r\n        "year": 1232,\r\n        "change_type": "formation",\r\n        "region": "Southwestern Sri Lanka",\r\n        "description": "Vijayabahu III established the kingdom at Dambadeniya after expelling the Kalinga (Odisha) invader Magha from much of the island. He secured the Tooth Relic and the Pali Tripitaka, re-establishing Sinhalese Buddhist sovereignty. The northern Jaffna Kingdom remained independent under Tamil rule.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.65\r\n      },\r\n      {\r\n        "year": 1412,\r\n        "change_type": "expansion",\r\n        "region": "Western and southern Sri Lanka",\r\n        "description": "Parakramabahu VI of Kotte reunified most of the island under Sinhalese rule for the last time, temporarily subduing the Jaffna Kingdom. His court at Kotte became a centre of Sinhalese literary achievement (the age of the Salalihini Sandeshaya).",\r\n        "population_affected": null,\r\n        "confidence_score": 0.65\r\n      },\r\n      {\r\n        "year": 1597,\r\n        "change_type": "dissolution",\r\n        "region": "Southwestern Sri Lanka",\r\n        "description": "Dharmapala of Kotte, having converted to Christianity under Portuguese influence, bequeathed his kingdom to the King of Portugal upon his death. The Portuguese established direct colonial rule over the lowland territories. The highland Kingdom of Kandy continued as an independent Sinhalese state.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.75\r\n      }\r\n    ],')
    new600vt = ('"name_variants": [\r\n      {\r\n        "name": "Kingdom of Dambadeniya",\r\n        "lang": "en",\r\n        "context": "Capital-based designation for the first drifting-capital phase after Polonnaruwa (Dambadeniya/Yapahuwa/Kurunegala). ETHICS-021: #600 was mislabelled with a corrupted Khmer-script name spanning 1232..1597.",\r\n        "period_start": 1232,\r\n        "period_end": 1341\r\n      },\r\n      {\r\n        "name": "Dambadeniya Rajadhaniya",\r\n        "lang": "si-Latn",\r\n        "context": "romanization of දඹදෙණිය රාජධානිය",\r\n        "period_start": 1232,\r\n        "period_end": 1341\r\n      }\r\n    ],\r\n    "territory_changes": [\r\n      {\r\n        "year": 1232,\r\n        "change_type": "LIBERATION",\r\n        "region": "Southwestern Sri Lanka",\r\n        "description": "Vijayabahu III established the kingdom at Dambadeniya after expelling the Kalinga (Odisha) invader Magha (invasion of 1215) from much of the island. He secured the Tooth Relic and the Pali Tripitaka, re-establishing Sinhalese Buddhist sovereignty. The northern Jaffna Kingdom remained independent under Tamil rule.",\r\n        "population_affected": null,\r\n        "confidence_score": 0.65\r\n      }\r\n    ],')
    raw = replace_once(raw, old600vt, new600vt, "#600 variants+tc")
    p600.write_bytes(raw.encode("utf-8"))
    json.loads(raw)
    print("OK #600 re-scope (batch_18)")


# ── SQL prod ─────────────────────────────────────────────────────────
# distribuzione dei siti di #386 (bucket generico) all'entità corretta
SITE_REHOME = {
    784: 142, 783: 142,      # Anuradhapura, Sigiriya → Anuradhapura #142
    351: 387,                 # Polonnaruwa → Polonnaruwa #387
    786: 388, 353: 388,       # Kandy, Dambulla → Kandy #388
    1188: None, 1189: None, 352: None,  # Galle (colonial), Sinharaja, Central Highlands (naturali) → NULL
}


def gen_sql(recs, new_chain) -> str:
    out = []
    w = out.append
    gampola = recs["gampola"]["name_original"]
    kotte = recs["kotte"]["name_original"]
    w("-- v6.99.121 (ETHICS-021) — split Sri Lanka. Backup pg_dump PRIMA.")
    w("-- Dual-write: JSON = batch_02/10/18 + batch_38. psql -v ON_ERROR_STOP=1.")
    w("BEGIN;")
    w("")
    w("-- guard: le nuove entità non esistono già")
    w(f"DO $$ BEGIN IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN ({q(gampola)}, {q(kotte)})) THEN RAISE EXCEPTION 'entità SL già presenti'; END IF; END $$;")
    w("")
    w("-- ── #142 re-scope → Anuradhapura ── (WHERE su PK: i nomi nativi hanno")
    w("-- caratteri fragili — zero-width space, ecc.; la PK è la chiave stabile)")
    w(f"UPDATE geo_entities SET name_original = {q(ANU_NAME)}, year_start = -437, year_end = 1017, confidence_score = 0.7, status = 'confirmed' WHERE id = 142 AND name_original <> {q(ANU_NAME)};")
    w("DELETE FROM name_variants WHERE entity_id = 142 AND name IN ('Sinhalese Kingdom', 'Kingdom of Kandy', 'Regno Singalese');")
    w("UPDATE name_variants SET period_start = -437, context = 'standard English name of the polity (ETHICS-021)' WHERE entity_id = 142 AND name = 'Anuradhapura Kingdom';")
    w("INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES")
    w(f"  (142, 'Rajarata', 'si', -437, 1017, 'the dry-zone king''s country core of the Anuradhapura state', 'Gunawardana, Robe and Plough (1979)'),")
    w(f"  (142, 'Regno di Anuradhapura', 'it', -437, 1017, 'denominazione italiana', NULL);")
    w("DELETE FROM territory_changes WHERE entity_id = 142 AND year = 1815;")
    w("UPDATE territory_changes SET year = -437, region = 'Rajarata (Sri Lanka settentrionale)', change_type = 'INDEPENDENCE', description = 'Convenzione mainstream: Pandukabhaya stabilisce la capitale ad Anuradhapura (~437 a.C.; cronologia corta 377 a.C., dato conteso). L''arrivo di Vijaya (~543 a.C., Mahavamsa) e'' TRADIZIONE fondativa, non confermata archeologicamente.', confidence_score = 0.5 WHERE entity_id = 142 AND year = -543;")
    w("")
    w("-- ── #386 Gajabahu: deprecate + re-home ──")
    w("UPDATE geo_entities SET status = 'deprecated', ethical_notes = COALESCE(ethical_notes,'') || ' DEPRECATA (ETHICS-021, v6.99.121): ''ගජබාහු'' era il nome di un RE (Gajabahu I, r. ~113-136), non di uno stato; il suo periodo cade dentro il regno di Anuradhapura (#142). I territory_changes e i siti sono stati ri-homati.' WHERE id = 386 AND status <> 'deprecated';")
    w("UPDATE territory_changes SET entity_id = 142 WHERE entity_id = 386;")
    for site_id, target in SITE_REHOME.items():
        w(f"UPDATE archaeological_sites SET entity_id = {qn(target)} WHERE id = {site_id} AND entity_id = 386;")
    w("")
    w("-- ── #600 re-scope → Dambadeniya ──")
    w(f"UPDATE geo_entities SET name_original = {q(DAM_NAME)}, year_end = 1341, wikidata_qid = 'Q3136869' WHERE id = 600 AND name_original <> {q(DAM_NAME)};")
    w("DELETE FROM name_variants WHERE entity_id = 600 AND name = 'Kingdom of Kotte';")
    w("DELETE FROM territory_changes WHERE entity_id = 600 AND year IN (1412, 1597);")
    w("UPDATE territory_changes SET change_type = 'LIBERATION' WHERE entity_id = 600 AND year = 1232;")
    w("")
    w("-- ── nuove entità Gampola + Kotte ──")
    for key in NEW_KEYS:
        r = recs[key]
        gj = json.dumps(r["boundary_geojson"], ensure_ascii=False, separators=(",", ": "))
        ref = f"(SELECT id FROM geo_entities WHERE name_original = {q(r['name_original'])})"
        w(f"-- {key}")
        w("INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end, capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source, confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)")
        w(f"VALUES ({q(r['name_original'])}, {q(r['name_original_lang'])}, {q(r['entity_type'])}, {r['year_start']}, {qn(r.get('year_end'))}, {q(r['capital_name'])}, {r['capital_lat']}, {r['capital_lon']}, {q(gj)}, 'historical_approximation', {r['confidence_score']}, 'confirmed', {q(r['ethical_notes'])}, {q(r.get('wikidata_qid'))}, ST_Multi(ST_GeomFromGeoJSON({q(gj)})));")
        for v in r["name_variants"]:
            w(f"INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES ({ref}, {q(v['name'])}, {q(v['lang'])}, {qn(v.get('period_start'))}, {qn(v.get('period_end'))}, {q(v.get('context'))}, {q(v.get('source'))});")
        for tc in r["territory_changes"]:
            w(f"INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES ({ref}, {tc['year']}, {q(tc['region'])}, {q(tc['change_type'])}, {q(tc['description'])}, {qn(tc.get('population_affected'))}, {tc.get('confidence_score', 0.6)});")
        for s in r["sources"]:
            w(f"INSERT INTO sources (entity_id, citation, url, source_type) VALUES ({ref}, {q(s['citation'])}, {q(s.get('url'))}, {q(s['source_type'])});")
        w("")
    w("-- ── catena Sinhalese trunk ──")
    ch = new_chain
    w("INSERT INTO dynasty_chains (name, name_lang, chain_type, region, description, confidence_score, status, ethical_notes, sources)")
    w(f"VALUES ({q(ch['name'])}, 'en', {q(ch['chain_type'])}, {q(ch['region'])}, {q(ch['description'])}, {ch['confidence_score']}, 'confirmed', {q(ch['ethical_notes'])}, {q(json.dumps(ch['sources'], ensure_ascii=False))});")

    def eref(name):
        return f"(SELECT id FROM geo_entities WHERE name_original = {q(name)})"
    for i, ln in enumerate(ch["links"]):
        name = recs[ln["_new"]]["name_original"] if ln.get("_new") else ln["entity_name"]
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES ((SELECT id FROM dynasty_chains WHERE name = {q(ch['name'])}), {eref(name)}, {i}, {qn(ln.get('transition_year'))}, {q(ln.get('transition_type'))}, {'true' if ln.get('is_violent') else 'false'}, {q(ln.get('description'))}, {q(ln.get('ethical_notes'))});")
    w("")
    w("-- ── validazione ──")
    w("DO $$")
    w("DECLARE n int; bad int;")
    w("BEGIN")
    w(f"  SELECT count(*) INTO n FROM geo_entities WHERE name_original IN ({q(gampola)}, {q(kotte)});")
    w("  IF n <> 2 THEN RAISE EXCEPTION 'attese 2 nuove entità, trovate %', n; END IF;")
    w("  SELECT count(*) INTO n FROM geo_entities WHERE id = 142 AND name_original = " + q(ANU_NAME) + " AND year_end = 1017;")
    w("  IF n <> 1 THEN RAISE EXCEPTION '#142 re-scope fallito'; END IF;")
    w("  SELECT count(*) INTO n FROM geo_entities WHERE id = 600 AND name_original = " + q(DAM_NAME) + ";")
    w("  IF n <> 1 THEN RAISE EXCEPTION '#600 re-scope fallito'; END IF;")
    w("  SELECT count(*) INTO n FROM geo_entities WHERE id = 386 AND status = 'deprecated';")
    w("  IF n <> 1 THEN RAISE EXCEPTION '#386 non deprecata'; END IF;")
    w("  SELECT count(*) INTO bad FROM archaeological_sites WHERE entity_id = 386;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% siti ancora su #386', bad; END IF;")
    w("  -- contiguità catena")
    w("  SELECT count(*) INTO bad FROM (SELECT chain_id FROM chain_links WHERE chain_id = (SELECT id FROM dynasty_chains WHERE name = " + q(ch['name']) + ") GROUP BY chain_id HAVING count(*) <> max(sequence_order)+1 OR min(sequence_order) <> 0) t;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION 'catena non contigua'; END IF;")
    w("  -- antimeridian guard")
    w(f"  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN ({q(gampola)}, {q(kotte)}) AND (ST_XMax(boundary_geom) - ST_XMin(boundary_geom)) >= 180;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% boundary attraversano antimeridiano', bad; END IF;")
    w("  RAISE NOTICE 'ETHICS-021 OK: #142/#600 re-scope, #386 deprecata, Gampola+Kotte, catena Sinhalese';")
    w("END $$;")
    w("")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main():
    recs = load()
    entities = [build_entity(recs[k]) for k in NEW_KEYS]
    ENT_OUT.write_text(json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT}: {len(entities)} entità")

    chain = build_chain()
    # JSON chain: risolvi i _new ai nomi
    chain_json = json.loads(json.dumps(chain))
    for ln in chain_json["links"]:
        if ln.get("_new"):
            ln["entity_name"] = recs[ln["_new"]]["name_original"]
        ln.pop("_new", None)
    CHAINS_OUT.write_text(json.dumps([chain_json], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAINS_OUT}")

    entity_surgery()

    # fence: refs catena risolvono in JSON-land vive
    effective = {}
    for path in sorted(Path("data/entities").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            if e.get("name_original"):
                effective[e["name_original"]] = e.get("status", "confirmed")
    for ln in chain_json["links"]:
        st = effective.get(ln["entity_name"])
        assert st is not None, f"ref catena non risolto: {ln['entity_name']!r}"
        assert st != "deprecated", f"ref catena deprecato: {ln['entity_name']!r}"
    print("OK fence: refs catena risolvono a entità vive")

    SQL_OUT.write_text(gen_sql(recs, chain), encoding="utf-8")
    print(f"OK {SQL_OUT}")


if __name__ == "__main__":
    main()
