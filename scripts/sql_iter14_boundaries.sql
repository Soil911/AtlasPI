-- Iter 14 — Phase A tier-1 batch 14: 10 historical boundaries

BEGIN;

-- 748 Pulotu -1500/1000 — Mythic isle west of Tonga; cultural region approx Tonga-Fiji
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[177.0,-16.0],[180.5,-16.5],[180.5,-22.5],[176.5,-22.0],[177.0,-16.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 748;

-- 309 Aboriginal Australian Nations -65000/present — Continent-wide
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[112.5,-10.5],[154.0,-10.5],[154.0,-39.5],[140.0,-39.5],[129.0,-37.0],[115.0,-35.0],[112.5,-22.0],[112.5,-10.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 309;

-- 754 Sau o Futuna 1500-1961 — Futuna + Alofi islands Polynesia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-178.30,-14.20],[-177.90,-14.20],[-177.90,-14.45],[-178.30,-14.45],[-178.30,-14.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 754;

-- 1031 Punt -2500/-1000 — Land of Punt (Horn of Africa / S Red Sea coast)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[40.0,17.0],[44.5,17.0],[46.0,13.5],[44.5,10.5],[40.5,11.5],[39.5,14.0],[40.0,17.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1031;

-- 1033 Tunjur Sultanate 1400-1640 — Darfur predecessor (W Sudan)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[22.5,15.5],[26.0,15.5],[26.3,12.0],[23.0,11.0],[21.5,13.0],[22.5,15.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1033;

-- 311 Yolŋu -40000/present — Arnhem Land NE Australia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[133.0,-11.5],[137.0,-11.5],[137.0,-14.5],[133.0,-14.5],[132.5,-12.5],[133.0,-11.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 311;

-- 963 Chiripa -1500/-100 — pre-Tiwanaku Bolivia (Lake Titicaca SW)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-69.00,-16.10],[-68.40,-16.10],[-68.40,-16.60],[-69.10,-16.60],[-69.15,-16.30],[-69.00,-16.10]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 963;

-- 230 USSR 1922-1991 — Soviet Union (large polygon)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[20.0,75.0],[180.0,75.0],[180.0,65.0],[180.0,45.0],[150.0,40.0],[80.0,35.0],[55.0,35.0],[45.0,38.0],[40.0,42.0],[35.0,45.0],[28.0,48.0],[20.0,55.0],[20.0,75.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 230;

-- 310 Kulin Nation -40000/present — Aboriginal SE Australia (Melbourne area)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[143.0,-35.5],[146.5,-35.5],[147.0,-39.0],[143.5,-39.0],[142.5,-37.0],[143.0,-35.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 310;

-- 313 Aelōn̄ in M̧ajeļ -2000/1885 — Marshall Islands proper (paralleled by 634 Ralik-Ratak)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[160.5,14.5],[172.5,14.5],[172.5,4.5],[160.5,4.5],[160.5,14.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 313;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (748,309,754,1031,1033,311,963,230,310,313) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (230,309,310,311,313,748,754,963,1031,1033) ORDER BY g.id;
