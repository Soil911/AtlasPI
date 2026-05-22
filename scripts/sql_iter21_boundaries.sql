-- Iter 21 — Phase A tier-1 batch 21

BEGIN;

-- 196 Ñuu Dzahui (Mixtec collective) -1500/1523 — Oaxaca highlands
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-98.5,18.0],[-96.5,18.0],[-96.0,16.0],[-98.0,15.8],[-99.0,17.0],[-98.5,18.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 196;

-- 197 Muyska (Muisca confederation, duplicate of 860) 600-1541 — Cundinamarca-Boyacá
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-74.5,6.5],[-72.5,6.5],[-72.5,4.0],[-74.5,4.0],[-74.7,5.5],[-74.5,6.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 197;

-- 966 Tupinambá 1000-1650 — Brazilian Atlantic coast aggregate
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-46.0,-5.0],[-34.5,-7.0],[-38.0,-25.0],[-48.5,-25.5],[-44.0,-12.0],[-46.0,-5.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 966;

-- 590 Eastern Ganga dynasty 498-1434 — Odisha + N coastal Andhra Pradesh
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[81.5,22.0],[87.5,22.5],[87.5,17.5],[83.0,17.0],[81.0,19.5],[81.5,22.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 590;

-- 452 太平天國 Taiping Heavenly Kingdom 1851-1864 — controlled S-central China around Nanjing
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[111.0,32.5],[121.0,32.5],[121.5,28.5],[118.0,27.0],[110.5,28.5],[111.0,32.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 452;

-- 566 Dugelezh Breizh (Duchy of Brittany) 939-1547 — Brittany peninsula France
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-5.0,48.8],[-1.0,48.5],[-1.5,47.0],[-3.0,47.0],[-5.2,47.5],[-5.0,48.8]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 566;

-- 854 Zagwe 900-1270 — Ethiopia (Lalibela Roha)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[37.5,14.5],[40.5,14.0],[41.0,11.0],[38.5,9.5],[37.0,11.5],[37.5,14.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 854;

-- 675 Niitsitapi (Blackfoot Confederacy) 1200-1877 — N Plains
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-115.0,52.5],[-105.0,52.5],[-104.5,46.5],[-114.0,46.5],[-115.5,49.0],[-115.0,52.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 675;

-- 726 Muscogee 1540-1832 — Aggregate Creek pre-removal SE US
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-88.5,35.0],[-82.5,35.0],[-81.0,32.5],[-82.0,30.5],[-85.5,30.0],[-88.0,30.5],[-88.5,32.5],[-88.5,35.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 726;

-- 682 Chinook Illahee 500-1851 — Lower Columbia River
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-124.0,46.5],[-122.0,46.5],[-122.0,45.5],[-124.5,45.5],[-124.0,46.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 682;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (196,197,966,590,452,566,854,675,726,682) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (196,197,452,566,590,675,682,726,854,966) ORDER BY g.id;
