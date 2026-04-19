-- v6.78 audit v4 Round 8: backfill historical_cities.entity_id NULL
-- Stesso pattern di sites: bbox prefilter + ST_Contains + temporal preference

CREATE TEMP TABLE entity_geoms AS
SELECT
  e.id, e.year_start, e.year_end,
  ST_GeomFromGeoJSON(e.boundary_geojson) AS geom,
  e.capital_name, e.capital_lat, e.capital_lon
FROM geo_entities e
WHERE e.boundary_geojson IS NOT NULL;

CREATE INDEX ix_entity_geoms_geom ON entity_geoms USING GIST (geom);

-- PRIORITY 1: city is CAPITAL of an entity (capital_name match by ILIKE on name_original or name_variants)
-- Per CAPITAL cities: prefer the entity that has this city as capital_name
UPDATE historical_cities c
SET entity_id = e.id
FROM geo_entities e
WHERE c.entity_id IS NULL
  AND c.city_type = 'CAPITAL'
  AND e.capital_lat IS NOT NULL
  AND ABS(e.capital_lat - c.latitude) < 0.5
  AND ABS(e.capital_lon - c.longitude) < 0.5;

SELECT 'Pass 1 (CAPITAL match)' AS status, COUNT(entity_id) AS linked FROM historical_cities;

-- PRIORITY 2: geo + temporal containment for cities WITH founded_year
WITH ranked AS (
  SELECT DISTINCT ON (c.id)
    c.id AS city_id, e.id AS entity_id
  FROM historical_cities c
  JOIN entity_geoms e ON ST_MakePoint(c.longitude, c.latitude) && e.geom
  WHERE c.entity_id IS NULL
    AND c.founded_year IS NOT NULL
    AND ST_Contains(e.geom, ST_SetSRID(ST_MakePoint(c.longitude, c.latitude), 4326))
    AND e.year_start <= COALESCE(c.abandoned_year, c.founded_year)
    AND (e.year_end IS NULL OR e.year_end >= c.founded_year)
  ORDER BY c.id, ABS(COALESCE(e.year_end, 2025) - e.year_start) ASC, e.id ASC
)
UPDATE historical_cities c
SET entity_id = r.entity_id
FROM ranked r WHERE c.id = r.city_id;

SELECT 'Pass 2 (geo+temporal)' AS status, COUNT(entity_id) AS linked FROM historical_cities;

-- PRIORITY 3: geo-only fallback
WITH ranked AS (
  SELECT DISTINCT ON (c.id)
    c.id AS city_id, e.id AS entity_id
  FROM historical_cities c
  JOIN entity_geoms e ON ST_MakePoint(c.longitude, c.latitude) && e.geom
  WHERE c.entity_id IS NULL
    AND ST_Contains(e.geom, ST_SetSRID(ST_MakePoint(c.longitude, c.latitude), 4326))
  ORDER BY c.id, ABS(COALESCE(e.year_end, 2025) - e.year_start) ASC, e.id ASC
)
UPDATE historical_cities c
SET entity_id = r.entity_id
FROM ranked r WHERE c.id = r.city_id;

SELECT
  COUNT(*) AS total, COUNT(entity_id) AS linked,
  COUNT(*) - COUNT(entity_id) AS still_null,
  ROUND(100.0 * COUNT(entity_id) / COUNT(*), 1) AS pct_linked
FROM historical_cities;
