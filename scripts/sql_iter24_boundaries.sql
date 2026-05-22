-- Iter 24 — Phase A tier-1 batch 24

BEGIN;

-- 975 Takedda 1100-1500 — Saharan copper-trading oasis Niger
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[5.0,18.0],[7.5,18.0],[7.5,16.0],[5.0,16.0],[5.0,18.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 975;

-- 142 Sinhala Kingdom (Anuradhapura tradition) -543/1815 — Sri Lanka
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[79.5,9.85],[82.0,9.0],[82.0,5.9],[79.5,5.9],[79.5,9.85]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 142;

-- 605 Zunghar Khanate 1634-1758 — Western Mongolia + Dzungaria + Tarim
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[75.0,50.0],[100.0,50.0],[102.0,44.0],[95.0,38.0],[75.0,40.0],[73.0,46.0],[75.0,50.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 605;

-- 608 Chagatai Khanate 1347-1680 — Central Asia post-Mongol successor
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[60.0,46.0],[95.0,46.0],[95.0,36.0],[60.0,36.0],[60.0,46.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 608;

-- 558 U Rwanda 1081-1961 — Kingdom of Rwanda
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[28.85,-1.05],[30.90,-1.05],[30.90,-2.85],[28.85,-2.85],[28.85,-1.05]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 558;

-- 227 Misiones Guaraníes 1609-1768 — Jesuit Guarani missions Paraguay/Argentina/Brazil
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-58.0,-25.5],[-53.5,-25.5],[-53.5,-29.0],[-58.0,-29.0],[-58.0,-25.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 227;

-- 539 Diaguita -400/1665 — NW Argentina + N Chile pre-Inca
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-71.0,-23.0],[-65.0,-23.5],[-64.5,-29.5],[-70.0,-30.0],[-71.5,-26.5],[-71.0,-23.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 539;

-- 677 Haida Gwaii 500-1876 — Queen Charlotte Islands NW Coast BC
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-133.5,54.5],[-131.0,54.5],[-130.5,51.8],[-133.5,52.0],[-133.5,54.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 677;

-- 670 Tarumanagara 358-669 — W Java early kingdom (Bogor)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[106.0,-5.8],[107.5,-5.8],[107.5,-7.2],[106.0,-7.2],[106.0,-5.8]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 670;

-- 1003 Tichitt -2000/-300 — Pre-Saharan urban Mauritania
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-11.5,19.0],[-9.0,19.0],[-9.0,17.5],[-11.5,17.5],[-11.5,19.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1003;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (975,142,605,608,558,227,539,677,670,1003) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (142,227,539,558,605,608,670,677,975,1003) ORDER BY g.id;
