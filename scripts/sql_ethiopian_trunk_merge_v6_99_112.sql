-- ETHICS-018 (v6.99.112): dedup trunk etiope + merge Aksum latino→nativo
--
-- Contenuto (dual-write con i JSON dello stesso commit):
--   1. Re-homing riferimenti #853 "Aksum" (latino) → #51 መንግሥተ አክሱም (nativo):
--      evento Ezana/Meroe, 3 name_variants EN/IT, fonte primaria iscrizioni di
--      Ezana, 5 territory_changes. La variante 'Medri Bahri' (2613) viene
--      ELIMINATA (cross-check: designa una polity successiva distinta, non
--      Aksum — entità da creare); la territory_change #93 di #51 viene
--      ELIMINATA (conflava conversione 325 + campagna di Meroe: superseduta
--      dalle più precise 2424/325-religiosa e 2425/350-Meroe in arrivo).
--   2. Catena #22 "Ethiopian State Trunk": sostituzione link con la linea
--      merged a 4 nodi nativi ደዐመተ → መንግሥተ አክሱም → ዛግዌ → የኢትዮጵያ ንጉሠ ነገሥት መንግሥት
--      + row aggiornata (description/notes/confidence 0.7/region/sources).
--      Aksum→Zagwe = DISSOLUTION (non CONQUEST: gli Zagwe emersero dalla
--      frammentazione post-collasso, non conquistarono Aksum).
--   3. Catena #100 (duplicato semantico, ometteva gli Zagwe): DELETE hard
--      (precedente v6.99.101).
--   4. #853 → status='deprecated' con pointer (ADR-005, niente DELETE).
--   5. Guard finali: transazione abortita se lo stato finale non è quello atteso.
--
-- Idempotente: guard per statement. Eseguire DOPO backup pg_dump. ON_ERROR_STOP=1.

BEGIN;

-- ── 1. Re-homing riferimenti #853 → #51 ─────────────────────────────────────

UPDATE event_entity_links SET entity_id = 51
WHERE id = 441 AND entity_id = 853;

UPDATE name_variants SET entity_id = 51
WHERE id IN (2610, 2611, 2612) AND entity_id = 853;

-- 'Medri Bahri' NON è un nome di Aksum (polity eritrea XV-XIX sec.) → rimossa
DELETE FROM name_variants WHERE id = 2613 AND entity_id = 853;

UPDATE sources SET entity_id = 51
WHERE id = 2416 AND entity_id = 853;

UPDATE territory_changes SET entity_id = 51
WHERE id IN (2423, 2424, 2425, 2426, 2427) AND entity_id = 853;

-- tc #93 di #51 conflava conversione+Meroe al 325 → superseduta da 2424+2425
DELETE FROM territory_changes WHERE id = 93 AND entity_id = 51;

-- ── 2. Catena #22: linea merged a 4 nodi ────────────────────────────────────

DELETE FROM chain_links WHERE chain_id = 22;

INSERT INTO chain_links (chain_id, entity_id, sequence_order, transition_year, transition_type, is_violent, description, ethical_notes) VALUES
(22, 799, 0, NULL, NULL, false,
 'D''mt (Daamat), the pre-Aksumite kingdom of the northern highlands (c. 800-400 BCE), with monumental architecture at Yeha. It dissolved c. 400 BCE under unclear circumstances; multiple smaller highland polities followed before Aksumite consolidation.',
 'D''mt is sometimes described as a South Arabian (Sabaean) colony — a framing rooted in 19th-century diffusionism, largely rejected by modern archaeology: D''mt was an indigenous state with trade contacts across the Red Sea, not a transplanted Arabian colony.'),
(22, 51, 1, 100, 'SUCCESSION', false,
 'The Kingdom of Aksum, one of the four great powers of the late-antique world (so ranked by the prophet Mani), controlling Red Sea trade through Adulis, minting its own coinage, converting to Christianity under Ezana (c. 330-340), destroying Meroe (c. 350) and ruling Himyarite Yemen (6th c.). Declined from the 7th century as Islamic expansion re-routed Red Sea trade.',
 'SUCCESSION here means regional state-tradition succession across a ~500-year gap (c. 400 BCE - 100 CE), not documented dynastic continuity — the link is academically contested and this is the chain''s weak ring (see chain-level notes).'),
(22, 491, 2, 940, 'DISSOLUTION', true,
 'The Zagwe dynasty of Roha/Lalibela emerged from the fragmentation that followed the collapse of the Aksumite state (c. 940-960, traditionally tied to Queen Gudit/Yodit''s destruction of Aksum). The transition year marks Aksum''s end, not a Zagwe conquest: the dynasty proper is conventionally dated c. 1137 in many chronologies (this dataset''s Zagwe entity starts c. 900), and the intervening century is poorly documented. The Zagwe ruled until 1270 and built the rock-hewn churches of Lalibela.',
 'Typed DISSOLUTION (power passed through the collapse of the predecessor, as with USSR→successor states), NOT CONQUEST: asserting a Zagwe conquest of Aksum would overstate what the sources support. The violence flag records the Gudit/Yodit destruction tradition, whose historicity and the queen''s identity are debated; the ''destruction of Aksum'' narrative partly reflects the displaced dynasty''s perspective.'),
(22, 24, 3, 1270, 'REVOLUTION', true,
 'Yekuno Amlak overthrew the last Zagwe king (c. 1270) and founded the Solomonic dynasty, claiming descent from the Aksumite royal line via King Solomon and the Queen of Sheba. The Kebra Nagast (''Glory of Kings'') was compiled to legitimize this claim. The dynasty ruled — through interruptions it does not advertise (Zemene Mesafint decentralization c. 1769-1855, Italian occupation 1936-41) — until Haile Selassie''s deposition in 1974.',
 'The Solomonic ''restoration'' narrative is political theology, not documented genealogy — over 700 years of CLAIMED continuity. The framing of the Zagwe as illegitimate usurpers comes from the dynasty that overthrew them.');

UPDATE dynasty_chains SET
  region = 'East Africa / Ethiopian Highlands / Eritrea',
  description = 'Political succession of the Ethiopian-Eritrean highland state tradition: the pre-Aksumite kingdom of D''mt (c. 800-400 BCE), the Kingdom of Aksum (c. 100-960 CE), the Zagwe dynasty (c. 900/1137-1270, builders of the Lalibela rock churches), and the Solomonic Mengist Ityop''p''ya (1270-1974). Merged in v6.99.112 from two previously duplicate chains (ETHICS-018); intermediate fragmentation periods are documented in the link notes, not asserted as continuity.',
  confidence_score = 0.7,
  ethical_notes = 'Three legitimation myths and one weak link, all declared. (1) The D''mt→Aksum link crosses a ~500-year archaeological gap (D''mt dissolves c. 400 BCE, Aksumite consolidation c. 100 CE): the chain asserts a regional state-tradition succession, NOT documented dynastic continuity — academically contested, hence the chain confidence is capped at 0.7. (2) The fall of Aksum is tied by tradition to Queen Gudit/Yodit (c. 940-960), whose identity and historicity are debated (Ethiopian chronicles frame her variously as Beta Israel or pagan — partly the perspective of the displaced dynasty); the Zagwe did not ''conquer'' Aksum — they emerged from the fragmentation that followed (the Zagwe dynasty proper is conventionally dated c. 1137 in many chronologies). (3) The Zagwe are portrayed as ''usurpers'' by Solomonic-era sources — winners'' historiography: they were a legitimate dynasty (Agaw-speaking, hence ''outsiders'' in later Amhara-dominated accounts) and produced the rock-hewn churches of Lalibela. (4) The Solomonic claim of descent from Solomon and the Queen of Sheba (Kebra Nagast) is foundational political theology, not documented genealogy; ''restoration'' is the victors'' framing, stated as such.',
  sources = '[{"citation": "Munro-Hay, S. ''Aksum: An African Civilisation of Late Antiquity'' (1991)", "url": null, "source_type": "academic"}, {"citation": "Phillipson, D.W. ''Ancient Ethiopia: Aksum, Its Antecedents and Successors'' (1998)", "url": null, "source_type": "academic"}, {"citation": "Henze, P. ''Layers of Time: A History of Ethiopia'' (2000)", "url": null, "source_type": "academic"}, {"citation": "Taddesse Tamrat, ''Church and State in Ethiopia, 1270-1527'' (1972)", "url": null, "source_type": "academic"}]'
WHERE id = 22;

-- ── 3. Catena #100: DELETE hard (duplicato semantico) ───────────────────────

DELETE FROM chain_links WHERE chain_id = 100;
DELETE FROM dynasty_chains WHERE id = 100;

-- ── 4. Deprecazione #853 ────────────────────────────────────────────────────

UPDATE geo_entities SET
  status = 'deprecated',
  ethical_notes = 'DEPRECATA (ETHICS-018, ADR-005, v6.99.112): duplicato in trascrizione latina dell''entita'' 51 (መንግሥተ አክሱም) — mancato dal merge v6.85 perche'' privo di wikidata_qid. Riferimenti (evento Ezana/Meroe, 3 name_variants, fonte primaria iscrizioni di Ezana, 5 territory_changes) ri-homati alla 51; la variante ''Medri Bahri'' e'' stata RIMOSSA perche'' designa una polity successiva distinta (altopiano eritreo, XV-XIX sec.), non Aksum — entita'' da creare. Lookup canonico via id 51. ' || COALESCE(ethical_notes, '')
WHERE id = 853 AND status = 'confirmed';

-- ── 5. Guard finali ─────────────────────────────────────────────────────────

DO $$
DECLARE
  n int;
BEGIN
  SELECT count(*) INTO n FROM chain_links WHERE entity_id = 853;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: % chain_links residui su #853', n; END IF;

  SELECT count(*) INTO n FROM event_entity_links WHERE entity_id = 853;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: % event_entity_links residui su #853', n; END IF;

  SELECT count(*) INTO n FROM name_variants WHERE entity_id = 853;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: % name_variants residui su #853', n; END IF;

  SELECT count(*) INTO n FROM territory_changes WHERE entity_id = 853;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: % territory_changes residui su #853', n; END IF;

  SELECT count(*) INTO n FROM dynasty_chains WHERE id = 100;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: catena #100 ancora presente'; END IF;

  SELECT count(*) INTO n FROM chain_links WHERE chain_id = 22;
  IF n <> 4 THEN RAISE EXCEPTION 'GUARD: catena #22 ha % link, attesi 4', n; END IF;

  SELECT count(*) INTO n FROM chain_links WHERE chain_id = 22 AND sequence_order = 0 AND transition_type IS NULL;
  IF n <> 1 THEN RAISE EXCEPTION 'GUARD: seq0 di #22 deve avere transition NULL'; END IF;

  SELECT count(*) INTO n FROM chain_links cl JOIN geo_entities g ON g.id = cl.entity_id WHERE g.status = 'deprecated';
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: % chain_links puntano a entita'' deprecate', n; END IF;

  SELECT count(*) INTO n FROM geo_entities WHERE id = 853 AND status = 'deprecated';
  IF n <> 1 THEN RAISE EXCEPTION 'GUARD: #853 non risulta deprecata'; END IF;

  SELECT count(*) INTO n FROM territory_changes WHERE id = 93;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: territory_change #93 (conflata) ancora presente'; END IF;

  SELECT count(*) INTO n FROM name_variants WHERE id = 2613;
  IF n <> 0 THEN RAISE EXCEPTION 'GUARD: variante Medri Bahri (2613) ancora presente'; END IF;
END $$;

COMMIT;

-- Verifiche post-run:
--   SELECT count(*) FROM dynasty_chains;  -- atteso 99
--   SELECT cl.sequence_order, g.id, g.name_original, cl.transition_year, cl.transition_type, cl.is_violent
--     FROM chain_links cl JOIN geo_entities g ON g.id=cl.entity_id WHERE cl.chain_id=22 ORDER BY 1;
--   SELECT id, status FROM geo_entities WHERE id IN (51, 853);
--   SELECT count(*) FROM name_variants WHERE entity_id = 51;   -- atteso 6
--   SELECT count(*) FROM territory_changes WHERE entity_id = 51;  -- atteso 6 (2 originali -1 conflata +5 migrate)
