-- Boundary Review v6.99.79 — Tier 2: Fatimid Caliphate collision group
-- 6 entities erroneously share the Fatimid polygon.
-- KEEP id=174 (الدولة الفاطمية / Fatimid Caliphate) as legitimate match.
-- Fix other 5 with capital-based circles of appropriate historical extent.

BEGIN;

-- id=174 الدولة الفاطمية (Fatimid Caliphate 909-1171) — KEEP polygon
-- Just clean metadata and add ethical note
UPDATE geo_entities
SET
  boundary_aourednik_precision = 2,  -- Was 1 (approx); 2=moderate seems fairer for Fatimid
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-fatimid-primary] This is the LEGITIMATE Fatimid Caliphate polygon match (boundary_aourednik_name="Fatimid Caliphate"). 5 other entities (Ikhshidid, Zirid, Crusader/Ayyubid Jerusalem, Ayyubid) were erroneously mapped to this same polygon — they have now been corrected to their own capital-based circles. Fatimid extent here represents the post-Maghreb-loss core (~2M km² Egypt + Levant + Hejaz). For peak extent including Ifriqiya/Sicily (969-973 CE) see history.'
WHERE id = 174;

-- id=481 الإخشيديون (Ikhshidid dynasty 935-969, Fustat) — Egypt + S Levant ~400km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 400000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-fatimid-fix] Replaced erroneous Fatimid Caliphate polygon (assigned to 6 different entities by aourednik) with 400km circle around Fustat. Ikhshidids ruled Egypt and southern Palestine/Syria (935-969 CE), conquered by Fatimids. Predecessor state to Fatimid Egypt.'
WHERE id = 481;

-- id=496 بنو زيري (Zirid dynasty 972-1152, al-Mansuriyya/Mahdia) — Ifriqiya ~450km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 450000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 450000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-fatimid-fix] Replaced erroneous Fatimid Caliphate polygon with 450km circle around Mahdia. Zirids were Berber dynasty (originally Fatimid vassals 972-1048) ruling Ifriqiya (modern Tunisia + parts of Algeria + Tripolitania), independent after 1048 break with Fatimids.'
WHERE id = 496;

-- id=470 Regnum Hierosolymitanum (Crusader 1099-1291, Jerusalem) — Palestine ~180km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 180000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 180000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-fatimid-fix] Replaced erroneous Fatimid Caliphate polygon with 180km circle around Jerusalem. Kingdom of Jerusalem (Regnum Hierosolymitanum) was the Crusader state established after 1st Crusade (1099) covering Palestine + parts of southern Lebanon + Transjordan, until fall of Acre (1291).'
WHERE id = 470;

-- id=175 الدولة الأيوبية (Ayyubid 1171-1260, Cairo) — Egypt+Levant+Yemen ~900km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 900000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 900000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-fatimid-fix] Replaced erroneous Fatimid Caliphate polygon with 900km circle around Cairo. Ayyubid Sultanate (founded by Saladin in 1171) covered Egypt, Syria, Upper Mesopotamia, Yemen, Hejaz, parts of Libya — vast empire that absorbed Fatimid Egypt. At peak ~2M km².'
WHERE id = 175;

-- id=511 مملكة بيت المقدس العربية (Arab Kingdom of Jerusalem 1187-1229) — Ayyubid Jerusalem hinterland ~100km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 100000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.5),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier2-fatimid-fix] Replaced erroneous Fatimid Caliphate polygon with 100km circle around Jerusalem. This entity ("Arab Kingdom of Jerusalem", 1187-1229) represents the Ayyubid administration of Jerusalem after Saladin reconquest (Hattin 1187) and before Frederick II Treaty of Jaffa (1229). Possibly redundant with Ayyubid empire entity — manual review recommended.'
WHERE id = 511;

-- Verify
SELECT id, name_original, entity_type, year_start,
       ROUND(ST_Area(boundary_geom)::numeric, 4) as area,
       boundary_source, boundary_aourednik_name, confidence_score
FROM geo_entities WHERE id IN (174, 175, 470, 481, 496, 511)
ORDER BY year_start;

COMMIT;
