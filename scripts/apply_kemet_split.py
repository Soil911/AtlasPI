"""Split Kemet (v6.99.122, ETHICS-022).

#26 empire → civilization (ombrello); 4 entità-periodo (tꜣ.wy Old/Middle/New
Kingdom + Πτολεμαϊκὴ βασιλεία); re-home 12 eventi + 2 link-conquistatore
(Kush #52, Xšāça #27); catena dei 3 Regni con note sui Periodi Intermedi.

Input:  research_output/split_period_entities.json (4 entità-periodo verificate)
Output: data/entities/batch_39_kemet_split.json (4 nuove)
        data/chains/batch_39_kemet_split.json (1 catena)
        chirurgia batch_00 (#26 retype + note)
        scripts/sql_kemet_split.sql (prod, transazionale)

Usage: PYTHONUTF8=1 python -m scripts.apply_kemet_split
"""
from __future__ import annotations

import json
from pathlib import Path

RESEARCH = Path("research_output/split_period_entities.json")
ENT_OUT = Path("data/entities/batch_39_kemet_split.json")
CHAINS_OUT = Path("data/chains/batch_39_kemet_split.json")
SQL_OUT = Path("scripts/sql_kemet_split.sql")

# nomi normalizzati (schema tꜣ.wy (X) — vedi ETHICS-022 §d)
NAMES = {
    "old_kingdom_egypt": ("tꜣ.wy (Old Kingdom)", "egy"),
    "middle_kingdom_egypt": ("tꜣ.wy (Middle Kingdom)", "egy"),
    "new_kingdom_egypt": ("tꜣ.wy (New Kingdom)", "egy"),
    "ptolemaic_kingdom": ("Πτολεμαϊκὴ βασιλεία", "grc"),
}
NEW_KEYS = list(NAMES)

# re-home eventi: eel_id → key dell'entità-periodo target (move)
EVENT_MOVE = {
    567: "old_kingdom_egypt", 18: "old_kingdom_egypt",
    568: "middle_kingdom_egypt",
    424: "new_kingdom_egypt", 426: "new_kingdom_egypt", 582: "new_kingdom_egypt",
    575: "new_kingdom_egypt", 577: "new_kingdom_egypt", 581: "new_kingdom_egypt",
    22: "new_kingdom_egypt", 427: "new_kingdom_egypt", 20: "new_kingdom_egypt",
}
# eventi di conquista straniera: event_id → (entità conquistatrice, ruolo)
CONQUEROR_ADD = {
    39: (52, "MAIN_ACTOR"),   # conquista kushita -747 → Kush #52
    217: (27, "MAIN_ACTOR"),  # conquista persiana -525 → Xšāça #27
}
# eel che RESTANO su #26 (ombrello): 423 (fondazione -3100), 24 (kushita, VICTIM),
# 348 (persiana, CONQUERED), 28 (Alessandro -334)


def q(s):
    return "NULL" if s is None else "'" + str(s).replace("'", "''") + "'"


def qn(v):
    return "NULL" if v is None else str(v)


def _fix_lang(code: str) -> str:
    """name_variants.lang è String(10): normalizza i codici lunghi/composti."""
    if code and len(code) > 10:
        # es. 'egy-Latn / en' → 'egy-Latn'; prendi il primo token e cap a 10
        first = code.replace("/", " ").split()[0]
        return first[:10]
    return code


def load():
    data = json.loads(RESEARCH.read_text(encoding="utf-8"))
    d = {i["key"]: i["record"] for i in data}
    # normalizza nome/lang delle entità-periodo + lang delle varianti (String(10))
    for key, (name, lang) in NAMES.items():
        d[key]["name_original"] = name
        d[key]["name_original_lang"] = lang
        for v in d[key].get("name_variants", []):
            v["lang"] = _fix_lang(v["lang"])
    return d


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


def build_chain(recs) -> dict:
    ok = recs["old_kingdom_egypt"]["name_original"]
    mk = recs["middle_kingdom_egypt"]["name_original"]
    nk = recs["new_kingdom_egypt"]["name_original"]
    return {
        "name": "Egyptian pharaonic kingdoms: tꜣ.wy (Old) → (Middle) → (New)",
        "name_lang": "en",
        "chain_type": "SUCCESSION",
        "region": "Northeast Africa / Nile Valley (Egypt)",
        "description": "The three 'Kingdom' high-points of pharaonic Egyptian statehood (Old, Middle, New), each separated from the next by an Intermediate Period of real state collapse and (for the New Kingdom's founding) by foreign Hyksos rule.",
        "confidence_score": 0.8,
        "ethical_notes": "This chain links only the three periods of FULL pharaonic statehood and does NOT assert continuous statehood: it is punctuated by the First Intermediate Period (c. -2160..-2055, rival Herakleopolitan and Theban dynasties) and the Second Intermediate Period (c. -1650..-1550), during which the Levantine Hyksos (15th Dynasty) ruled Lower Egypt as a FOREIGN power. The links are typed RESTORATION precisely to mark these interruptions. The Ptolemaic Kingdom (a Macedonian-Greek state) is deliberately NOT in this chain: ~750 years of Third Intermediate Period, Late Period and foreign rule (Kushite 25th Dynasty — see Kush #52; Assyrian, Achaemenid Persian — see Xšāça #27; then Argead Macedonian) separate it from the New Kingdom. The 'Kemet' entity #26 is the civilisation umbrella over all of this, not a continuous state.",
        "sources": [
            {"citation": "Ian Shaw (ed.), The Oxford History of Ancient Egypt, Oxford University Press, 2000", "url": None, "source_type": "academic"},
            {"citation": "Erik Hornung, Rolf Krauss, David Warburton (eds.), Ancient Egyptian Chronology, Brill (HdO 83), 2006", "url": None, "source_type": "academic"},
        ],
        "links": [
            {"_key": "old_kingdom_egypt", "transition_year": None, "transition_type": None, "is_violent": False,
             "description": "The Old Kingdom (c. -2686..-2160), the 'pyramid age' of the 3rd-6th Dynasties, ruled from Memphis (Inbu-hedj).",
             "ethical_notes": None},
            {"_key": "middle_kingdom_egypt", "transition_year": -2055, "transition_type": "RESTORATION", "is_violent": True,
             "description": "Mentuhotep II reunified Egypt by war (c. -2055), ending the First Intermediate Period, and founded the Middle Kingdom (11th-13th Dynasties).",
             "ethical_notes": "The FIRST INTERMEDIATE PERIOD (c. -2160..-2055) — real state collapse with rival Herakleopolitan and Theban dynasties — intervened between the Old and Middle Kingdoms. RESTORATION marks that interruption; the reunification itself was a military conquest."},
            {"_key": "new_kingdom_egypt", "transition_year": -1550, "transition_type": "RESTORATION", "is_violent": True,
             "description": "Ahmose I expelled the Hyksos and founded the New Kingdom (18th-20th Dynasties, c. -1550..-1069), the era of the Egyptian Empire in Nubia and the Levant.",
             "ethical_notes": "The SECOND INTERMEDIATE PERIOD (c. -1650..-1550), during which the Levantine Hyksos (15th Dynasty) ruled Lower Egypt as a FOREIGN power, intervened between the Middle and New Kingdoms. RESTORATION marks that interruption; Ahmose's expulsion of the Hyksos was a war of conquest."},
        ],
    }


def entity_surgery():
    p = Path("data/entities/batch_00_original.json")
    raw = p.read_bytes().decode("utf-8")
    old = ('"name_original": "Kemet",\r\n    "name_original_lang": "egy",\r\n    "entity_type": "empire",')
    new = ('"name_original": "Kemet",\r\n    "name_original_lang": "egy",\r\n    "entity_type": "civilization",')
    lf_old, lf_new = old.replace("\r\n", "\n"), new.replace("\r\n", "\n")
    if raw.count(old) == 1:
        raw = raw.replace(old, new)
    elif raw.count(lf_old) == 1:
        raw = raw.replace(lf_old, lf_new)
    else:
        raise AssertionError(f"#26 retype: {raw.count(old)}/{raw.count(lf_old)}")
    old_notes = 'Quelli mostrati sono una approssimazione del Nuovo Regno (~1400 a.C.)."'
    append = (' ETHICS-022 (v6.99.122): entita\' RI-TIPIZZATA da empire a civilization. '
              'km.t (terra nera) nomina la TERRA/civilta\', non uno stato continuo: i '
              '3070 anni -3100..-30 comprendono i tre Periodi Intermedi di collasso statale '
              '(FIP ~-2160..-2055, SIP ~-1650..-1550, TIP ~-1069..-664) e il dominio '
              'STRANIERO Hyksos, kushita (XXV din., -747, vedi Kush #52), assiro, persiano '
              '(vedi Xšāça #27) e macedone. Le fasi di statualita\' piena sono entita\' proprie: '
              'tꜣ.wy (Old/Middle/New Kingdom) e Πτολεμαϊκὴ βασιλεία. La continuita\' e\' '
              'quella di una civilta\', non di un impero.')
    # inserisce `append` prima della " di chiusura del valore JSON
    new_notes = old_notes[:-1] + append + '"'
    if raw.count(old_notes) == 1:
        raw = raw.replace(old_notes, new_notes)
    else:
        raise AssertionError(f"#26 notes: {raw.count(old_notes)}")
    p.write_bytes(raw.encode("utf-8"))
    json.loads(raw)
    print("OK #26 retype + notes (batch_00)")


def gen_sql(recs, chain) -> str:
    out = []
    w = out.append
    names = [recs[k]["name_original"] for k in NEW_KEYS]
    w("-- v6.99.122 (ETHICS-022) — split Kemet. Backup pg_dump PRIMA.")
    w("-- Dual-write: JSON = batch_00 (#26 retype) + batch_39. psql -v ON_ERROR_STOP=1.")
    w("BEGIN;")
    w("")
    w(f"DO $$ BEGIN IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN ({', '.join(q(n) for n in names)})) THEN RAISE EXCEPTION 'entità Kemet già presenti'; END IF; END $$;")
    w("")
    w("-- ── #26 retype empire → civilization + note ──")
    w("UPDATE geo_entities SET entity_type = 'civilization', ethical_notes = ethical_notes || ' ETHICS-022 (v6.99.122): entità RI-TIPIZZATA da empire a civilization. km.t (terra nera) nomina la TERRA/civiltà, non uno stato continuo: i 3070 anni -3100..-30 comprendono i tre Periodi Intermedi di collasso e il dominio straniero Hyksos, kushita (XXV din. -747, Kush #52), assiro, persiano (Xšāça #27) e macedone. Le fasi di statualità piena sono entità proprie (tꜣ.wy Old/Middle/New Kingdom + Πτολεμαϊκὴ βασιλεία).' WHERE id = 26 AND entity_type = 'empire';")
    w("")
    w("-- ── nuove entità-periodo ──")
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
            w(f"INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES ({ref}, {tc['year']}, {q(tc['region'])}, {q(tc['change_type'])}, {q(tc['description'])}, {qn(tc.get('population_affected'))}, {tc.get('confidence_score', 0.7)});")
        for s in r["sources"]:
            w(f"INSERT INTO sources (entity_id, citation, url, source_type) VALUES ({ref}, {q(s['citation'])}, {q(s.get('url'))}, {q(s['source_type'])});")
        w("")
    w("-- ── re-home 12 eventi interni (move eel.entity_id) ──")
    for eel_id, key in EVENT_MOVE.items():
        ref = f"(SELECT id FROM geo_entities WHERE name_original = {q(recs[key]['name_original'])})"
        w(f"UPDATE event_entity_links SET entity_id = {ref} WHERE id = {eel_id} AND entity_id = 26;")
    w("")
    w("-- ── conquiste straniere: AGGIUNGI il link del conquistatore (Kemet resta VICTIM) ──")
    for ev_id, (conq_id, role) in CONQUEROR_ADD.items():
        w(f"INSERT INTO event_entity_links (event_id, entity_id, role, notes) SELECT {ev_id}, {conq_id}, '{role}', 'ETHICS-022: agentività del conquistatore straniero, aggiunta perché il solo link a Kemet (terra conquistata) la rendeva un evento ''egiziano''.' WHERE NOT EXISTS (SELECT 1 FROM event_entity_links WHERE event_id = {ev_id} AND entity_id = {conq_id});")
    w("")
    w("-- ── catena 3 Regni ──")
    w("INSERT INTO dynasty_chains (name, name_lang, chain_type, region, description, confidence_score, status, ethical_notes, sources)")
    w(f"VALUES ({q(chain['name'])}, 'en', {q(chain['chain_type'])}, {q(chain['region'])}, {q(chain['description'])}, {chain['confidence_score']}, 'confirmed', {q(chain['ethical_notes'])}, {q(json.dumps(chain['sources'], ensure_ascii=False))});")
    for i, ln in enumerate(chain["links"]):
        ref = f"(SELECT id FROM geo_entities WHERE name_original = {q(recs[ln['_key']]['name_original'])})"
        w("INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)")
        w(f"VALUES ((SELECT id FROM dynasty_chains WHERE name = {q(chain['name'])}), {ref}, {i}, {qn(ln.get('transition_year'))}, {q(ln.get('transition_type'))}, {'true' if ln.get('is_violent') else 'false'}, {q(ln.get('description'))}, {q(ln.get('ethical_notes'))});")
    w("")
    w("-- ── validazione ──")
    w("DO $$")
    w("DECLARE n int; bad int;")
    w("BEGIN")
    w(f"  SELECT count(*) INTO n FROM geo_entities WHERE name_original IN ({', '.join(q(n) for n in names)});")
    w("  IF n <> 4 THEN RAISE EXCEPTION 'attese 4 entità-periodo, trovate %', n; END IF;")
    w("  SELECT count(*) INTO n FROM geo_entities WHERE id = 26 AND entity_type = 'civilization';")
    w("  IF n <> 1 THEN RAISE EXCEPTION '#26 non ri-tipizzata'; END IF;")
    w("  SELECT count(*) INTO bad FROM event_entity_links WHERE id IN (" + ",".join(str(k) for k in EVENT_MOVE) + ") AND entity_id = 26;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% eventi non ri-homati', bad; END IF;")
    w("  SELECT count(*) INTO n FROM event_entity_links WHERE event_id = 39 AND entity_id = 52;")
    w("  IF n <> 1 THEN RAISE EXCEPTION 'link Kush mancante'; END IF;")
    w("  SELECT count(*) INTO n FROM event_entity_links WHERE event_id = 217 AND entity_id = 27;")
    w("  IF n <> 1 THEN RAISE EXCEPTION 'link Xšāça mancante'; END IF;")
    w(f"  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN ({', '.join(q(n) for n in names)}) AND (ST_XMax(boundary_geom) - ST_XMin(boundary_geom)) >= 180;")
    w("  IF bad <> 0 THEN RAISE EXCEPTION '% boundary attraversano antimeridiano', bad; END IF;")
    w("  RAISE NOTICE 'ETHICS-022 OK: #26 civilization, 4 entità-periodo, 12 eventi re-homed + 2 conquistatori, catena 3 Regni';")
    w("END $$;")
    w("")
    w("COMMIT;")
    return "\n".join(out) + "\n"


def main():
    recs = load()
    entities = [build_entity(recs[k]) for k in NEW_KEYS]
    ENT_OUT.write_text(json.dumps(entities, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {ENT_OUT}: {len(entities)} entità")

    chain = build_chain(recs)
    chain_json = json.loads(json.dumps(chain))
    for ln in chain_json["links"]:
        ln["entity_name"] = recs[ln["_key"]]["name_original"]
        ln.pop("_key", None)
    CHAINS_OUT.write_text(json.dumps([chain_json], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK {CHAINS_OUT}")

    entity_surgery()

    # fence: refs catena vivi
    effective = {}
    for path in sorted(Path("data/entities").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            if e.get("name_original"):
                effective[e["name_original"]] = e.get("status", "confirmed")
    for ln in chain_json["links"]:
        st = effective.get(ln["entity_name"])
        assert st is not None and st != "deprecated", f"ref catena: {ln['entity_name']!r} ({st})"
    print("OK fence: refs catena vivi")

    SQL_OUT.write_text(gen_sql(recs, chain), encoding="utf-8")
    print(f"OK {SQL_OUT}")


if __name__ == "__main__":
    main()
