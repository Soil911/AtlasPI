-- Iter 11 — Phase A tier-1 batch 11: 10 historical boundaries

BEGIN;

-- 1000 Koumbi Saleh 700-1235 — Ghana Empire capital (S Mauritania)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-8.50,16.30],[-7.20,16.30],[-7.30,15.30],[-8.50,15.20],[-8.80,15.80],[-8.50,16.30]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 1000;

-- 909 Lakamha' (Palenque) 226-799 — Maya Classic city Chiapas
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-92.30,17.70],[-91.70,17.70],[-91.65,17.30],[-92.25,17.20],[-92.40,17.50],[-92.30,17.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 909;

-- 960 Taíno (Lucayan) 600-1520 — Bahamas archipelago Caribbean Arawakan
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-79.50,27.20],[-72.50,27.20],[-72.20,20.80],[-78.50,20.50],[-80.00,24.50],[-79.50,27.20]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 960;

-- 804 𒋫𒄿𒈠 Tayma kingdom -1500/-550 — NW Arabia oasis
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[38.00,28.50],[39.50,28.50],[39.50,27.00],[38.00,26.80],[37.80,27.80],[38.00,28.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 804;

-- 962 Tres Zapotes -900/300 — Olmec/Epi-Olmec lowland Veracruz
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-95.80,18.80],[-94.60,18.80],[-94.50,18.20],[-95.70,18.10],[-95.90,18.50],[-95.80,18.80]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 962;

-- 820 𐡀𐡅𐡓𐡄𐡉 Edessa (Osroene) -132/244 — Upper Mesopotamia (Urhay/Şanlıurfa)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[37.80,37.70],[39.80,37.70],[40.20,36.50],[39.20,35.80],[37.50,36.20],[37.80,37.70]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 820;

-- 794 Marajoara 400-1300 — Lower Amazon Marajo island cultural complex
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-51.00,0.50],[-48.00,0.30],[-48.00,-1.50],[-51.00,-1.50],[-51.20,-0.50],[-51.00,0.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 794;

-- 949 Paracas -800/-100 — S Peru coast cultural region (Ica/Paracas peninsula)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-76.30,-13.50],[-75.50,-13.50],[-75.20,-14.50],[-76.00,-15.00],[-76.50,-14.30],[-76.30,-13.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 949;

-- 819 𒆥𒁮 Qedar (Arab tribal federation) -800/-100 — N Arabia (Dūmat al-Jandal)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[36.50,32.00],[42.50,32.00],[43.50,28.50],[40.50,26.00],[37.00,28.00],[36.50,32.00]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 819;

-- 791 Tongva 500-1834 — California Tongva/Gabrieleño (LA Basin)
UPDATE geo_entities SET boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[[-119.20,34.50],[-117.30,34.40],[-117.20,33.30],[-118.80,33.40],[-119.50,33.90],[-119.20,34.50]]]]}',
    boundary_source = 'historical_approximation', boundary_aourednik_name = NULL, boundary_aourednik_year = NULL, boundary_aourednik_precision = NULL, boundary_ne_iso_a3 = NULL
WHERE id = 791;

UPDATE geo_entities SET boundary_geom = ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_GeomFromGeoJSON(boundary_geojson)), 3))
WHERE id IN (1000,909,960,804,962,820,794,949,819,791) AND boundary_geojson IS NOT NULL;
COMMIT;

SELECT g.id, g.name_original, ROUND((ST_Area(g.boundary_geom::geography)/1000000.0)::numeric, 0) AS area_km2
FROM geo_entities g WHERE g.id IN (791,794,804,819,820,909,949,960,962,1000) ORDER BY g.id;
