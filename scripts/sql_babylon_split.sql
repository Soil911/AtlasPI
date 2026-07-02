-- v6.99.106 — Babylon #171 split (ETHICS-015 + emendamento 2026-07-02).
-- Generato da scripts/apply_babylon_split.py — NON editare a mano.
-- Dual-write: questo SQL allinea la prod live; i JSON allineano il fresh-seed.
-- Applicare con: ssh ... "docker exec -i cra-atlaspi-db psql -U atlaspi -d atlaspi -v ON_ERROR_STOP=1" < scripts/sql_babylon_split.sql
BEGIN;

-- ── 0. Nuova entita': Babilonia post-cassita (emendamento §1) ──
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)') THEN
    RAISE EXCEPTION 'entita'' Post-Kassite gia'' presente — script gia'' applicato?';
  END IF;
END $$;

INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,
                          capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,
                          confidence_score, status, ethical_notes, boundary_geom)
VALUES ('𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)', 'akk',
        'kingdom', -1155, -626,
        'Babylon', 32.5427, 44.4209,
        '{"type": "MultiPolygon", "coordinates": [[[[43.6, 34.2], [47.6, 33.4], [48.1, 30.6], [46.0, 29.9], [44.3, 30.3], [42.9, 31.9], [43.6, 34.2]]]]}', 'historical_approximation',
        0.62, 'confirmed', 'ETHICS-015 (emendamento 2026-07-02): entita'' creata nella decomposizione del super-aggregato ''Babilonia'' per coprire il periodo post-cassita (-1155..-626), altrimenti privo di rappresentazione. NON e'' un regno indipendente continuo: la periodizzazione segue Brinkman (Post-Kassite Babylonia) e comprende la II Dinastia di Isin (Nabucodonosor I), le successive case dinastiche caldee e aramee frammentate, e la dominazione assira dal 729 a.C. (''doppia monarchia'': Tiglath-Pileser III assume direttamente la corona babilonese). ETHICS-002/007 (non-eufemismo): nel 689 a.C. Sennacherib rase al suolo Babilonia dopo la rivolta di Mushezib-Marduk — deviazione delle acque sull''area urbana, deportazione della statua di Marduk in Assiria; attribuzione esplicita al perpetratore assiro. La guerra civile di Shamash-shuma-ukin contro Ashurbanipal (652-648 a.C.) si concluse con assedio e carestia a Babilonia. Anno di inizio approssimato (1158/1157/1155 a.C. secondo la cronologia adottata). Il confine e'' un''approssimazione onesta della Babilonia propria (tra i fiumi, da Sippar al Golfo), NON i confini di un impero: per gran parte del periodo l''autorita'' politica reale era frammentata o subordinata all''Assiria.',
        ST_Multi(ST_GeomFromGeoJSON('{"type": "MultiPolygon", "coordinates": [[[[43.6, 34.2], [47.6, 33.4], [48.1, 30.6], [46.0, 29.9], [44.3, 30.3], [42.9, 31.9], [43.6, 34.2]]]]}')));

INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), 'Post-Kassite Babylonia', 'en', -1155, -626, 'periodizzazione storiografica standard', 'Brinkman, J.A. A Political History of Post-Kassite Babylonia, 1158-722 B.C. (1968)');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), 'māt Akkadī', 'akk', -1155, -626, 'designazione nativa del paese (''terra di Akkad'') nelle fonti babilonesi del I millennio a.C.', 'Brinkman, J.A. A Political History of Post-Kassite Babylonia, 1158-722 B.C. (1968)');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), 'Babilonia post-cassita', 'it', -1155, -626, 'denominazione italiana', NULL);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), -1155, 'Babilonia (Mesopotamia meridionale)', 'INDEPENDENCE', 'Dopo l''invasione elamita di Shutruk-Nahhunte e Kutir-Nahhunte, che pone fine alla dinastia cassita, il potere passa alla II Dinastia di Isin: Nabucodonosor I (~1125-1104 a.C.) sconfigge l''Elam e recupera la statua di Marduk. Inizio del periodo post-cassita.', NULL, 0.65);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), -729, 'Babilonia', 'CONQUEST_MILITARY', 'Tiglath-Pileser III d''Assiria assume direttamente la corona babilonese (''doppia monarchia''): inizio della dominazione assira diretta, contestata da ripetute rivolte caldee (Marduk-apla-iddina II).', NULL, 0.75);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), -689, 'Babilonia (citta'')', 'CONQUEST_MILITARY', 'Sennacherib distrugge Babilonia dopo la rivolta di Mushezib-Marduk: la citta'' viene rasa al suolo e allagata, la statua di Marduk deportata in Assiria. Ricostruita da Esarhaddon a partire dal 680 a.C.', NULL, 0.8);
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), 'Brinkman, J.A. A Political History of Post-Kassite Babylonia, 1158-722 B.C. Analecta Orientalia 43. Roma: Pontificium Institutum Biblicum, 1968.', 'https://cdli.earth/publications/1699895', 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), 'Frame, Grant. Babylonia 689-627 B.C.: A Political History. Uitgaven van het Nederlands Historisch-Archaeologisch Instituut te Istanbul. Leiden: Nederlands Instituut voor het Nabije Oosten, 1992. ISBN 978-90-6258-069-9.', NULL, 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), 'Beaulieu, Paul-Alain. A History of Babylon, 2200 BC - AD 75. Blackwell History of the Ancient World. Hoboken: Wiley-Blackwell, 2018. ISBN 978-1-4051-8899-9.', 'https://www.wiley.com/en-us/A+History+of+Babylon,+2200+BC+AD+75-p-9781405188999', 'academic');

-- ── 1. Catena #88 seq2: 171 → 1039 (Old Babylonian) ──
UPDATE chain_links SET entity_id = 1039 WHERE chain_id = 88 AND entity_id = 171;

-- ── 2. Eventi: re-homing per periodo (171 → 1039/811/490/post-cassita) ──
UPDATE event_entity_links SET entity_id = (SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'), notes = 'City of Babylon destroyed during the Assyrian-dominated post-Kassite period (not Neo-Babylonian); razed and flooded by Sennacherib after Mushezib-Marduk''s revolt' WHERE id = 340 AND event_id = 213 AND entity_id = 171;  -- evento 213 (-689)
UPDATE event_entity_links SET entity_id = 490 WHERE id = 343 AND event_id = 214 AND entity_id = 171;  -- evento 214 (-612)
UPDATE event_entity_links SET entity_id = 490 WHERE id = 345 AND event_id = 215 AND entity_id = 171;  -- evento 215 (-586)
UPDATE event_entity_links SET entity_id = 490 WHERE id = 346 AND event_id = 216 AND entity_id = 171;  -- evento 216 (-539)
UPDATE event_entity_links SET entity_id = 1039 WHERE id = 576 AND event_id = 448 AND entity_id = 171;  -- evento 448 (-1595)
UPDATE event_entity_links SET entity_id = 811 WHERE id = 579 AND event_id = 455 AND entity_id = 171;  -- evento 455 (-1225)

-- ── 3. Ruler Hammurabi #61 → 1039 (incluso il name_fallback — emendamento §3) ──
UPDATE historical_rulers SET entity_id = 1039, entity_name_fallback = '𒆍𒀭𒊏𒆠 (Old Babylonian)' WHERE id = 61 AND entity_id = 171;

-- ── 4. Citta' Bābilim #15 → 1039 (caveat multi-periodo: emendamento §4) ──
UPDATE historical_cities SET entity_id = 1039 WHERE id = 15 AND entity_id = 171;

-- ── 5. territory_changes: 416 → 1039; 417/418 DELETE (gia' presenti su #490 — emendamento §2) ──
UPDATE territory_changes SET entity_id = 1039 WHERE id = 416 AND entity_id = 171;
DELETE FROM territory_changes WHERE id IN (417, 418) AND entity_id = 171;

-- ── 6. Deprecazione #171 + nota (sources/name_variants restano, come da piano) ──
UPDATE geo_entities SET ethical_notes = ethical_notes || ' DEPRECATA (ETHICS-015, 2026-07-02): questa entita'' era un super-aggregato che presentava come un unico impero continuo (-1894..-539) stati distinti separati da cesure violente (sacco ittita -1595, dominazione cassita, conquista assira, indipendenza caldea -626, caduta persiana -539). Vedi le entita''-periodo: 𒆍𒀭𒊏𒆠 (Old Babylonian) -1894..-1595, 𒌭𒀸𒋗 (Cassiti) -1595..-1155, 𒆳𒆍𒀭𒊏𒆠 (Post-Kassite) -1155..-626, 𒆳𒆍𒀭𒊏𒆠 (Neo-Babylonian) -626..-539. La continuita'' ''babilonese'' e'' documentata dalla catena di successione mesopotamica (#88), non da un''entita'' unica.' WHERE id = 171 AND ethical_notes NOT LIKE '%ETHICS-015%';
UPDATE geo_entities SET status = 'deprecated' WHERE id = 171;

-- ── 7. Fix nota stantia su #1039 (il periodo cassita ora e' coperto) ──
UPDATE geo_entities SET ethical_notes = replace(ethical_notes, 'The intermediate Kassite period (-1595 to -1155) is not separately covered as entity yet.', 'The intermediate Kassite period (-1595 to -1155) is covered by the Kassite entity (𒌭𒀸𒋗), and the post-Kassite period (-1155 to -626) by 𒆳𒆍𒀭𒊏𒆠 (Post-Kassite) — see ETHICS-015.') WHERE id = 1039;

-- ── guard finale (ETHICS-015: eventi su entita' VIVE, zero ref residui) ──
DO $$
DECLARE bad int; ent_id int; ent_status text; ys int; ye int;
BEGIN
  SELECT count(*) INTO bad FROM (
    SELECT entity_id FROM chain_links WHERE entity_id = 171
    UNION ALL SELECT entity_id FROM event_entity_links WHERE entity_id = 171
    UNION ALL SELECT entity_id FROM historical_rulers WHERE entity_id = 171
    UNION ALL SELECT entity_id FROM historical_cities WHERE entity_id = 171
    UNION ALL SELECT entity_id FROM territory_changes WHERE entity_id = 171
  ) q;
  IF bad > 0 THEN RAISE EXCEPTION 'ref residui a 171: %', bad; END IF;

  SELECT count(*) INTO bad FROM (
    SELECT count(*) n, max(sequence_order) mx, min(sequence_order) mn
    FROM chain_links WHERE chain_id = 88
  ) q WHERE mn <> 0 OR mx <> n - 1 OR n <> 7;
  IF bad > 0 THEN RAISE EXCEPTION 'catena 88 non contigua o len != 7'; END IF;

  SELECT e.id, e.status, e.year_start, e.year_end INTO ent_id, ent_status, ys, ye
  FROM event_entity_links l JOIN geo_entities e ON e.id = l.entity_id WHERE l.id = 340;
  IF ent_status = 'deprecated' OR ys > -689 OR ye < -689 THEN
    RAISE EXCEPTION 'evento 213 su entita'' non valida: id=% status=% range=%..%', ent_id, ent_status, ys, ye;
  END IF;

  SELECT count(*) INTO bad FROM sources WHERE entity_id = (SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)');
  IF bad <> 3 THEN RAISE EXCEPTION 'nuova entita'': attese 3 sources, trovate %', bad; END IF;
  SELECT count(*) INTO bad FROM territory_changes WHERE entity_id = (SELECT id FROM geo_entities WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)');
  IF bad <> 3 THEN RAISE EXCEPTION 'nuova entita'': attesi 3 territory_changes, trovati %', bad; END IF;

  -- antimeridian guard (CLAUDE.md geometric checks)
  SELECT count(*) INTO bad FROM geo_entities
  WHERE name_original = '𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)'
    AND (boundary_geom IS NULL OR ST_XMax(boundary_geom) - ST_XMin(boundary_geom) >= 180);
  IF bad > 0 THEN RAISE EXCEPTION 'nuova entita'': boundary_geom NULL o antimeridian'; END IF;

  SELECT count(*) INTO bad FROM geo_entities WHERE id = 171 AND status <> 'deprecated';
  IF bad > 0 THEN RAISE EXCEPTION '171 non deprecata'; END IF;
END $$;

-- verifica leggibile pre-commit
SELECT l.id AS link, l.event_id, e.id AS entity, e.name_original, e.status
FROM event_entity_links l JOIN geo_entities e ON e.id = l.entity_id
WHERE l.id IN (340,343,345,346,576,579) ORDER BY l.event_id;

COMMIT;
