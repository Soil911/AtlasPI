-- Iter 28 — Phase A tier-1 batch 28

BEGIN;

-- 961 Izapa -1500/1200 — Soconusco Chiapas/Guatemala (Olmec→Maya transition)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-93.0,15.5],[-92.0,15.5],[-92.0,14.5],[-93.0,14.5],[-93.0,15.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 961;

-- 725 Numunuu 1700-1875 — Comanche (overlap with 216)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-105.5,38.5],[-98.5,38.5],[-96.5,35.0],[-97.5,31.5],[-101.5,28.5],[-105.0,29.5],[-106.0,33.5],[-105.5,38.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 725;

-- 914 Yokib (Piedras Negras) 297-808 — Classic Maya Usumacinta basin
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.5,17.4],[-90.8,17.4],[-90.75,16.8],[-91.45,16.75],[-91.55,17.1],[-91.5,17.4]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 914;

-- 427 Grand Duchy of Finland 1809-1917 — autonomous part of Russian Empire
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[21.0,70.0],[31.5,70.0],[33.5,68.0],[28.0,60.0],[22.0,60.0],[20.5,64.0],[21.0,70.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 427;

-- 934 Isthmus Zoque -1000/1521 — Pre-Hispanic Isthmus Tehuantepec
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-95.5,17.5],[-93.5,17.5],[-93.5,16.0],[-95.5,16.0],[-95.5,17.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 934;

-- 846 Betsimisaraka 1712-1817 — Madagascar E coast
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[48.5,-13.5],[50.5,-13.5],[50.0,-22.0],[48.5,-22.0],[48.0,-17.5],[48.5,-13.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 846;

-- 735 Ingoma yUburundi (Kingdom of Burundi) 1680-1966
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[29.0,-2.3],[30.85,-2.3],[30.85,-4.5],[29.0,-4.5],[29.0,-2.3]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 735;

-- 830 Torwa (alt of 991 Butua) 1450-1683 — SW Zimbabwe Khami
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[27.5,-19.0],[31.0,-19.5],[31.5,-22.0],[28.0,-22.5],[26.5,-21.0],[27.5,-19.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 830;

-- 1008 Berbera early 800-1500 — Somaliland Red Sea port
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[45.0,11.0],[46.0,11.0],[46.0,9.5],[44.5,9.5],[44.5,10.8],[45.0,11.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1008;

-- 732 Imbangala 1600-1750 — Angola Kasanje warrior band
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[15.5,-8.5],[19.0,-8.5],[19.0,-11.0],[15.5,-11.0],[15.5,-8.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 732;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (961,725,914,427,934,846,735,830,1008,732) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (427,725,732,735,830,846,914,934,961,1008) ORDER BY g.id;
