-- v6.85 audit v4 Round 14: merge entity duplicates (44 secondary → primary)
-- Strategia conservativa:
--   1) UPDATE FK rulers/sites/cities/chain_links da secondary a primary
--   2) UPDATE secondary.status = 'deprecated' + ethical_notes pointer
--   3) NO DELETE (preserva permalinks /v1/entities/{secondary_id} esistenti)
--
-- Mapping da Round 2/3:
--   primary_id -> secondary_ids
-- Salto entity 147 Kanem-Bornu (chain_link aggregate-pertinent, NON spostato a 647 Kanem-only)

BEGIN;

-- Helper: function per redirect FK + flag deprecated
-- (inline per chiarezza; tabelle: historical_rulers, archaeological_sites,
--  historical_cities, chain_links)

-- ─── Mapping completo ─────────────────────────────────────────────
CREATE TEMP TABLE merge_map (primary_id INT, secondary_id INT);
INSERT INTO merge_map VALUES
  (412, 737), (339, 608), (559, 735), (296, 465), (491, 854),
  (337, 606), (661, 739), (413, 738), (419, 731),
  (43, 548), (690, 904), (160, 414), (424, 571), (145, 605),
  (38, 723), (24, 855), (323, 611), (213, 710), (206, 709),
  (112, 848), (90, 585), (52, 552), (143, 477), (203, 720),
  (475, 494), (12, 849), (27, 847), (97, 586), (33, 653),
  (199, 657), (187, 482), (150, 852), (490, 497), (554, 744),
  (111, 594), (397, 612), (151, 851), (741, 1009), (157, 558),
  (489, 500), (830, 991),
  -- Round 3 collisions (native script vs Latin transliteration)
  (218, 859), (513, 532), (219, 726);

-- ─── Pass 1: redirect FK historical_rulers ───────────────────────
UPDATE historical_rulers r
SET entity_id = m.primary_id
FROM merge_map m
WHERE r.entity_id = m.secondary_id;

-- ─── Pass 2: redirect FK archaeological_sites ────────────────────
UPDATE archaeological_sites s
SET entity_id = m.primary_id
FROM merge_map m
WHERE s.entity_id = m.secondary_id;

-- ─── Pass 3: redirect FK historical_cities ───────────────────────
UPDATE historical_cities c
SET entity_id = m.primary_id
FROM merge_map m
WHERE c.entity_id = m.secondary_id;

-- ─── Pass 4: redirect FK chain_links ─────────────────────────────
-- Edge case: se chain_link contiene SIA primary CHE secondary nello stesso
-- chain (improbabile ma possibile), il redirect crea duplicato. Skip
-- chain_links di tipo (chain_id, primary_id) già esistenti.
DELETE FROM chain_links cl
WHERE EXISTS (
  SELECT 1 FROM merge_map m WHERE cl.entity_id = m.secondary_id
  AND EXISTS (
    SELECT 1 FROM chain_links cl2
    WHERE cl2.chain_id = cl.chain_id AND cl2.entity_id = m.primary_id
  )
);

UPDATE chain_links cl
SET entity_id = m.primary_id
FROM merge_map m
WHERE cl.entity_id = m.secondary_id;

-- ─── Pass 5: flag secondary entities ─────────────────────────────
UPDATE geo_entities g
SET
  status = 'deprecated',
  ethical_notes = COALESCE(g.ethical_notes, '') ||
    ' [v6.85 audit v4 Round 14] DUPLICATE merged: questa entity è stata identificata come duplicato di entity ' || m.primary_id || ' (cross-reference Wikidata Q-ID condiviso). FK su rulers/sites/cities/chain_links sono state ricollegate alla primary. Status=deprecated; entity preservata per non rompere permalinks /v1/entities/' || g.id || ' esistenti, ma considerare canonical lookup via primary id ' || m.primary_id || '.'
FROM merge_map m
WHERE g.id = m.secondary_id;

-- Verify
SELECT 'Total entities' AS metric, COUNT(*) AS value FROM geo_entities
UNION ALL
SELECT 'Deprecated', COUNT(*) FROM geo_entities WHERE status = 'deprecated'
UNION ALL
SELECT 'Confirmed/active', COUNT(*) FROM geo_entities WHERE status != 'deprecated';

SELECT 'Rulers redirected' AS metric, COUNT(*) AS value
FROM historical_rulers r
WHERE r.entity_id IN (SELECT primary_id FROM merge_map);

COMMIT;
