-- Post Phase H: fix unique entity with NULL boundary
-- id=1009 سلطنة مقديشو (Sultanate of Mogadishu, 900-1530, city-state, capital at 2.04N 45.34E)

BEGIN;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 50000)::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Generated 50km circle boundary around Mogadishu coordinates. Sultanate of Mogadishu (سلطنة مقديشو, 900-1530 CE) was an Arab-Somali maritime sultanate on Banadir coast, founded by Persian Arab settlers; ruled by Muzaffar dynasty + later Ajuran suzerainty; traded with Swahili coast, India, Yemen, China (Zheng He visit 1418); ended by Ajuran expansion absorbing Banadir cities.'
WHERE id = 1009;

SELECT id, name_original, ROUND(ST_Area(boundary_geom)::numeric, 4) as area, boundary_source, confidence_score
FROM geo_entities WHERE id = 1009;

COMMIT;
