-- B1c (v6.99.110): estensioni catene esistenti su prod — dual-write con i JSON
-- (le 21 catene NUOVE arrivano via ingest_chains al boot; queste 3 estensioni no,
--  perché l'ingest salta i nomi già presenti — vedi ETHICS-017).
--
-- Contenuto:
--   1. Catena #97 (Arakan): rename (il vecchio nome portava il range '– 1430 CE',
--      falso dopo l'estensione) + 2 link nuovi (Mrauk U #691, Konbaung #360).
--   2. Catena #27 (Mesoamerican → Colonial Mexico Trunk): +1 link (Segundo Imperio #522)
--      + description allineata al JSON.
--   3. Catena #49 (Mesoamerican Classic-to-Colonial trunk): +1 link (Segundo Imperio #522).
--   4. name_variants #412: variante latina 'Dar Wadai' (ex nome primario JSON,
--      backport ETHICS-001/ETHICS-017 §7).
--
-- Idempotente: guard NOT EXISTS su ogni INSERT.
-- Eseguire DOPO backup pg_dump. ON_ERROR_STOP=1.

BEGIN;

-- 1a. Rename catena #97 (JSON e prod devono restare identici: dedup key dell'ingest)
UPDATE dynasty_chains
SET name = 'Arakan succession: Dhaññavati → Vesālī → Lemro → Mrauk U (c. 580 BCE – 1785 CE)',
    description = 'The successive kingdoms of the Arakan coastal strip (now Rakhine State, Myanmar), representing over 2000 years of continuous polity in a region geographically separated from the Irrawaddy Valley by mountains — extended in v6.99.110 to the Mrauk U kingdom (1430-1785) and its violent end in the Konbaung conquest. The Arakan tradition maintained a distinct Arakanese/Rakhine identity, Buddhist culture with strong Hindu elements, and significant maritime trade contacts with India and Southeast Asia.'
WHERE id = 97
  AND name = 'Arakan succession: Dhaññavati → Vesālī → Lemro (c. 580 BCE – 1430 CE)';

-- 1b. Catena #97: link Mrauk U (seq 3)
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
SELECT 97, 691, 3, 1430, 'SUCCESSION', false,
  'The kingdom of Mrauk U (1430-1785), founded by Min Saw Mon, who regained the Arakanese throne with help from the Bengal Sultanate — the origin of the court''s distinctive Buddhist-Islamic syncretism (kings bore Muslim titles alongside Buddhist ones, and Muslim communities were integral to the kingdom). At its height (16th-17th c.) Mrauk U controlled the coast from the Ganges delta to Cape Negrais, fielding a formidable fleet, and repelled the Toungoo empire.',
  'Mrauk U''s own record includes large-scale slave-raiding into Bengal (with Portuguese mercenaries based at Chittagong/Dianga) — documented, not euphemised. Its history is today contested terrain: both Rakhine Buddhist and Rohingya Muslim narratives claim it, and the kingdom''s genuinely plural character resists both exclusivist readings (no single version of history).'
WHERE NOT EXISTS (SELECT 1 FROM chain_links WHERE chain_id = 97 AND entity_id = 691);

-- 1c. Catena #97: link Konbaung (seq 4)
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
SELECT 97, 360, 4, 1785, 'CONQUEST', true,
  'Konbaung conquest of Arakan: Bodawpaya''s invasion force under Crown Prince Thado Minsaw (over 20,000 men) crossed the Arakan Mountains in December 1784 and took Mrauk U on 2 January 1785, ending c. 355 years of Arakanese independence. The Mahamuni Buddha image — the palladium of Arakanese kingship — was dismantled and carried off to Amarapura; some 20,000 people were deported to the Konbaung capital region; the royal library was burned.',
  'Recorded as the violent conquest and cultural despoliation it was. The conquest''s aftermath — flight of tens of thousands of Arakanese into British Bengal, Chin Byan''s cross-border resistance (1811-1815) — entangled Arakan in Anglo-Burmese relations and led to the First Anglo-Burmese War (1824-26), after which Arakan passed to British rule. The region''s modern tragedies (including the 2017 Rohingya genocide) have roots in the layered dispossessions that began here; the chain-level notes flag this continuity.'
WHERE NOT EXISTS (SELECT 1 FROM chain_links WHERE chain_id = 97 AND entity_id = 360);

-- 2a. Catena #27: description allineata al JSON (menzione Segundo Imperio + gap repubbliche)
UPDATE dynasty_chains
SET description = REPLACE(description,
  'The Primer Imperio Mexicano (1821-23) represents independence.',
  'The Primer Imperio Mexicano (1821-23) represents independence; the Segundo Imperio Mexicano (1864-67, imposed by the French Intervention) was appended in v6.99.110 — the republics between and after (1824-1864, 1867-) are not yet entities and are documented in the link notes.')
WHERE id = 27;

-- 2b. Catena #27: link Segundo Imperio (seq 3)
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
SELECT 27, 522, 3, 1864, 'CONQUEST', true,
  'Second Mexican Empire (1864-1867): imposed by Napoleon III''s French Intervention (invasion 1862, Mexico City taken June 1863); Maximilian of Habsburg accepted the crown in April 1864, sustained by the French army against Juárez''s republic. After the French withdrawal (1866-67) the empire collapsed: Maximilian was captured and executed at Querétaro (19 June 1867).',
  'GAP DOCUMENTED: the First Mexican Republic (1824-1864, including the Reforma and Juárez''s legitimate government, which never ceased to exist during the Intervention) and the Restored Republic (1867-) are not yet entities in this dataset — this link does NOT mean the First Empire transitioned directly into the Second; four decades of republican history and a foreign invasion lie between. The empire was a French imperial imposition resisted by the republican government throughout.'
WHERE NOT EXISTS (SELECT 1 FROM chain_links WHERE chain_id = 27 AND entity_id = 522);

-- 3. Catena #49: link Segundo Imperio (seq 5)
INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes)
SELECT 49, 522, 5, 1864, 'CONQUEST', true,
  'Second Mexican Empire (1864-1867): imposed by Napoleon III''s French Intervention (invasion 1862, Mexico City taken June 1863); Maximilian of Habsburg accepted the crown in April 1864, sustained by the French army against Juárez''s republic. After the French withdrawal (1866-67) the empire collapsed: Maximilian was captured and executed at Querétaro (19 June 1867).',
  'GAP DOCUMENTED: the First Mexican Republic (1824-1864, including the Reforma and Juárez''s legitimate government, which never ceased to exist during the Intervention) and the Restored Republic (1867-) are not yet entities in this dataset — this link does NOT mean the First Empire transitioned directly into the Second; four decades of republican history and a foreign invasion lie between. The empire was a French imperial imposition resisted by the republican government throughout.'
WHERE NOT EXISTS (SELECT 1 FROM chain_links WHERE chain_id = 49 AND entity_id = 522);

-- 4. Variante latina per Wadai #412 (ex nome primario del JSON)
INSERT INTO name_variants (entity_id, name, lang, period_start, period_end, context, source)
SELECT 412, 'Dar Wadai', 'ar-Latn', 1501, 1912,
  'Latinised form, former primary name in this dataset (native Arabic name backported per ETHICS-001 in v6.99.110)',
  'AtlasPI ETHICS-017 §7'
WHERE NOT EXISTS (SELECT 1 FROM name_variants WHERE entity_id = 412 AND name = 'Dar Wadai');

COMMIT;

-- Verifiche post-run:
--   SELECT id, name FROM dynasty_chains WHERE id IN (27, 49, 97);
--   SELECT chain_id, sequence_order, entity_id FROM chain_links
--     WHERE chain_id IN (27, 49, 97) ORDER BY chain_id, sequence_order;
--   SELECT name, lang FROM name_variants WHERE entity_id = 412;
