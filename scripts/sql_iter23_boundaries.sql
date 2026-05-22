-- Iter 23 — Phase A tier-1 batch 23

BEGIN;

-- 506 Sur (Tyre) -2750/-332 — Phoenician city Lebanon coast
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[35.10,33.40],[35.30,33.40],[35.30,33.20],[35.10,33.20],[35.10,33.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 506;

-- 1004 Awdaghust 700-1230 — Trans-Saharan trade Mauritania
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-11.0,18.0],[-9.5,18.0],[-9.5,17.0],[-11.0,17.0],[-11.0,18.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1004;

-- 999 Gao-Saney 600-1275 — Niger River bend Songhai precursor
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-1.0,16.5],[0.5,16.5],[0.5,15.5],[-1.0,15.5],[-1.0,16.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 999;

-- 222 Wôpanâak (Wampanoag) -12000/present — Massachusetts/Rhode Island
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-72.0,42.5],[-69.5,42.5],[-69.5,41.0],[-72.0,41.0],[-72.0,42.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 222;

-- 596 Hyderabad State 1724-1948 — Asaf Jahi (Telangana + parts of Maharashtra/Karnataka/AP)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[74.5,21.5],[81.5,21.5],[81.5,15.5],[74.5,15.5],[74.5,21.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 596;

-- 703 Rajahnate of Maynila 1258-1571 — Manila bay (Tagalog)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[120.85,14.75],[121.20,14.75],[121.20,14.40],[120.85,14.40],[120.85,14.75]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 703;

-- 507 Sidon -3000/-332 — Phoenician city Lebanon coast
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[35.30,33.65],[35.50,33.65],[35.50,33.45],[35.30,33.45],[35.30,33.65]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 507;

-- 908 Yax Mutal (Tikal) -400/900 — Classic Maya hegemonic city
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-90.0,17.7],[-89.0,17.7],[-89.0,16.8],[-90.0,16.8],[-90.0,17.7]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 908;

-- 465 Tuyuhun (alternate transliteration of 296) 285-663
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[94.0,38.5],[103.0,38.5],[103.5,36.5],[102.0,34.0],[98.0,33.0],[94.0,34.0],[94.0,38.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 465;

-- 342 Ghurids 879-1215 — Afghan-Indian empire (Firuzkuh)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[60.0,38.0],[80.0,38.0],[80.0,30.0],[68.0,25.5],[60.0,30.0],[60.0,38.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 342;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (506,1004,999,222,596,703,507,908,465,342) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (222,342,465,506,507,596,703,908,999,1004) ORDER BY g.id;
