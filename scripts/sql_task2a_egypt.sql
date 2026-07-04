-- v6.99.128 (Task 2a / ETHICS-023) — Egitto/Nubia: TIP + Late Period + restore Meroe #552.
-- Dual-write: data/entities/batch_40 + batch_16 (Meroe) + data/chains/batch_39,21.
-- Backup pg_dump PRIMA. psql -v ON_ERROR_STOP=1. Confini INHERITATI (#1058/#1057).
BEGIN;

-- guard: le entità nuove non esistono
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM geo_entities WHERE name_original IN ('tꜣ.wy (Third Intermediate Period)', 'tꜣ.wy (Late Period)')) THEN
    RAISE EXCEPTION 'TIP/Late già presenti — script già applicato?'; END IF;
  IF NOT EXISTS (SELECT 1 FROM geo_entities WHERE id=552 AND status='deprecated') THEN
    RAISE EXCEPTION 'Meroe #552 non è deprecated — restore già applicato?'; END IF;
END $$;

-- ── tꜣ.wy (Third Intermediate Period) (confine inherited da #1058) ──
INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,
  confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)
VALUES ('tꜣ.wy (Third Intermediate Period)', 'egy', 'period', -1069, -664,
  'Tanis (Djanet)', 30.9758, 31.8804, '{"type": "Polygon", "coordinates": [[[29.8, 31.45], [29.3, 30.2], [28.5, 28.3], [28.2, 25.4], [30, 22.5], [30.6, 19.6], [31.6, 18.2], [33.7, 19.3], [33.6, 22.2], [33.9, 26], [32.9, 29.4], [32.4, 31.25], [29.8, 31.45]]]}', 'historical_approximation',
  0.62, 'confirmed', 'Modelling five dynasties (21st-25th) spanning ~400 years of politically fragmented Egypt as ONE entity is a periodization simplification: for most of the period Egypt was NOT unified but split between Tanis (Lower Egypt) and the Theban High Priests of Amun (Upper Egypt), later subdivided among competing Libyan-descended (Meshwesh) rulers of the 22nd-24th dynasties. A single "capital" (Tanis) is therefore a convenience that erases contemporaneous rival seats (Thebes, Bubastis, Herakleopolis, Sais, Napata). ETHICS-002: the Kushite (Nubian) 25th Dynasty of Piye, Shabaka and Taharqa, ruling from Napata, is not a "foreign invasion" to be euphemized as decline — it reversed the earlier New Kingdom Egyptian military conquest and colonial domination of Kush (Nubia), so the "invaders" framing common in older Western Egyptology reflects the perspective of the conquered northern elite, not a neutral fact. The period ended through violence by named perpetrators: the Neo-Assyrian empire under Ashurbanipal sacked Thebes in 664 BCE and installed Psamtik I; historiographies conflict on whether the Saite 26th Dynasty represents indigenous "reunification" or an Assyrian client-state that only later won independence — both readings are recorded here without arbitration.', 'Q212728',
  ST_Multi(ST_GeomFromGeoJSON('{"type": "Polygon", "coordinates": [[[29.8, 31.45], [29.3, 30.2], [28.5, 28.3], [28.2, 25.4], [30, 22.5], [30.6, 19.6], [31.6, 18.2], [33.7, 19.3], [33.6, 22.2], [33.9, 26], [32.9, 29.4], [32.4, 31.25], [29.8, 31.45]]]}')));
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'tꜣ.wy', 'egy', NULL, NULL, 'Ancient Egyptian self-designation of the land itself, ''The Two Lands'' (Upper and Lower Egypt), Egyptological pronunciation ''Tawy''; the polity had no single ancient name for this fragmented era.', 'Wikipedia, ''Upper and Lower Egypt'' / ''Km (hieroglyph)''');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Dritte Zwischenzeit', 'de', NULL, NULL, 'German original of the ''Third Intermediate Period'' scholarly convention, whence the English term derives.', 'Wikidata Q212728 (German label)');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Libyan Period / Libyan anarchy', 'en', NULL, NULL, 'Alternative Egyptological label emphasizing the Libyan-descended (Meshwesh) 22nd-24th dynasties; ''anarchy'' is a dated, value-laden term.', 'Wikidata Q212728 (also known as)');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'al-ʿaṣr al-intiqālī al-thālith', 'ar', NULL, NULL, 'Modern Arabic rendering used in Egyptian scholarship and museums for the Third Intermediate Period.', 'Arabic Wikipedia, العصر الانتقالي الثالث');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Third Intermediate Period of Egypt', 'en', NULL, NULL, 'Standard Egyptological periodization label (21st-25th dynasties, c. 1069-664 BCE); era il name_original inglese, normalizzato alla convenzione tꜣ.wy (X) come i fratelli di catena.', 'Metropolitan Museum of Art, Heilbrunn Timeline of Art History');
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), -1069, 'Nile Delta and Nile Valley (Egypt)', 'FOUNDING', 'Accession of Smendes I at Tanis after the death of Ramesses XI ends the New Kingdom''s 20th Dynasty; central authority fractures between Tanis (Lower Egypt) and the Theban High Priests of Amun (Upper Egypt), inaugurating the Third Intermediate Period.', NULL, 0.62);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), -945, 'Lower Egypt (Bubastis)', 'RESTORATION', 'Sheshonq I, a ruler of Libyan (Meshwesh) descent from Bubastis, founds the 22nd Dynasty and briefly re-establishes direct control over most of Egypt, before renewed fragmentation into the 23rd and 24th dynasties.', NULL, 0.62);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), -728, 'Egypt and Nubia (Kush)', 'CONQUEST', 'The Kushite (Nubian) king Piye (Piankhi) of Napata campaigns north and subdues the Delta rulers, uniting Egypt under the 25th Dynasty; this reverses the earlier New Kingdom Egyptian conquest and domination of Kush. Date c.728 BCE per Piye''s Victory Stela; Kushite control over Upper Egypt began earlier under Kashta.', NULL, 0.62);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), -664, 'Egypt (Thebes, Memphis, Sais)', 'CONQUEST', 'The Neo-Assyrian empire under Ashurbanipal sacks Thebes in 663 BCE and expels the Kushite Tantamani; Psamtik I is installed at Sais and founds the Saite 26th Dynasty, ending the Third Intermediate Period and later reunifying Egypt independently.', NULL, 0.62);
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Kitchen, Kenneth A. (1996). The Third Intermediate Period in Egypt (1100-650 BC). 3rd ed. Warminster: Aris & Phillips. (The foundational chronological study of the period.)', NULL, 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Metropolitan Museum of Art, Heilbrunn Timeline of Art History, ''Egypt in the Third Intermediate Period (ca. 1070-664 B.C.).''', 'https://www.metmuseum.org/essays/egypt-in-the-third-intermediate-period-1070-712-b-c', 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Wikidata, ''Third Intermediate Period of Egypt'' (Q212728), instance of periodization, 1069-664 BCE. Confirms the correct Q-id (hint Q1189047 is ''romantic love'' and is incorrect).', 'https://www.wikidata.org/wiki/Q212728', 'secondary');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Taylor, John H. (2000). ''The Third Intermediate Period (1069-664 BC)'', in Ian Shaw (ed.), The Oxford History of Ancient Egypt. Oxford: Oxford University Press, pp. 330-368.', NULL, 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Third Intermediate Period)'), 'Piye Victory Stela (Gebel Barkal, Napata), c. 727 BCE, Egyptian Museum Cairo JE 48862 — primary royal inscription documenting the Kushite conquest of Egypt and founding of the 25th Dynasty.', NULL, 'primary');

-- ── tꜣ.wy (Late Period) (confine inherited da #1057) ──
INSERT INTO geo_entities (name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon, boundary_geojson, boundary_source,
  confidence_score, status, ethical_notes, wikidata_qid, boundary_geom)
VALUES ('tꜣ.wy (Late Period)', 'egy', 'period', -664, -332,
  'Sais (Zau)', 30.9666, 30.7693, '{"type": "Polygon", "coordinates": [[[30.4, 31.35], [32.35, 31.1], [32.6, 29.5], [33.3, 25.9], [32.95, 24], [31.3, 21.45], [30.6, 21.45], [31, 23.9], [30.4, 26.2], [29.85, 29.2], [30.2, 30.5], [30.4, 31.35]]]}', 'historical_approximation',
  0.82, 'confirmed', 'The period was defined by two foreign conquests that must be named as such, not smoothed over. In 525 BCE the Achaemenid king Cambyses II defeated Psamtik III at Pelusium, sacked Memphis and imposed direct Persian rule (27th Dynasty); Greek sources (Herodotus) portray Cambyses as a desecrator of Egyptian temples and animal cults, though modern scholarship (e.g. the Udjahorresnet inscription) argues this hostile image is partly propaganda — both readings should stand. In 343 BCE Artaxerxes III reconquered Egypt by force, expelling the last native pharaoh Nectanebo II, and ancient tradition again accuses the Persians of temple violence. The Saite capital Sais was itself the seat of an Egyptianized Libyan-descended dynasty, so "native" restoration here is a matter of degree; population figures for this era are not reliably attested and are given as null rather than invented.', 'Q621917',
  ST_Multi(ST_GeomFromGeoJSON('{"type": "Polygon", "coordinates": [[[30.4, 31.35], [32.35, 31.1], [32.6, 29.5], [33.3, 25.9], [32.95, 24], [31.3, 21.45], [30.6, 21.45], [31, 23.9], [30.4, 26.2], [29.85, 29.2], [30.2, 30.5], [30.4, 31.35]]]}')));
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'km.t', 'egy', NULL, NULL, 'Kemet, ''the Black Land'', the most common ancient Egyptian self-designation for the country (fertile Nile soil), transliterated km.t', 'Wikipedia, ''Km and Km.t (Kemet) (hieroglyphs)''; British Museum / standard Egyptological usage');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Late Period of ancient Egypt', 'en', NULL, NULL, 'Standard Egyptological label for the 26th-31st Dynasties, c. 664-332 BCE', 'Metropolitan Museum of Art, ''Egypt in the Late Period (ca. 664-332 B.C.)''');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Mudrāya (𐎸𐎭𐎼𐎠𐎹)', 'peo', NULL, NULL, 'Old Persian name for the Egyptian satrapy under Achaemenid rule (27th and 31st Dynasties)', 'Achaemenid royal inscriptions (Behistun/DNa); Wikipedia ''Late Period of ancient Egypt''');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Saïs (Σάϊς)', 'grc', NULL, NULL, 'Ancient Greek name of the Saite-dynasty capital, from which the ''26th (Saite) Dynasty'' takes its name', 'Herodotus, Histories; EES resource on Sais');
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), -664, 'Egypt (Nile valley and Delta)', 'RESTORATION', 'Psamtik I of Sais reunified Egypt under a native (Egyptianized Libyan-descended) dynasty, ending the Nubian 25th Dynasty and casting off Neo-Assyrian overlordship; opens the Saite renaissance and the Late Period.', NULL, 0.82);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), -525, 'Egypt', 'CONQUEST', 'The Achaemenid king Cambyses II defeated Psamtik III at the Battle of Pelusium, captured Memphis, and annexed Egypt as a Persian satrapy (First Persian Period / 27th Dynasty).', NULL, 0.82);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), -343, 'Egypt', 'OCCUPATION', 'Artaxerxes III (Ochus) reconquered Egypt by force, driving out the last native pharaoh Nectanebo II and re-establishing Persian rule (Second Persian Period / 31st Dynasty).', NULL, 0.82);
INSERT INTO territory_changes (entity_id, year, region, change_type, description, population_affected, confidence_score) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), -332, 'Egypt', 'CONQUEST', 'Alexander III of Macedon took Egypt from the Achaemenid satrap Mazaces without a battle, ending Persian rule and the Late Period; Egypt passes to Argead/Ptolemaic Macedonian control.', NULL, 0.82);
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'The Metropolitan Museum of Art, ''Egypt in the Late Period (ca. 664-332 B.C.)'', Heilbrunn Timeline of Art History.', 'https://www.metmuseum.org/essays/egypt-in-the-late-period-ca-712-332-b-c', 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Lloyd, A. B., ''The Late Period (664-332 BC)'', in I. Shaw (ed.), The Oxford History of Ancient Egypt, Oxford University Press, 2000.', NULL, 'academic');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Herodotus, Histories, Book II (Euterpe) and Book III, on Saite Egypt and Cambyses'' conquest.', 'https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0126', 'primary');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Wikidata item Q621917, ''Late Period of ancient Egypt'' (instance of periodization; start time 664 BCE, end time 332 BCE).', 'https://www.wikidata.org/wiki/Q621917', 'secondary');
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
  ((SELECT id FROM geo_entities WHERE name_original = 'tꜣ.wy (Late Period)'), 'Twenty-sixth Dynasty of Egypt / Late Period of ancient Egypt, Wikipedia (dynastic sequence, Sais as Saite capital, Persian periods).', 'https://en.wikipedia.org/wiki/Late_Period_of_ancient_Egypt', 'secondary');

-- ── restore Meroe #552 (un-deprecate + note convergenti JSON=prod) ──
UPDATE geo_entities SET status='confirmed', ethical_notes='ETHICS: This entity covers the specifically Meroitic phase of the Kingdom of Kush, when the capital shifted south to Meroe and the civilization developed its own distinctive script (Meroitic), iron-smelting industry, and cultural forms distinct from Egyptian influence. Western scholarship long dismissed Meroe as a derivative Egyptian civilization; this view has been challenged by Africanist scholars who emphasize its indigenous African character. The Meroitic script remains only partially deciphered, meaning indigenous textual sources are largely inaccessible -- a significant historiographic gap. Women rulers (Kandakes/Candaces) held significant political and military power, a feature often minimized in Eurocentric accounts. The kingdom''s decline and conquest by Aksum c. 350 CE ended one of Africa''s longest-lived civilizations. Archaeological evidence from Meroe is extensive but has been unevenly studied, with early excavations by colonial-era archaeologists (Reisner, Garstang) following methods now considered destructive. [RESTORED v6.99.128] This entity was deprecated in the v6.85 merge as a supposed duplicate of Kush #52 (they were assumed to share Wikidata Q241790); it is in fact the distinct MEROITIC PHASE of the Kingdom of Kush and is here restored as a phase-entity (ETHICS-015/023, like the tꜣ.wy phases of the pharaonic kingdoms) and re-linked into the Nile Valley / Kush chain #99 after Napata. The wikidata_qid is left null because Q241790 designates the whole Kingdom of Kush (held by #52); Meroe is its southern-capital phase, not a separate polity.' WHERE id=552;

-- ── catena 137 (Regni faraonici): +TIP (seq 3) +Late (seq 4) ──
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
VALUES (137, (SELECT id FROM geo_entities WHERE name_original='tꜣ.wy (Third Intermediate Period)'), 3, -1069, 'DISSOLUTION', false, 'The death of Ramesses XI and accession of Smendes I at Tanis (c. 1069 BCE) ended the New Kingdom and opened four centuries of political fragmentation: Tanite pharaohs of the 21st Dynasty in the north shared power with the Theban High Priests of Amun, and Libyan-descended (Meshwesh) dynasties (22nd-24th) later ruled competing seats.', 'Modelling ~400 years of a divided Egypt (21st-25th dynasties) as one chain node is a periodization convenience; the entity record documents the fragmentation and the Kushite 25th Dynasty''s reversal of the New Kingdom''s earlier domination of Nubia.');
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
VALUES (137, (SELECT id FROM geo_entities WHERE name_original='tꜣ.wy (Late Period)'), 4, -664, 'RESTORATION', true, 'After the Neo-Assyrian sack of Thebes (663 BCE) under Ashurbanipal, Psamtik I of Sais opened the Late Period (26th Saite Dynasty, native Egyptianized Libyan-descended), consolidating an independent reunified Egypt by c. 656 BCE; it ended with the Achaemenid (525, 343 BCE) and Macedonian (332 BCE) conquests.', 'is_violent=true: the reunification followed the Assyrian sack of Thebes; historiographies differ on whether the Saite dynasty was an indigenous restoration or an Assyrian client that later won independence — both readings are recorded on the entity.');
UPDATE dynasty_chains SET name='Egyptian pharaonic kingdoms: tꜣ.wy (Old) → (Middle) → (New) → (Third Intermediate) → (Late Period)' WHERE id=137;

-- ── catena 99 (Nilotica/Kush): +Meroe (seq 3) ──
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
VALUES (99, 552, 3, -300, 'REFORM', false, 'The Kushite kingdom''s primary royal, political and burial focus shifted south toward Meroe (Begrawiya) by c. 300 BCE (Meroe was already significant earlier, and Napata retained religious weight); the Meroitic period developed its own script, large-scale iron industry and the ruling Kandake (Candace) queens, and the kingdom endured until its conquest by Aksum c. 350 CE.', 'Restored as a distinct Meroitic phase-entity (ETHICS-015/023) after being wrongly deprecated as a duplicate of Kush in v6.85; the earlier merge conflated the Meroitic phase with the umbrella Kingdom of Kush (#52, Q241790).');
UPDATE dynasty_chains SET name='Nile Valley / Kush dynastic trunk: Kerma → Kush → Napata → Meroe' WHERE id=99;

-- ── validazione finale ──
DO $$
DECLARE n int; bad int;
BEGIN
  SELECT count(*) INTO n FROM geo_entities WHERE name_original IN ('tꜣ.wy (Third Intermediate Period)', 'tꜣ.wy (Late Period)') AND status='confirmed';
  IF n <> 2 THEN RAISE EXCEPTION 'attese 2 entità nuove confirmed, trovate %', n; END IF;
  IF EXISTS (SELECT 1 FROM geo_entities WHERE id=552 AND status<>'confirmed') THEN RAISE EXCEPTION 'Meroe non ripristinata'; END IF;
  -- contiguità sequence_order catene 99/137
  SELECT count(*) INTO bad FROM (SELECT chain_id FROM chain_links WHERE chain_id IN (99,137) GROUP BY chain_id HAVING count(*) <> max(sequence_order)+1 OR min(sequence_order)<>0) t;
  IF bad <> 0 THEN RAISE EXCEPTION 'sequence_order non contigui su % catene', bad; END IF;
  -- antimeridian guard sui confini nuovi
  SELECT count(*) INTO bad FROM geo_entities WHERE name_original IN ('tꜣ.wy (Third Intermediate Period)', 'tꜣ.wy (Late Period)') AND (ST_XMax(boundary_geom)-ST_XMin(boundary_geom)) >= 180;
  IF bad <> 0 THEN RAISE EXCEPTION '% confini attraversano l''antimeridiano', bad; END IF;
  RAISE NOTICE 'Task 2a OK: TIP + Late Period + Meroe restore + catene 99/137';
END $$;
COMMIT;
