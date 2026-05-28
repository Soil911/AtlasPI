-- Boundary Review v6.99.79 — Tier 2 Batch 1: 9 aourednik super-group polygons
-- Total: 40 entities. Keep ~5 primary matches, fix ~35 with circles.

BEGIN;

-- ========== KINGDOM OF DAVID AND SOLOMON (5 entities, all to fix) ==========
-- "United Monarchy" is itself disputed historically; polygon mismatch for all 5
-- Tadmor (Palmyra) — caravanserai oasis ~40km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 40000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 40000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/levant-fix] Replaced erroneous "Kingdom of David and Solomon" polygon (anachronistic+contested) with 40km circle around Palmyra. Tadmor/Palmyra was an oasis trading city (Bronze Age through Roman), not part of the Israelite kingdom.'
WHERE id = 180;

-- Phoenicia (confederation of coastal cities Tyre/Sidon/Byblos/Arwad) ~250km along Levant coast
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/levant-fix] Replaced erroneous "Kingdom of David and Solomon" polygon with 200km circle around Tyre. Phoenicia was a confederation of independent coastal city-states (Tyre, Sidon, Byblos, Arwad) along Lebanese/Syrian coast, not a unified kingdom or part of Israelite kingdom.'
WHERE id = 269;

-- Edom — Negev + S Jordan ~150km from Bozrah
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/levant-fix] Replaced erroneous "Kingdom of David and Solomon" polygon with 150km circle around Bozrah. Edom was an Iron Age kingdom in southern Jordan/Negev highlands, separate from and often hostile to Israel/Judah.'
WHERE id = 499;

-- Kingdom of Israel (Northern) ~120km from Samaria
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 120000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 120000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/levant-fix] Replaced erroneous "Kingdom of David and Solomon" polygon with 120km circle around Samaria. Kingdom of Israel (northern) had separate capital at Samaria (then Shechem, then Tirzah), distinct from southern Judah; ended with Assyrian conquest 720 BCE.'
WHERE id = 270;

-- Kingdom of Judah ~100km from Jerusalem
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/levant-fix] Replaced erroneous "Kingdom of David and Solomon" polygon with 100km circle around Jerusalem. Kingdom of Judah was the southern Iron Age Israelite kingdom, smaller than Israel; existed 930 BCE - 586 BCE (Babylonian conquest).'
WHERE id = 271;

-- ========== TAINO (6 entities, KEEP id=532) ==========
-- 532 Taino confederation = primary match, keep polygon
UPDATE geo_entities SET
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-taino-primary] LEGITIMATE Taino polygon match (boundary_aourednik_name="Taino"). 5 specific cacicazgos (Quisqueya, Borikén, Cuba, Jamaica, Xaragua) erroneously shared this polygon — they have been corrected to their island-specific circles. Taino polygon here represents the Greater Antilles + Lucayan zone.'
WHERE id = 532;

-- Quisqueya (Hispaniola cacicazgos) ~180km from Maguana
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 180000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 180000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-taino-fix] Replaced erroneous shared Taino polygon with 180km circle around Maguana. Quisqueya = Taino name for Hispaniola (modern DR + Haiti) with 5 paramount cacicazgos.'
WHERE id = 946;

-- Borikén (Puerto Rico) ~80km from Guaynia
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-taino-fix] Replaced erroneous shared Taino polygon with 80km circle around Guaynia. Borikén = Taino name for Puerto Rico — main cacique Agüeybaná I at contact (1493).'
WHERE id = 945;

-- Cuba cacicazgos ~400km from Bayamo (Cuba is large)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-taino-fix] Replaced erroneous shared Taino polygon with 400km circle around Bayamo. Cuba had multiple cacicazgos (Baracoa, Bayamo, Camagüey, Guanacanabibes, Habana, Hanábana, Jagua, Macaca, Maniabón, Maisí, Sabana) — Taino + Ciboney peoples; Hatuey led resistance to Spanish 1511-12.'
WHERE id = 947;

-- Jamaica cacicazgos ~100km from Maima
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-taino-fix] Replaced erroneous shared Taino polygon with 100km circle around Maima. Jamaica (Xaymaca) had Taino cacicazgos pre-contact; primary site Maima near St Ann''s Bay.'
WHERE id = 948;

-- Xaragua (SW Hispaniola kingdom of Anacaona) ~80km from Yaguana
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-taino-fix] Replaced erroneous shared Taino polygon with 80km circle around Yaguana (modern Léogâne, Haiti). Xaragua was the SW Hispaniola Taino kingdom (Tiburon peninsula) — last ruler Anacaona executed by Spanish 1504.'
WHERE id = 797;

-- ========== GREEK CITY-STATES (5 entities, all to fix) ==========
-- 274 Mycenae ~80km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/greek-fix] Replaced erroneous "Greek city-states" polygon with 80km circle around Mycenae. Mycenae was a Late Bronze Age palace center (1600-1100 BCE) in Argolid Peloponnese, NOT a Classical Greek city-state.'
WHERE id = 274;

-- 812 Arzawa (Anatolian, NOT Greek) ~300km from Apasa/Ephesus
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/greek-fix] Replaced erroneous "Greek city-states" polygon with 300km circle around Apasa. Arzawa was a Late Bronze Age Anatolian kingdom in western Anatolia (Late 15th-13th c. BCE), Hittite rival — NOT Greek.'
WHERE id = 812;

-- 814 Karia (Anatolian, partially Hellenized later) ~150km from Mylasa
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/greek-fix] Replaced erroneous "Greek city-states" polygon with 150km circle around Mylasa. Caria was a SW Anatolian Iron Age region (Late 1100-129 BCE) with Carian and later Hellenized population (Hekatomnid dynasty including Mausolus, 4th c. BCE); finally Roman after 129 BCE.'
WHERE id = 814;

-- 65 Macedon (Argead+Antigonid 808-168 BCE, Pella) — heartland ~250km (Alexander's empire NOT here since this is the long range)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/greek-fix] Replaced erroneous "Greek city-states" polygon with 250km circle around Pella. Kingdom of Macedon was a Hellenic kingdom (not city-state). 250km represents Macedonian heartland; for Alexander''s peak conquests (336-323 BCE) see Hellenistic empire entities separately.'
WHERE id = 65;

-- 286 Syracuse ~30km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/greek-fix] Replaced erroneous "Greek city-states" polygon with 30km circle around Syracuse. Syracuse was an individual Greek city-state in SE Sicily (Corinthian colony 734 BCE - Roman conquest 212 BCE), at peak controlled most of E Sicily under Dionysius I/II.'
WHERE id = 286;

-- ========== MINOR STATES — Hellenistic Anatolia (4 entities) ==========
-- 615 Cappadocia ~250km from Mazaka
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/anatolia-fix] Replaced erroneous "minor states" polygon with 250km circle around Mazaka. Cappadocia was a Hellenistic kingdom (331 BCE - 17 CE) in eastern Anatolian highlands (Ariarathid + Roman client dynasty); annexed to Rome under Tiberius.'
WHERE id = 615;

-- 278 Bithynia ~150km from Nicomedia
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/anatolia-fix] Replaced erroneous "minor states" polygon with 150km circle around Nicomedia. Bithynia was a Hellenistic kingdom in NW Anatolia (297-74 BCE), Thracian-derived dynasty; bequeathed to Rome 74 BCE.'
WHERE id = 278;

-- 79 Pontus ~300km from Amasya (peak under Mithridates VI extended to Crimea)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/anatolia-fix] Replaced erroneous "minor states" polygon with 300km circle around Amasya. Kingdom of Pontus (281-63 BCE) covered N Anatolia Black Sea coast + later Crimea, Cilicia under Mithridates VI (peak ~88 BCE); annexed to Rome after Mithridatic Wars.'
WHERE id = 79;

-- 281 Galatia ~200km from Ancyra
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/anatolia-fix] Replaced erroneous "minor states" polygon with 200km circle around Ancyra. Galatia was a central Anatolian kingdom of Celtic invaders (Gauls) settled after 278 BCE; annexed to Rome 25 BCE under Augustus.'
WHERE id = 281;

-- ========== HOLY ROMAN EMPIRE (4 entities, all to fix — none was HRE proper) ==========
-- 567 Pisa Commune ~30km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/hre-fix] Replaced erroneous Holy Roman Empire polygon with 30km circle around Pisa. Comune di Pisa was an Italian city-republic (1000-1406) with maritime power in Mediterranean; never controlled HRE territory.'
WHERE id = 567;

-- 82 Florence Republic ~80km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/hre-fix] Replaced erroneous Holy Roman Empire polygon with 80km circle around Firenze. Florentine Republic (1115-1532) controlled Tuscany including Pisa (after 1406), Siena (after 1555 under Medici Grand Duchy).'
WHERE id = 82;

-- 83 Swiss Confederation ~200km
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.7),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/hre-fix] Replaced erroneous Holy Roman Empire polygon with 200km circle around Bern. Swiss Confederation (Schweizerische Eidgenossenschaft) formed 1291 (3 cantons Rütli) → 13 cantons (Alte Eidgenossenschaft) → modern Switzerland; technically inside HRE de jure until 1648 Peace of Westphalia.'
WHERE id = 83;

-- 87 Hanseatic League — federation of trading cities (not territorial) ~70km from Lübeck
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 70000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 70000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/hre-fix] Replaced erroneous Holy Roman Empire polygon with 70km circle around Lübeck. Hanseatic League (Hanse) was a commercial confederation of merchant guilds and trading cities (Baltic/North Sea, peak 14th c.) — NOT a territorial polity. Circle around Lübeck (the leading Hanse city) is approximate; for the network of Hanse cities see member-state entities separately.'
WHERE id = 87;

-- ========== BYZANTINE EMPIRE (4 entities, all to fix — none was Byzantine proper) ==========
-- 485 Rum Seljuks ~500km from Konya (central Anatolia)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/byzantine-fix] Replaced erroneous Byzantine Empire polygon with 500km circle around Konya. Sultanate of Rum (Anatolian Seljuks, 1077-1307) controlled central + eastern Anatolia after Manzikert 1071; peak under Kaykhusraw I/II, fell to Mongols 1243 then fragmented into beyliks.'
WHERE id = 485;

-- 476 Zengid ~300km from Aleppo (N Syria + Mosul)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 300000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/byzantine-fix] Replaced erroneous Byzantine Empire polygon with 300km circle around Aleppo. Zengid dynasty (1127-1250, founded by Imad ad-Din Zengi) ruled Aleppo/Mosul, Seljuk Atabegate; Nur ad-Din unified Syria; absorbed by Saladin/Ayyubids.'
WHERE id = 476;

-- 96 Principality of Arbanon (Albanian) ~80km from Kruja
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/byzantine-fix] Replaced erroneous Byzantine Empire polygon with 80km circle around Kruja. Principata e Arberit (Principality of Arbanon, 1190-1479) was the first Albanian feudal principality founded by Progon family; expanded under Skanderbeg as League of Lezhë 1444-1479 against Ottomans.'
WHERE id = 96;

-- 80 Despotate of Epirus ~250km from Arta (NW Greece + Albania coast)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/byzantine-fix] Replaced erroneous Byzantine Empire polygon with 250km circle around Arta. Despotate of Epirus (1205-1479) was a Byzantine successor state founded after 4th Crusade (1204) by Michael I Komnenos Doukas; covered NW Greece + Albania + Macedonia.'
WHERE id = 80;

-- ========== HUARI EMPIRE (4 entities, KEEP id=198 Wari) ==========
-- 198 Wari (legitimate match) — keep polygon
UPDATE geo_entities SET
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-huari-primary] LEGITIMATE Huari/Wari Empire polygon match. 3 other entities (Sicán, Ichma, Chanka) erroneously shared this polygon — now corrected. Wari peak extent (~800 CE) covered modern Peru highlands + coast from Cajamarca to Cusco; capital Huari near Ayacucho.'
WHERE id = 198;

-- 640 Sicán ~150km from Batán Grande (N Peru coast)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-huari-fix] Replaced erroneous Huari/Wari Empire polygon with 150km circle around Batán Grande. Sicán/Lambayeque culture (750-1375 CE) on N Peru coast (Lambayeque/La Leche valleys), famous for goldworking; conquered by Chimor c.1375.'
WHERE id = 640;

-- 951 Ichma/Ychsma ~100km from Pachacamac
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-huari-fix] Replaced erroneous Huari/Wari Empire polygon with 100km circle around Pachacamac. Ichma/Ychsma kingdom (900-1470 CE) centered on Pachacamac oracle/pilgrimage site (south of modern Lima); subsumed by Inca empire ~1470.'
WHERE id = 951;

-- 952 Chanka ~200km from Andahuaylas
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-huari-fix] Replaced erroneous Huari/Wari Empire polygon with 200km circle around Andahuaylas. Chanka confederation (1000-1440 CE) was a powerful pre-Inca ethnic federation in Apurímac/Ayacucho region, defeated by Pachacuti and absorbed into Inca empire (battle of Yawar Pampa).'
WHERE id = 952;

-- ========== SRIVIJAYA EMPIRE (4 entities, all to fix — none was Srivijaya proper) ==========
-- 901 Tambralinga ~100km from Ligor (Nakhon Si Thammarat)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/srivijaya-fix] Replaced erroneous Srivijaya Empire polygon with 100km circle around Ligor. Tambralinga (650-1365 CE) was a Malay Peninsula kingdom, Srivijaya tributary then independent (Chandrabhanu invaded Sri Lanka 1247); absorbed into Sukhothai.'
WHERE id = 901;

-- 899 Galuh ~100km from Kawali (West Java)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/srivijaya-fix] Replaced erroneous Srivijaya Empire polygon with 100km circle around Kawali. Galuh kingdom (669-1482 CE) was a West Javanese kingdom, often paired/merged with Sunda; capital varied (Karangkamulyan, Kawali, etc.); part of Sundanese cultural area.'
WHERE id = 899;

-- 866 Malayu ~250km from Minanga Tamwan (Sumatra)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 250000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/srivijaya-fix] Replaced erroneous Srivijaya Empire polygon with 250km circle around Minanga Tamwan. Malayu kingdom (671-1347 CE) was a Sumatran Malay kingdom, Srivijaya predecessor/contemporary; relocated to Dharmasraya (highland Sumatra) after Chola raid 1025.'
WHERE id = 866;

-- 900 Ta-hua-lo ~80km from Malayur
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 80000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2/srivijaya-fix] Replaced erroneous Srivijaya Empire polygon with 80km circle around Malayur (Jambi uplands). Ta-hua-lo (Tamiang? 1225-1300 CE) was a Sumatran polity mentioned in 13th c. Chinese sources; identity debated, possibly highland Malayu successor.'
WHERE id = 900;

-- ========== SUI EMPIRE (4 entities, KEEP id=448 隋朝) ==========
-- 448 Sui Dynasty (legitimate match) — keep polygon
UPDATE geo_entities SET
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-sui-primary] LEGITIMATE Sui Empire polygon match (581-618 CE). 3 other entities (Northern Qi/Wei pre-Sui, Chen southern dynasty, Northern Zhou) erroneously shared this unified-China polygon — corrected. Sui briefly reunified China after 4 centuries of division, predecessor to Tang.'
WHERE id = 448;

-- 462 Northern Qi pre-Sui ~400km from Ye (NE China)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-sui-fix] Replaced erroneous unified-China Sui polygon with 400km circle around Ye. 隋以前北朝 = "Northern dynasties before Sui" = Northern Qi (550-577) capital Ye, controlled E half of N China (Hebei/Henan/Shandong); destroyed by Northern Zhou.'
WHERE id = 462;

-- 464 Chen Dynasty ~500km from Jiankang (Nanjing)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-sui-fix] Replaced erroneous unified-China Sui polygon with 500km circle around Jiankang. 陳朝 = Chen Dynasty (557-589) was the last of the Southern Dynasties, controlled lower Yangtze + S China + Vietnam (down to Hue); conquered by Sui 589 ending the division era.'
WHERE id = 464;

-- 463 Northern Zhou ~500km from Chang'an (NW China)
UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 500000)::geometry),
  boundary_source = 'approximate_circle', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-sui-fix] Replaced erroneous unified-China Sui polygon with 500km circle around Chang''an. 北周 = Northern Zhou (557-581) was a Xianbei dynasty controlling NW China (Guanzhong + later all N China after destroying N Qi 577); Yang Jian usurped to found Sui 581.'
WHERE id = 463;

-- Verify all 40
SELECT id, name_original, ROUND(ST_Area(boundary_geom)::numeric, 4) as area, boundary_source, confidence_score
FROM geo_entities WHERE id IN (180, 269, 270, 271, 499, 532, 945, 946, 947, 948, 797, 274, 812, 814, 65, 286, 615, 278, 79, 281, 567, 82, 83, 87, 485, 476, 96, 80, 198, 640, 951, 952, 901, 899, 866, 900, 448, 462, 464, 463)
ORDER BY id;

COMMIT;
