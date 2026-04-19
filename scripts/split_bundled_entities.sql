-- v6.86 audit v4 Round 15: split bundled entities (Babilonia + Chola)
-- Riconosce che entities long-duration possono raggruppare polities discrete.
-- Aggiunge entities per le fasi specifiche; lascia entity originale come
-- "aggregate" con ethical_notes che spiega cosa è coperto separatamente.

BEGIN;

-- ─── BABILONIA SPLIT ──────────────────────────────────────────────
-- Esistente: id 171 𒆍𒀭𒊏𒆠 (-1894 to -539) aggregate
-- Esistente: id 490 𒆳𒆍𒀭𒊏𒆠 (-626 to -539) Neo-Babylonian (specific)
-- Nuovo: Old Babylonian Empire (-1894 to -1595)
-- Kassite phase (-1595 to -1155) NON coperto separatamente (deferred)

INSERT INTO geo_entities (
  name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon,
  confidence_score, status, ethical_notes, wikidata_qid
) VALUES (
  '𒆍𒀭𒊏𒆠 (Old Babylonian)', 'akk', 'empire', -1894, -1595,
  'Babylon', 32.5429, 44.4209,
  0.85, 'confirmed',
  'ETHICS-001: Old Babylonian Empire (Hammurabi dynasty), -1894 a -1595 BCE. Distinct from Neo-Babylonian (id=490, -626 to -539). The intermediate Kassite period (-1595 to -1155) is not separately covered as entity yet. The Code of Hammurabi (~1754 BCE) belongs to this period. Q733897 verified Wikidata.',
  'Q733897'
);

-- Update id 171 to clarify aggregate
UPDATE geo_entities SET
  ethical_notes = COALESCE(ethical_notes, '') ||
    ' [v6.86 audit v4 Round 15] CIVILTÀ aggregate: questa entity copre l''intera storia babilonese -1894 a -539. Le fasi specifiche sono coperte da entities dedicate: Old Babylonian Empire (id appena creato, -1894 to -1595), Neo-Babylonian Empire (id 490, -626 to -539). La fase Kassite/Middle Babylonian (-1595 to -1155) non è ancora coperta come entity separata.'
WHERE id = 171;

-- ─── CHOLA SPLIT ──────────────────────────────────────────────────
-- Esistente: id 110 சோழ நாடு (-300 to 1279) bundled
-- Approccio: id 110 → focus su Medieval (year_start 848), nuovo entity per Sangam-era

INSERT INTO geo_entities (
  name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon,
  confidence_score, status, ethical_notes, wikidata_qid
) VALUES (
  'சோழர் (Sangam-era)', 'ta', 'kingdom', -300, 300,
  'Uraiyur', 10.7905, 78.6864,
  0.6, 'confirmed',
  'ETHICS-001: Early Cholas / Sangam-era Tamil kingdom, regional dynasty del delta Kaveri (-300 to 300 CE). Distinct from Medieval Chola Empire (id 110, restricted to 848-1279 dopo split v6.86). After Sangam era there was a 650-year gap (Kalabhra interregnum + Pallava rule) before Vijayalaya restored Chola rule in 848. Confidence 0.6 perché Sangam literature (Pattuppattu, Ettuthokai) è la fonte primaria ma con cronologie incerte. Q3532146 verified.',
  'Q3532146'
);

-- Update id 110 to focus on Medieval Chola Empire
UPDATE geo_entities SET
  year_start = 848,
  ethical_notes = COALESCE(ethical_notes, '') ||
    ' [v6.86 audit v4 Round 15] SPLIT: year_start aggiornato da -300 a 848 per focalizzare su Medieval Chola Empire (Vijayalaya founding). Sangam-era Cholas (-300 to 300 CE) ora coperta da entity separata. Wikidata Q6806806 (Chola Empire) ufficialmente 848-1070, AtlasPI estende a 1279 per includere Late Chola decline (Kulottunga III, ultimo grande sovrano d. 1218; ultimo Chola d. 1279).'
WHERE id = 110;

-- Verify
SELECT id, name_original, year_start, year_end, wikidata_qid
FROM geo_entities
WHERE id IN (110, 171, 490)
   OR wikidata_qid IN ('Q733897', 'Q3532146')
ORDER BY id;

COMMIT;
