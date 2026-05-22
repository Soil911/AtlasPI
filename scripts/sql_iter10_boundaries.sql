-- Iter 10 — Phase A tier-1 batch 10: 10 historical boundaries

BEGIN;

-- 798 𐩣𐩲𐩬 Maʿīn (Minaean) -800/-100 — N Yemen (Qarnāwu)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[44.50,16.50],[46.00,16.50],[46.30,15.30],[45.50,14.30],[44.20,15.00],[44.50,16.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 798;

-- 935 Mitla 750-1521 — Zapotec/post-Zapotec city Oaxaca
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-96.40,16.95],[-96.10,16.95],[-96.05,16.75],[-96.35,16.70],[-96.45,16.85],[-96.40,16.95]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 935;

-- 676 Nuuchahnulth 500-1849 — Vancouver Island W coast (Pacific NW)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-128.50,50.80],[-125.10,50.70],[-124.80,49.30],[-125.90,48.40],[-128.20,49.30],[-128.50,50.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 676;

-- 907 Salakanagara 130-362 — W Java Sundanese pre-Tarumanagara
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[105.20,-5.80],[106.50,-5.80],[106.50,-6.80],[105.20,-6.85],[105.10,-6.30],[105.20,-5.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 907;

-- 937 Teuchitlán cultural region -300/900 — Jalisco/Nayarit guachimontones tradition
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-104.50,21.50],[-102.50,21.50],[-102.20,20.20],[-104.00,19.80],[-105.00,20.50],[-104.50,21.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 937;

-- 3 İstanbul (Byzantium → Constantinople → Istanbul, city) -657 to present
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[28.65,41.30],[29.30,41.30],[29.30,40.80],[28.65,40.80],[28.65,41.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 3;

-- 802 Γέρρα Gerrha -650/-150 — E Arabia trading city (probably Thaj area)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[48.50,27.30],[50.50,27.30],[50.80,25.80],[49.20,25.00],[48.30,26.00],[48.50,27.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 802;

-- 570 Herzogtum Baiern (Bavaria Duchy) 555-1623 — Bavaria
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[9.00,50.50],[13.80,50.50],[14.00,48.80],[12.50,47.40],[10.20,47.40],[9.00,48.50],[9.00,50.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 570;

-- 1018 Manda 800-1430 — Lamu archipelago Swahili (Manda island)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[40.85,-1.95],[41.15,-1.95],[41.20,-2.25],[40.90,-2.30],[40.80,-2.10],[40.85,-1.95]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1018;

-- 642 Cantona -1000/1050 — Central Mexico fortified city (Puebla)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-97.70,19.80],[-97.10,19.80],[-97.05,19.40],[-97.65,19.30],[-97.80,19.55],[-97.70,19.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 642;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (798,935,676,907,937,3,802,570,1018,642) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (3,570,642,676,798,802,907,935,937,1018) ORDER BY g.id;
