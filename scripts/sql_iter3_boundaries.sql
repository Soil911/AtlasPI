-- Iter 3 — Phase A tier-1 batch 3: 10 historical boundaries
-- 2026-05-22 16:40 (autonomous loop)

BEGIN;

-- 653 Lithuania Grand Duchy Великое княжество Литовское 1236-1795
-- Peak (15th c.) from Baltic to Black Sea: Lithuania + Belarus + N Ukraine + parts of Russia/Latvia/Poland
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[21.0,56.5],[28.0,56.7],[33.5,55.0],[36.5,52.5],[34.0,49.0],[28.0,46.0],[22.5,47.5],[20.5,51.0],[21.0,56.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 653;

-- 782 Chahta Yakni (Choctaw Nation) 1500-1830
-- Mississippi + Alabama + parts of Louisiana
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-91.5,34.5],[-87.5,34.5],[-86.8,32.5],[-87.5,30.5],[-90.5,30.5],[-92.0,32.0],[-91.5,34.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 782;

-- 979 Daura (Hausa Bakwai city-state) 900-1805
-- Small region around Daura, Katsina State, N Nigeria
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[7.5,13.7],[9.0,13.7],[9.2,12.8],[8.0,12.5],[7.3,13.0],[7.5,13.7]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 979;

-- 691 Mrauk U (Arakan kingdom) မြောက်ဦးခေတ် 1430-1785
-- Coastal Rakhine state + parts of Bangladesh Chittagong region
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[91.5,22.0],[94.0,22.0],[94.5,20.0],[94.2,18.5],[92.8,18.0],[91.8,19.0],[91.5,22.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 691;

-- 978 Gobir (Hausa Bakwai) 1000-1808
-- NW Hausaland, capital Alkalawa; centered around modern Sokoto State
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[4.5,14.0],[7.0,14.0],[7.0,12.8],[5.5,12.5],[4.3,13.0],[4.5,14.0]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 978;

-- 1014 Bono-Manso (Akan precursor kingdom) 1270-1500
-- Central Ghana, Brong-Ahafo region around Techiman
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-2.2,8.5],[-0.5,8.5],[0.0,7.5],[-0.8,6.8],[-2.3,6.8],[-2.7,7.7],[-2.2,8.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1014;

-- 784 Nueta (Mandan) 1100-1837
-- Plains tribe along Missouri River, modern North Dakota (Knife River/Heart River)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-102.5,48.5],[-99.5,48.0],[-99.0,46.0],[-101.0,45.5],[-102.8,46.5],[-103.0,47.5],[-102.5,48.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 784;

-- 578 Landgrafschaft Hessen 1264-1567
-- Modern Hessen state (capitals Kassel + Marburg + Darmstadt)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[7.7,51.7],[10.2,51.7],[10.0,50.3],[9.5,49.5],[8.0,49.6],[7.5,50.5],[7.7,51.7]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 578;

-- 568 Mark Brandenburg (Margraviate) 1157-1618
-- NE Germany, around Berlin + Brandenburg an der Havel + parts of Poland W (later)
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[11.3,53.5],[14.5,53.5],[15.5,52.5],[14.5,51.5],[12.5,51.5],[11.5,52.5],[11.3,53.5]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 568;

-- 756 Marovo (Solomon Islands chiefdom) 1700-1900
-- New Georgia island, around Marovo Lagoon
UPDATE geo_entities SET
    boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[157.40,-8.20],[158.20,-8.20],[158.30,-8.85],[157.80,-9.00],[157.30,-8.70],[157.40,-8.20]]]]}',
    boundary_source = 'historical_approximation',
    boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 756;

-- Recompute boundary_geom
UPDATE geo_entities SET
    boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (653, 782, 979, 691, 978, 1014, 784, 578, 568, 756)
  AND boundary_geojson IS NOT NULL;

COMMIT;

SELECT g.id, g.name_original, g.boundary_source,
       ST_NumGeometries(g.boundary_geom) AS n_polys,
       ROUND((ST_Area(g.boundary_geom::geography) / 1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g
WHERE g.id IN (568, 578, 653, 691, 756, 782, 784, 978, 979, 1014)
ORDER BY g.id;
