-- Iter 16 — Phase A tier-1 batch 16: 10 historical boundaries

BEGIN;

-- 922 Nojpeten 1200-1697 — Itza Maya island capital Lake Peten Itza
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-90.20,17.40],[-89.30,17.40],[-89.10,16.50],[-90.00,16.30],[-90.30,16.90],[-90.20,17.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 922;

-- 292 Çatalhöyük -7500/-5700 — Neolithic proto-city Anatolia Konya plain
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[32.50,37.80],[33.20,37.80],[33.20,37.30],[32.50,37.30],[32.50,37.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 292;

-- 915 Uxmal 600-1200 — Puuc Maya city Yucatan
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-89.90,20.60],[-89.40,20.60],[-89.40,20.20],[-89.90,20.20],[-89.90,20.60]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 915;

-- 549 Q'umarkaj 1225-1524 — K'iche' Maya capital Guatemala highlands
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.50,15.50],[-90.80,15.50],[-90.70,14.80],[-91.50,14.70],[-91.65,15.10],[-91.50,15.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 549;

-- 275 Skythia -900/-200 — Pontic Steppe nomadic confederation
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[28.0,50.0],[44.0,49.0],[48.0,45.0],[40.0,43.0],[28.0,44.5],[26.0,47.0],[28.0,50.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 275;

-- 293 Dilmun تلمون -3000/-538 — Bronze Age trading civilization Persian Gulf (Bahrain + E Arabia coast)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[50.00,27.00],[51.00,27.00],[51.00,25.50],[50.40,25.40],[50.00,26.40],[50.00,27.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 293;

-- 285 Corinth Κόρινθος -800/-146 — Greek city-state Isthmus of Corinth
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[22.50,38.20],[23.30,38.20],[23.30,37.65],[22.60,37.60],[22.40,37.90],[22.50,38.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 285;

-- 859 Tsalagi 1000-1838 — Eastern Band Cherokee proto-confederation (overlaps with 218 Cherokee Nation curated)
-- Distinct from 218 by date range (deeper antiquity); pre-contact SE Appalachian range
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-85.5,36.6],[-82.3,36.6],[-82.0,35.6],[-82.5,34.8],[-83.4,34.0],[-85.0,33.7],[-86.2,34.3],[-86.5,35.4],[-85.5,36.6]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 859;

-- 284 Epirus Βασίλειον τῆς Ἠπείρου -470/-167 — Pyrrhus' Hellenistic kingdom
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[19.50,40.50],[21.50,40.50],[22.00,38.80],[20.50,38.50],[19.20,39.20],[19.50,40.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 284;

-- 544 Dine Bikeyah 1400-1868 — Navajo homeland Four Corners area
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-112.0,37.0],[-107.5,37.0],[-107.5,34.8],[-110.0,34.5],[-112.5,35.5],[-112.0,37.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 544;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (922,292,915,549,275,293,285,859,284,544) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (275,284,285,292,293,544,549,859,915,922) ORDER BY g.id;
