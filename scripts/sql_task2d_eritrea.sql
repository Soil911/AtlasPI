-- v6.99.131 (Task 2d / ETHICS-026) — Eritrea: Colonia Eritrea + catena Medri Bahri.
-- Backup PRIMA. ON_ERROR_STOP=1. Confine inherited da #658. Catena NUOVA via SQL.
BEGIN;
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original = 'Colonia Eritrea') THEN
    RAISE EXCEPTION 'Colonia Eritrea già presente'; END IF;
  IF EXISTS (SELECT 1 FROM dynasty_chains WHERE name = 'Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea') THEN
    RAISE EXCEPTION 'catena eritrea già presente'; END IF;
END $$;

-- ── Colonia Eritrea (confine inherited da #658) ──
INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,
  confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)
VALUES ('Colonia Eritrea', 'it', 'colony', 1890, 1941,
  'Asmara', 15.338, 38.932, '{"type": "Polygon", "coordinates": [[[36.42951, 14.42211], [36.32322, 14.82249], [36.75389, 16.29186], [36.85253, 16.95655], [37.16747, 17.26314], [37.904, 17.42754], [38.41009, 17.998307], [38.990623, 16.840626], [39.26611, 15.922723], [39.814294, 15.435647], [41.179275, 14.49108], [41.734952, 13.921037], [42.276831, 13.343992], [42.589576, 13.000421], [43.081226, 12.699639], [42.779642, 12.455416], [42.35156, 12.54223], [42.00975, 12.86582], [41.59856, 13.45209], [41.1552, 13.77333], [40.8966, 14.11864], [40.02625, 14.51959], [39.34061, 14.53155], [39.0994, 14.74064], [38.51295, 14.50547], [37.90607, 14.95943], [37.59377, 14.2131], [36.42951, 14.42211]]]}', 'historical_approximation',
  0.9, 'confirmed', 'Colonia Eritrea was an occupation regime of the Kingdom of Italy, later intensified under Mussolini''s Fascist state, which used the colony as the launchpad for the 1935-36 invasion and conquest of Ethiopia. The regime imposed racial segregation: separate "native" schools were decreed in 1909, urban segregation in Asmara in 1916, the 1933 legislation regulated the legal status of mixed-race (meticci) children, and "madamato" (Italian-Eritrean unions) was criminalized in 1937 with prison terms of one to five years. Italian settlers reached roughly 75,000 by 1939 (about 53,000 in Asmara alone, out of a city of ~98,000), a demographic transformation imposed on the colonized population. Eritrean troops (ascari) were also conscripted into these campaigns of conquest. The capital''s Latinate name ("Eritrea," from the Greek for the Red Sea) itself supplanted indigenous designations; the highland Tigrinya kingdom of Medri Bahri is recorded as name variant and predecessor rather than erased.', 'Q1232988',
  ST_Multi(ST_GeomFromGeoJSON('{"type": "Polygon", "coordinates": [[[36.42951, 14.42211], [36.32322, 14.82249], [36.75389, 16.29186], [36.85253, 16.95655], [37.16747, 17.26314], [37.904, 17.42754], [38.41009, 17.998307], [38.990623, 16.840626], [39.26611, 15.922723], [39.814294, 15.435647], [41.179275, 14.49108], [41.734952, 13.921037], [42.276831, 13.343992], [42.589576, 13.000421], [43.081226, 12.699639], [42.779642, 12.455416], [42.35156, 12.54223], [42.00975, 12.86582], [41.59856, 13.45209], [41.1552, 13.77333], [40.8966, 14.11864], [40.02625, 14.51959], [39.34061, 14.53155], [39.0994, 14.74064], [38.51295, 14.50547], [37.90607, 14.95943], [37.59377, 14.2131], [36.42951, 14.42211]]]}')));
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'ኤርትራ', 'ti', NULL, NULL, 'Tigrinya name of the territory (Ertra); the Tigrinya-speaking highlands formed the colony''s core and its predecessor kingdom Medri Bahri', 'Wikipedia, ''Eritrea'' / ''Asmara'' (Tigrinya orthography)');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'إرتريا', 'ar', NULL, NULL, 'Arabic name (Iritriyā); Arabic was widely used in the Muslim coastal lowlands and became a co-official language of Eritrea', 'Wikipedia, ''Eritrea'' Arabic-language article');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'Erythrea', 'la', NULL, NULL, 'Latinate form (from Greek Erythra Thalassa, ''Red Sea''); alias su Wikidata Q1232988', 'Wikidata Q1232988 official-name statement');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'Medri Bahri', 'ti', NULL, NULL, 'ምድሪ ባሕሪ (''Land of the Sea''), the Tigrinya highland kingdom that preceded and was absorbed by the colony', 'Wikipedia, ''Medri Bahri''');
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 1890, 'Eritrean coast and highlands (Massawa, Asmara, Assab)', 'FOUNDING', 'King Umberto I of Italy proclaimed the unified Colony of Eritrea on 1 January 1890 by royal decree, consolidating footholds seized at Assab and Massawa (occupied 1885) under General Oreste Baratieri''s occupation of the highlands.', NULL, 0.9);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 1896, 'Adwa (Tigray), Ethiopian frontier', 'CONQUEST', 'Italian expansion inland was halted when Emperor Menelik II''s Ethiopian army decisively defeated General Oreste Baratieri''s Italian colonial force at the Battle of Adwa on 1 March 1896; over 7,000 Italian-side troops were killed, fixing Eritrea''s southern boundary at the Mareb river.', 7000, 0.9);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 1936, 'Italian East Africa (Eritrea, Ethiopia, Somaliland)', 'ANNEXATION', 'After Mussolini''s Fascist Italy invaded and conquered Ethiopia (1935-36) using Eritrea as its base, Eritrea was administratively merged into Africa Orientale Italiana (Italian East Africa) as its northern governorate.', NULL, 0.9);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 1941, 'Eritrea', 'OCCUPATION', 'British and Commonwealth forces defeated the Italians at the Battle of Keren (Feb-March 1941), captured Asmara on 1 April 1941, and took the Italian surrender on 8 April 1941, ending Italian rule and beginning a British Military Administration.', NULL, 0.9);
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'Negash, Tekeste. Italian Colonialism in Eritrea, 1882-1941: Policies, Praxis and Impact. Uppsala: Acta Universitatis Upsaliensis (Studia Historica Upsaliensia 148), 1987.', NULL, 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'Iyob, Ruth. The Eritrean Struggle for Independence: Domination, Resistance, Nationalism, 1941-1993. Cambridge: Cambridge University Press, 1995.', 'https://www.cambridge.org/core/books/eritrean-struggle-for-independence/', 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'Barrera, Giulia. ''Mussolini''s Colonial Race Laws and State-Settler Relations in Africa Orientale Italiana (1935-41).'' Journal of Modern Italian Studies 8, no. 3 (2003): 425-443.', 'https://doi.org/10.1080/09585170320000113770', 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 'Jonas, Raymond. The Battle of Adwa: African Victory in the Age of Empire. Cambridge, MA: Belknap Press of Harvard University Press, 2011.', NULL, 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), '''Italian Eritrea'' and ''Battle of Keren'' (East African Campaign, WWII), cross-verified with Britannica, ''Eritrea: Contesting for the coastlands and beyond.''', 'https://www.britannica.com/place/Eritrea', 'secondary');

-- ── catena NUOVA (COLONIAL) + 2 link ──
INSERT INTO dynasty_chains (name, name_lang, chain_type, region, description, confidence_score, status, ethical_notes, sources)
VALUES ('Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea', 'en', 'COLONIAL', 'Horn of Africa / Eritrean highlands and Red Sea coast', 'The Eritrean highland state from the Medri Bahri kingdom of the Bahr Negash (c. 1137-1879) to its incorporation into Italy''s Colonia Eritrea (1890-1941). A deliberately short two-link chain (ETHICS-017): between Medri Bahri''s end and the Italian colony the highlands were briefly contested by Egypt (1870s) and Ethiopia (Yohannes IV) before Italy consolidated the colony from Massawa (1885) and proclaimed it on 1 January 1890.', 0.7, 'confirmed', 'COLONIAL chain (ETHICS-002: colonial oppression is a first-class datum). Colonia Eritrea was an occupation regime of the Kingdom of Italy, intensified under Fascism and used as the springboard for the 1935-36 invasion of Ethiopia, imposing racial segregation and criminalising Italian-Eritrean unions (madamato, 1937). The chain does NOT end the Eritrean story at colonization: after the Italian defeat (1941) came the British Military Administration (1941-52), the UN-imposed federation with then annexation by Ethiopia (1952/1962), the 30-year Eritrean War of Independence (1961-1991, EPLF) and independence by referendum in 1993. The independent State of Eritrea (1993-) and the British/Ethiopian interregnum are not yet entities in this dataset (queued extension).', '[{"citation": "Negash, Tekeste. Italian Colonialism in Eritrea, 1882-1941. Uppsala: Studia Historica Upsaliensia 148, 1987.", "url": null, "source_type": "academic"}, {"citation": "Iyob, Ruth. The Eritrean Struggle for Independence. Cambridge University Press, 1995.", "url": null, "source_type": "academic"}]');
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
VALUES ((SELECT id FROM dynasty_chains WHERE name = 'Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea'), 658, 0, NULL, NULL, false, 'Medri Bahri (c. 1137-1879), the Christian highland kingdom of the Bahr Negash (''lord of the sea''), centred on Debarwa, spanning the Eritrean plateau between the Mereb river and the Red Sea escarpment.', NULL);
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
VALUES ((SELECT id FROM dynasty_chains WHERE name = 'Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea'), (SELECT id FROM geo_entities WHERE name_original = 'Colonia Eritrea'), 1, 1890, 'CONQUEST', true, 'Italy consolidated the Red Sea coast (Assab 1882, Massawa 1885) and the highlands by military conquest, proclaiming the unified Colonia Eritrea on 1 January 1890; the 1896 Battle of Adwa (Ethiopian victory over Italy) halted Italian expansion inland but Eritrea remained an Italian colony until 1941.', 'Colonial conquest, perpetrator named (Kingdom of Italy). Between Medri Bahri''s end (1879) and the colony, the highlands had been contested by Egypt and by Ethiopia (Yohannes IV).');

DO $$ DECLARE bad int;
BEGIN
  IF NOT EXISTS (SELECT 1 FROM geo_entities WHERE name_original='Colonia Eritrea' AND status='confirmed') THEN RAISE EXCEPTION 'entità non creata'; END IF;
  SELECT count(*) INTO bad FROM chain_links WHERE chain_id=(SELECT id FROM dynasty_chains WHERE name = 'Eritrean state trunk: ምድረ ባሕሪ → Colonia Eritrea');
  IF bad<>2 THEN RAISE EXCEPTION 'catena eritrea attesi 2 link, trovati %', bad; END IF;
  SELECT count(*) INTO bad FROM geo_entities WHERE name_original='Colonia Eritrea' AND (ST_XMax(boundary_geom)-ST_XMin(boundary_geom))>=180;
  IF bad<>0 THEN RAISE EXCEPTION 'confine antimeridiano'; END IF;
  RAISE NOTICE 'Task 2d OK: Colonia Eritrea + catena Medri Bahri (2 link)';
END $$;
COMMIT;
