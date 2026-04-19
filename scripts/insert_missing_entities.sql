-- v6.82 audit v4 Round 12: insert 2 missing entities + extend Regnum Francorum
-- Entities mancanti rilevate da audit (rulers Napoleon/Nadir Shah/Charlemagne).

BEGIN;

-- 1. Premier Empire français (1804-1814/1815)
INSERT INTO geo_entities (
  name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon,
  confidence_score, status, ethical_notes, wikidata_qid
) VALUES (
  'Premier Empire français', 'fr', 'empire', 1804, 1815,
  'Paris', 48.8566, 2.3522,
  0.9, 'confirmed',
  'ETHICS-001: nome originale in francese (lingua amministrativa). L''impero napoleonico (1804-1815) è separato dalla République française (1789-1804) e dalla Restaurazione (1815+). I confini variarono enormemente — i Cento Giorni (marzo-luglio 1815) sono inclusi nella periodo. ETHICS-002: l''impero portò avanti le idee della Rivoluzione (Codice Civile, abolizione feudalismo) ma anche guerre napoleoniche con ~3-6M morti, schiavitù reintrodotta nelle colonie (1802), repressioni in Spagna/Russia/Germania. La narrativa ''glorie napoleoniche'' va bilanciata con il costo umano. Q71084 verified Wikidata.',
  'Q71084'
);

-- 2. Afsharid Iran (1736-1796)
INSERT INTO geo_entities (
  name_original, name_original_lang, entity_type, year_start, year_end,
  capital_name, capital_lat, capital_lon,
  confidence_score, status, ethical_notes, wikidata_qid
) VALUES (
  'افشاریان', 'fa', 'empire', 1736, 1796,
  'مشهد', 36.297, 59.6062,
  0.85, 'confirmed',
  'ETHICS-001: nome originale in persiano (Afsharyan). Dinastia turcomanna fondata da Nadir Shah (1736-1747), uno dei più grandi conquistatori iraniani — sconfisse Mughal a Karnal (1739) e saccheggio'' Delhi (Peacock Throne preso). ETHICS-002: il sacco di Delhi del 1739 vide ~30,000 vittime in massacri urbani. Le campagne ottomane e nel Caucaso furono parimenti brutali. Dopo l''assassinio di Nadir Shah (1747) l''impero collassò rapidamente; il successore Shahrokh regnò solo a Khorasan. ETHICS-003: la storiografia iraniana enfatizza Nadir come ''Napoleone d''Iran'' ma è cauto sulle violenze. Q63149558 verified.',
  'Q63149558'
);

-- 3. Extend Regnum Francorum (id=431) year_end 751 → 800 + ethical_notes update
-- Reason: gap 751-800 era Pippin il Breve (regno carolingio pre-imperiale).
UPDATE geo_entities SET
  year_end = 800,
  ethical_notes = COALESCE(ethical_notes, '') ||
    ' [v6.82 audit v4 Round 12] Esteso year_end 751→800 per coprire il regno Carolingio pre-imperiale di Pippin il Breve (751-768) e Carlo Magno re (768-800). Il 751 era convenzione "fine Merovingi" (deposizione Childerico III), ma il regno non si interrompe — passa solo da Merovingi a Carolingi. La fase imperiale (800+) è coperta da entity 89 Imperium Francorum.'
WHERE id = 431;

-- Verify
SELECT id, name_original, year_start, year_end, wikidata_qid
FROM geo_entities
WHERE id = 431
   OR wikidata_qid IN ('Q71084', 'Q63149558');

COMMIT;
