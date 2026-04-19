-- v6.77 audit v4 Round 7: backfill archaeological_sites.entity_id
-- v2 ottimizzato: prefilter bbox && (operatore PostGIS) prima di ST_Contains

-- Crea indice spaziale temporaneo se non esiste
CREATE INDEX IF NOT EXISTS ix_geo_entities_boundary_geom_temp
  ON geo_entities USING GIST (ST_GeomFromGeoJSON(boundary_geojson))
  WHERE boundary_geojson IS NOT NULL;

-- Materialize la geometry una volta sola in temp table
CREATE TEMP TABLE entity_geoms AS
SELECT
  e.id,
  e.year_start,
  e.year_end,
  ST_GeomFromGeoJSON(e.boundary_geojson) AS geom
FROM geo_entities e
WHERE e.boundary_geojson IS NOT NULL;

CREATE INDEX ix_entity_geoms_geom ON entity_geoms USING GIST (geom);

-- Pass 1: geo + temporal con bbox prefilter
WITH ranked AS (
  SELECT DISTINCT ON (s.id)
    s.id AS site_id,
    e.id AS entity_id
  FROM archaeological_sites s
  JOIN entity_geoms e ON ST_MakePoint(s.longitude, s.latitude) && e.geom
  WHERE s.entity_id IS NULL
    AND s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
    AND s.date_start IS NOT NULL
    AND ST_Contains(e.geom, ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326))
    AND e.year_start <= COALESCE(s.date_end, s.date_start)
    AND (e.year_end IS NULL OR e.year_end >= s.date_start)
  ORDER BY s.id, ABS(COALESCE(e.year_end, 2025) - e.year_start) ASC, e.id ASC
)
UPDATE archaeological_sites s
SET entity_id = r.entity_id
FROM ranked r
WHERE s.id = r.site_id;

SELECT 'Pass 1 done' AS status, COUNT(entity_id) AS linked FROM archaeological_sites;

-- Pass 2: geo-only fallback (no date_start)
WITH ranked AS (
  SELECT DISTINCT ON (s.id)
    s.id AS site_id,
    e.id AS entity_id
  FROM archaeological_sites s
  JOIN entity_geoms e ON ST_MakePoint(s.longitude, s.latitude) && e.geom
  WHERE s.entity_id IS NULL
    AND s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
    AND ST_Contains(e.geom, ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326))
  ORDER BY s.id, ABS(COALESCE(e.year_end, 2025) - e.year_start) ASC, e.id ASC
)
UPDATE archaeological_sites s
SET entity_id = r.entity_id
FROM ranked r
WHERE s.id = r.site_id;

-- Final
SELECT
  COUNT(*) AS total_sites,
  COUNT(entity_id) AS linked,
  COUNT(*) - COUNT(entity_id) AS still_null,
  ROUND(100.0 * COUNT(entity_id) / COUNT(*), 1) AS pct_linked
FROM archaeological_sites;
