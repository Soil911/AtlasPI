-- Iter 26 — Phase A tier-1 batch 26

BEGIN;

-- 173 Umayyad Caliphate 661-750 — Damascus-based empire from Iberia to Indus
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-9.5,44.5],[-8.0,38.0],[5.0,32.0],[28.0,30.0],[40.0,25.0],[60.0,30.0],[72.0,32.0],[68.0,38.0],[50.0,40.0],[35.0,38.0],[20.0,36.0],[0.0,35.0],[-9.5,38.0],[-9.5,44.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 173;

-- 881 Ma-i 971-1339 — Mindoro polity Philippines
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[120.3,13.5],[121.8,13.5],[121.8,12.0],[120.3,12.0],[120.3,13.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 881;

-- 888 Ngoenyang 638-1292 — N Thai Tai pre-Lan Na (Chiang Saen)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[99.0,21.0],[101.5,21.0],[101.5,19.0],[99.0,19.0],[99.0,21.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 888;

-- 942 Vínland 1000-1020 — Norse settlement Newfoundland
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-56.0,51.8],[-55.4,51.8],[-55.4,51.3],[-56.0,51.3],[-56.0,51.8]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 942;

-- 943 Eystribyggð 985-1450 — Norse Eastern Settlement Greenland
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-46.5,61.0],[-44.5,61.0],[-44.5,60.0],[-46.5,60.0],[-46.5,61.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 943;

-- 1039 Old Babylonian Empire -1894/-1595 — Hammurabi peak
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[42.0,35.5],[48.5,35.5],[49.0,30.0],[44.0,29.5],[41.5,32.0],[42.0,35.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1039;

-- 654 Konungsveldið Noregs 1217-1380 — Norway peak (Hákon IV/Magnús V)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[4.0,71.0],[30.0,71.0],[31.0,68.5],[12.0,58.0],[6.0,58.0],[4.0,65.0],[4.0,71.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 654;

-- 938 Paquimé (Casas Grandes) 1200-1450 — Chihuahua Mexico
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-108.5,30.8],[-107.5,30.8],[-107.5,29.8],[-108.5,29.8],[-108.5,30.8]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 938;

-- 713 Province of Carolina 1663-1729 — colonial English
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-83.0,36.5],[-75.5,36.5],[-78.5,32.0],[-82.0,30.5],[-85.5,32.0],[-83.0,36.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 713;

-- 788 Haak'u (Acoma Sky City) 1150-1599 — New Mexico Pueblo
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-108.0,35.5],[-107.0,35.5],[-107.0,34.5],[-108.0,34.5],[-108.0,35.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 788;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (173,881,888,942,943,1039,654,938,713,788) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (173,654,713,788,881,888,938,942,943,1039) ORDER BY g.id;
