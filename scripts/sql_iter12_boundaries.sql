-- Iter 12 — Phase A tier-1 batch 12: 10 historical boundaries

BEGIN;

-- 808 Isin -2017/-1794 — Sumerian/Old Babylonian S Mesopotamia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[44.50,32.50],[47.00,32.50],[47.00,30.50],[44.30,30.30],[44.50,32.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 808;

-- 912 Oxwitik (Copán) 426-822 — Maya Classic SE periphery (Honduras)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-89.50,15.20],[-88.40,15.20],[-88.30,14.50],[-89.20,14.30],[-89.60,14.80],[-89.50,15.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 912;

-- 807 Yamhad -1810/-1517 — Old Syrian (Halab/Aleppo)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[36.30,37.00],[39.00,37.00],[39.20,35.50],[37.50,34.80],[36.00,35.50],[36.30,37.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 807;

-- 929 Huexotzinco 1300-1521 — Aztec-resistant Nahua city Puebla
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-98.60,19.40],[-98.10,19.40],[-98.05,19.00],[-98.60,18.95],[-98.65,19.20],[-98.60,19.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 929;

-- 988 Hammadid Emirate 1014-1152 — central Maghreb (Qal'at Bani Hammad N Algeria)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[2.50,36.50],[8.00,36.50],[8.50,34.50],[4.00,34.00],[2.00,35.30],[2.50,36.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 988;

-- 986 Midrarid Emirate (Sijilmasa) 772-976 — SE Morocco trans-Saharan trade
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-5.50,32.50],[-3.50,32.50],[-3.20,31.00],[-4.50,30.30],[-5.80,31.30],[-5.50,32.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 986;

-- 985 Rustamid Imamate (Tahert) 776-909 — Ibadi emirate W Algeria
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[0.50,36.00],[3.50,36.00],[3.80,34.80],[1.50,34.30],[0.20,35.20],[0.50,36.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 985;

-- 871 Halin 100-832 — Pyu city-state Upper Burma
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[95.50,22.80],[96.00,22.80],[96.05,22.30],[95.50,22.25],[95.45,22.55],[95.50,22.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 871;

-- 634 Ralik-Ratak (Marshall Islands chiefdoms) -2000/1885 — Micronesia atolls
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[160.50,14.50],[172.50,14.50],[172.50,4.50],[160.50,4.50],[160.50,14.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 634;

-- 913 Pa' Chan (Yaxchilán) 359-808 — Maya Classic Usumacinta basin
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.50,17.40],[-90.80,17.40],[-90.75,16.80],[-91.45,16.75],[-91.55,17.10],[-91.50,17.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 913;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (808,912,807,929,988,986,985,871,634,913) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (634,807,808,871,912,913,929,985,986,988) ORDER BY g.id;
