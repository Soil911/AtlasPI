-- Iter 8 — Phase A tier-1 batch 8: 10 historical boundaries (incl. mid-tier 5-6 src)

BEGIN;

-- 719 Muzo 800-1559 — Eastern Cordillera Colombia (emerald region)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-74.50,6.20],[-73.50,6.20],[-73.40,5.40],[-74.10,4.90],[-74.60,5.50],[-74.50,6.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 719;

-- 891 Kintamani 882-914 — Bali highland kingdom (pre-Warmadewa)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[115.05,-8.05],[115.55,-8.05],[115.60,-8.45],[115.05,-8.50],[115.00,-8.25],[115.05,-8.05]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 891;

-- 123 遼朝 Liao Empire 916-1125 — Khitan empire (Mongolia + N China + Manchuria)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[95.0,50.0],[130.0,50.0],[133.0,44.0],[125.0,39.0],[113.0,38.5],[103.0,40.0],[95.0,43.0],[95.0,50.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 123;

-- 139 ហ្វូណន Funan 50-550 — Mekong delta SE Asia (Oc Eo cap)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[103.50,13.00],[107.50,13.00],[108.50,11.50],[107.00,9.50],[104.00,9.80],[103.50,11.50],[103.50,13.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 139;

-- 129 ပုဂံ Pagan/Bagan Kingdom 849-1297 — Central + Upper Burma
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[93.50,24.50],[98.50,25.00],[99.50,22.50],[98.50,19.50],[95.00,17.50],[93.00,19.50],[93.00,22.50],[93.50,24.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 129;

-- 170 𒀸𒋩 Assur/Assyria empire -2025/-609 — Mesopotamia + Levant + parts Egypt at peak
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[36.50,38.00],[48.00,38.00],[49.50,33.50],[46.00,30.00],[39.00,30.50],[35.50,33.50],[36.50,38.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 170;

-- 870 Beikthano (Pyu city-state) -200/900 — Central Burma
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[94.80,20.40],[95.40,20.40],[95.45,20.00],[94.85,19.95],[94.75,20.20],[94.80,20.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 870;

-- 1007 Zeila 800-1500 — Somaliland Red Sea trading port
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[43.30,11.70],[44.30,11.70],[44.35,11.10],[43.40,10.95],[43.20,11.35],[43.30,11.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1007;

-- 66 Λακεδαίμων Sparta -900/-192 — S Peloponnese (Laconia + Messenia)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[21.60,37.30],[22.80,37.40],[23.00,36.70],[22.00,36.30],[21.50,36.70],[21.60,37.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 66;

-- 910 Uxte''tuun (Calakmul) -300/900 — Maya S Yucatan / Campeche
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-90.30,18.80],[-88.50,18.80],[-88.30,17.30],[-89.50,17.10],[-90.50,17.70],[-90.30,18.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 910;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (719,891,123,139,129,170,870,1007,66,910) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (66,123,129,139,170,719,870,891,910,1007) ORDER BY g.id;
