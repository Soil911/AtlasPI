-- Iter 13 — Phase A tier-1 batch 13: 10 historical boundaries

BEGIN;

-- 644 Cacicazgo de Coclé 300-1520 — Panama central (Sitio Conte / El Caño)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-80.80,8.80],[-79.80,8.80],[-79.70,8.10],[-80.80,8.10],[-80.95,8.50],[-80.80,8.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 644;

-- 920 K'iik'aab (Quiriguá) 426-810 — Maya SE periphery Guatemala Motagua valley
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-89.20,15.50],[-88.70,15.50],[-88.70,15.10],[-89.30,15.10],[-89.40,15.30],[-89.20,15.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 920;

-- 1001 Wadan 1141-1500 — Adrar trans-Saharan oasis Mauritania
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-12.40,21.00],[-10.50,21.00],[-10.20,19.80],[-11.80,19.50],[-12.70,20.30],[-12.40,21.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1001;

-- 772 Wiradjuri -20000/1840 — Aboriginal Australia central NSW
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[145.0,-31.5],[150.5,-31.7],[150.8,-34.5],[148.0,-35.5],[144.0,-35.0],[143.8,-33.0],[145.0,-31.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 772;

-- 770 Taotao Tano -1500/1668 — Mariana Islands (Chamorro)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[144.50,20.50],[146.50,20.50],[146.50,13.00],[144.40,13.00],[144.30,17.50],[144.50,20.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 770;

-- 771 Noongar boodja -40000/1829 — SW Australia Aboriginal nation
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[115.0,-30.0],[120.5,-30.5],[122.0,-33.0],[120.5,-35.5],[115.0,-35.2],[114.5,-32.0],[115.0,-30.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 771;

-- 1006 Sultanate of Shewa 896-1285 — central Ethiopia Walale
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[38.50,10.20],[40.50,10.30],[40.80,8.50],[39.50,7.50],[38.20,8.20],[38.50,10.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1006;

-- 679 Polotsk Principality 987-1397 — Belarus/Lithuania border (Western Dvina)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[26.50,56.50],[31.00,56.50],[31.50,54.50],[28.00,53.80],[26.20,55.00],[26.50,56.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 679;

-- 1002 Oualata 1100-1500 — Mauritania trans-Saharan trading post
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-8.20,17.80],[-6.50,17.80],[-6.30,16.80],[-7.50,16.30],[-8.50,16.80],[-8.20,17.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1002;

-- 753 Hau o ʻUvea 1500-1961 — Wallis (Uvea) island Polynesia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-178.30,-13.10],[-176.00,-13.10],[-176.00,-13.55],[-178.30,-13.55],[-178.30,-13.10]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 753;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (644,920,1001,772,770,771,1006,679,1002,753) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (644,679,753,770,771,772,920,1001,1002,1006) ORDER BY g.id;
