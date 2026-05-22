-- Iter 19 — Phase A tier-1 batch 19

BEGIN;

-- 857 Ngati Toa / Te Ati Awa 1820-1840 — NZ Cook Strait area
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[173.5,-40.0],[176.0,-40.0],[176.0,-42.5],[173.5,-42.5],[173.5,-40.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 857;

-- 295 Nāgar -300/300 — Sri Lankan Naga clan/early Tamil polities (mainly N Sri Lanka)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[79.5,10.0],[81.5,10.0],[81.5,8.0],[79.5,8.0],[79.5,10.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 295;

-- 282 Commagene -163/72 — Hellenistic kingdom upper Euphrates (Samosata)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[37.0,38.5],[39.0,38.5],[39.0,37.0],[37.0,37.0],[37.0,38.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 282;

-- 304 Naoero (Nauru) -1000/1888 — Single island Micronesia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[166.85,-0.45],[167.00,-0.45],[167.00,-0.60],[166.85,-0.60],[166.85,-0.45]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 304;

-- 550 Cuzcatan 900-1528 — Pipil Nahua kingdom W El Salvador
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-90.0,14.3],[-88.5,14.3],[-88.5,13.2],[-90.0,13.2],[-90.0,14.3]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 550;

-- 551 Lenca -1000/1539 — Honduras + El Salvador interior
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-89.5,14.7],[-87.5,14.7],[-86.5,13.8],[-87.5,13.0],[-89.5,13.5],[-89.5,14.7]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 551;

-- 1034 Res Publica Romana -509/-27 — Roman Republic (peak Mediterranean)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-9.0,44.5],[18.0,46.5],[28.0,42.0],[36.0,38.0],[36.0,30.0],[28.0,30.0],[10.0,30.0],[-5.0,32.0],[-9.5,38.0],[-9.0,44.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1034;

-- 998 Djenne-Djeno -250/1400 — Niger Inland Delta Mali (proto-urban)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-5.5,15.2],[-3.8,15.2],[-3.5,13.5],[-5.5,13.0],[-6.0,14.5],[-5.5,15.2]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 998;

-- 944 Kalinago 1200-1800 — Lesser Antilles Caribbean
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-62.5,18.5],[-60.5,18.5],[-59.5,11.0],[-62.0,10.5],[-63.5,15.0],[-62.5,18.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 944;

-- 171 Babylon (Babylonia old kingdom) -1894/-539 — S Mesopotamia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[43.5,34.5],[48.0,34.5],[48.0,30.5],[44.5,30.0],[42.5,31.5],[43.5,34.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 171;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (857,295,282,304,550,551,1034,998,944,171) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (171,282,295,304,550,551,857,944,998,1034) ORDER BY g.id;
