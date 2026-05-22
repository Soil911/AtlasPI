-- Iter 6 — Phase A tier-1 batch 6: 10 historical boundaries

BEGIN;

-- 1020 Mafia Sultanate 1100-1500 — Mafia Island Tanzania Swahili
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.45,-7.75],[39.95,-7.75],[40.05,-8.20],[39.50,-8.35],[39.30,-8.00],[39.45,-7.75]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1020;

-- 905 Balanguingui 1300-1848 — Sulu archipelago piracy raid polity
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[121.50,6.20],[122.20,6.20],[122.30,5.60],[121.80,5.20],[121.40,5.60],[121.50,6.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 905;

-- 882 Namayan 1175-1571 — Manila bay area pre-Hispanic polity
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[120.85,14.75],[121.20,14.75],[121.20,14.40],[120.85,14.40],[120.85,14.75]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 882;

-- 1021 Tumbatu 1100-1500 — Zanzibar Swahili (Tumbatu island)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.20,-5.70],[39.40,-5.70],[39.45,-5.95],[39.20,-6.00],[39.15,-5.85],[39.20,-5.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1021;

-- 582 Hertogdom Brabant 1183-1795 — Low Countries (Brussels, Antwerp, Leuven)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[3.80,51.60],[5.80,51.60],[5.90,50.80],[4.80,50.50],[3.70,50.80],[3.80,51.60]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 582;

-- 995 Engaruka 1400-1700 — N Tanzania irrigated agriculture settlement
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[35.85,-2.90],[36.10,-2.90],[36.15,-3.15],[35.85,-3.20],[35.80,-3.05],[35.85,-2.90]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 995;

-- 1022 Chwaka 1000-1500 — Pemba Swahili (Chwaka Bay, NE Pemba)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.70,-5.05],[39.90,-5.05],[39.95,-5.25],[39.75,-5.30],[39.65,-5.15],[39.70,-5.05]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1022;

-- 573 Duche de Savoie 1003-1720 — Savoy duchy (alpine, between France & Italy)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[5.50,46.50],[7.50,46.50],[7.80,45.50],[7.50,44.40],[6.50,44.20],[5.70,45.30],[5.50,46.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 573;

-- 769 Tuanga ni Butaritari 1500-1892 — Gilbert Islands atoll (Kiribati)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[172.70,3.30],[173.20,3.30],[173.25,3.00],[172.70,2.95],[172.65,3.15],[172.70,3.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 769;

-- 778 Niswi-mishkodewinan (Three Fires Council — Ojibwe/Odawa/Potawatomi) 1400-1855
-- Around Great Lakes region (Michilimackinac center)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-92.0,49.5],[-82.0,49.0],[-80.0,46.0],[-83.0,42.5],[-87.5,41.8],[-91.5,44.5],[-93.0,47.0],[-92.0,49.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 778;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (1020,905,882,1021,582,995,1022,573,769,778) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (573,582,769,778,882,905,995,1020,1021,1022) ORDER BY g.id;
