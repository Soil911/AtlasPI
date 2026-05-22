-- Iter 7 — Phase A tier-1 batch 7: 10 historical boundaries

BEGIN;

-- 827 Pemba 900-1822 — Pemba Island Swahili (Chwaka cap)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.65,-4.85],[39.95,-4.85],[40.00,-5.45],[39.65,-5.55],[39.55,-5.10],[39.65,-4.85]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 827;

-- 583 Grevskabet Flandern 862-1795 — County of Flanders (Gent, Brugge, Lille)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[2.20,51.30],[4.40,51.50],[4.30,50.70],[2.60,50.40],[2.00,50.80],[2.20,51.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 583;

-- 59 Kongeriget Danmark 935- — Denmark (peninsular Jutland + islands)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[8.20,57.70],[10.95,57.75],[12.70,56.10],[12.50,54.70],[9.00,54.70],[8.10,55.20],[8.20,57.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 59;

-- 828 Sofala 950-1898 — Mozambique central coast gold-trade port
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[34.50,-19.30],[35.50,-19.30],[35.60,-20.50],[34.70,-20.80],[34.40,-19.80],[34.50,-19.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 828;

-- 681 Herzogtum Pommern 1121-1637 — Pomerania duchy (Baltic S coast)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[12.30,54.50],[17.30,54.60],[17.50,53.40],[14.20,53.20],[12.30,53.80],[12.30,54.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 681;

-- 1017 Vumba Kuu 1300-1700 — Wadigo Swahili (Shimoni / Diani Kenya-Tanzania)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.20,-4.40],[39.85,-4.40],[39.95,-4.90],[39.30,-5.00],[39.10,-4.70],[39.20,-4.40]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1017;

-- 579 Furstentum Walachei 1247-1330 — Wallachia origin (Basarab I)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[22.50,45.20],[26.80,45.30],[28.20,44.80],[27.50,43.80],[22.80,43.80],[22.50,45.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 579;

-- 824 Mvita (Mombasa) 900-1837 — Swahili Kenya coast
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.40,-3.80],[39.95,-3.80],[40.00,-4.30],[39.50,-4.40],[39.30,-4.10],[39.40,-3.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 824;

-- 577 Markgrafschaft Meissen 929-1423 — Wettin precursor margraviate (Saxony)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[12.30,51.80],[14.50,51.80],[14.80,50.80],[13.50,50.40],[12.20,50.80],[12.30,51.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 577;

-- 569 Herzogtum Sachsen 804-1296 — Old Saxon Duchy (Magdeburg cap)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[6.80,54.00],[11.50,54.00],[12.50,52.30],[10.50,51.30],[7.40,51.50],[6.80,53.00],[6.80,54.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 569;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (827,583,59,828,681,1017,579,824,577,569) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (59,569,577,579,583,681,824,827,828,1017) ORDER BY g.id;
