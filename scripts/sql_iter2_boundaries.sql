-- Iter 2 — Phase A tier-1 batch 2: 10 historical boundaries
-- 2026-05-22 (autonomous loop resumed after Claude Code restart gap)

BEGIN;

-- 591 Kamarupa কামরূপ (Assam India) 350-1140
-- Brahmaputra valley + parts of Bhutan/Bangladesh
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[88.50,27.20],[92.50,27.50],[95.80,27.20],[96.50,26.20],[95.00,24.80],[91.80,24.50],[89.50,25.00],[88.50,26.40],[88.50,27.20]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 591;

-- 459 Four Oirats / Dörben Oirat (Western Mongol confederation) 1399-1634
-- Western Mongolia + Dzungaria + parts of Tarim Basin + Uvs Nuur basin
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[80.0,50.5],[100.0,50.5],[102.0,46.5],[97.0,42.0],[88.0,41.5],[82.0,43.5],[80.0,47.0],[80.0,50.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 459;

-- 164 Kilwa Sultanate 957-1513
-- Coastal Tanzania around Kilwa Kisiwani island + tributary network
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.0,-8.5],[40.2,-8.5],[40.7,-9.5],[40.5,-11.0],[39.8,-11.5],[39.0,-10.8],[39.0,-8.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 164;

-- 219 Mvskoke (Creek Confederacy) 1600-1832
-- Alabama + Georgia + N Florida + parts of TN + SC
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-88.5,35.0],[-82.5,35.0],[-81.0,32.5],[-82.0,30.5],[-85.5,30.0],[-88.0,30.5],[-88.5,32.5],[-88.5,35.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 219;

-- 607 Kingdom of Khotan ᠬᠣᠲᠠᠨ ᠬᠠᠭᠠᠨᠯᠢᠭ -200 to 1006
-- S Tarim Basin oasis kingdom around Hotan (Khotan)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[78.0,38.5],[82.5,38.5],[83.0,37.0],[81.5,35.8],[78.5,36.0],[77.5,37.5],[78.0,38.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 607;

-- 471 Comitatus Tripolitanus (Crusader County of Tripoli) 1102-1289
-- N Lebanon coast + Bekaa valley + Mt. Lebanon
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[35.50,34.80],[36.40,34.80],[36.50,34.10],[36.20,33.60],[35.80,33.50],[35.40,33.80],[35.50,34.80]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 471;

-- 609 Karakhanid Khanate قره‌خانیان 840-1212
-- Central Asia from Kashgar to Bukhara — Transoxiana + Tarim Basin W
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[62.0,44.0],[80.0,45.0],[81.0,42.0],[78.0,38.5],[71.0,37.5],[64.0,38.5],[60.5,41.0],[62.0,44.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 609;

-- 165 Ajuran Empire (Ajuuraan) 1300-1700
-- Southern Somalia: Shabelle + Jubba river valleys, Mogadishu hub
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[41.5,4.0],[45.5,4.5],[46.5,2.5],[45.2,0.0],[42.5,-0.5],[41.0,1.5],[41.5,4.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 165;

-- 715 Nieuw-Holland / Dutch Brazil 1630-1654
-- NE Brazil coast: Pernambuco, Paraíba, Rio Grande do Norte, parts of Ceará/Bahia
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-39.5,-3.0],[-34.8,-5.5],[-34.8,-8.5],[-37.0,-10.5],[-39.0,-9.0],[-40.0,-6.0],[-39.5,-3.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 715;

-- 1026 Tekrur pre-Almoravid 500-1040
-- Senegal River valley (Tukulor homeland)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-16.5,17.0],[-13.0,17.5],[-12.0,16.0],[-13.0,14.8],[-15.5,15.0],[-16.5,16.0],[-16.5,17.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1026;

-- Recompute boundary_geom
UPDATE geo_entities SET
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (591, 459, 164, 219, 607, 471, 609, 165, 715, 1026)
  AND boundary_geojson IS NOT NULL;

COMMIT;

SELECT g.id, g.name_original, g.boundary_source, g.confidence_score,
       ST_NumGeometries(g.boundary_geom) AS n_polys,
       ROUND((ST_Area(g.boundary_geom::geography) / 1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g
WHERE g.id IN (164, 165, 219, 459, 471, 591, 607, 609, 715, 1026)
ORDER BY g.id;
