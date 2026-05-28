-- Post Phase H: 16 entities in 8 aourednik NAME-sharing groups
-- Classification:
--   LEGIT SHARED (same culture/dynasty, just periods): Japan, Makkura, Song, Pallavas
--   SUPER-GROUP LABELS (different polities): Malaysian Islamic states, minor Hindu and Buddhist states, Ptolemaic Kingdom, Tiahuanaco Empire

BEGIN;

-- ───── JAPAN (legit shared, but periods diverge — give distinct circles) ─────
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 350000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 350000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced shared Japan aourednik polygon with 350km circle. Nara period (710-794) was the classical Japanese era centered on Heijo-kyo (Nara), imperial Buddhist court, Kojiki + Nihon Shoki compilation.'
WHERE id = 443;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 350000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 350000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Muromachi shogunate (1336-1573) Ashikaga rule from Kyoto Muromachi district; Sengoku warring states emerged late period; ended with Oda Nobunaga 1573.'
WHERE id = 446;

-- ───── MAKKURA (Nubian Christian kingdoms — different) ─────
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Makouria (Ⲙⲁⲕⲟⲩⲣⲓⲁ, 340-1312 CE) Christian Nubian kingdom, capital Old Dongola; absorbed Nobadia 7th c.; resisted Arab raids via Baqt treaty 651; fell to Islamic Funj sultanate 1312.'
WHERE id = 822;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Nobadia (Ⲛⲟⲩⲃⲁⲇⲓⲁ, 350-707 CE) Northern Christian Nubian kingdom, capital Faras; converted to Coptic Miaphysite Christianity 543; merged with Makouria ~707.'
WHERE id = 974;

-- ───── MALAYSIAN ISLAMIC STATES (super-group label — different islands!) ─────
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced erroneous "Malaysian Islamic states" super-group polygon with 150km circle. Gowa-Tallo (1300-1669) was a Makassarese twin kingdom in S Sulawesi, controlled spice trade until Treaty of Bungaya 1669 (Dutch + Bone alliance).'
WHERE id = 684;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced "Malaysian Islamic states" polygon with 100km circle. Kasultanan Pajang (1548-1588) brief Javanese sultanate succeeding Demak, capital Pajang (Sukoharjo, C Java); fell to Mataram Sultanate 1588.'
WHERE id = 700;

-- ───── MINOR HINDU AND BUDDHIST STATES (super-group — Borneo+Sumatra different) ─────
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced "minor Hindu and Buddhist states" super-group polygon with 200km circle. Kutai Martadipura (350-1635) was the earliest known Hindu kingdom in Indonesia (E Borneo Mahakam River), Pallava-influenced Yupa stone inscriptions; absorbed by Kutai Kartanegara Sultanate 1635.'
WHERE id = 672;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced "minor Hindu and Buddhist states" super-group polygon with 100km circle. Peureulak (840-1292) was a sultanate in N Sumatra (Aceh region), one of the earliest Islamic states in SE Asia; absorbed by Samudera Pasai.'
WHERE id = 886;

-- ───── PALLAVAS (legit — both S Indian, but Chola is post-Pallava successor) ─────
UPDATE geo_entities SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH-pallava-primary] LEGITIMATE Pallava polygon — Pallava dynasty centered at Kanchipuram. Chola Nadu (id=110) is post-Pallava successor empire — corrected separately.' WHERE id = 131;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced shared Pallavas polygon with 400km circle. சோழ நாடு (Medieval Chola Empire, 848-1279) was a Tamil empire at its peak under Rajaraja I + Rajendra I — controlled S India, Sri Lanka, Maldives + naval raids to Srivijaya + Bengal.'
WHERE id = 110;

-- ───── PTOLEMAIC KINGDOM (super-group — Hasmonean is Judean, not Ptolemaic) ─────
UPDATE geo_entities SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH-ptolemy-primary] LEGITIMATE Ptolemaic Kingdom polygon — Ptolemaic Egypt 305-30 BCE. Hasmonean (id=616) erroneously matched — corrected.' WHERE id = 178;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 120000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 120000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced erroneous Ptolemaic Kingdom polygon (Ptolemaic Egypt) with 120km circle around Jerusalem. Hasmonean Kingdom (ממלכת החשמונאים, 140-37 BCE) was the independent Judean state founded by Maccabean revolt against Seleucids; ended with Herodian/Roman intervention 37 BCE.'
WHERE id = 616;

-- ───── SONG EMPIRE (Northern + Southern Song — same dynasty, distinct periods) ─────
UPDATE geo_entities SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH-song-primary] LEGITIMATE Song Empire polygon — full Northern Song extent before Jin invasion 1127.' WHERE id = 106;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 700000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 700000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.75),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced shared Song polygon with 700km circle around Linan (Hangzhou). 南宋 (Southern Song, 1127-1279) was the Song dynasty restricted to S China after Jin invasion sacked Kaifeng; ended with Mongol conquest at Battle of Yamen 1279.'
WHERE id = 450;

-- ───── TIAHUANACO EMPIRE (different cultures — Tiwanaku vs Atacama Likan-antay) ─────
UPDATE geo_entities SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH-tiwanaku-primary] LEGITIMATE Tiwanaku polygon — Andean empire centered on Lake Titicaca 300-1000 CE. Likan-antay (id=958) is separate Atacama culture — corrected.' WHERE id = 202;
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced erroneous Tiahuanaco Empire polygon with 150km circle. Likan-antay (Atacameños, 500-1536) Atacama Desert culture (modern N Chile + S Peru + Bolivia altiplano); ayllu confederation; conquered by Inca ~1450 then Spanish 1536.'
WHERE id = 958;

SELECT COUNT(*) FROM geo_entities WHERE id IN (443,446,822,974,684,700,672,886,131,110,178,616,106,450,202,958);

COMMIT;
