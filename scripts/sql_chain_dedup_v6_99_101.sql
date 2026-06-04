-- v6.99.101 — chain dedup: rimuove le 30 dynasty_chains duplicate (solo-prod).
--
-- Root cause: ingest_chains calcolava il set `existing` UNA volta dal DB e non
-- assorbiva i nomi inseriti nello stesso run; la sorgente JSON elencava alcune
-- catene-trunk sia nel vecchio batch_01 sia nei nuovi file per-regione, così un
-- singolo ingest inseriva entrambe. Il JSON è stato poi deduplicato (77 nomi
-- unici) ma l'ingest INSERT-only ha lasciato in prod i 30 doppioni.
--
-- ETHICS-002/003: una catena successoria duplicata è una continuità *fantasma*
-- mostrata due volte agli agenti. Verificato a monte: tutte e 30 le coppie sono
-- byte-identiche (stesso set di entità linkate, 0 divergenti).
--
-- Strategia: tiene MIN(id) per ogni `name`, elimina il resto + i loro chain_links.
-- Idempotente: una seconda esecuzione non trova doppioni e non cancella nulla.

BEGIN;

\echo '── BEFORE ──'
SELECT count(*) AS total_chains, count(DISTINCT name) AS distinct_names FROM dynasty_chains;

-- 1) elimina i chain_links delle catene-doppione (FK NO ACTION → prima i figli)
WITH ranked AS (
    SELECT id, row_number() OVER (PARTITION BY name ORDER BY id) AS rn FROM dynasty_chains
)
DELETE FROM chain_links WHERE chain_id IN (SELECT id FROM ranked WHERE rn > 1);

-- 2) elimina le righe-doppione (tiene il MIN(id) per name)
WITH ranked AS (
    SELECT id, row_number() OVER (PARTITION BY name ORDER BY id) AS rn FROM dynasty_chains
)
DELETE FROM dynasty_chains WHERE id IN (SELECT id FROM ranked WHERE rn > 1);

\echo '── AFTER ──'
SELECT count(*) AS total_chains, count(DISTINCT name) AS distinct_names FROM dynasty_chains;

-- guard: total deve uguagliare distinct (0 doppioni residui) → altrimenti ROLLBACK
DO $$
DECLARE t int; d int;
BEGIN
    SELECT count(*), count(DISTINCT name) INTO t, d FROM dynasty_chains;
    IF t <> d THEN
        RAISE EXCEPTION 'dedup incompleto: % chains, % distinct names', t, d;
    END IF;
END $$;

COMMIT;
