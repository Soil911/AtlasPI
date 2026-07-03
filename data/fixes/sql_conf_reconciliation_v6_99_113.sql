-- ADR-011 (v6.99.113): riconciliazione confidence JSON->prod
-- Generato da scripts/reconcile_confidence.py — NON editare a mano.
-- Eseguire DOPO backup pg_dump. ON_ERROR_STOP=1.
BEGIN;
UPDATE geo_entities SET confidence_score = 0.65 WHERE id = 25 AND confidence_score = 0.6;  -- batch_32_boost
UPDATE geo_entities SET confidence_score = 0.6 WHERE id = 39 AND confidence_score = 0.35;  -- batch_32_boost
DO $$
DECLARE n int;
BEGIN
  SELECT count(*) INTO n FROM geo_entities WHERE id = 25 AND confidence_score = 0.65;
  IF n <> 1 THEN RAISE EXCEPTION 'GUARD: id 25 non aggiornato'; END IF;
  SELECT count(*) INTO n FROM geo_entities WHERE id = 39 AND confidence_score = 0.6;
  IF n <> 1 THEN RAISE EXCEPTION 'GUARD: id 39 non aggiornato'; END IF;
END $$;
COMMIT;
