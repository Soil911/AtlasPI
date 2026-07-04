-- v6.99.127 (Task 1 ultracode / ADR-011) — batch 3 review confidence.
-- Chiude la coda conf_review_queue.json: alza prod al valore JSON dove le
-- fonti + la precisione di datazione lo giustificano (verify-agent + refuter
-- avversariale). Gli altri sono stati abbassati nel JSON (json:=prod).
-- Idempotente. Eseguire DOPO backup pg_dump. psql -v ON_ERROR_STOP=1.
BEGIN;
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 78 AND confidence_score = 0.7;  -- Великое княжество Московское
UPDATE geo_entities SET confidence_score = 0.825 WHERE id = 288 AND confidence_score = 0.75;  -- Մեծ Հայք / Armenia Magna
UPDATE geo_entities SET confidence_score = 0.7 WHERE id = 343 AND confidence_score = 0.6;  -- هوتکیان
UPDATE geo_entities SET confidence_score = 0.8 WHERE id = 450 AND confidence_score = 0.75;  -- 南宋
UPDATE geo_entities SET confidence_score = 0.825 WHERE id = 486 AND confidence_score = 0.75;  -- خلافة قرطبة
UPDATE geo_entities SET confidence_score = 0.55 WHERE id = 566 AND confidence_score = 0.5;  -- Dugelezh Breizh
UPDATE geo_entities SET confidence_score = 0.725 WHERE id = 588 AND confidence_score = 0.65;  -- ಪಶ್ಚಿಮ ಚಾಳುಕ್ಯ
UPDATE geo_entities SET confidence_score = 0.925 WHERE id = 715 AND confidence_score = 0.85;  -- Nieuw-Holland
UPDATE geo_entities SET confidence_score = 0.9 WHERE id = 912 AND confidence_score = 0.85;  -- Oxwitik
UPDATE geo_entities SET confidence_score = 0.85 WHERE id = 913 AND confidence_score = 0.7;  -- Pa' Chan
UPDATE geo_entities SET confidence_score = 0.8 WHERE id = 920 AND confidence_score = 0.7;  -- K'iik'aab
DO $$
DECLARE bad int;
BEGIN
  SELECT count(*) INTO bad FROM (VALUES (78,0.75),(288,0.825),(343,0.7),(450,0.8),(486,0.825),(566,0.55),(588,0.725),(715,0.925),(912,0.9),(913,0.85),(920,0.8)) v(eid,c)
    WHERE NOT EXISTS (SELECT 1 FROM geo_entities g WHERE g.id=v.eid AND g.confidence_score=v.c);
  IF bad <> 0 THEN RAISE EXCEPTION '% confidence raise non applicate', bad; END IF;
  RAISE NOTICE 'conf batch 3 OK: 11 confidence alzate';
END $$;
COMMIT;
