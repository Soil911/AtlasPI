-- Iter 20 — Phase A tier-1 batch 20

BEGIN;

-- 991 Butua 1450-1683 — Torwa dynasty SW Zimbabwe (Khami)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[27.5,-19.0],[31.0,-19.5],[31.5,-22.0],[28.0,-22.5],[26.5,-21.0],[27.5,-19.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 991;

-- 203 Iréchecua Tzintzuntzáni (Tarascan/Purépecha) 1300-1530 — Michoacán Mexico
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-103.5,20.5],[-100.5,20.5],[-100.0,18.5],[-103.0,18.0],[-103.5,19.5],[-103.5,20.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 203;

-- 865 Kahuripan 1019-1045 — East Java (Airlangga's kingdom)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[111.5,-6.5],[114.5,-6.8],[114.5,-8.5],[111.5,-8.3],[111.0,-7.5],[111.5,-6.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 865;

-- 533 Mosquitia 1625-1894 — Caribbean coast Honduras + Nicaragua
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-85.5,16.5],[-83.0,16.5],[-83.0,12.0],[-84.5,11.5],[-86.0,13.0],[-85.5,16.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 533;

-- 453 大理國 Dali Kingdom 937-1253 — Yunnan China
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[98.0,28.5],[105.5,28.5],[105.5,22.0],[98.0,22.0],[97.5,25.5],[98.0,28.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 453;

-- 720 Irecha Irechekwa (Purépecha duplicate of 203, distinct entry) 1300-1530
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-103.5,20.5],[-100.5,20.5],[-100.0,18.5],[-103.0,18.0],[-103.5,19.5],[-103.5,20.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 720;

-- 869 Śrī Kṣetra 50-900 — Pyu city Upper Burma
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[95.0,19.0],[96.0,19.0],[96.0,18.5],[95.0,18.5],[95.0,19.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 869;

-- 195 Bēnizàa (Zapotec) -700/1521 — Oaxaca valley + Monte Albán
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-97.5,17.5],[-95.5,17.5],[-95.5,16.0],[-97.5,16.0],[-97.5,17.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 195;

-- 220 Wendat (Huron) 1400-1650 — Georgian Bay/Ontario
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-81.5,45.5],[-78.5,45.5],[-78.5,43.5],[-81.5,43.5],[-81.5,45.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 220;

-- 169 Akkad -2334/-2154 — Mesopotamian empire
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[40.5,37.5],[48.0,37.5],[49.5,32.0],[45.0,29.5],[40.0,32.0],[40.5,37.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 169;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (991,203,865,533,453,720,869,195,220,169) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (169,195,203,220,453,533,720,865,869,991) ORDER BY g.id;
