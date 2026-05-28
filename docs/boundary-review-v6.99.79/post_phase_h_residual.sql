-- Post Phase H residual fixes: 2 entities flagged by new area-sanity guard
-- Mayapan (city-state 9 deg² > 4×2 ceiling) and Garoumele (settlement 31 deg² > 0.5×2)

BEGIN;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 30000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced Maya city-states super-group polygon (9 deg2) with 30km circle. Mayapan was the dominant Postclassic Maya city-state in N Yucatan (1220-1441) under Cocom dynasty, overthrown by Xiu uprising; collapse left Yucatan in decentralized league before Spanish contact.'
WHERE id = 917;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 25000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 25000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced Bornu-Kanem super-group polygon (31 deg2) with 25km circle. Garoumele was a fortified Sef dynasty settlement W of Lake Chad (1200-1480), capital of Bornu kingdom after Bulala drove Sefuwa from Njimi ~1380; Bornu Empire later moved capital to Birni Ngazargamu ~1460.'
WHERE id = 1012;

SELECT id, name_original, ROUND(ST_Area(boundary_geom)::numeric, 4) as area, boundary_source
FROM geo_entities WHERE id IN (917, 1012);

COMMIT;
