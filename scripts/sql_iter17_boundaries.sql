-- Iter 17 — Phase A tier-1 batch 17: 10 historical boundaries

BEGIN;

-- 272 Troia / Wilusa -3000/-1180 — Bronze Age NW Anatolia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[26.00,40.00],[26.80,40.00],[26.80,39.55],[26.00,39.55],[26.00,40.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 272;

-- 538 Avakuarusu (Guarani confederation) -200/1632 — Paraguay + N Argentina + S Brazil
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-62.0,-19.0],[-54.0,-19.5],[-52.0,-24.5],[-56.0,-29.0],[-62.5,-26.5],[-62.5,-22.0],[-62.0,-19.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 538;

-- 543 Ndee (Apache confederation) 1400-1886 — SW USA + N Mexico
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-112.0,36.5],[-104.5,36.5],[-103.5,33.5],[-107.0,29.5],[-111.5,30.5],[-112.5,33.5],[-112.0,36.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 543;

-- 542 Quilombos 1580-1888 — Brazil maroon communities (peak Palmares Alagoas/Pernambuco)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-38.5,-8.0],[-36.0,-8.0],[-36.0,-10.5],[-38.5,-10.5],[-38.5,-8.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 542;

-- 618 Illyria / Ardiaei -250/-167 — Adriatic coast (Albania + Montenegro + Bosnia coast)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[16.5,43.5],[19.5,43.7],[20.0,41.5],[19.0,40.0],[17.5,40.5],[16.0,42.0],[16.5,43.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 618;

-- 316 PNG Highland societies -50000/present — Papua New Guinea highlands
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[141.5,-3.0],[148.0,-5.5],[148.5,-7.5],[143.0,-7.5],[140.5,-5.5],[141.5,-3.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 316;

-- 276 Sarmatia -500/400 — Eurasian steppe (Don to Volga)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[36.0,52.0],[55.0,52.0],[60.0,48.0],[55.0,43.0],[38.0,45.0],[35.0,48.0],[36.0,52.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 276;

-- 308 Torres Strait Islander peoples -8000/present — Torres Strait islands
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[141.5,-9.0],[144.5,-9.0],[144.5,-11.5],[141.5,-11.5],[141.5,-9.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 308;

-- 277 Indus Valley Civilization -3300/-1300 — Pakistan + NW India
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[66.0,33.0],[78.0,33.5],[78.0,23.0],[71.0,22.5],[65.5,24.5],[66.0,33.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 277;

-- 861 Tairona 200-1600 — Sierra Nevada de Santa Marta Colombia
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-74.5,11.5],[-73.0,11.5],[-72.8,10.8],[-74.0,10.5],[-74.5,11.0],[-74.5,11.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 861;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (272,538,543,542,618,316,276,308,277,861) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (272,276,277,308,316,538,542,543,618,861) ORDER BY g.id;
