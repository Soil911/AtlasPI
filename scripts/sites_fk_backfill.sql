-- v6.77 audit v4 Round 7: backfill archaeological_sites.entity_id NULL
-- Strategia in 2 passi:
--   1) Match per containment geografico + overlap temporale (preferisce entity più specifica)
--   2) Per sites senza date, fallback solo geografico
-- ETHICS: i sites archeologici sono "luoghi", le entities sono "polities".
-- Il match site→entity dice "questo sito si trovava in questa polity al tempo
-- del sito". Per siti con multipla copertura politica nel tempo, usiamo la
-- entity più specifica (year_end - year_start narrow) per privilegiare
-- attribuzione politica precisa al periodo del sito.

-- Pass 1: geo + temporal match (preferisce narrower entity)
WITH ranked AS (
  SELECT DISTINCT ON (s.id)
    s.id AS site_id,
    e.id AS entity_id,
    e.name_original AS entity_name,
    s.name_original AS site_name
  FROM archaeological_sites s
  CROSS JOIN geo_entities e
  WHERE s.entity_id IS NULL
    AND s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
    AND e.boundary_geojson IS NOT NULL
    AND ST_Contains(
      ST_SetSRID(ST_GeomFromGeoJSON(e.boundary_geojson), 4326),
      ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326)
    )
    AND s.date_start IS NOT NULL
    AND e.year_start <= COALESCE(s.date_end, s.date_start)
    AND (e.year_end IS NULL OR e.year_end >= s.date_start)
  ORDER BY s.id, ABS(COALESCE(e.year_end, 2025) - e.year_start) ASC, e.id ASC
)
UPDATE archaeological_sites s
SET entity_id = r.entity_id
FROM ranked r
WHERE s.id = r.site_id;

-- Report Pass 1 affected
SELECT 'Pass 1 (geo+temporal) backfilled' AS pass, COUNT(*) AS n
FROM archaeological_sites WHERE entity_id IS NOT NULL;

-- Pass 2: geo-only fallback per sites senza date_start
WITH ranked AS (
  SELECT DISTINCT ON (s.id)
    s.id AS site_id,
    e.id AS entity_id
  FROM archaeological_sites s
  CROSS JOIN geo_entities e
  WHERE s.entity_id IS NULL
    AND s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
    AND e.boundary_geojson IS NOT NULL
    AND ST_Contains(
      ST_SetSRID(ST_GeomFromGeoJSON(e.boundary_geojson), 4326),
      ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326)
    )
  ORDER BY s.id, ABS(COALESCE(e.year_end, 2025) - e.year_start) ASC, e.id ASC
)
UPDATE archaeological_sites s
SET entity_id = r.entity_id
FROM ranked r
WHERE s.id = r.site_id;

-- Final report
SELECT
  COUNT(*) AS total_sites,
  COUNT(entity_id) AS linked,
  COUNT(*) - COUNT(entity_id) AS still_null,
  ROUND(100.0 * COUNT(entity_id) / COUNT(*), 1) AS pct_linked
FROM archaeological_sites;
