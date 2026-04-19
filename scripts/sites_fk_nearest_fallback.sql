-- v6.80 audit v4 Round 10: nearest-neighbor fallback per sites NULL residui (86)
-- Strategia: per ogni site senza entity_id (perché nessuna entity AtlasPI ha
-- boundary che lo contiene), trova entity moderna più vicina via capital coords.
-- Privilegia entity con entity_type='republic' o 'empire' attiva ad oggi.

WITH ranked AS (
  SELECT DISTINCT ON (s.id)
    s.id AS site_id,
    e.id AS entity_id,
    ST_Distance(
      ST_SetSRID(ST_MakePoint(s.longitude, s.latitude), 4326)::geography,
      ST_SetSRID(ST_MakePoint(e.capital_lon, e.capital_lat), 4326)::geography
    ) / 1000.0 AS dist_km
  FROM archaeological_sites s
  CROSS JOIN geo_entities e
  WHERE s.entity_id IS NULL
    AND s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
    AND e.capital_lat IS NOT NULL
    AND e.capital_lon IS NOT NULL
    AND e.year_end IS NULL  -- entità ancora esistente (es. repubbliche moderne)
    AND e.entity_type IN ('republic', 'empire', 'kingdom', 'federation')
  ORDER BY s.id, dist_km ASC
)
UPDATE archaeological_sites s
SET entity_id = r.entity_id
FROM ranked r
WHERE s.id = r.site_id
  AND r.dist_km < 5000.0;  -- ragionevole: <5000km per evitare match assurdi

SELECT
  COUNT(*) AS total,
  COUNT(entity_id) AS linked,
  COUNT(*) - COUNT(entity_id) AS still_null,
  ROUND(100.0 * COUNT(entity_id) / COUNT(*), 1) AS pct
FROM archaeological_sites;
