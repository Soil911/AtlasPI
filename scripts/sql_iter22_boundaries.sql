-- Iter 22 — Phase A tier-1 batch 22

BEGIN;

-- 977 Zazzau 1000-1808 — Hausa Bakwai city-state Kaduna State Nigeria (Zaria)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[7.0,11.5],[8.5,11.5],[8.5,10.5],[7.0,10.5],[7.0,11.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 977;

-- 201 Caral-Supe -3000/-1800 — Caral Supe valley Peru (Andean Norte Chico)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-77.8,-10.5],[-76.8,-10.5],[-76.5,-11.5],[-77.8,-11.5],[-77.8,-10.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 201;

-- 694 Kerajaan Gelgel 1460-1686 — Bali post-Majapahit
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[114.40,-8.05],[115.75,-8.10],[115.70,-8.85],[114.50,-8.80],[114.40,-8.05]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 694;

-- 168 Sumer -4500/-1900 — S Mesopotamia (Ur, Eridu, Uruk etc.)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[44.0,32.5],[48.0,32.5],[48.5,29.5],[45.0,29.5],[44.0,32.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 168;

-- 667 Rascia (Grand Principality of) 1083-1217 — Medieval Serbia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[18.5,44.5],[22.0,44.5],[22.0,42.0],[19.5,41.5],[18.0,43.0],[18.5,44.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 667;

-- 864 林邑 Linyi/Lâm Ấp 192-605 — Pre-Champa central Vietnam coast
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[107.5,17.5],[109.5,17.0],[109.5,13.5],[107.0,13.5],[107.5,17.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 864;

-- 160 Hausa Bakwai 1000-1804 — Seven Hausa city-states aggregate (overlap with Birane 414)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[5.40,14.20],[9.80,14.20],[10.20,12.30],[9.50,10.80],[7.20,10.50],[5.20,11.50],[5.00,13.20],[5.40,14.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 160;

-- 727 Oceti Sakowin (Great Sioux Nation) 1680-1877 — N + W Plains
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-110.5,49.0],[-95.0,49.0],[-94.0,44.5],[-99.0,42.0],[-104.0,42.5],[-110.5,46.5],[-110.5,49.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 727;

-- 188 Sabaʾ سبأ -1200/275 — S Arabia (Yemen) Marib
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[43.0,16.5],[46.5,16.5],[47.5,14.0],[45.5,12.5],[43.5,13.0],[43.0,16.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 188;

-- 982 Ile-Ife 800-1500 — Yoruba sacred origin city SW Nigeria
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[4.2,7.8],[5.0,7.8],[5.0,7.2],[4.2,7.2],[4.2,7.8]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 982;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (977,201,694,168,667,864,160,727,188,982) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (160,168,188,201,667,694,727,864,977,982) ORDER BY g.id;
