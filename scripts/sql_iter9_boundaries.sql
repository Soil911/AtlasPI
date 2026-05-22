-- Iter 9 — Phase A tier-1 batch 9: 10 historical boundaries

BEGIN;

-- 800 𐪁𐪈𐪕𐪌 (Lihyanite/Dedanite kingdom) -600/-100 — NW Arabia (Dadan/al-Ula)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[37.50,28.00],[39.50,28.00],[39.80,26.50],[38.50,25.30],[37.30,26.00],[37.50,28.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 800;

-- 799 ደዐመተ Dʿmt 800-400 BCE — Eritrean/N Ethiopian highlands (pre-Aksum, Yeha cap)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[38.20,15.20],[40.50,15.30],[40.80,13.50],[39.20,12.50],[38.00,13.30],[37.80,14.50],[38.20,15.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 799;

-- 918 Dos Pilas 629-761 — Petexbatun Maya city, Petén Guatemala
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.00,16.70],[-90.30,16.70],[-90.20,16.20],[-90.80,16.10],[-91.10,16.40],[-91.00,16.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 918;

-- 1023 Garamantes -500/700 — Fezzan oasis kingdom Libya (Garama cap)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[10.00,28.00],[16.00,28.00],[16.50,26.00],[13.50,24.50],[10.50,25.50],[10.00,28.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1023;

-- 641 Kaminaljuyú -1200/900 — Maya highland city (modern Guatemala City)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-90.80,14.80],[-90.30,14.80],[-90.25,14.40],[-90.70,14.30],[-90.85,14.55],[-90.80,14.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 641;

-- 916 Chichen Itza 600-1200 — Postclassic Maya N Yucatan
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-89.50,21.30],[-87.80,21.30],[-87.70,20.30],[-88.80,19.90],[-89.70,20.50],[-89.50,21.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 916;

-- 811 𒌭𒀸𒋗 Kassite Babylonia -1595/-1155
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[42.50,35.00],[48.00,35.00],[49.00,32.00],[47.50,29.50],[43.00,30.50],[42.00,32.50],[42.50,35.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 811;

-- 911 Oxwitzá / Caracol 300-1050 — Maya city Belize Vaca Plateau
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-89.30,17.20],[-88.50,17.20],[-88.40,16.50],[-89.20,16.40],[-89.40,16.80],[-89.30,17.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 911;

-- 70 First Bulgarian Empire 681-1018 — Balkans (Pliska, Preslav)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[22.00,46.00],[29.50,46.00],[30.20,42.20],[26.50,40.50],[22.20,41.20],[21.50,43.50],[22.00,46.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 70;

-- 921 Lamanai -1500/1680 — Belize Maya site (long occupation)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-88.85,17.95],[-88.40,17.95],[-88.30,17.50],[-88.75,17.40],[-88.90,17.70],[-88.85,17.95]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 921;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (800,799,918,1023,641,916,811,911,70,921) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (70,641,799,800,811,911,916,918,921,1023) ORDER BY g.id;
