-- v6.99.125 (M4/ADR-011) — batch 2 review confidence: 9 stati storici maggiori,
-- date precise ben attestate, 2-3 fonti academic/primary. Alza prod al valore
-- JSON (riconcilia coda). Idempotente. psql -v ON_ERROR_STOP=1.
BEGIN;

-- Confederazione polacco-lituana 1569-1795 (stato documentatissimo)
UPDATE geo_entities SET confidence_score = 0.8  WHERE id = 62  AND confidence_score = 0.7  AND status = 'confirmed';
-- Regno nabateo -312..106 (Petra; annessione romana 106)
UPDATE geo_entities SET confidence_score = 0.81 WHERE id = 179 AND confidence_score = 0.7  AND status = 'confirmed';
-- Moghulistan 1347-1462 (khanato successore chagataide)
UPDATE geo_entities SET confidence_score = 0.725 WHERE id = 339 AND confidence_score = 0.6  AND status = 'confirmed';
-- Periodo Nara 710-794
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 443 AND confidence_score = 0.65 AND status = 'confirmed';
-- Shogunato Muromachi 1336-1573
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 446 AND confidence_score = 0.65 AND status = 'confirmed';
-- Periodo Azuchi-Momoyama 1568-1600
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 447 AND confidence_score = 0.65 AND status = 'confirmed';
-- Cinque Dinastie 907-960 (Cina)
UPDATE geo_entities SET confidence_score = 0.75 WHERE id = 451 AND confidence_score = 0.65 AND status = 'confirmed';
-- Hetmanato cosacco 1649-1764
UPDATE geo_entities SET confidence_score = 0.7  WHERE id = 678 AND confidence_score = 0.6  AND status = 'confirmed';
-- Dinastia Ngô 939-967 (Vietnam)
UPDATE geo_entities SET confidence_score = 0.7  WHERE id = 877 AND confidence_score = 0.6  AND status = 'confirmed';

DO $$
DECLARE bad int;
BEGIN
  SELECT count(*) INTO bad FROM (VALUES (62,0.8),(179,0.81),(339,0.725),(443,0.75),(446,0.75),(447,0.75),(451,0.75),(678,0.7),(877,0.7)) v(eid,c)
    WHERE NOT EXISTS (SELECT 1 FROM geo_entities g WHERE g.id=v.eid AND g.confidence_score=v.c);
  IF bad <> 0 THEN RAISE EXCEPTION '% confidence non applicate', bad; END IF;
  RAISE NOTICE 'M4 conf batch 2 OK: 9 confidence alzate';
END $$;

COMMIT;
