-- v6.99.102 — B1a chain-link extensions (generato da scripts/apply_chain_links_b1a.py).
-- Dual-write: questo SQL allinea la prod live; data/chains/*.json allinea il fresh-seed.
-- ETHICS-002/003/007: claim di successione con transition_type onesto + ethical_notes.
BEGIN;

-- 1. Iran #9: Afsharid tra Safavidi e Qajar
UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = 9 AND sequence_order >= 1;
INSERT INTO chain_links (chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes) VALUES
  (9,1038,1,1736,'CONQUEST',true,'Afsharid dynasty (1736-1796), founded by Nader Shah, a Turkmen military commander who rose from the chaos after the Safavid collapse (1722 Ghilzai Afghan sack of Isfahan). He expelled the Afghans, deposed the last Safavid puppet (Abbas III), and crowned himself shah in 1736, reunifying Iran; his campaigns reached Delhi (1739) and Central Asia.','Nader Shah''s reunification was extraordinarily violent: the 1739 sack of Delhi included a massacre of ~30,000 inhabitants and the looting of the Mughal treasury (the Peacock Throne, the Koh-i-Noor). His reign degenerated into paranoid tyranny (he blinded his own son, ordered mass executions) until his assassination in 1747, after which Iran fragmented again. The Zand dynasty (Karim Khan, 1751-1794) ruled much of central/southern Iran during this interregnum but is not yet a separate entity here — a DB-coverage gap, not a judgment of marginality.');
UPDATE chain_links SET description = 'Agha Mohammad Khan Qajar crowned Shah in 1796, completing the reunification of Iran after the Afsharid collapse (Nader Shah''s assassination, 1747) and the Zand ascendancy (1751-1794, still compressed here as the Zand are not yet a separate entity). His campaigns included the 1795 sack of Tiflis (modern Tbilisi) with massacres and enslavement of Georgian Christians.' WHERE chain_id = 9 AND entity_id = 505;

-- 2a. France #8: Premier Empire tra Royaume de France e République
UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = 8 AND sequence_order >= 3;
INSERT INTO chain_links (chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes) VALUES
  (8,1037,3,1804,'REVOLUTION',true,'First French Empire (1804-1815). After the 1789 Revolution abolished the monarchy (First Republic, 1792) and the 1799 coup of 18 Brumaire, Napoleon Bonaparte crowned himself Emperor on 2 December 1804. At its height the Empire dominated continental Europe; it collapsed after the disastrous 1812 Russian campaign and the defeat at Waterloo (1815).','This node makes explicit one of the episodes the chain otherwise compresses: the First Republic (1792-1804), First Empire (1804-1815), Bourbon Restoration (1815-1830), July Monarchy, Second Republic, and Second Empire (1852-1870) all preceded the current republican form. The Napoleonic Wars caused an estimated 3-6 million deaths; the Empire also reinstated slavery in the French colonies (1802), reversing the 1794 revolutionary abolition.');

-- 2b. France #74: Premier Empire tra Royaume de France e République
UPDATE chain_links SET sequence_order = sequence_order + 1 WHERE chain_id = 74 AND sequence_order >= 3;
INSERT INTO chain_links (chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes) VALUES
  (74,1037,3,1804,'REVOLUTION',true,'First French Empire (1804-1815). After the 1789 Revolution abolished the monarchy (First Republic, 1792) and the 1799 coup of 18 Brumaire, Napoleon Bonaparte crowned himself Emperor on 2 December 1804. At its height the Empire dominated continental Europe; it collapsed after the disastrous 1812 Russian campaign and the defeat at Waterloo (1815).','This node makes explicit one of the episodes the chain otherwise compresses: the First Republic (1792-1804), First Empire (1804-1815), Bourbon Restoration (1815-1830), July Monarchy, Second Republic, and Second Empire (1852-1870) all preceded the current republican form. The Napoleonic Wars caused an estimated 3-6 million deaths; the Empire also reinstated slavery in the French colonies (1802), reversing the 1794 revolutionary abolition.');

-- 3. Romania #35: restructure — drop #579 (German name), consolidate Wallachia on #93, append Kingdom #441
DELETE FROM chain_links WHERE chain_id = 35;
INSERT INTO chain_links (chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes) VALUES
  (35,93,0,NULL,NULL,false,'Principality of Wallachia (Țara Românească), founded by Basarab I c. 1330 after independence from the Kingdom of Hungary at the Battle of Posada (1330). It produced Vlad III Țepeș (the historical basis for Dracula). An Ottoman vassal from the 16th century while retaining internal autonomy.',NULL);
INSERT INTO chain_links (chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes) VALUES
  (35,94,1,1346,'SUCCESSION',false,'Principality of Moldavia, founded 1346 under Dragoș as a Hungarian march, achieving independence under Bogdan I (1359). Stephen the Great (1457-1504) resisted Ottoman expansion. Wallachia and Moldavia were PARALLEL principalities (not one succeeding the other), both Ottoman vassals from the 16th century; the linear order here is a model artifact — they unite at the next node.',NULL);
INSERT INTO chain_links (chain_id,entity_id,sequence_order,transition_year,transition_type,is_violent,description,ethical_notes) VALUES
  (35,441,2,1859,'UNIFICATION',false,'United Principalities of Moldavia and Wallachia, formed when Alexandru Ioan Cuza was elected prince of both Moldavia (Jan 1859) and Wallachia (Feb 1859); formal union as Romania in 1862, full independence in 1878 (Treaty of Berlin, after the violent 1877-78 Russo-Turkish war). Proclaimed the Kingdom of Romania (Regatul României) under Carol I in 1881; the monarchy lasted until 1947, when it was abolished under Soviet pressure.','Greater Romania (1918) integrated Transylvania, Bessarabia, and Bukovina, changing the ethnic balance — still contested by Hungarian historiography. Romania''s alignment with Nazi Germany (1940-44) and the Iași pogrom (1941, ~13,000 Jews killed) are part of the record; Ceaușescu''s nationalist narrative minimized them.');

-- guard: ogni catena toccata deve avere sequence_order contigui da 0
DO $$ DECLARE bad int; BEGIN
  SELECT count(*) INTO bad FROM (
    SELECT chain_id, count(*) n, max(sequence_order) mx, min(sequence_order) mn
    FROM chain_links WHERE chain_id IN (8,9,74,35) GROUP BY chain_id
  ) q WHERE mn <> 0 OR mx <> n - 1;
  IF bad > 0 THEN RAISE EXCEPTION 'sequence_order non contiguo in % catene', bad; END IF;
END $$;
COMMIT;
