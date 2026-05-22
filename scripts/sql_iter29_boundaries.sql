-- Iter 29 — Phase A FINAL batch: 7 remaining boundaries

BEGIN;

-- 1037 Premier Empire français 1804-1815 — Napoleonic Empire peak
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-5.0,51.5],[3.5,53.5],[13.0,52.0],[14.5,46.0],[12.0,42.0],[8.0,40.0],[-2.5,42.5],[-5.0,46.0],[-5.0,51.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1037;

-- 1038 Afsharid Empire 1736-1796 — Nader Shah Iran/Afghanistan/Caucasus
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[40.0,42.0],[72.0,42.0],[72.0,25.0],[44.0,25.0],[40.0,30.0],[40.0,42.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1038;

-- 903 Pahang (tua) 1250-1454 — Malay Peninsula E coast
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[101.5,4.5],[103.5,4.5],[103.5,2.5],[101.5,2.5],[101.5,4.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 903;

-- 967 Emberá-Wounaan (Darién) 1200-present — Panama/Colombia Darién
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-78.5,9.0],[-77.0,9.0],[-76.5,7.5],[-78.0,6.5],[-79.0,7.5],[-78.5,9.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 967;

-- 980 Wangara 800-1500 — Soninke gold-trading diaspora Bambuk-Bure
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-13.0,13.5],[-9.5,13.5],[-9.5,11.0],[-13.0,11.0],[-13.0,13.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 980;

-- 747 Bazin/Bagirmi 1500-1800 — Lake Chad
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[16.0,12.5],[20.0,12.5],[20.0,9.5],[16.0,9.5],[16.0,12.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 747;

-- 1032 Daju Sultanate (سلطنة الداجو) 1200-1400 — Pre-Tunjur Darfur
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[22.5,15.5],[26.0,15.5],[26.3,12.0],[23.0,11.0],[21.5,13.0],[22.5,15.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1032;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (1037,1038,903,967,980,747,1032) AND boundary_geojson IS NOT NULL;
COMMIT;

-- Final stats
SELECT count(*) AS remaining_approximate FROM geo_entities WHERE boundary_source = 'approximate_generated';
SELECT count(*) AS total_curated FROM geo_entities WHERE boundary_source = 'historical_approximation';
SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (747,903,967,980,1032,1037,1038) ORDER BY g.id;
