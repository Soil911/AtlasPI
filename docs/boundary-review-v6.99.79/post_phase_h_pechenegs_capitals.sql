-- Post Phase H: complete capital coverage
-- id=325 Pechenegs (Pontic steppe confederation) — nomadic, no fixed capital
-- 23 entities with capital_lat/lon but NULL capital_name

BEGIN;

-- ============================================================
-- 325 Pechenegs (Печенеги / Beçenek, 860-1091 CE)
-- ============================================================
UPDATE geo_entities SET
  capital_lat = 47.0,
  capital_lon = 33.0,
  capital_name = 'court itinerant (no fixed capital)',
  ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Set approximate center of Pecheneg core territory (Pontic steppe ~47N 33E) with name "court itinerant" — Pechenegs were a Turkic nomadic confederation without fixed capital, controlling area from Volga to Danube 860-1091 CE; raided Byzantine + Rus borderlands; absorbed by Cumans + Magyars + Kievan Rus 1091.'
WHERE id = 325;

-- ============================================================
-- 23 entities with capital coords but NULL capital_name
-- Set to 'unknown' so the field is populated, with ETHICS note
-- ============================================================
UPDATE geo_entities SET
  capital_name = 'unknown (coordinates provided, name not documented)'
WHERE capital_lat IS NOT NULL AND capital_lon IS NOT NULL AND capital_name IS NULL;

SELECT
  (SELECT COUNT(*) FROM geo_entities WHERE capital_lat IS NULL OR capital_lon IS NULL) as no_coords,
  (SELECT COUNT(*) FROM geo_entities WHERE capital_name IS NULL) as no_name,
  (SELECT COUNT(*) FROM geo_entities WHERE boundary_geojson IS NULL) as no_boundary;

COMMIT;
