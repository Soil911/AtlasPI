-- Iter 4 — Phase A tier-1 batch 4: 10 historical boundaries
-- 2026-05-22 (autonomous loop, foreground mode)

BEGIN;

-- 777 Apalachee 1000-1704 — Florida panhandle, around Anhaica (Tallahassee)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-85.5,30.8],[-83.5,30.8],[-83.0,30.0],[-84.0,29.5],[-85.5,29.7],[-85.5,30.8]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 777;

-- 826 Amu / Lamu archipelago 1370-1895 — Swahili Kenya coast (around Lamu Island)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[40.50,-1.80],[41.20,-1.80],[41.30,-2.40],[40.85,-2.55],[40.50,-2.35],[40.50,-1.80]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 826;

-- 941 Haudenosaunee proto-confederacy 800-1142 — Upstate NY / Iroquoia
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-79.5,44.0],[-75.0,44.5],[-74.0,42.5],[-75.5,41.8],[-78.5,42.0],[-79.5,43.0],[-79.5,44.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 941;

-- 774 Etalwa (Etowah chiefdom) 1000-1550 — NW Georgia Mississippian
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-85.2,34.6],[-84.0,34.6],[-83.8,33.7],[-84.7,33.4],[-85.4,33.9],[-85.2,34.6]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 774;

-- 780 Shawanwaki (Shawnee) 1400-1832 — Ohio Valley + KY + WV pre-removal
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-85.5,40.5],[-80.5,40.5],[-79.5,38.5],[-82.0,36.5],[-85.5,37.0],[-86.0,39.0],[-85.5,40.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 780;

-- 695 Kesultanan Cirebon 1527-1677 — Javanese N coast
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[107.80,-6.30],[109.20,-6.40],[109.20,-7.10],[108.50,-7.50],[107.80,-7.20],[107.80,-6.30]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 695;

-- 752 Taupulega o Tokelau 1000-1889 — 3 atolls (Atafu, Nukunonu, Fakaofo) Pacific
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-173.0,-8.4],[-171.0,-8.4],[-171.0,-9.5],[-172.5,-9.7],[-173.2,-9.0],[-173.0,-8.4]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 752;

-- 796 Sachapuyas (Chachapoya) 800-1545 — NE Peru cloud forest, Kuelap
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-78.5,-5.5],[-77.0,-5.5],[-76.5,-7.0],[-77.5,-7.5],[-78.5,-7.0],[-78.5,-5.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 796;

-- 755 Roviana 1600-1900 — New Georgia Solomon Islands, Roviana Lagoon
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[157.10,-8.10],[157.85,-8.10],[157.95,-8.55],[157.45,-8.65],[157.05,-8.45],[157.10,-8.10]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 755;

-- 968 Milagro-Quevedo 500-1535 — Coastal Ecuador (Guayas basin)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-80.5,-1.0],[-79.0,-1.0],[-78.8,-2.5],[-80.0,-3.0],[-80.5,-2.0],[-80.5,-1.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 968;

UPDATE geo_entities SET
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (777, 826, 941, 774, 780, 695, 752, 796, 755, 968) AND boundary_geojson IS NOT NULL;

COMMIT;

SELECT g.id, g.name_original, g.boundary_source,
       ROUND((ST_Area(g.boundary_geom::geography) / 1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (695, 752, 755, 774, 777, 780, 796, 826, 941, 968) ORDER BY g.id;
