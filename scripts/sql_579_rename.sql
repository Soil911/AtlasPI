-- v6.99.108 — rename #579 Furstentum Walachei → Terra Transalpina (ETHICS-001).
-- Generato da scripts/apply_579_rename.py — NON editare a mano.
BEGIN;

UPDATE geo_entities SET name_original = 'Terra Transalpina', name_original_lang = 'la', ethical_notes = 'ETHICS-001: The early Wallachian voivodates before the Battle of Posada (1330) are poorly documented and historiographically contested. Romanian national historiography emphasizes continuity with Daco-Roman populations; Hungarian historiography emphasizes Hungarian suzerainty over the region. The status ''disputed'' reflects genuine scholarly uncertainty. ETHICS-001 (rename 2026-07-02): name_original is ''Terra Transalpina'', the contemporary Latin designation of the Hungarian royal chancery for the trans-Carpathian Wallachian polity — an exonym, declared as such, but the only contemporary WRITTEN naming tradition (proto-Romanian had no written form in this period; the self-designation ''Țara Românească'' is attested only from the 14th century and belongs to the successor entity). The 1247 Diploma of the Joannites names the component voivodates individually (''terra Lytua'', ''terra Szeneslai'') — ''Terra Transalpina'' as a unified name is partially retrospective for 1247. The previous name_original ''Fürstentum Walachei'' was MODERN German historiography, wrongly described as contemporary — kept as name_variant for traceability. NOTE: the capital ''Curtea de Arges'' is too firm for this period — early Wallachian political centers are uncertain and shifted (Câmpulung, Curtea de Argeș). ETHICS-003: This entry covers the proto-state period (1247-1330) before the established Principality of Wallachia (already in the database starting 1330). The dates and political structure of this period are genuinely uncertain. Boundary da aourednik/historical-basemaps (1279, strategy=capital_in_polygon, precision=1). CC BY 4.0.

[v6.30-displaced-rollback] Boundary reverted to capital-based approximation: aourednik fuzzy match placed polygon centroid=2817km / edge=0km from capital (exceeded thresholds). Regenerated as 80.0km radius circle.' WHERE id = 579 AND name_original = 'Furstentum Walachei';

INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 579, 'Fürstentum Walachei', 'de', 1247, 1330, 'modern German historiographical name; was this record''s name_original until 2026-07-02 (ETHICS-001 rename — not a contemporary form)', NULL
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 579 AND name = 'Fürstentum Walachei');
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
  SELECT 579, 'terra Lytua / terra Szeneslai', 'la', 1247, 1330, 'the component voivodates (Litovoi, Seneslau) as actually named in the Diploma of the Joannites (1247), the earliest document on organized Wallachian polities', 'Diploma of the Joannites (1247), Hungarian royal chancery'
  WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 579 AND name = 'terra Lytua / terra Szeneslai');

DO $$ DECLARE bad int; BEGIN
  SELECT count(*) INTO bad FROM geo_entities WHERE id = 579 AND name_original <> 'Terra Transalpina';
  IF bad > 0 THEN RAISE EXCEPTION 'rename 579 non applicato'; END IF;
  SELECT count(*) INTO bad FROM name_variants WHERE entity_id = 579;
  IF bad < 4 THEN RAISE EXCEPTION 'variants 579 attese >= 4, trovate %', bad; END IF;
END $$;

SELECT id, name_original, name_original_lang, status, confidence_score FROM geo_entities WHERE id = 579;

COMMIT;
