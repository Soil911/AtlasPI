"""Apply the Babylon #171 split (ETHICS-015 + emendamento 2026-07-02).

Decomposizione del super-aggregato "Babilonia" #171 (-1894..-539): deprecazione
dell'entita' e re-homing dei riferimenti alle entita'-periodo #1039 (Old
Babylonian), #811 (Cassiti), #490 (Neo-Babylonian) e alla NUOVA entita'
post-cassita (-1155..-626, `data/entities/batch_37_babylon_split.json`),
creata dall'emendamento per l'evento #213 (Sennacherib -689, altrimenti
anacronistico su #490).

# ETHICS-015: mostrare "Babilonia" come impero unico e continuo dal 1894 al
# 539 a.C. falsa la storia (nasconde sacco ittita, dominazione cassita,
# conquista assira, indipendenza caldea). La continuita' resta documentata
# dalla catena #88 (una *catena*, non una *entita'*).
# ETHICS-002/007: gli eventi sensibili (Gerusalemme -586, deportazione,
# massacro di Sennacherib -689) restano su entita' VIVE, mai persi.

Dual-write (lezione S51/ETHICS-012 — zero divergenza JSON<->prod):
  * JSON sorgente (fresh-seed): questo script edita 7 file in place.
  * prod SQL: emette ``scripts/sql_babylon_split.sql`` (transazionale,
    guard-rail inclusi) da applicare via ssh/psql con ON_ERROR_STOP=1.
  La nuova entita' e' INSERITA anche via SQL (stesso contenuto del JSON,
  letto da batch_37 — fonte unica); l'ingest al boot poi la salta per nome.

Usage: PYTHONUTF8=1 python -m scripts.apply_babylon_split
       (poi rivedi il .sql, backup pg_dump, applica a prod, deploy)
"""

from __future__ import annotations

import json
from pathlib import Path

SQL_OUT = Path("scripts/sql_babylon_split.sql")

# ─── nomi esatti (== name_original JSON) ↔ id prod (verificati 2026-07-02) ────
BABYLON_AGGREGATE = "𒆍𒀭𒊏𒆠"                      # id 171 → deprecated
OLD_BABYLONIAN = "𒆍𒀭𒊏𒆠 (Old Babylonian)"        # id 1039
KASSITE = "𒌭𒀸𒋗"                                  # id 811
NEO_BABYLONIAN = "𒆳𒆍𒀭𒊏𒆠"                        # id 490
POST_KASSITE = "𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)"           # NUOVA — id assegnato da prod
ID = {OLD_BABYLONIAN: 1039, KASSITE: 811, NEO_BABYLONIAN: 490, BABYLON_AGGREGATE: 171}

# id prod delle righe da ri-homare (snapshot prod 2026-07-02)
CHAIN_88 = 88
EVENT_LINKS = {
    # link_id: (event_id, event_year, new_entity_name)
    576: (448, -1595, OLD_BABYLONIAN),   # sacco ittita → fine Old Babylonian
    579: (455, -1225, KASSITE),          # Tukulti-Ninurta → Babilonia cassita
    340: (213, -689, POST_KASSITE),      # Sennacherib → post-cassita (EMENDAMENTO §1)
    343: (214, -612, NEO_BABYLONIAN),    # caduta di Ninive
    345: (215, -586, NEO_BABYLONIAN),    # distruzione Primo Tempio
    346: (216, -539, NEO_BABYLONIAN),    # conquista di Ciro
}
RULER_HAMMURABI = 61
CITY_BABILIM = 15
TC_FOUNDATION = 416          # -1894 → 1039 (move)
TC_DELETE = (417, 418)       # -586/-539 → DELETE: #490 ha gia' le proprie righe
                             # (EMENDAMENTO §2 — evitare duplicati/doppio conteggio)

# note evento #213 (identiche JSON <-> prod)
EVENT_213_NOTES = (
    "City of Babylon destroyed during the Assyrian-dominated post-Kassite "
    "period (not Neo-Babylonian); razed and flooded by Sennacherib after "
    "Mushezib-Marduk's revolt"
)

# nota di deprecazione #171 (appesa alle ethical_notes esistenti, JSON <-> prod)
DEPRECATION_NOTE = (
    " DEPRECATA (ETHICS-015, 2026-07-02): questa entita' era un super-aggregato "
    "che presentava come un unico impero continuo (-1894..-539) stati distinti "
    "separati da cesure violente (sacco ittita -1595, dominazione cassita, "
    "conquista assira, indipendenza caldea -626, caduta persiana -539). Vedi le "
    "entita'-periodo: 𒆍𒀭𒊏𒆠 (Old Babylonian) -1894..-1595, 𒌭𒀸𒋗 (Cassiti) "
    "-1595..-1155, 𒆳𒆍𒀭𒊏𒆠 (Post-Kassite) -1155..-626, 𒆳𒆍𒀭𒊏𒆠 (Neo-Babylonian) "
    "-626..-539. La continuita' 'babilonese' e' documentata dalla catena di "
    "successione mesopotamica (#88), non da un'entita' unica."
)

# fix nota stantia su #1039 (il periodo cassita ORA e' coperto da #811)
OLD_1039_SENTENCE = (
    "The intermediate Kassite period (-1595 to -1155) is not separately "
    "covered as entity yet."
)
NEW_1039_SENTENCE = (
    "The intermediate Kassite period (-1595 to -1155) is covered by the "
    "Kassite entity (𒌭𒀸𒋗), and the post-Kassite period (-1155 to -626) by "
    "𒆳𒆍𒀭𒊏𒆠 (Post-Kassite) — see ETHICS-015."
)


# ─── helpers ──────────────────────────────────────────────────────────────────
def _newline_of(path: Path) -> str:
    return "\r\n" if b"\r\n" in path.read_bytes() else "\n"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data) -> None:
    """Riscrive il JSON preservando il line-ending originale del file."""
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    with path.open("w", encoding="utf-8", newline=_newline_of(path)) as f:
        f.write(text)


def _replace_exact(path: Path, old: str, new: str) -> None:
    """Chirurgia a stringa (byte-preserving) per i file in formato compatto."""
    raw = path.read_bytes().decode("utf-8")
    n = raw.count(old)
    if n != 1:
        raise SystemExit(f"{path}: attese 1 occorrenza di {old!r}, trovate {n}")
    path.write_bytes(raw.replace(old, new).encode("utf-8"))


def _sql_str(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


NEW_ENTITY_SUBQ = (
    f"(SELECT id FROM geo_entities WHERE name_original = {_sql_str(POST_KASSITE)})"
)


# ─── JSON edits ───────────────────────────────────────────────────────────────
def edit_entities_batch_03() -> dict:
    """#171: deprecated + nota; ritorna il territory_change -1894 da spostare."""
    path = Path("data/entities/batch_03_africa_mideast.json")
    data = _load(path)
    ent = next(e for e in data if e["name_original"] == BABYLON_AGGREGATE)
    assert ent["year_start"] == -1894 and ent["year_end"] == -539
    tcs = ent["territory_changes"]
    assert [tc["year"] for tc in tcs] == [-1894, -586, -539], "territory_changes inattesi su #171"
    foundation_tc = tcs[0]
    ent["territory_changes"] = []
    ent["status"] = "deprecated"
    if "ETHICS-015" not in (ent.get("ethical_notes") or ""):
        ent["ethical_notes"] = (ent.get("ethical_notes") or "") + DEPRECATION_NOTE
    _save(path, data)
    return foundation_tc


def edit_entities_batch_36(foundation_tc: dict) -> None:
    """#1039: riceve il territory_change -1894; fix della nota stantia."""
    path = Path("data/entities/batch_36_prod_reconciliation.json")
    data = _load(path)
    ent = next(e for e in data if e["name_original"] == OLD_BABYLONIAN)
    assert ent["territory_changes"] == [], "#1039 territory_changes non vuoto"
    ent["territory_changes"] = [foundation_tc]
    if OLD_1039_SENTENCE not in ent["ethical_notes"]:
        raise SystemExit("frase stantia non trovata nelle note di #1039")
    ent["ethical_notes"] = ent["ethical_notes"].replace(OLD_1039_SENTENCE, NEW_1039_SENTENCE)
    _save(path, data)


def edit_chain_88() -> None:
    """Catena #88 seq2: 𒆍𒀭𒊏𒆠 → 𒆍𒀭𒊏𒆠 (Old Babylonian). File compatto → chirurgia."""
    _replace_exact(
        Path("data/chains/batch_30_ancient_mesopotamian.json"),
        f'"entity_name": "{BABYLON_AGGREGATE}",',
        f'"entity_name": "{OLD_BABYLONIAN}",',
    )


def edit_events_batch_09() -> None:
    """Eventi 213/214/215/216: re-point per anno (round-trip JSON stabile)."""
    path = Path("data/events/batch_09_ancient_expansion.json")
    data = _load(path)
    by_year = {-689: POST_KASSITE, -612: NEO_BABYLONIAN, -586: NEO_BABYLONIAN, -539: NEO_BABYLONIAN}
    hits = 0
    for ev in data:
        target = by_year.get(ev.get("year"))
        if not target:
            continue
        for link in ev.get("entity_links", []):
            if link["entity_name_original"] == BABYLON_AGGREGATE:
                link["entity_name_original"] = target
                if ev["year"] == -689:
                    link["notes"] = EVENT_213_NOTES
                hits += 1
    if hits != 4:
        raise SystemExit(f"batch_09: attesi 4 link, trovati {hits}")
    _save(path, data)


def edit_events_batch_24() -> None:
    """Eventi 448 (-1595 → Old Babylonian) e 455 (-1225 → Cassiti)."""
    path = Path("data/events/batch_24_bronze_age.json")
    data = _load(path)
    by_year = {-1595: OLD_BABYLONIAN, -1225: KASSITE}
    hits = 0
    for ev in data:
        target = by_year.get(ev.get("year"))
        if not target:
            continue
        for link in ev.get("entity_links", []):
            if link["entity_name_original"] == BABYLON_AGGREGATE:
                link["entity_name_original"] = target
                hits += 1
    if hits != 2:
        raise SystemExit(f"batch_24: attesi 2 link, trovati {hits}")
    _save(path, data)


def edit_ruler_hammurabi() -> None:
    path = Path("data/rulers/batch_01_global_expansion.json")
    data = _load(path)
    ruler = next(r for r in data if r.get("name_original") == "𒄩𒄠𒈬𒊏𒁉")
    assert ruler["entity_name"] == BABYLON_AGGREGATE
    ruler["entity_name"] = OLD_BABYLONIAN
    _save(path, data)


def edit_city_babilim() -> None:
    """Bābilim: fix del riferimento MORTO 'Māt Akkadī' (divergenza preesistente,
    emendamento §4) → Old Babylonian, come da piano. File compatto → chirurgia."""
    _replace_exact(
        Path("data/cities/batch_01_mediterranean_mena.json"),
        '"entity_name_original": "Māt Akkadī",',
        f'"entity_name_original": "{OLD_BABYLONIAN}",',
    )


# ─── SQL emission ─────────────────────────────────────────────────────────────
def emit_sql(foundation_tc: dict) -> None:
    new_ent = _load(Path("data/entities/batch_37_babylon_split.json"))[0]
    assert new_ent["name_original"] == POST_KASSITE

    boundary_json = json.dumps(new_ent["boundary_geojson"])

    sql: list[str] = [
        "-- v6.99.106 — Babylon #171 split (ETHICS-015 + emendamento 2026-07-02).",
        "-- Generato da scripts/apply_babylon_split.py — NON editare a mano.",
        "-- Dual-write: questo SQL allinea la prod live; i JSON allineano il fresh-seed.",
        "-- Applicare con: ssh ... \"docker exec -i cra-atlaspi-db psql -U atlaspi -d atlaspi -v ON_ERROR_STOP=1\" < scripts/sql_babylon_split.sql",
        "BEGIN;",
        "",
        "-- ── 0. Nuova entita': Babilonia post-cassita (emendamento §1) ──",
        "DO $$ BEGIN",
        f"  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original = {_sql_str(POST_KASSITE)}) THEN",
        "    RAISE EXCEPTION 'entita'' Post-Kassite gia'' presente — script gia'' applicato?';",
        "  END IF;",
        "END $$;",
        "",
        "INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,",
        "                          capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,",
        "                          confidence_score, status, ethical_notes, boundary_geom)",
        f"VALUES ({_sql_str(new_ent['name_original'])}, {_sql_str(new_ent['name_original_lang'])},",
        f"        {_sql_str(new_ent['entity_type'])}, {new_ent['year_start']}, {new_ent['year_end']},",
        f"        {_sql_str(new_ent['capital_name'])}, {new_ent['capital_lat']}, {new_ent['capital_lon']},",
        f"        {_sql_str(boundary_json)}, {_sql_str(new_ent['boundary_source'])},",
        f"        {new_ent['confidence_score']}, {_sql_str(new_ent['status'])}, {_sql_str(new_ent['ethical_notes'])},",
        f"        ST_Multi(ST_GeomFromGeoJSON({_sql_str(boundary_json)})));",
        "",
    ]
    for nv in new_ent["name_variants"]:
        sql.append(
            "INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES"
            f"\n  ({NEW_ENTITY_SUBQ}, {_sql_str(nv['name'])}, {_sql_str(nv['lang'])},"
            f" {_sql_str(nv.get('period_start'))}, {_sql_str(nv.get('period_end'))},"
            f" {_sql_str(nv.get('context'))}, {_sql_str(nv.get('source'))});"
        )
    for tc in new_ent["territory_changes"]:
        sql.append(
            "INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES"
            f"\n  ({NEW_ENTITY_SUBQ}, {tc['year']}, {_sql_str(tc['region'])}, {_sql_str(tc['change_type'])},"
            f" {_sql_str(tc['description'])}, {_sql_str(tc.get('population_affected'))}, {tc['confidence_score']});"
        )
    for s in new_ent["sources"]:
        sql.append(
            "INSERT INTO sources (entity_id, citation, url, source_type) VALUES"
            f"\n  ({NEW_ENTITY_SUBQ}, {_sql_str(s['citation'])}, {_sql_str(s.get('url'))}, {_sql_str(s['source_type'])});"
        )

    sql += [
        "",
        "-- ── 1. Catena #88 seq2: 171 → 1039 (Old Babylonian) ──",
        f"UPDATE chain_links SET entity_id = 1039 WHERE chain_id = {CHAIN_88} AND entity_id = 171;",
        "",
        "-- ── 2. Eventi: re-homing per periodo (171 → 1039/811/490/post-cassita) ──",
    ]
    for link_id, (event_id, year, target) in sorted(EVENT_LINKS.items()):
        eid = ID.get(target)
        target_sql = str(eid) if eid else NEW_ENTITY_SUBQ
        extra = f", notes = {_sql_str(EVENT_213_NOTES)}" if event_id == 213 else ""
        sql.append(
            f"UPDATE event_entity_links SET entity_id = {target_sql}{extra} "
            f"WHERE id = {link_id} AND event_id = {event_id} AND entity_id = 171;  -- evento {event_id} ({year})"
        )

    sql += [
        "",
        "-- ── 3. Ruler Hammurabi #61 → 1039 (incluso il name_fallback — emendamento §3) ──",
        f"UPDATE historical_rulers SET entity_id = 1039, entity_name_fallback = {_sql_str(OLD_BABYLONIAN)} "
        f"WHERE id = {RULER_HAMMURABI} AND entity_id = 171;",
        "",
        "-- ── 4. Citta' Bābilim #15 → 1039 (caveat multi-periodo: emendamento §4) ──",
        f"UPDATE historical_cities SET entity_id = 1039 WHERE id = {CITY_BABILIM} AND entity_id = 171;",
        "",
        "-- ── 5. territory_changes: 416 → 1039; 417/418 DELETE (gia' presenti su #490 — emendamento §2) ──",
        f"UPDATE territory_changes SET entity_id = 1039 WHERE id = {TC_FOUNDATION} AND entity_id = 171;",
        f"DELETE FROM territory_changes WHERE id IN {TC_DELETE} AND entity_id = 171;",
        "",
        "-- ── 6. Deprecazione #171 + nota (sources/name_variants restano, come da piano) ──",
        f"UPDATE geo_entities SET ethical_notes = ethical_notes || {_sql_str(DEPRECATION_NOTE)} "
        "WHERE id = 171 AND ethical_notes NOT LIKE '%ETHICS-015%';",
        "UPDATE geo_entities SET status = 'deprecated' WHERE id = 171;",
        "",
        "-- ── 7. Fix nota stantia su #1039 (il periodo cassita ora e' coperto) ──",
        f"UPDATE geo_entities SET ethical_notes = replace(ethical_notes, {_sql_str(OLD_1039_SENTENCE)}, {_sql_str(NEW_1039_SENTENCE)}) "
        "WHERE id = 1039;",
        "",
        "-- ── guard finale (ETHICS-015: eventi su entita' VIVE, zero ref residui) ──",
        "DO $$",
        "DECLARE bad int; ent_id int; ent_status text; ys int; ye int;",
        "BEGIN",
        "  SELECT count(*) INTO bad FROM (",
        "    SELECT entity_id FROM chain_links WHERE entity_id = 171",
        "    UNION ALL SELECT entity_id FROM event_entity_links WHERE entity_id = 171",
        "    UNION ALL SELECT entity_id FROM historical_rulers WHERE entity_id = 171",
        "    UNION ALL SELECT entity_id FROM historical_cities WHERE entity_id = 171",
        "    UNION ALL SELECT entity_id FROM territory_changes WHERE entity_id = 171",
        "  ) q;",
        "  IF bad > 0 THEN RAISE EXCEPTION 'ref residui a 171: %', bad; END IF;",
        "",
        "  SELECT count(*) INTO bad FROM (",
        "    SELECT count(*) n, max(sequence_order) mx, min(sequence_order) mn",
        f"    FROM chain_links WHERE chain_id = {CHAIN_88}",
        "  ) q WHERE mn <> 0 OR mx <> n - 1 OR n <> 7;",
        "  IF bad > 0 THEN RAISE EXCEPTION 'catena 88 non contigua o len != 7'; END IF;",
        "",
        "  SELECT e.id, e.status, e.year_start, e.year_end INTO ent_id, ent_status, ys, ye",
        "  FROM event_entity_links l JOIN geo_entities e ON e.id = l.entity_id WHERE l.id = 340;",
        "  IF ent_status = 'deprecated' OR ys > -689 OR ye < -689 THEN",
        "    RAISE EXCEPTION 'evento 213 su entita'' non valida: id=% status=% range=%..%', ent_id, ent_status, ys, ye;",
        "  END IF;",
        "",
        f"  SELECT count(*) INTO bad FROM sources WHERE entity_id = {NEW_ENTITY_SUBQ};",
        "  IF bad <> 3 THEN RAISE EXCEPTION 'nuova entita'': attese 3 sources, trovate %', bad; END IF;",
        f"  SELECT count(*) INTO bad FROM territory_changes WHERE entity_id = {NEW_ENTITY_SUBQ};",
        "  IF bad <> 3 THEN RAISE EXCEPTION 'nuova entita'': attesi 3 territory_changes, trovati %', bad; END IF;",
        "",
        "  -- antimeridian guard (CLAUDE.md geometric checks)",
        "  SELECT count(*) INTO bad FROM geo_entities",
        f"  WHERE name_original = {_sql_str(POST_KASSITE)}",
        "    AND (boundary_geom IS NULL OR ST_XMax(boundary_geom) - ST_XMin(boundary_geom) >= 180);",
        "  IF bad > 0 THEN RAISE EXCEPTION 'nuova entita'': boundary_geom NULL o antimeridian'; END IF;",
        "",
        "  SELECT count(*) INTO bad FROM geo_entities WHERE id = 171 AND status <> 'deprecated';",
        "  IF bad > 0 THEN RAISE EXCEPTION '171 non deprecata'; END IF;",
        "END $$;",
        "",
        "-- verifica leggibile pre-commit",
        "SELECT l.id AS link, l.event_id, e.id AS entity, e.name_original, e.status",
        "FROM event_entity_links l JOIN geo_entities e ON e.id = l.entity_id",
        "WHERE l.id IN (340,343,345,346,576,579) ORDER BY l.event_id;",
        "",
        "COMMIT;",
    ]
    SQL_OUT.write_text("\n".join(sql) + "\n", encoding="utf-8")


def main() -> None:
    foundation_tc = edit_entities_batch_03()
    edit_entities_batch_36(json.loads(json.dumps(foundation_tc)))
    edit_chain_88()
    edit_events_batch_09()
    edit_events_batch_24()
    edit_ruler_hammurabi()
    edit_city_babilim()
    emit_sql(foundation_tc)
    print("JSON aggiornati (7 file). SQL →", SQL_OUT)


if __name__ == "__main__":
    main()
