-- ETHICS-019 (v6.99.118): fix mislabel di regime su #240 e #534.
-- Vedi docs/ethics/ETHICS-019-mislabel-regimi-cambogia-haiti.md.
--
-- #240: portava il nome della Repubblica Khmer (1970-75) su un record che in
--   anni/evento/note descrive la Kampuchea Democratica (1975-79).
-- #534: il Primo Impero di Haiti (Dessalines, 1804-06) era etichettato
--   'Repiblik Dayiti' con entity_type='kingdom'.
--
-- Uso (dopo pg_dump di backup):
--   ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
--     "docker exec -i cra-atlaspi-db psql -U atlaspi -d atlaspi -v ON_ERROR_STOP=1" \
--     < scripts/sql_ethics019_mislabel_fix.sql
--
-- Idempotenza: i WHERE asseriscono i valori vecchi; una seconda esecuzione
-- non trova righe e il blocco di validazione finale fallisce (rollback pulito).

BEGIN;

-- ─── #240: Kampuchea Democratica ─────────────────────────────────────────
UPDATE geo_entities SET
    name_original = 'កម្ពុជាប្រជាធិបតេយ្យ',
    wikidata_qid  = 'Q330988',
    ethical_notes = ethical_notes || ' ETHICS-019 (v6.99.118): record rinominato - portava erroneamente il nome della Repubblica Khmer (សាធារណរដ្ឋខ្មែរ, stato distinto, 1970-1975). I Khmer Rossi controllavano il paese dal 17 aprile 1975; il nome di stato ''Kampuchea Democratica'' fu proclamato formalmente con la costituzione del gennaio 1976; gli anni 1975-1979 seguono la convenzione del periodo di regime.'
WHERE id = 240
  AND name_original = 'សាធារណរដ្ឋខ្មែរ'
  AND wikidata_qid = 'Q1054184';

-- Variante km ora ridondante col primario → romanizzazione (precedente: ar-Latn).
UPDATE name_variants SET
    name    = 'Kampuchea Prâcheathippadey',
    lang    = 'km-Latn',
    context = 'romanizzazione del nome ufficiale khmer'
WHERE id = 619
  AND entity_id = 240
  AND name = 'កម្ពុជាប្រជាធិបតេយ្យ';

-- Nota event-link genocidio: non spiega piu' il vecchio mismatch.
UPDATE event_entity_links SET
    notes = 'state under Khmer Rouge control from April 1975; the state name Democratic Kampuchea was formally proclaimed in January 1976 (ETHICS-019)'
WHERE id = 109
  AND entity_id = 240
  AND notes = 'predecessor Khmer Republic; Democratic Kampuchea was the formal state name';

-- ─── #534: Primo Impero di Haiti ─────────────────────────────────────────
UPDATE geo_entities SET
    name_original = 'Anpi an Ayiti',
    entity_type   = 'empire',
    ethical_notes = ethical_notes || ' ETHICS-019 (v6.99.118): primary name corrected from the erroneous ''Repiblik Dayiti'' -- the 1804-1806 state was an EMPIRE (Dessalines was crowned Emperor Jacques I; official name in the 1805 imperial constitution: Empire d''Haïti, period spelling Empire d''Hayti). ''Anpi an Ayiti'' is the attested modern Haitian Creole form; Kreyòl orthography is 20th-century, explicitly not a period spelling.'
WHERE id = 534
  AND name_original = 'Repiblik Dayiti'
  AND entity_type = 'kingdom';

INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
SELECT 534, 'Empire d''Haïti', 'fr', 1804, 1806,
       'Official name in the 1805 imperial constitution (period spelling: Empire d''Hayti); French was the state''s written administrative language',
       'Constitution impériale d''Haïti, 20 May 1805'
WHERE NOT EXISTS (
    SELECT 1 FROM name_variants WHERE entity_id = 534 AND name = 'Empire d''Haïti'
);

-- ─── Validazione: tutte le modifiche devono aver colpito ────────────────
DO $$
DECLARE
    n240  int; n619 int; n109 int; n534 int; nvar int;
BEGIN
    SELECT count(*) INTO n240 FROM geo_entities
      WHERE id = 240 AND name_original = 'កម្ពុជាប្រជាធិបតេយ្យ' AND wikidata_qid = 'Q330988';
    SELECT count(*) INTO n619 FROM name_variants
      WHERE id = 619 AND name = 'Kampuchea Prâcheathippadey' AND lang = 'km-Latn';
    SELECT count(*) INTO n109 FROM event_entity_links
      WHERE id = 109 AND notes LIKE '%ETHICS-019%';
    SELECT count(*) INTO n534 FROM geo_entities
      WHERE id = 534 AND name_original = 'Anpi an Ayiti' AND entity_type = 'empire';
    SELECT count(*) INTO nvar FROM name_variants
      WHERE entity_id = 534 AND name = 'Empire d''Haïti' AND lang = 'fr';
    IF n240 <> 1 OR n619 <> 1 OR n109 <> 1 OR n534 <> 1 OR nvar <> 1 THEN
        RAISE EXCEPTION 'ETHICS-019 validation failed: n240=% n619=% n109=% n534=% nvar=%',
            n240, n619, n109, n534, nvar;
    END IF;
    RAISE NOTICE 'ETHICS-019 OK: #240 e #534 corretti, variante fr inserita';
END $$;

COMMIT;
