-- Iter 18 — Phase A tier-1 batch 18: 10 historical boundaries

BEGIN;

-- 418 Miji ya Pwani 800-1505 — Swahili coastal towns aggregate (broader Swahili region)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[39.0,-1.5],[42.0,-1.5],[44.0,-12.0],[40.0,-15.5],[38.5,-7.0],[39.0,-1.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 418;

-- 349 Sogdiana -500/1000 — Iranian Central Asia (Zarafshan + Kashka valleys)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[64.0,41.0],[71.5,41.5],[72.0,38.5],[65.5,38.0],[63.5,39.5],[64.0,41.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 349;

-- 305 Saudeleur 1100-1628 — Pohnpei (Caroline Islands, Nan Madol)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[158.10,7.00],[158.50,7.00],[158.50,6.70],[158.10,6.70],[158.10,7.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 305;

-- 146 Wagadou (Ghana Empire) 300-1200 — W Sahel (Mauritania + Mali)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-12.0,18.0],[-5.0,18.0],[-4.0,14.5],[-9.5,13.0],[-13.5,15.0],[-12.0,18.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 146;

-- 297 Tu'i Ha'atakalaua 1470-1799 — Tonga islands successor dynasty
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-176.5,-15.0],[-173.0,-15.0],[-173.0,-23.0],[-176.5,-23.0],[-176.5,-15.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 297;

-- 307 Lapita -1600/-500 — Austronesian expansion cultural region (Bismarcks to Tonga/Samoa)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[145.0,-2.0],[173.0,-8.0],[-172.0,-15.0],[-172.0,-22.0],[155.0,-22.0],[145.0,-12.0],[145.0,-2.0]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 307;

-- 630 Safineis (Samnite Confederation) -600/-82 — central Italy Apennines
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[13.5,42.5],[15.5,42.5],[15.7,41.0],[14.0,40.5],[13.3,41.5],[13.5,42.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 630;

-- 312 Belau (Palau) -1000/1783 — Caroline Islands W
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[131.0,8.5],[135.0,8.5],[135.0,2.5],[131.0,2.5],[131.0,8.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 312;

-- 860 Muisca 600-1541 — Cundinamarca-Boyacá plateau Colombia (Bogota savannas)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-74.5,6.5],[-72.5,6.5],[-72.5,4.0],[-74.5,4.0],[-74.7,5.5],[-74.5,6.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 860;

-- 617 Herodian Kingdom -37/6 — Judea + Galilee + Iturea (Roman client kingdom)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[34.5,33.5],[36.5,33.5],[36.5,32.0],[36.0,30.5],[35.0,30.5],[34.3,31.5],[34.5,33.5]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 617;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (418,349,305,146,297,307,630,312,860,617) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (146,297,305,307,312,349,418,617,630,860) ORDER BY g.id;
