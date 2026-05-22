-- Bugfix polygons: differentiate distinct entities + fix antimeridian crossing
-- 2026-05-22 v6.99.58

BEGIN;

-- BUG 1: Pa' Chan (913 Yaxchilán) and Yokib (914 Piedras Negras) are DIFFERENT
-- Classic Maya cities ~20km apart along Usumacinta River.
-- Yaxchilán: ~16.90°N, -90.97°W
-- Piedras Negras: ~17.16°N, -91.27°W

-- 913 Pa' Chan (Yaxchilán) — south of Piedras Negras
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.10,17.05],[-90.70,17.05],[-90.65,16.75],[-91.10,16.70],[-91.20,16.90],[-91.10,17.05]]]]}',
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON('{"type":"MultiPolygon","coordinates":[[[[-91.10,17.05],[-90.70,17.05],[-90.65,16.75],[-91.10,16.70],[-91.20,16.90],[-91.10,17.05]]]]}')), 3))
WHERE id = 913;

-- 914 Yokib (Piedras Negras) — north of Yaxchilán
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.50,17.45],[-91.10,17.45],[-91.10,17.10],[-91.50,17.05],[-91.55,17.25],[-91.50,17.45]]]]}',
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON('{"type":"MultiPolygon","coordinates":[[[[-91.50,17.45],[-91.10,17.45],[-91.10,17.10],[-91.50,17.05],[-91.55,17.25],[-91.50,17.45]]]]}')), 3))
WHERE id = 914;

-- BUG 2: Maynila (703) and Namayan (882) are DIFFERENT Manila Bay polities
-- Maynila (Rajahnate): Pasig River mouth, W bank — modern Intramuros/Manila
-- Namayan: upriver from Manila, around Santa Ana — modern Mandaluyong/San Juan area

-- 703 Rajahnate of Maynila — Pasig river mouth W bank, Manila Bay
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[120.85,14.75],[121.02,14.75],[121.02,14.55],[120.85,14.55],[120.85,14.75]]]]}',
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON('{"type":"MultiPolygon","coordinates":[[[[120.85,14.75],[121.02,14.75],[121.02,14.55],[120.85,14.55],[120.85,14.75]]]]}')), 3))
WHERE id = 703;

-- 882 Namayan — upriver Santa Ana area, E of Maynila
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[121.02,14.65],[121.18,14.65],[121.20,14.45],[121.02,14.45],[121.02,14.65]]]]}',
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON('{"type":"MultiPolygon","coordinates":[[[[121.02,14.65],[121.18,14.65],[121.20,14.45],[121.02,14.45],[121.02,14.65]]]]}')), 3))
WHERE id = 882;

-- BUG 3: Lapita (307) crosses antimeridian (span 345°) — labels render wrongly on Leaflet
-- Split into Western (Bismarcks-Solomons-Fiji) and Eastern (Tonga-Samoa) hemispheres
-- as separate polygons in same MultiPolygon

UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[145.0,-2.0],[178.5,-12.0],[178.5,-22.0],[155.0,-22.0],[145.0,-12.0],[145.0,-2.0]]],[[[-180.0,-12.0],[-172.0,-15.0],[-172.0,-22.0],[-180.0,-22.0],[-180.0,-12.0]]]]}',
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON('{"type":"MultiPolygon","coordinates":[[[[145.0,-2.0],[178.5,-12.0],[178.5,-22.0],[155.0,-22.0],[145.0,-12.0],[145.0,-2.0]]],[[[-180.0,-12.0],[-172.0,-15.0],[-172.0,-22.0],[-180.0,-22.0],[-180.0,-12.0]]]]}')), 3))
WHERE id = 307;

COMMIT;

-- Verify fix
SELECT id, name_original, ST_NumGeometries(boundary_geom) AS n_polys,
       ST_XMin(boundary_geom) AS xmin, ST_XMax(boundary_geom) AS xmax,
       ST_XMax(boundary_geom)-ST_XMin(boundary_geom) AS span,
       ROUND((ST_Area(boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities WHERE id IN (307, 703, 882, 913, 914) ORDER BY id;
