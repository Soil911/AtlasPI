-- v6.99.125 (M4/ADR-011) — batch 1 review confidence: 6 entità maggiori,
-- ben-sourced (≥3 fonti academic/primary) e con date PRECISE ben attestate,
-- dove la confidence JSON più alta è giustificata. Alza prod al valore JSON
-- (riconcilia la coda `conf_review_queue.json` + migliora prod onestamente).
-- Idempotente (WHERE sul valore vecchio). psql -v ON_ERROR_STOP=1.
--
-- Nessuna è disputed (no cap ETHICS-003); tutte confirmed e >0.5 (ETHICS-013 ok).
BEGIN;

-- Sasanidi 224-651 (impero persiano pre-islamico, datazione precisa)
UPDATE geo_entities SET confidence_score = 0.9  WHERE id = 121 AND confidence_score = 0.75 AND status = 'confirmed';
-- Periodo Heian 794-1185 (storiografia giapponese estesa)
UPDATE geo_entities SET confidence_score = 0.8  WHERE id = 444 AND confidence_score = 0.65 AND status = 'confirmed';
-- Shogunato Kamakura 1185-1333
UPDATE geo_entities SET confidence_score = 0.8  WHERE id = 445 AND confidence_score = 0.65 AND status = 'confirmed';
-- Vicereame del Río de la Plata 1776-1814 (7 fonti academic, unità coloniale documentata)
UPDATE geo_entities SET confidence_score = 0.925 WHERE id = 213 AND confidence_score = 0.7 AND status = 'confirmed';
-- Dinastia Đinh 968-980 (Vietnam)
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 878 AND confidence_score = 0.6 AND status = 'confirmed';
-- Dinastia Tiền Lê (Prima Lê) 980-1009
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 879 AND confidence_score = 0.6 AND status = 'confirmed';

DO $$
DECLARE bad int;
BEGIN
  SELECT count(*) INTO bad FROM (VALUES (121,0.9),(444,0.8),(445,0.8),(213,0.925),(878,0.75),(879,0.75)) v(eid,c)
    WHERE NOT EXISTS (SELECT 1 FROM geo_entities g WHERE g.id=v.eid AND g.confidence_score=v.c);
  IF bad <> 0 THEN RAISE EXCEPTION '% confidence non applicate', bad; END IF;
  RAISE NOTICE 'M4 conf batch 1 OK: 6 confidence alzate (Sasanidi/Heian/Kamakura/Río de la Plata/Đinh/Tiền Lê)';
END $$;

COMMIT;
