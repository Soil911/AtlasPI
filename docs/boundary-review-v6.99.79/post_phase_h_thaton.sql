-- Post Phase H: fix last ETHICS-006 displaced entity
-- id=872 Thaton (Mon kingdom S Burma) matched to "Thai Kingdoms" polygon
-- centered in N Thailand — 456 km capital displacement

BEGIN;

UPDATE geo_entities SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(ST_SetSRID(ST_MakePoint(capital_lon, capital_lat), 4326)::geography, 200000)::geometry),
  boundary_source = 'approximate_circle',
  boundary_aourednik_name = NULL,
  boundary_aourednik_year = NULL,
  boundary_aourednik_precision = NULL,
  confidence_score = LEAST(confidence_score, 0.65),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Replaced erroneous "Thai Kingdoms" super-group polygon (centroid 456km away from Thaton capital in N Thailand) with 200km circle around Thaton. သထုံ Thaton/Sudhammavati (300-1057 CE) was the Mon kingdom of Lower Burma (modern Mon State + Bago region), capital of Suvannabhumi tradition; conquered by Pagan king Anawrahta 1057 who absorbed its monks + scriptures to convert Pagan to Theravada Buddhism. ETHICS: Mon ≠ Thai linguistically + culturally; aourednik super-group label was geographically and ethnographically wrong.'
WHERE id = 872;

SELECT id, name_original, ROUND(ST_Area(boundary_geom)::numeric, 4) as area, boundary_source, confidence_score
FROM geo_entities WHERE id = 872;

COMMIT;
