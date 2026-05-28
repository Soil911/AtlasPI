-- Phase H follow-up: link ETHICS-critical events (genocides, massacres,
-- ethnic cleansings, deportations) to entities in DB.
-- ETHICS-007: ogni evento deve avere actor/victim esplicito, no eufemismi.
--
-- For each event, link to:
--   - MAIN_ACTOR = perpetrator entity (if in DB)
--   - VICTIM = victim entity/people (if in DB)
--   - AFFECTED = bystander state (if relevant)
--
-- Where victim entity is not in DB (e.g., specific indigenous nations,
-- religious minorities), add ETHICS note + leave VICTIM unlinked.

BEGIN;

-- ============================================================
-- 244 Lindisfarne 793 (Viking raid on monastery)
-- Norse raiders not represented as a single entity in DB.
-- AFFECTED: Northumbrian Anglo-Saxon kingdom (not in DB either).
-- Skip: no clear entity link possible.
-- ============================================================

-- ============================================================
-- 602 Sack of Jerusalem 1099 (Crusader capture + massacre)
-- MAIN_ACTOR: 470 Regnum Hierosolymitanum (Crusader Kingdom)
-- VICTIM: 174 الدولة الفاطمية (Fatimid Caliphate)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (602, 470, 'MAIN_ACTOR', '[v6.99.80-postH] First Crusaders under Godfrey of Bouillon + Raymond + Tancred established Kingdom of Jerusalem after the massacre.'),
  (602, 174, 'VICTIM', '[v6.99.80-postH] Fatimid garrison + Muslim and Jewish civilian population of Jerusalem.');

-- ============================================================
-- 604 Sack of Rome 1527 (Imperial troops sacked Rome)
-- MAIN_ACTOR: 30 Sacrum Imperium Romanum (Holy Roman Empire / Charles V)
-- VICTIM: 100 Regno d'Italia not yet existed; closest is Vatican but not in DB.
-- Use SIR as MAIN_ACTOR + AFFECTED note for Papal States (no entity).
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (604, 30, 'MAIN_ACTOR', '[v6.99.80-postH] Charles V Habsburg unpaid mutinous Imperial army (Spanish tercios + German Landsknechte, many Lutheran) sacked Rome. Pope Clement VII fled to Castel SantAngelo.');

-- ============================================================
-- 79 Pequot War / Mystic Massacre 1636-1637
-- MAIN_ACTOR: No single colony entity in DB (Massachusetts Bay / Connecticut Colony pre-USA).
-- VICTIM: Pequot Nation (not in DB).
-- Best link: 245 USA (anachronistic; alternatively note + skip).
-- Skip MAIN_ACTOR; add ETHICS note via update.
-- ============================================================
UPDATE historical_events SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Cannot link to entity: Massachusetts Bay Colony + Connecticut Colony + Pequot Nation not represented as separate entities in current DB. ETHICS-007 narrative properly preserved in description + main_actor.'
WHERE id = 79;

-- ============================================================
-- 489 Haymarket affair 1886
-- MAIN_ACTOR: 245 USA (Chicago Police)
-- VICTIM: workers + 5 anarchists executed
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (489, 245, 'MAIN_ACTOR', '[v6.99.80-postH] Chicago Police fired on labor rally. State of Illinois later executed 4 anarchist defendants in tainted trial (Albert Parsons, August Spies, George Engel, Adolph Fischer).');

-- ============================================================
-- 13 Herero & Nama Genocide 1904 (Vernichtungsbefehl)
-- MAIN_ACTOR: 260 Deutsch-Ostafrika no — was DSWA (German South West Africa).
-- Closest: 98 Deutsches Kaiserreich (Imperial Germany)
-- VICTIM: Herero + Nama nations (not in DB)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (13, 98, 'MAIN_ACTOR', '[v6.99.80-postH] Imperial German Army under General Lothar von Trotha issued Vernichtungsbefehl (Extermination Order) on 2 October 1904, ordering all Herero — armed or not — to leave Germany territory or be shot. Estimated 65-80% of Herero population (50,000-65,000) and 50% of Nama population (10,000) killed.');

-- ============================================================
-- 266 Jallianwala Bagh Massacre 1919
-- MAIN_ACTOR: 5 British Raj
-- VICTIM: civilian Indians (no specific entity)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (266, 5, 'MAIN_ACTOR', '[v6.99.80-postH] Brigadier-General Reginald Dyer, British Indian Army, ordered troops to fire on Baisakhi-day crowd of ~10,000 unarmed civilians (Sikh+Hindu+Muslim) in enclosed garden. Official British figure: 379 killed, 1,200 wounded; Indian estimates 1,000+ killed.');

-- ============================================================
-- 490 + 31 Nanjing Massacre 1937 (duplicates)
-- MAIN_ACTOR: 32 大日本帝國 (Empire of Japan)
-- VICTIM: 243 中華民國 (Republic of China)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (490, 32, 'MAIN_ACTOR', '[v6.99.80-postH] Imperial Japanese Army Central China Area Army (Gen. Iwane Matsui commanding, Prince Yasuhiko Asaka at Nanjing); ~100,000-300,000 Chinese killed in 6 weeks of mass murder + mass rape (estimated 20,000-80,000 women raped).'),
  (490, 243, 'VICTIM', '[v6.99.80-postH] Civilians and surrendered soldiers of the Republic of China.'),
  (31, 32, 'MAIN_ACTOR', '[v6.99.80-postH] Same event as id=490 (duplicate); recommend merge in cleanup PR.'),
  (31, 243, 'VICTIM', '[v6.99.80-postH] Same event as id=490 (duplicate); recommend merge.');

-- ============================================================
-- 16 השואה Holocaust 1941-1945
-- MAIN_ACTOR: 229 Deutsches Reich (Nazi Germany)
-- VICTIM: European Jewish people, Roma, Sinti, disabled, LGBTQ+, political dissidents
-- (Jewish people not represented as entity in current DB)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (16, 229, 'MAIN_ACTOR', '[v6.99.80-postH] Nazi German state (NSDAP, SS, Wehrmacht, Einsatzgruppen, collaborating Vichy + Slovakia + Hungary + Romania + Croatia regimes) systematically murdered approximately 6 million European Jews, plus Roma (250,000-500,000), Sinti, disabled people (T4 program 200,000+), LGBTQ+ persons (5,000-15,000), political dissidents, Soviet POWs (3.3 million). Total estimated 11 million murdered in Holocaust + Porajmos + T4.');

-- ============================================================
-- 471 Executive Order 9066 1942
-- MAIN_ACTOR: 245 USA
-- VICTIM: Japanese American population (no separate entity)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (471, 245, 'MAIN_ACTOR', '[v6.99.80-postH] FDR signed EO 9066 authorizing forced relocation of ~120,000 Japanese Americans (62% US citizens) to internment camps (Manzanar, Tule Lake, Heart Mountain, Topaz, etc.) until 1946. Formal US apology + $20,000 reparations per survivor came in Civil Liberties Act of 1988.');

-- ============================================================
-- 183 Argentina Dirty War 1976-1983
-- MAIN_ACTOR: No 1976 Argentina entity in DB.
-- Cannot link; ETHICS note added.
-- ============================================================
UPDATE historical_events SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Cannot link to entity: 1976 Argentine military junta (Videla, Massera, Agosti, Viola, Galtieri, Bignone) not represented as separate entity from modern Argentina in current DB. ETHICS-007 narrative preserved via main_actor text; 30,000 desaparecidos documented by CONADEP + Nunca Más report.'
WHERE id = 183;

-- ============================================================
-- 17 Rwanda Genocide 1994
-- MAIN_ACTOR: 558 U Rwanda (modern Rwanda — though Hutu Power regime was distinct)
-- Or 157 u Rwanda (kingdom 1081-1962) — anachronistic.
-- Use 558 with ETHICS note.
-- VICTIM: Tutsi people (not separately in DB), moderate Hutus.
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (17, 558, 'MAIN_ACTOR', '[v6.99.80-postH] Hutu Power government of Rwanda (MRND + CDR) and Interahamwe militia killed approximately 500,000-1,000,000 Tutsi and moderate Hutu over ~100 days. ETHICS-007: linked entity is modern Rwanda (1962-) but perpetrator was specifically Habyarimana regime + post-assassination interim govt — not the Tutsi-led RPF government that ended the genocide.');

-- ============================================================
-- 28 September 11 Attacks 2001
-- MAIN_ACTOR: Al-Qaeda (not a state entity, no DB representation)
-- VICTIM: 245 USA
-- AFFECTED: Possibly Saudi (origin of hijackers), Afghan (Taliban host)
-- ============================================================
INSERT INTO event_entity_links (event_id, entity_id, role, notes) VALUES
  (28, 245, 'VICTIM', '[v6.99.80-postH] 19 Al-Qaeda hijackers attacked US targets (WTC twin towers New York; Pentagon; United 93 crashed in Pennsylvania). 2,977 victims killed + 19 hijackers. Triggered US 20-year Global War on Terror (Afghanistan invasion 2001, Iraq 2003). MAIN_ACTOR Al-Qaeda not represented as entity in DB (non-state actor).');

-- ============================================================
-- 349 Darfur Genocide 2003-
-- MAIN_ACTOR: Sudanese government / Bashir / Janjaweed (no separate entity).
-- VICTIM: Fur, Masalit, Zaghawa peoples (not in DB)
-- ============================================================
UPDATE historical_events SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Cannot link MAIN_ACTOR: modern Sudan + Janjaweed militia + Bashir regime (1989-2019) not represented as distinct entities in current DB. ICC indicted Omar al-Bashir for genocide (March 2009) — first sitting head of state indicted by ICC. Estimated 200,000-400,000 killed, 2.5M displaced from 2003-present.'
WHERE id = 349;

-- ============================================================
-- 208 Ghouta chemical attack 2013
-- MAIN_ACTOR: Syrian Arab Armed Forces under Assad
-- VICTIM: Syrian civilians (rebel-held East Ghouta)
-- No modern Syria entity in DB.
-- ============================================================
UPDATE historical_events SET ethical_notes = COALESCE(ethical_notes, '') || E'\n\n[v6.99.80-postH] Cannot link MAIN_ACTOR: modern Syrian Arab Republic (1963-) under Assad regime not represented as entity in current DB. Sarin nerve agent rockets fired at rebel-held East Ghouta district of Damascus 21 August 2013; estimated 281-1,729 killed (UN OPCW investigation confirmed sarin use; UN inspectors found Syrian govt responsibility consistent with evidence).'
WHERE id = 208;

-- Verify
SELECT 'Linked events: ' || COUNT(DISTINCT event_id) FROM event_entity_links
WHERE notes LIKE '%v6.99.80-postH%';

COMMIT;
