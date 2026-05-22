-- Iter 5 — Phase A tier-1 batch 5: 10 historical boundaries

BEGIN;

-- 751 Patuiki o Niue 1700-1900 — Niue Island (Pacific)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-170.10,-18.95],[-169.78,-18.95],[-169.78,-19.20],[-170.10,-19.20],[-170.10,-18.95]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 751;

-- 898 Cotabato (Buayan) 1350-1520 — Mindanao Pulangi/Cotabato basin
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[124.20,7.50],[125.40,7.50],[125.50,6.40],[124.60,5.80],[123.90,6.40],[124.20,7.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 898;

-- 884 Madja-as 1212-1569 — Panay island confederation, Philippines
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[121.80,11.85],[123.20,11.90],[123.30,10.50],[122.10,10.20],[121.70,10.80],[121.80,11.85]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 884;

-- 574 Herzogtum Kurland und Semgallen 1561-1795 — Latvia W coast (Polish-Lithuanian fief)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[20.80,57.80],[24.20,57.80],[24.50,57.00],[24.00,56.20],[21.00,56.40],[20.80,57.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 574;

-- 643 Tlaxcallan 1348-1525 — Aztec-resistant city-republic, central Mexico
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-98.50,19.80],[-97.50,19.80],[-97.50,19.00],[-98.10,18.70],[-98.60,19.20],[-98.50,19.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 643;

-- 1013 Kong (Dyula trade city-state) 1300-1500 — N Côte d'Ivoire
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-5.30,10.20],[-4.20,10.20],[-3.90,9.40],[-4.60,8.80],[-5.50,9.30],[-5.30,10.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1013;

-- 775 Moundville 1050-1500 — Black Warrior valley Alabama Mississippian
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-88.20,33.80],[-86.70,33.80],[-86.60,32.60],[-87.50,32.30],[-88.30,32.90],[-88.20,33.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 775;

-- 785 Hiraacá (Hidatsa) 1300-1885 — Plains tribe Knife River North Dakota
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-103.00,48.50],[-100.50,48.50],[-100.30,46.80],[-101.80,46.30],[-103.50,47.30],[-103.00,48.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 785;

-- 906 Gelgel pre-sultanate Bali 1343-1550 — Bali (Majapahit successor)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[114.40,-8.05],[115.75,-8.10],[115.70,-8.85],[114.50,-8.80],[114.40,-8.05]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 906;

-- 1015 Bighu (Begho) 1400-1500 — Dyula trading city Ghana (Brong-Ahafo)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-2.50,8.40],[-2.00,8.40],[-1.95,7.90],[-2.40,7.85],[-2.65,8.10],[-2.50,8.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1015;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (751,898,884,574,643,1013,775,785,906,1015) AND boundary_geojson IS NOT NULL;

COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (574,643,751,775,785,884,898,906,1013,1015) ORDER BY g.id;
