-- Iter 27 — Phase A tier-1 batch 27

BEGIN;

-- 1011 Essouk-Tadmakka 700-1450 — Mali trans-Saharan terminal
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[0.0,19.5],[2.0,19.5],[2.0,18.0],[0.0,18.0],[0.0,19.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1011;

-- 793 Cholōllān 1200-1519 — Aztec-period Puebla pilgrimage city
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-98.45,19.20],[-97.95,19.20],[-97.95,18.85],[-98.45,18.85],[-98.45,19.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 793;

-- 790 Hopituh Shi-nu-mu (Hopi) 1100-1700 — Arizona mesas
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-111.0,36.5],[-110.0,36.5],[-110.0,35.5],[-111.0,35.5],[-111.0,36.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 790;

-- 965 Quimbaya 1-1540 — Middle Cauca valley Colombia gold-working
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-76.0,5.5],[-75.0,5.5],[-75.0,4.0],[-76.0,4.0],[-76.0,5.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 965;

-- 92 Tywysogaeth Cymru (Principality of Wales) 1216-1283 — Gwynedd-led Wales
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-5.5,53.4],[-2.7,53.4],[-2.7,51.4],[-5.5,51.4],[-5.5,53.4]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 92;

-- 932 Chalco 1200-1465 — Aztec-era Nahua altepetl Valley of Mexico
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-99.0,19.4],[-98.7,19.4],[-98.7,19.1],[-99.0,19.1],[-99.0,19.4]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 932;

-- 954 Cañari 500-1463 — S Ecuadorian highlands pre-Inca
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-79.5,-2.5],[-78.5,-2.5],[-78.5,-3.5],[-79.5,-3.5],[-79.5,-2.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 954;

-- 955 Manteño-Huancavilca 500-1535 — Coastal Ecuador (overlap 968 Milagro-Quevedo)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-80.5,-1.0],[-79.5,-1.0],[-79.5,-3.0],[-80.7,-2.5],[-80.5,-1.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 955;

-- 931 Xochimilco 1100-1430 — Nahua altepetl Lake Texcoco (Valley of Mexico)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-99.20,19.30],[-99.00,19.30],[-99.00,19.15],[-99.20,19.15],[-99.20,19.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 931;

-- 1040 Sangam-era Chola -300/300 — S India Tamil
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[78.0,12.5],[80.0,12.5],[80.0,9.5],[78.0,9.5],[78.0,12.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1040;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (1011,793,790,965,92,932,954,955,931,1040) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (92,790,793,931,932,954,955,965,1011,1040) ORDER BY g.id;
