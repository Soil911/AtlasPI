-- Post Phase H VISUAL: replace 58 rectangle bbox placeholder polygons with
-- entity-type-appropriate circles around capital coordinates.
--
-- Detection: ST_Equals(boundary_geom, ST_Multi(ST_Envelope(boundary_geom)))
-- (the polygon IS its own envelope = a rectangle/square)
-- AND ST_NPoints <= 6 (only 4-5 corners)
--
-- Visual problem (Phase H follow-up): rectangles look like wireframe boxes
-- on the world map, not like real geographic entities. Even at coarse
-- approximation, a circle around the capital is more honest visually
-- (clearly approximate, not pretending to be a real polygon).
--
-- Radius per entity_type (km):
--   city / city-state                : 30
--   principality / duchy             : 80
--   chiefdom                         : 100
--   tribal_nation / tribal_federation: 150
--   confederation                    : 200 (or 80 for island)
--   kingdom                          : 250
--   sultanate                        : 250
--   republic                         : 500
--   dynasty                          : 400
--   caliphate                        : 600
--   khanate                          : 800 (nomadic, large)
--   empire                           : 800
--   colony                           : 500

BEGIN;

-- Use a CTE to compute radius per entity_type, then UPDATE all rectangles at once.
WITH type_radii AS (
  SELECT * FROM (VALUES
    ('city', 30000),
    ('city-state', 30000),
    ('principality', 80000),
    ('duchy', 80000),
    ('chiefdom', 100000),
    ('tribal_nation', 150000),
    ('tribal_federation', 150000),
    ('confederation', 200000),
    ('kingdom', 250000),
    ('sultanate', 250000),
    ('republic', 500000),
    ('dynasty', 400000),
    ('caliphate', 600000),
    ('khanate', 800000),
    ('empire', 800000),
    ('colony', 500000),
    ('cultural_region', 200000),
    ('settlement', 30000),
    ('settlement-complex', 50000),
    ('earthwork-complex', 20000),
    ('polity', 100000),
    ('emirate', 200000),
    ('federation', 500000),
    ('imamate', 200000),
    ('disputed_territory', 250000),
    ('civilization', 600000),
    ('culture', 400000)
  ) AS t(etype, radius_m)
),
rectangles AS (
  SELECT id, name_original, entity_type, capital_lat, capital_lon
  FROM geo_entities
  WHERE boundary_geom IS NOT NULL
    AND ST_NPoints(boundary_geom) <= 6
    AND ST_Equals(boundary_geom, ST_Multi(ST_Envelope(boundary_geom)))
    AND capital_lat IS NOT NULL
    AND capital_lon IS NOT NULL
)
UPDATE geo_entities g SET
  boundary_geojson = ST_AsGeoJSON(ST_Multi(ST_Buffer(
    ST_SetSRID(ST_MakePoint(g.capital_lon, g.capital_lat), 4326)::geography,
    COALESCE(tr.radius_m, 200000)
  )::geometry)),
  boundary_geom = ST_Multi(ST_Buffer(
    ST_SetSRID(ST_MakePoint(g.capital_lon, g.capital_lat), 4326)::geography,
    COALESCE(tr.radius_m, 200000)
  )::geometry),
  boundary_source = 'approximate_circle',
  confidence_score = LEAST(g.confidence_score, 0.5),
  ethical_notes = COALESCE(g.ethical_notes, '') || E'\n\n[v6.99.80-postH-visual] Replaced rectangle bbox placeholder polygon (visually obvious as bounding box, not real boundary) with capital-based circle of ' ||
    (COALESCE(tr.radius_m, 200000) / 1000)::text || 'km radius. Approximate but visually honest as approximation rather than pretending to be a documented boundary.'
FROM rectangles r
LEFT JOIN type_radii tr ON tr.etype = r.entity_type
WHERE g.id = r.id;

-- Verify
SELECT 'rectangles_remaining: ' || COUNT(*) as result
FROM geo_entities
WHERE boundary_geom IS NOT NULL
  AND ST_NPoints(boundary_geom) <= 6
  AND ST_Equals(boundary_geom, ST_Multi(ST_Envelope(boundary_geom)));

COMMIT;
