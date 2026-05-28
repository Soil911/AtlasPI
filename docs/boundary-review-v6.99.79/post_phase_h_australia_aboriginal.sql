-- Post Phase H: replace rectangle bbox of Aboriginal Australian Nations
-- with hand-coded polygon following Australian continental coastline approximation.
--
-- The previous polygon was a perfect rectangle [112.5-154E × -39.5 to -10.5S]
-- = 1113 deg² covering ocean as well as land. Visually obvious as placeholder.
--
-- The new polygon traces major Australian coastal features at ~20 points,
-- still very approximate but visually recognizable as Australia.
--
-- ETHICS-009: Aboriginal Australian Nations represent ~250+ distinct nations
-- with separate languages, songlines, and custodial relationships to country.
-- The continental polygon is appropriate ONLY as a marker for "Aboriginal
-- presence across the continent before colonization" — specific nations
-- (Noongar id=771, Wiradjuri id=772, Yolŋu id=311, Kulin id=310, Torres
-- Strait id=308) should retain their own region-specific polygons.

BEGIN;

-- Australian continent rough coastline (clockwise from NW Cape)
-- Major coastal points: NW Cape → Darwin → Cape York → Brisbane → Sydney
-- → Melbourne → Tasmania (skip — separate island) → Adelaide → Perth → NW Cape
UPDATE geo_entities SET
  boundary_geojson = '{"type":"MultiPolygon","coordinates":[[[
    [114.0,-21.5],[114.5,-26.0],[115.5,-30.0],[114.5,-33.5],
    [119.0,-34.5],[127.0,-32.5],[133.5,-32.0],[138.0,-35.5],
    [140.0,-37.5],[143.0,-38.5],[146.5,-38.7],[150.0,-37.2],
    [151.5,-32.0],[153.5,-28.0],[153.0,-25.0],[152.0,-22.0],
    [148.0,-20.0],[145.5,-15.5],[142.5,-10.7],[141.5,-13.0],
    [139.0,-17.0],[136.5,-15.5],[132.0,-12.0],[129.5,-15.0],
    [126.5,-14.0],[122.5,-16.5],[121.0,-19.5],[118.0,-20.5],
    [114.0,-21.5]
  ]]]}',
  boundary_geom = ST_Multi(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[
    [114.0,-21.5],[114.5,-26.0],[115.5,-30.0],[114.5,-33.5],
    [119.0,-34.5],[127.0,-32.5],[133.5,-32.0],[138.0,-35.5],
    [140.0,-37.5],[143.0,-38.5],[146.5,-38.7],[150.0,-37.2],
    [151.5,-32.0],[153.5,-28.0],[153.0,-25.0],[152.0,-22.0],
    [148.0,-20.0],[145.5,-15.5],[142.5,-10.7],[141.5,-13.0],
    [139.0,-17.0],[136.5,-15.5],[132.0,-12.0],[129.5,-15.0],
    [126.5,-14.0],[122.5,-16.5],[121.0,-19.5],[118.0,-20.5],
    [114.0,-21.5]
  ]]}')),
  boundary_source = 'historical_approximation',
  confidence_score = LEAST(confidence_score, 0.6),
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH-visual] Replaced placeholder rectangle bbox (1113 deg² covering ocean) with hand-coded continental coastline polygon (~28 points, ~700 deg² actual land area). Still approximate but no longer visually obvious as bbox rectangle. Polygon represents the geographic spread of Aboriginal Australian peoples before British colonization began 1788; specific nations have their own region-specific polygons (Noongar SW, Wiradjuri NSW, Yolŋu Arnhem, Kulin Victoria, Torres Strait northern islands, etc.).'
WHERE id = 309;

SELECT id, name_original, ROUND(ST_Area(boundary_geom)::numeric, 1) as area, ST_NPoints(boundary_geom) as npoints, boundary_source FROM geo_entities WHERE id = 309;

COMMIT;
