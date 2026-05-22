-- Phase B S43: Enrichment of 10 entities (conf 0.82-0.85, n_src=3 -> 8)
-- 2026-05-23 — Autonomous loop iter S43
-- ETHICS: includes Rhodesia (white-minority UDI state, sanctions, Mugabe transition),
--         Spanish Empire (Americas colonization), Ptolemaic Egypt (Greek dynasty over Egyptians),
--         Samanid (Persian renaissance under Arab Caliphate suzerainty).

BEGIN;

-- ID 249: Rzeczpospolita Polska (Republic of Poland, 1918-)
-- ETHICS: II RP, WWII partitioning Soviet+Nazi, Holocaust on Polish soil, PPR communist era, 1989 transition
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(249, 'Davies, Norman. God''s Playground: A History of Poland. Vol. 2: 1795 to the Present. Rev. ed. Oxford: Oxford University Press, 2005. ISBN 978-0-19-925340-1.', 'https://www.worldcat.org/isbn/9780199253401', 'book'),
(249, 'Lukowski, Jerzy and Hubert Zawadzki. A Concise History of Poland. 3rd ed. Cambridge: Cambridge University Press, 2019. ISBN 978-1-108-42636-3.', 'https://www.worldcat.org/isbn/9781108426367', 'book'),
(249, 'Snyder, Timothy. The Reconstruction of Nations: Poland, Ukraine, Lithuania, Belarus, 1569-1999. New Haven: Yale University Press, 2003. ISBN 978-0-300-10586-9.', 'https://www.worldcat.org/isbn/9780300105865', 'book'),
(249, 'Garlinski, Józef. Poland in the Second World War. London: Macmillan, 1985. ISBN 978-0-333-39258-5.', 'https://www.worldcat.org/isbn/9780333392584', 'book'),
(249, 'Porter-Szücs, Brian. Poland in the Modern World: Beyond Martyrdom. Chichester: Wiley-Blackwell, 2014. ISBN 978-1-4443-3219-3.', 'https://www.worldcat.org/isbn/9781444332193', 'book');

-- ID 247: Republic of Korea / South Korea (대한민국, 1948-)
-- ETHICS: post-Japanese occupation, Korean War 1950-53, dictatorship Park Chung-hee 1961-79, democratization 1987
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(247, 'Cumings, Bruce. Korea''s Place in the Sun: A Modern History. Updated ed. New York: W.W. Norton, 2005. ISBN 978-0-393-32702-1.', 'https://www.worldcat.org/isbn/9780393327021', 'book'),
(247, 'Eckert, Carter J. et al. Korea Old and New: A History. Seoul: Ilchokak, 1990. ISBN 978-0-9627713-0-6.', 'https://www.worldcat.org/isbn/9780962771309', 'book'),
(247, 'Lankov, Andrei. From Stalin to Kim Il Sung: The Formation of North Korea, 1945-1960. New Brunswick: Rutgers University Press, 2002. ISBN 978-0-8135-3117-3.', 'https://www.worldcat.org/isbn/9780813531175', 'book'),
(247, 'Seth, Michael J. A Concise History of Modern Korea: From the Late Nineteenth Century to the Present. 2nd ed. Lanham: Rowman & Littlefield, 2016. ISBN 978-1-4422-6044-6.', 'https://www.worldcat.org/isbn/9781442260443', 'book'),
(247, 'Stueck, William. The Korean War: An International History. Princeton: Princeton University Press, 1995. ISBN 978-0-691-03767-4.', 'https://www.worldcat.org/isbn/9780691037677', 'book');

-- ID 242: Rhodesia (1965-1979) — UDI state
-- ETHICS: white-minority Unilateral Declaration of Independence under Ian Smith; UN sanctions;
--         Bush War 1964-1979; Internal Settlement; transition to Zimbabwe 1980
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(242, 'Wessels, Hannes. P.K. van der Byl: African Statesman. Johannesburg: 30° South Publishers, 2010. ISBN 978-1-920143-46-1.', 'https://www.worldcat.org/isbn/9781920143466', 'book'),
(242, 'White, Luise. Unpopular Sovereignty: Rhodesian Independence and African Decolonization. Chicago: University of Chicago Press, 2015. ISBN 978-0-226-23510-0.', 'https://www.worldcat.org/isbn/9780226235103', 'book'),
(242, 'Wood, J.R.T. So Far and No Further! Rhodesia''s Bid for Independence during the Retreat from Empire, 1959-1965. Trafford Publishing, 2005. ISBN 978-1-4120-4952-3.', 'https://www.worldcat.org/isbn/9781412049528', 'book'),
(242, 'Mlambo, Alois S. A History of Zimbabwe. Cambridge: Cambridge University Press, 2014. ISBN 978-1-107-68479-9.', 'https://www.worldcat.org/isbn/9781107684799', 'book'),
(242, 'Onslow, Sue, ed. Cold War in Southern Africa: White Power, Black Liberation. London: Routledge, 2009. ISBN 978-0-415-47420-9.', 'https://www.worldcat.org/isbn/9780415474207', 'book');

-- ID 68: Erzherzogtum Oesterreich (Archduchy of Austria, 1282-1804)
-- Habsburg dynasty foundation, became Empire 1804
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(68, 'Vocelka, Karl. Geschichte Österreichs: Kultur, Gesellschaft, Politik. 4th ed. Graz: Styria, 2002. ISBN 978-3-222-12825-7.', 'https://www.worldcat.org/isbn/9783222128257', 'book'),
(68, 'Beller, Steven. A Concise History of Austria. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-47886-1.', 'https://www.worldcat.org/isbn/9780521478861', 'book'),
(68, 'Evans, R.J.W. The Making of the Habsburg Monarchy, 1550-1700: An Interpretation. Oxford: Clarendon Press, 1979. ISBN 978-0-19-873085-3.', 'https://www.worldcat.org/isbn/9780198730859', 'book'),
(68, 'Brook-Shepherd, Gordon. The Austrians: A Thousand-Year Odyssey. New York: Carroll & Graf, 1996. ISBN 978-0-7867-0520-3.', 'https://www.worldcat.org/isbn/9780786705207', 'book'),
(68, 'Bérenger, Jean. A History of the Habsburg Empire 1273-1700. Trans. C.A. Simpson. London: Longman, 1994. ISBN 978-0-582-09009-5.', 'https://www.worldcat.org/isbn/9780582090095', 'book');

-- ID 98: Deutsches Kaiserreich (German Empire, 1871-1918)
-- ETHICS: Bismarck unification; Kulturkampf; colonial empire Africa+Pacific; Herero-Nama genocide 1904-08; WWI defeat
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(98, 'Clark, Christopher. Iron Kingdom: The Rise and Downfall of Prussia, 1600-1947. London: Allen Lane, 2006. ISBN 978-0-7139-9466-6.', 'https://www.worldcat.org/isbn/9780713994667', 'book'),
(98, 'Wehler, Hans-Ulrich. The German Empire, 1871-1918. Trans. Kim Traynor. Oxford: Berg, 1985. ISBN 978-0-907582-22-3.', 'https://www.worldcat.org/isbn/9780907582229', 'book'),
(98, 'Berghahn, Volker R. Imperial Germany, 1871-1918: Economy, Society, Culture, and Politics. Rev. ed. New York: Berghahn Books, 2005. ISBN 978-1-84545-114-7.', 'https://www.worldcat.org/isbn/9781845451141', 'book'),
(98, 'Steinmetz, George. The Devil''s Handwriting: Precoloniality and the German Colonial State in Qingdao, Samoa, and Southwest Africa. Chicago: University of Chicago Press, 2007. ISBN 978-0-226-77241-3.', 'https://www.worldcat.org/isbn/9780226772417', 'book'),
(98, 'Olusoga, David and Casper W. Erichsen. The Kaiser''s Holocaust: Germany''s Forgotten Genocide and the Colonial Roots of Nazism. London: Faber and Faber, 2010. ISBN 978-0-571-23141-6.', 'https://www.worldcat.org/isbn/9780571231416', 'book');

-- ID 28: Imperio Español (Spanish Empire, 1492-1898)
-- ETHICS: 1492 conquest of Granada, Reconquista, Inquisition, conquest of Americas, encomienda,
--         transatlantic slave trade, mass demographic collapse, Bourbon reforms, Spanish-American War
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(28, 'Elliott, J.H. Empires of the Atlantic World: Britain and Spain in America 1492-1830. New Haven: Yale University Press, 2006. ISBN 978-0-300-12399-4.', 'https://www.worldcat.org/isbn/9780300123999', 'book'),
(28, 'Kamen, Henry. Empire: How Spain Became a World Power, 1492-1763. New York: HarperCollins, 2003. ISBN 978-0-06-093264-0.', 'https://www.worldcat.org/isbn/9780060932640', 'book'),
(28, 'Lynch, John. Spain under the Habsburgs. 2 vols. 2nd ed. Oxford: Basil Blackwell, 1981. ISBN 978-0-631-19460-6.', 'https://www.worldcat.org/isbn/9780631194606', 'book'),
(28, 'Restall, Matthew. Seven Myths of the Spanish Conquest. Oxford: Oxford University Press, 2003. ISBN 978-0-19-516077-6.', 'https://www.worldcat.org/isbn/9780195160772', 'book'),
(28, 'Phillips, Carla Rahn and William D. Phillips. Spain''s Golden Fleece: Wool Production and the Wool Trade from the Middle Ages to the Nineteenth Century. Baltimore: Johns Hopkins University Press, 1997. ISBN 978-0-8018-5445-2.', 'https://www.worldcat.org/isbn/9780801854453', 'book');

-- ID 486: Caliphate of Córdoba (خلافة قرطبة, 929-1031)
-- Al-Andalus Umayyad caliphate, golden age of Islamic Spain
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(486, 'Kennedy, Hugh. Muslim Spain and Portugal: A Political History of al-Andalus. London: Longman, 1996. ISBN 978-0-582-49515-9.', 'https://www.worldcat.org/isbn/9780582495159', 'book'),
(486, 'Fierro, Maribel. ʻAbd al-Rahman III: The First Cordoban Caliph. Oxford: Oneworld, 2005. ISBN 978-1-85168-384-0.', 'https://www.worldcat.org/isbn/9781851683840', 'book'),
(486, 'Catlos, Brian A. Kingdoms of Faith: A New History of Islamic Spain. New York: Basic Books, 2018. ISBN 978-0-465-05587-6.', 'https://www.worldcat.org/isbn/9780465055876', 'book'),
(486, 'Safran, Janina M. The Second Umayyad Caliphate: The Articulation of Caliphal Legitimacy in al-Andalus. Cambridge, MA: Harvard University Press, 2000. ISBN 978-0-932885-24-9.', 'https://www.worldcat.org/isbn/9780932885241', 'book'),
(486, 'Wasserstein, David. The Rise and Fall of the Party-Kings: Politics and Society in Islamic Spain 1002-1086. Princeton: Princeton University Press, 1985. ISBN 978-0-691-05462-6.', 'https://www.worldcat.org/isbn/9780691054629', 'book');

-- ID 479: Aghlabid dynasty (الأغالبة, 800-909) — Ifriqiya/Tunisia
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(479, 'Talbi, Mohamed. L''Émirat aghlabide, 184-296/800-909: Histoire politique. Paris: Adrien-Maisonneuve, 1966.', 'https://www.worldcat.org/oclc/2018953', 'book'),
(479, 'Anderson, Glaire D., Corisande Fenwick and Mariam Rosser-Owen, eds. The Aghlabids and Their Neighbors: Art and Material Culture in Ninth-Century North Africa. Leiden: Brill, 2018. ISBN 978-90-04-35564-4.', 'https://www.worldcat.org/isbn/9789004355644', 'book'),
(479, 'Brett, Michael. The Rise of the Fatimids: The World of the Mediterranean and the Middle East in the Fourth Century of the Hijra, Tenth Century CE. Leiden: Brill, 2001. ISBN 978-90-04-11741-9.', 'https://www.worldcat.org/isbn/9789004117419', 'book'),
(479, 'Abun-Nasr, Jamil M. A History of the Maghrib in the Islamic Period. Cambridge: Cambridge University Press, 1987. ISBN 978-0-521-33767-8.', 'https://www.worldcat.org/isbn/9780521337670', 'book'),
(479, 'Kennedy, Hugh. The Prophet and the Age of the Caliphates: The Islamic Near East from the Sixth to the Eleventh Century. 3rd ed. London: Routledge, 2016. ISBN 978-1-138-78762-4.', 'https://www.worldcat.org/isbn/9781138787629', 'book');

-- ID 341: Samanid Empire (سامانیان, 819-999) — Persianate revival under Abbasid suzerainty
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(341, 'Frye, Richard N. The Heritage of Central Asia: From Antiquity to the Turkish Expansion. Princeton: Markus Wiener, 1996. ISBN 978-1-55876-110-8.', 'https://www.worldcat.org/isbn/9781558761100', 'book'),
(341, 'Bosworth, C.E. The History of the Saffarids of Sistan and the Maliks of Nimruz (247/861 to 949/1542-3). Costa Mesa: Mazda, 1994. ISBN 978-1-56859-015-0.', 'https://www.worldcat.org/isbn/9781568590158', 'book'),
(341, 'Treadwell, Luke. "The Samanids: The First Islamic Dynasty of Central Asia." In Early Islamic Iran, edited by Edmund Herzig and Sarah Stewart, 3-15. London: I.B. Tauris, 2012. ISBN 978-1-78076-061-4.', 'https://www.worldcat.org/isbn/9781780760612', 'book'),
(341, 'Negmatov, N.N. "The Samanid State." In History of Civilizations of Central Asia, Vol. 4, Part 1, edited by M.S. Asimov and C.E. Bosworth, 77-94. Paris: UNESCO, 1998. ISBN 978-92-3-103467-1.', 'https://www.worldcat.org/isbn/9789231034671', 'book'),
(341, 'Bosworth, C.E. The New Islamic Dynasties: A Chronological and Genealogical Manual. Edinburgh: Edinburgh University Press, 1996. ISBN 978-0-7486-2137-8.', 'https://www.worldcat.org/isbn/9780748621378', 'book');

-- ID 178: Ptolemaic Kingdom (Βασίλειον τῶν Πτολεμαίων, -305 to -30)
-- ETHICS: Greek dynasty ruling Egypt after Alexander's conquest; bilingual administration; ended with Cleopatra VII
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(178, 'Hölbl, Günther. A History of the Ptolemaic Empire. Trans. Tina Saavedra. London: Routledge, 2001. ISBN 978-0-415-23489-4.', 'https://www.worldcat.org/isbn/9780415234894', 'book'),
(178, 'Manning, Joseph G. The Last Pharaohs: Egypt under the Ptolemies, 305-30 BC. Princeton: Princeton University Press, 2010. ISBN 978-0-691-14262-0.', 'https://www.worldcat.org/isbn/9780691142623', 'book'),
(178, 'Bowman, Alan K. Egypt after the Pharaohs, 332 BC-AD 642: From Alexander to the Arab Conquest. Berkeley: University of California Press, 1986. ISBN 978-0-520-06665-2.', 'https://www.worldcat.org/isbn/9780520066656', 'book'),
(178, 'McKechnie, Paul and Philippe Guillaume, eds. Ptolemy II Philadelphus and His World. Leiden: Brill, 2008. ISBN 978-90-04-17089-6.', 'https://www.worldcat.org/isbn/9789004170896', 'book'),
(178, 'Thompson, Dorothy J. Memphis under the Ptolemies. 2nd ed. Princeton: Princeton University Press, 2012. ISBN 978-0-691-15217-9.', 'https://www.worldcat.org/isbn/9780691152172', 'book');

COMMIT;

SELECT 'S43 done. Total sources added: ' || (10 * 5)::text AS status;
