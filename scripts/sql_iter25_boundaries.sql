-- Iter 25 — Phase A tier-1 batch 25

BEGIN;

-- 491 Zagwe (alt) 900-1270 — Ethiopia (dup of 854)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[37.5,14.5],[40.5,14.0],[41.0,11.0],[38.5,9.5],[37.0,11.5],[37.5,14.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 491;

-- 111 Maratha Empire 1674-1818 — Deccan + N+W India
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[68.0,28.0],[88.0,28.0],[88.0,18.0],[78.0,12.5],[72.0,15.0],[68.5,21.0],[68.0,28.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 111;

-- 668 Kediri 1042-1222 — E Java (Daha)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[111.5,-6.5],[114.0,-6.8],[114.0,-8.3],[111.5,-8.3],[111.0,-7.5],[111.5,-6.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 668;

-- 688 Sunda Kingdom 669-1579 — W Java (Pakuan Pajajaran)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[105.0,-5.5],[108.5,-5.7],[108.5,-7.8],[105.0,-7.5],[105.0,-5.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 688;

-- 718 Kitu (Quitu) 980-1470 — N Ecuadorian highlands
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-79.0,0.5],[-77.5,0.5],[-77.5,-1.5],[-79.0,-1.5],[-79.0,0.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 718;

-- 604 Kazakh Khanate (?) 1634-1771 — Caspian Volga steppe nomadic
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[40.0,53.0],[60.0,53.0],[62.0,46.0],[45.0,44.0],[39.0,48.0],[40.0,53.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 604;

-- 347 Kushano-Sasanian 230-365 — Bactria (Balkh)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[63.0,38.5],[72.0,38.5],[72.0,32.5],[63.0,32.5],[63.0,38.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 347;

-- 981 Sosso 1180-1235 — Soninke kingdom W Sudan (post-Ghana pre-Mali)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-12.0,16.0],[-7.5,16.0],[-7.0,13.5],[-11.5,12.5],[-13.0,14.5],[-12.0,16.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 981;

-- 145 Zunghar (alt of 605) 1634-1755
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[75.0,50.0],[100.0,50.0],[102.0,44.0],[95.0,38.0],[75.0,40.0],[73.0,46.0],[75.0,50.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 145;

-- 290 Xianbei 93-234 — Northern frontier steppe confederation
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[100.0,50.0],[125.0,50.0],[130.0,43.0],[120.0,40.0],[100.0,42.0],[100.0,50.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 290;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (491,111,668,688,718,604,347,981,145,290) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (111,145,290,347,491,604,668,688,718,981) ORDER BY g.id;
