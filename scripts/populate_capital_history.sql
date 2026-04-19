-- v6.84 audit v4 Round 13: populate capital_history per polities long-duration
-- con capitali multiple già documentate in ethical_notes (v6.65 + v6.66 audit).

BEGIN;

-- Helper macro: insert una capitale alla volta (per chiarezza)

-- ─── id 30 Sacrum Imperium Romanum (HRE) ──────────────────────────
-- L'HRE non ebbe capitale ufficiale. Documentiamo le sedi notabili.
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (30, 'Aachen', 50.7753, 6.0839, 800, 1562, 1, 'Sede principale incoronazioni imperiali (Carlo Magno→Massimiliano II)'),
  (30, 'Frankfurt am Main', 50.1109, 8.6821, 1562, 1806, 2, 'Sede elezione imperatori dal 1562'),
  (30, 'Regensburg', 49.0134, 12.1016, 1663, 1806, 3, 'Sede Dieta Perpetua (Immerwährender Reichstag)'),
  (30, 'Wien', 48.2082, 16.3738, 1438, 1806, 4, 'Sede de facto Asburgo (capitale Erzherzogtum Österreich, NON dell''HRE come tale)');

-- ─── id 18 Manden Kurufaba (Mali) ────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (18, 'Niani', 11.38, -8.68, 1235, 1600, 1, 'Capitale convenzionale (Delafosse 1912, Niane). CONTESTATO: Hunwick & Boulègue 2008 rigettano questa identificazione'),
  (18, 'Court itinerant', NULL, NULL, 1235, 1600, 2, 'Green (2022): Mali può non aver avuto capitale fissa, corte del mansa mobile');

-- ─── id 12 مغلیہ سلطنت (Mughal) ──────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (12, 'Agra', 27.1767, 78.0081, 1526, 1648, 1, 'Capitale primaria sotto Babur, Humayun, Akbar, Jahangir (esclusi anni Suri 1540-1555)'),
  (12, 'Shahjahanabad/Delhi', 28.6139, 77.2090, 1648, 1857, 2, 'Trasferimento capitale da Shah Jahan'),
  (12, 'Aurangabad', 19.8762, 75.3433, 1681, 1707, 3, 'Sede campo militare Aurangzeb in Deccan');

-- ─── id 2 Osmanlı İmparatorluğu (Ottoman) ────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (2, 'Söğüt', 40.0190, 30.1879, 1299, 1335, 1, 'Beylik fondativo Osman I'),
  (2, 'Bursa', 40.1828, 29.0665, 1335, 1365, 2, 'Conquistata da Orhan, prima vera capitale'),
  (2, 'Edirne', 41.6771, 26.5557, 1365, 1453, 3, 'Capitale balcanica, base per espansione europea'),
  (2, 'İstanbul/Kostantiniyye', 41.0082, 28.9784, 1453, 1922, 4, 'Conquistata da Mehmed II, capitale fino dissoluzione');

-- ─── id 108 明朝 (Ming) ──────────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (108, '南京 (Nanjing)', 32.0603, 118.7969, 1368, 1421, 1, 'Capitale fondativa Hongwu'),
  (108, '北京 (Beijing)', 39.9042, 116.4074, 1421, 1644, 2, 'Trasferimento Yongle, costruzione Città Proibita');

-- ─── id 106 宋朝 (Song) ──────────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (106, '開封 (Kaifeng)', 34.7972, 114.3073, 960, 1127, 1, 'Capitale Northern Song'),
  (106, '臨安/Lin''an (Hangzhou)', 30.27, 120.15, 1127, 1279, 2, 'Capitale Southern Song dopo caduta nord ai Jin');

-- ─── id 24 Solomonic Ethiopia ─────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (24, 'Tegulet', 9.4, 39.45, 1270, 1400, 1, 'Capitale iniziale della dinastia salomonide'),
  (24, 'Court itinerant', NULL, NULL, 1400, 1636, 2, 'Roving camp medievale caratteristico'),
  (24, 'Gondar', 12.6028, 37.4661, 1636, 1855, 3, 'Capitale stabile per ~220 anni'),
  (24, 'Mekelle', 13.4969, 39.4669, 1881, 1889, 4, 'Sede temporanea di Yohannes IV'),
  (24, 'Addis Abeba', 9.0250, 38.7469, 1886, 1974, 5, 'Capitale moderna fondata da Menelik II');

-- ─── id 170 𒀸𒋩 (Assiria) ───────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (170, 'Aššur', 35.454, 43.258, -2025, -705, 1, 'Capitale per ~1320 anni (vasta maggioranza del periodo)'),
  (170, 'Kalhu/Nimrud', 36.0961, 43.3286, -879, -705, 2, 'Capitale sotto Ashurnasirpal II → Sennacherib'),
  (170, 'Dur-Sharrukin', 36.5092, 43.2294, -706, -705, 3, 'Brevissima sede Sargon II'),
  (170, 'Nineveh', 36.3586, 43.1528, -705, -612, 4, 'Capitale finale Sennacherib → caduta');

-- ─── id 52 Kush ──────────────────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (52, 'Kerma', 19.6042, 30.4124, -1070, -750, 1, 'Centro originario'),
  (52, 'Napata', 18.53, 31.83, -750, -590, 2, 'Capitale durante XXV Dinastia (governo Egitto)'),
  (52, 'Meroë', 16.9386, 33.7489, -590, 350, 3, 'Capitale dopo sacco Napata (Psamtik II)');

-- ─── id 177 Seleucidi ─────────────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (177, 'Seleucia on Tigris', 33.0928, 44.5119, -312, -240, 1, 'Capitale fondativa Seleuco I (presso Babilonia)'),
  (177, 'Antioch', 36.2069, 36.1568, -240, -63, 2, 'Trasferimento, capitale durante apice ellenistico');

-- ─── id 147 Kanem-Bornu ──────────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (147, 'Njimi', 13.5, 15.0, 700, 1380, 1, 'Capitale Kanem (fase originaria)'),
  (147, 'Ngazargamu', 13.0667, 12.0167, 1470, 1808, 2, 'Capitale Bornu sotto Mai Ali Gaji'),
  (147, 'Kukawa', 12.9167, 13.5667, 1814, 1893, 3, 'Capitale tarda Bornu fino conquista coloniale');

-- ─── id 76 Regnum Langobardorum ──────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (76, 'Verona/Cividale (corte itinerante)', 45.4642, 11.0, 568, 572, 1, 'Sede mobile pre-conquista Pavia'),
  (76, 'Papia (Pavia)', 45.1847, 9.1582, 572, 774, 2, 'Capitale stabile dopo assedio di 3 anni');

-- ─── id 99 Oesterreich-Ungarn ────────────────────────────────────
INSERT INTO capital_history (entity_id, name, lat, lon, year_start, year_end, ordering, notes) VALUES
  (99, 'Wien', 48.2082, 16.3738, 1867, 1918, 1, 'Capitale Cisleithania (parte austriaca + sede imperiale)'),
  (99, 'Budapest', 47.4979, 19.0402, 1867, 1918, 2, 'Capitale Transleithania (parte ungherese, pari grado per affari interni)');

-- Verify
SELECT entity_id, COUNT(*) AS capitals_count
FROM capital_history
GROUP BY entity_id
ORDER BY entity_id;

COMMIT;
