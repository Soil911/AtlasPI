-- Iter 15 — Phase A tier-1 batch 15: 10 historical boundaries

BEGIN;

-- 306 Chamorro / Taotao Tano' -2000/1668 — Mariana Islands (broad continuous occupation)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[144.50,20.80],[146.30,20.80],[146.30,13.00],[144.40,13.00],[144.30,17.50],[144.50,20.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 306;

-- 964 Sapzurro / Kuna (Dulenega) 1000-present — Darién + San Blas Panama/Colombia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-78.80,9.50],[-77.20,9.60],[-77.20,8.20],[-78.50,8.20],[-78.90,8.80],[-78.80,9.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 964;

-- 498 Ugarit -1450/-1185 — Bronze Age city-state Levant coast (Ras Shamra)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[35.60,35.90],[36.30,35.90],[36.30,35.20],[35.55,35.20],[35.50,35.60],[35.60,35.90]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 498;

-- 1019 Shanga 750-1437 — Lamu archipelago Swahili (Pate island)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[41.00,-2.00],[41.30,-2.00],[41.35,-2.30],[41.05,-2.35],[40.95,-2.15],[41.00,-2.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1019;

-- 925 Xochicalco 650-900 — Epiclassic Mesoamerican city Morelos Mexico
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-99.40,18.95],[-99.10,18.95],[-99.10,18.65],[-99.40,18.65],[-99.40,18.95]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 925;

-- 927 El Tajín 600-1200 — Classic Veracruz Mexico
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-97.50,20.60],[-97.10,20.60],[-97.10,20.30],[-97.50,20.30],[-97.50,20.60]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 927;

-- 993 Shilluk Reth pre-1490 — White Nile Sudan
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[30.50,11.00],[33.00,11.00],[33.20,9.20],[31.50,9.00],[30.20,10.00],[30.50,11.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 993;

-- 919 Aguateca 700-810 — Petexbatun Maya (twin city to Dos Pilas)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-90.90,16.55],[-90.50,16.55],[-90.50,16.20],[-90.90,16.20],[-90.90,16.55]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 919;

-- 940 Spiro 900-1450 — Caddoan Mississippian Oklahoma
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-95.20,35.70],[-94.30,35.70],[-94.30,34.80],[-95.20,34.80],[-95.20,35.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 940;

-- 1016 Kuba pre-Shyaam 1300-1625 — Bantu kingdom DR Congo Kasai
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[20.00,-3.50],[23.50,-3.50],[24.00,-5.20],[21.50,-6.00],[19.50,-5.00],[20.00,-3.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1016;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (306,964,498,1019,925,927,993,919,940,1016) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (306,498,919,925,927,940,964,993,1016,1019) ORDER BY g.id;
