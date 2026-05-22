-- Phase D — name_variants for top 0-result user queries (Phase D analytics-driven)
-- name_variants has no unique constraint, so we just INSERT (idempotent risk acceptable for one-shot)

BEGIN;

-- Frankish / Carolingian (entities 431 Regnum Francorum, 89 Imperium Francorum)
INSERT INTO name_variants (entity_id, name, lang, context) VALUES
(431, 'Frankish Kingdom', 'en', 'Common English name'),
(431, 'Merovingian Kingdom', 'en', 'Dynasty-based English name'),
(431, 'Royaume mérovingien', 'fr', 'Mérovingiens'),
(431, 'Fränkisches Reich', 'de', 'German form'),
(431, 'Frankish realm', 'en', 'Generic'),
(89, 'Carolingian Empire', 'en', 'Common English name (Charlemagne)'),
(89, 'Frankish Empire', 'en', 'Generic Frankish'),
(89, 'Empire of Charlemagne', 'en', 'Eponymous'),
(89, 'Karolingerreich', 'de', 'German form'),
(89, 'Empire carolingien', 'fr', 'French form'),
(89, 'Holy Roman Empire (early)', 'en', 'Crowned 800 CE');

-- Crusader States
INSERT INTO name_variants (entity_id, name, lang, context) VALUES
(472, 'Crusader Antioch', 'en', 'Crusader Levant'),
(472, 'Crusader State of Antioch', 'en', NULL),
(472, 'Outremer (Antioch)', 'en', 'Crusader Outremer'),
(472, 'Principato d''Antiochia', 'it', 'Italian crusader name'),
(471, 'Crusader Tripoli', 'en', 'Crusader Levant'),
(471, 'County of Tripoli', 'en', 'Common English name'),
(471, 'Outremer (Tripoli)', 'en', NULL),
(471, 'Contea di Tripoli', 'it', NULL),
(473, 'Crusader Edessa', 'en', NULL),
(473, 'County of Edessa', 'en', NULL),
(473, 'Outremer (Edessa)', 'en', NULL),
(473, 'Contea di Edessa', 'it', NULL);

-- Maori (entity 55 Aotearoa)
INSERT INTO name_variants (entity_id, name, lang, context) VALUES
(55, 'Maori', 'en', 'Indigenous people of NZ'),
(55, 'Māori', 'mi', 'Self-designation with macron'),
(55, 'New Zealand (pre-colonial)', 'en', 'Common English geographic'),
(55, 'Maori iwi', 'en', 'Iwi (tribes) collective'),
(55, 'Pre-colonial Aotearoa', 'en', NULL);

-- Bantu peoples (variants on major Bantu polities)
INSERT INTO name_variants (entity_id, name, lang, context) VALUES
(10, 'Bantu Kingdom of Kongo', 'en', 'Major Bantu kingdom'),
(10, 'Kongo Bantu', 'en', NULL),
(156, 'Bantu Buganda', 'en', 'Major Bantu kingdom'),
(156, 'Bantu kingdom', 'en', 'Generic Bantu polity'),
(558, 'Bantu Rwanda', 'en', NULL),
(403, 'Bantu Ndongo', 'en', NULL),
(34, 'Bantu Zulu', 'en', NULL),
(34, 'Zulu Bantu', 'en', NULL);

-- Hellenistic kingdoms
INSERT INTO name_variants (entity_id, name, lang, context) VALUES
(282, 'Hellenistic Commagene', 'en', 'Hellenistic Anatolia'),
(284, 'Hellenistic Epirus', 'en', 'Pyrrhus kingdom'),
(347, 'Hellenistic Bactria', 'en', 'Greek Bactria');

-- Renaissance (Italian states 1300-1500)
-- 422 Milano, 23 Venezia (entity id), 81 Genova (if exists)
INSERT INTO name_variants (entity_id, name, lang, context) VALUES
(422, 'Renaissance Milan', 'en', 'Sforza/Visconti Milan'),
(422, 'Sforza Milan', 'en', NULL),
(422, 'Visconti Milan', 'en', NULL),
(23, 'Renaissance Venice', 'en', 'Italian Renaissance period'),
(23, 'Venetian Renaissance', 'en', NULL);

COMMIT;
SELECT count(*) AS total_variants FROM name_variants;
