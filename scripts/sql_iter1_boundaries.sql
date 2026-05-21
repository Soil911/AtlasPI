-- Iter 1 — Phase A tier-1 batch 1: 10 historical boundaries
-- 2026-05-21 (autonomous loop)

BEGIN;

-- 217 Lakȟóta Oyáte (Great Sioux Nation) 1600-1877
-- Great Plains: from Mille Lacs (MN/WI start) westward, Black Hills epicenter post-1700
-- ~1850 peak territory: Dakotas (W), Montana (E), Wyoming (Powder R.), Nebraska (W), NE Colorado
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-110.5,49.0],[-97.0,49.0],[-95.0,46.5],[-96.5,42.5],[-100.0,41.0],[-105.0,41.5],[-108.5,44.0],[-110.5,45.5],[-110.5,49.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 217;

-- 296 吐谷浑 Tuyuhun (Murong Xianbei) 285-670
-- Qinghai region: Qaidam Basin (W) to upper Yellow River (E), Kunlun (S) to Qilian (N)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[94.0,38.5],[103.0,38.5],[103.5,36.5],[102.0,34.0],[98.0,33.0],[94.0,34.0],[94.0,38.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 296;

-- 669 Butuan (rajahnate, NE Mindanao) 1001-1521
-- Coastal kingdom around Agusan River delta, NE Mindanao Philippines
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[125.30,9.30],[125.95,9.35],[126.10,8.85],[125.85,8.40],[125.30,8.50],[125.10,8.95],[125.30,9.30]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 669;

-- 216 Comancheria 1700-1875
-- Southern Plains empire: TX Panhandle, W Oklahoma, E New Mexico, S Kansas, S Colorado
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-105.5,38.5],[-98.5,38.5],[-96.5,35.0],[-97.5,31.5],[-101.5,28.5],[-105.0,29.5],[-106.0,33.5],[-105.5,38.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 216;

-- 472 Principatus Antiochenus (Crusader) 1098-1268
-- Antioch + N Syria coastal: Latakia to Cilician Gates, inland to Aleppo region
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[35.30,37.20],[37.30,37.10],[37.40,35.80],[36.80,35.30],[35.70,35.40],[35.30,36.10],[35.30,37.20]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 472;

-- 976 Katsina 1100-1805 (Hausa city-state)
-- Hausa Bakwai city-state, N Nigeria around Katsina city
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[6.80,13.50],[8.40,13.50],[8.40,12.30],[7.00,12.10],[6.50,12.80],[6.80,13.50]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 976;

-- 575 Principatus Transsilvaniae 1570-1711 (Ottoman vassal)
-- Carpathian arc enclosing the historical Transylvanian basin
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[22.50,47.80],[25.50,47.80],[26.80,46.80],[26.50,45.70],[24.50,45.40],[22.40,45.80],[22.10,46.80],[22.50,47.80]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 575;

-- 414 Birane Hausa (Hausa Bakwai collective) 1000-1804
-- Seven Hausa city-states: Kano, Katsina, Daura, Zaria, Rano, Gobir, Biram
-- N Nigeria + S Niger region
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[5.40,14.20],[9.80,14.20],[10.20,12.30],[9.50,10.80],[7.20,10.50],[5.20,11.50],[5.00,13.20],[5.40,14.20]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 414;

-- 141 渤海國 Balhae/Parhae 698-926
-- E Manchuria + N Korea + Russian Primorye
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[124.50,47.80],[133.50,47.80],[135.20,44.50],[131.50,41.80],[127.50,40.10],[125.50,41.50],[124.50,44.50],[124.50,47.80]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 141;

-- 562 Igbo-Ukwu 800-1000 (SE Nigeria, bronze metallurgy site)
-- Small site near Awka; cultural sphere ~Anambra State
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[6.65,6.50],[7.50,6.50],[7.50,5.85],[6.65,5.85],[6.65,6.50]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 562;

-- Recompute boundary_geom
UPDATE geo_entities SET
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (217, 296, 669, 216, 472, 976, 575, 414, 141, 562)
  AND boundary_geojson IS NOT NULL;

COMMIT;

-- Verify
SELECT g.id, g.name_original, g.boundary_source, g.confidence_score,
       ST_NumGeometries(g.boundary_geom) AS n_polys,
       ROUND((ST_Area(g.boundary_geom::geography) / 1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g
WHERE g.id IN (141, 216, 217, 296, 414, 472, 562, 575, 669, 976)
ORDER BY g.id;
