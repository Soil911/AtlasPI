-- v6.99.107 — chain_links → entita' deprecate: fix + follow-up ETHICS-012.
-- Generato da scripts/apply_chain_deprecated_fixes.py — NON editare a mano.
-- Dual-write: questo SQL allinea la prod; i JSON allineano il fresh-seed.
BEGIN;

-- ── 1. Re-point dei 4 link a entita' deprecate → primary (mappa merge v6.85) ──
UPDATE chain_links SET entity_id = 24 WHERE chain_id = 100 AND entity_id = 855;  -- Mengist Ityop'p'ya → የኢትዮጵያ ንጉሠ ነገሥት መንግሥት
UPDATE chain_links SET entity_id = 27 WHERE chain_id = 101 AND entity_id = 847;  -- هخامنشیان → Xšāça
UPDATE chain_links SET entity_id = 143 WHERE chain_id = 106 AND entity_id = 477;  -- دولت غزنویان → غزنویان
UPDATE chain_links SET entity_id = 12 WHERE chain_id = 106 AND entity_id = 849;  -- سلطنت مغلیہ → مغلیہ سلطنت

-- ── 2. Chain 99: rimozione link Meroe (552, dup di Kush 52 gia' in catena) ──
DELETE FROM chain_links WHERE chain_id = 99 AND entity_id = 552;
UPDATE dynasty_chains SET name = 'Nile Valley / Kush dynastic trunk: Kerma → Kush → Napata' WHERE id = 99;
UPDATE dynasty_chains SET ethical_notes = COALESCE(ethical_notes, '') || ' NOTE (ADR-005/ETHICS-001, 2026-07-02): the Meroitic-phase node was removed from this chain because the ''Meroe'' entity was deprecated as a duplicate of Kush (v6.85 merge map 52←552), which is already this chain''s seq-1 node and whose span (-1070..350) includes the Meroitic phase (c. -300..350, capital at Medewi/Meroë, Meroitic script, iron industry, ruling Kandakes). The phase remains part of the historical record via the Kush entity and the Napata node; a dedicated native-named Meroitic-phase entity (like the Napata one) is open future work, not an erasure.' WHERE id = 99 AND COALESCE(ethical_notes, '') NOT LIKE '%ADR-005/ETHICS-001, 2026-07-02%';

-- ── 3. Cap ETHICS-003: disputed ≤ 0.70 (follow-up #3 di ETHICS-012) ──
UPDATE geo_entities SET confidence_score = 0.7 WHERE status = 'disputed' AND confidence_score > 0.7;

-- ── 4. name_variants mancanti in prod (follow-up #5 di ETHICS-012, fonte batch_36) ──
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1037, 'First French Empire', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1037 AND name = 'First French Empire');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1037, 'Napoleonic Empire', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1037 AND name = 'Napoleonic Empire');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1037, 'Premier Empire', 'fr', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1037 AND name = 'Premier Empire');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1038, 'Afsharid dynasty', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1038 AND name = 'Afsharid dynasty');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1038, 'Afsharid Empire', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1038 AND name = 'Afsharid Empire');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1038, 'Afshariyan', 'fa', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1038 AND name = 'Afshariyan');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1039, 'Old Babylonian Empire', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1039 AND name = 'Old Babylonian Empire');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1039, 'First Dynasty of Babylon', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1039 AND name = 'First Dynasty of Babylon');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1040, 'Early Cholas', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1040 AND name = 'Early Cholas');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 1040, 'Sangam-era Chola', 'en', NULL, NULL, NULL, NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 1040 AND name = 'Sangam-era Chola');

-- ── guard finale ──
DO $$
DECLARE bad int;
BEGIN
  SELECT count(*) INTO bad FROM chain_links cl JOIN geo_entities g ON g.id = cl.entity_id
  WHERE g.status = 'deprecated';
  IF bad > 0 THEN RAISE EXCEPTION 'chain_links verso entita'' deprecate: %', bad; END IF;

  SELECT count(*) INTO bad FROM (
    SELECT chain_id, count(*) n, max(sequence_order) mx, min(sequence_order) mn
    FROM chain_links WHERE chain_id IN (99,100,101,106) GROUP BY chain_id
  ) q WHERE mn <> 0 OR mx <> n - 1;
  IF bad > 0 THEN RAISE EXCEPTION 'sequence_order non contiguo in % catene', bad; END IF;

  SELECT count(*) INTO bad FROM geo_entities WHERE status = 'disputed' AND confidence_score > 0.70;
  IF bad > 0 THEN RAISE EXCEPTION 'cap ETHICS-003 non applicato su % entita''', bad; END IF;

  SELECT count(*) INTO bad FROM name_variants WHERE entity_id IN (1037,1038,1039,1040);
  IF bad < 4 THEN RAISE EXCEPTION 'name_variants follow-up #5 incompleto (%)', bad; END IF;
END $$;

SELECT cl.chain_id, cl.sequence_order, cl.entity_id, g.name_original, g.status
FROM chain_links cl JOIN geo_entities g ON g.id = cl.entity_id
WHERE cl.chain_id IN (99,100,101,106) ORDER BY cl.chain_id, cl.sequence_order;

COMMIT;
