-- Boundary Review v6.99.79 — Tier 1B + Bantou collision group
-- Fixes 4 entities that all shared the generic "Bantou" linguistic-area polygon
-- (entire sub-Saharan Africa from Cameroon to South Africa, ~693 deg²).
-- This is an aourednik ingestion error — Bantu is a linguistic family,
-- not a polity. Each entity gets its own historically-realistic polygon.

BEGIN;

-- id=994 Bunyoro pre-Babito (kingdom 1300, Western Uganda) — Cwezi/early Bunyoro
-- Bigo+Ntusi were major centers. Kingdom extended ~200km radius from Bigo.
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1B/bantou-fix] Replaced erroneously-shared "Bantou" linguistic polygon (entire sub-Saharan Africa) with 200km capital-based circle around Bigo. Bunyoro pre-Babito was the Cwezi-era kingdom precursor of Bunyoro-Kitara, centered on the Bigo/Ntusi earthwork sites in Western Uganda. Bantu is a linguistic family (~500 languages), NOT a unified polity.'
WHERE id = 994;

-- id=996 Bigo bya Mugenyi (earthwork-complex 1300) — archaeological site ~8km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 8000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 8000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1B/bantou-fix] Replaced erroneously-shared "Bantou" linguistic polygon (693 deg², entire sub-Saharan Africa) with 8km circle. Bigo bya Mugenyi is an archaeological earthwork complex in Mubende District, Uganda — 5km of trenches enclosing ~3km² area, attributed to Cwezi dynasty (14th-15th c. CE).'
WHERE id = 996;

-- id=1010 Ntusi (settlement 1000-1400) — earthwork site near Bigo ~5km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 5000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 5000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1B/bantou-fix] Replaced erroneously-shared "Bantou" linguistic polygon with 5km circle. Ntusi is an Early Iron Age settlement complex in Sembabule District, Uganda (10th-14th c. CE), with extensive earthworks, cattle enclosures, and rock shelters — a precursor and contemporary of Bigo bya Mugenyi.'
WHERE id = 1010;

-- id=1030 Mbundu pre-Ndongo (confederation 1200, N Angola) — ~150km
UPDATE geo_entities
SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 150000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.55),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.79-tier1B/bantou-fix] Replaced erroneously-shared "Bantou" linguistic polygon (693 deg², entire sub-Saharan Africa) with 150km circle. Mbundu pre-Ndongo refers to the proto-Ndongo Mbundu chiefdoms of northern Angola (12th-16th c. CE) that coalesced into the Kingdom of Ndongo. Centered around the upper Kwanza River valley.'
WHERE id = 1030;

-- Verify
SELECT id, name_original, entity_type,
       ROUND(ST_Area(boundary_geom)::numeric, 4) as area,
       boundary_source, boundary_aourednik_name, confidence_score
FROM geo_entities WHERE id IN (994, 996, 1010, 1030)
ORDER BY id;

COMMIT;
