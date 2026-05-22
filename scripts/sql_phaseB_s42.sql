-- Phase B S42: Enrichment of 10 entities (conf 0.85, n_src=3 -> 8)
-- 2026-05-23 — Autonomous loop iter S42
-- ETHICS: includes colonial empire (Filipinas Spanish), authoritarian regimes (Estado Novo,
--         Pahlavi successor Islamic Republic), settler state (Rhodesia → Zimbabwe).

BEGIN;

-- ID 683: Capitania General de las Islas Filipinas (1565-1898) — Spanish colony
-- ETHICS: 333 years of Spanish colonial rule; encomienda, forced labor, religious conversion,
--         Moro Wars against Muslim south, end via 1898 Spanish-American War
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(683, 'Phelan, John Leddy. The Hispanization of the Philippines: Spanish Aims and Filipino Responses, 1565-1700. Madison: University of Wisconsin Press, 1959. ISBN 978-0-299-02214-9.', 'https://www.worldcat.org/isbn/9780299022143', 'book'),
(683, 'Newson, Linda A. Conquest and Pestilence in the Early Spanish Philippines. Honolulu: University of Hawai''i Press, 2009. ISBN 978-0-8248-3272-8.', 'https://www.worldcat.org/isbn/9780824832728', 'book'),
(683, 'Reed, Robert R. Colonial Manila: The Context of Hispanic Urbanism and Process of Morphogenesis. Berkeley: University of California Press, 1978. ISBN 978-0-520-03379-1.', 'https://www.worldcat.org/isbn/9780520033795', 'book'),
(683, 'Aguilar, Filomeno V. Migration Revolution: Philippine Nationhood and Class Relations in a Globalized Age. Singapore: NUS Press, 2014. ISBN 978-9971-69-769-1.', 'https://www.worldcat.org/isbn/9789971697693', 'book'),
(683, 'Schumacher, John N. The Propaganda Movement, 1880-1895: The Creation of a Filipino Consciousness. Rev. ed. Manila: Ateneo de Manila University Press, 1997. ISBN 978-971-550-209-2.', 'https://www.worldcat.org/isbn/9789715502092', 'book');

-- ID 268: Arab Republic of Egypt (1953-)
-- ETHICS: 1952 Free Officers coup, Nasser pan-Arabism, Sadat assassination 1981, Mubarak era,
--         2011 revolution, 2013 military coup
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(268, 'Goldschmidt, Arthur. Modern Egypt: The Formation of a Nation-State. 2nd ed. Boulder: Westview Press, 2004. ISBN 978-0-8133-4202-4.', 'https://www.worldcat.org/isbn/9780813342023', 'book'),
(268, 'Vatikiotis, P.J. The History of Modern Egypt: From Muhammad Ali to Mubarak. 4th ed. Baltimore: Johns Hopkins University Press, 1991. ISBN 978-0-8018-4214-5.', 'https://www.worldcat.org/isbn/9780801842146', 'book'),
(268, 'Cook, Steven A. The Struggle for Egypt: From Nasser to Tahrir Square. New York: Oxford University Press, 2012. ISBN 978-0-19-979526-0.', 'https://www.worldcat.org/isbn/9780199795260', 'book'),
(268, 'Beinin, Joel and Frédéric Vairel, eds. Social Movements, Mobilization, and Contestation in the Middle East and North Africa. 2nd ed. Stanford: Stanford University Press, 2013. ISBN 978-0-8047-8568-9.', 'https://www.worldcat.org/isbn/9780804785686', 'book'),
(268, 'Osman, Tarek. Egypt on the Brink: From the Rise of Nasser to the Fall of Mubarak. New Haven: Yale University Press, 2013. ISBN 978-0-300-19705-6.', 'https://www.worldcat.org/isbn/9780300197051', 'book');

-- ID 258: Republic of Finland (Suomi, 1917-)
-- ETHICS: 1917 independence from Russia, 1918 civil war, Winter War, Continuation War
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(258, 'Jussila, Osmo, Seppo Hentilä and Jukka Nevakivi. From Grand Duchy to a Modern State: A Political History of Finland since 1809. London: Hurst, 1999. ISBN 978-1-85065-528-8.', 'https://www.worldcat.org/isbn/9781850655282', 'book'),
(258, 'Meinander, Henrik. A History of Finland. London: Hurst, 2011. ISBN 978-1-85065-995-8.', 'https://www.worldcat.org/isbn/9781850659952', 'book'),
(258, 'Kirby, David. A Concise History of Finland. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-83225-0.', 'https://www.worldcat.org/isbn/9780521832250', 'book'),
(258, 'Tepora, Tuomas and Aapo Roselius, eds. The Finnish Civil War 1918: History, Memory, Legacy. Leiden: Brill, 2014. ISBN 978-90-04-24366-8.', 'https://www.worldcat.org/isbn/9789004243668', 'book'),
(258, 'Singleton, Fred. A Short History of Finland. 2nd ed. Cambridge: Cambridge University Press, 1998. ISBN 978-0-521-64727-4.', 'https://www.worldcat.org/isbn/9780521647274', 'book');

-- ID 257: Republic of Ireland (Éire, 1922-)
-- ETHICS: Irish War of Independence, partition, Civil War, Troubles in NI, neutrality WWII
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(257, 'Foster, R.F. Modern Ireland 1600-1972. London: Allen Lane, 1988. ISBN 978-0-7139-9010-1.', 'https://www.worldcat.org/isbn/9780713990102', 'book'),
(257, 'Ferriter, Diarmaid. The Transformation of Ireland 1900-2000. London: Profile Books, 2004. ISBN 978-1-86197-307-3.', 'https://www.worldcat.org/isbn/9781861973078', 'book'),
(257, 'Townshend, Charles. The Republic: The Fight for Irish Independence, 1918-1923. London: Allen Lane, 2013. ISBN 978-1-84614-461-2.', 'https://www.worldcat.org/isbn/9781846144615', 'book'),
(257, 'Bartlett, Thomas. Ireland: A History. Cambridge: Cambridge University Press, 2010. ISBN 978-1-107-42234-6.', 'https://www.worldcat.org/isbn/9781107422346', 'book'),
(257, 'Lee, J.J. Ireland 1912-1985: Politics and Society. Cambridge: Cambridge University Press, 1989. ISBN 978-0-521-26648-0.', 'https://www.worldcat.org/isbn/9780521266482', 'book');

-- ID 252: Islamic Republic of Iran (1979-)
-- ETHICS: 1979 revolution, hostage crisis, Iran-Iraq war, Green Movement 2009, sanctions
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(252, 'Axworthy, Michael. Revolutionary Iran: A History of the Islamic Republic. Rev. ed. London: Allen Lane, 2014. ISBN 978-0-241-95455-0.', 'https://www.worldcat.org/isbn/9780241954553', 'book'),
(252, 'Keddie, Nikki R. Modern Iran: Roots and Results of Revolution. Updated ed. New Haven: Yale University Press, 2006. ISBN 978-0-300-12105-1.', 'https://www.worldcat.org/isbn/9780300121056', 'book'),
(252, 'Abrahamian, Ervand. A History of Modern Iran. 2nd ed. Cambridge: Cambridge University Press, 2018. ISBN 978-1-316-62578-7.', 'https://www.worldcat.org/isbn/9781316625781', 'book'),
(252, 'Bayat, Asef. Life as Politics: How Ordinary People Change the Middle East. 2nd ed. Stanford: Stanford University Press, 2013. ISBN 978-0-8047-8327-2.', 'https://www.worldcat.org/isbn/9780804783279', 'book'),
(252, 'Takeyh, Ray. Guardians of the Revolution: Iran and the World in the Age of the Ayatollahs. New York: Oxford University Press, 2009. ISBN 978-0-19-532784-2.', 'https://www.worldcat.org/isbn/9780195327847', 'book');

-- ID 1034: Res Publica Romana (Roman Republic, -509 to -27)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(1034, 'Cornell, T.J. The Beginnings of Rome: Italy and Rome from the Bronze Age to the Punic Wars (c. 1000-264 BC). London: Routledge, 1995. ISBN 978-0-415-01596-1.', 'https://www.worldcat.org/isbn/9780415015967', 'book'),
(1034, 'Beard, Mary. SPQR: A History of Ancient Rome. London: Profile Books, 2015. ISBN 978-1-84668-381-7.', 'https://www.worldcat.org/isbn/9781846683817', 'book'),
(1034, 'Flower, Harriet I., ed. The Cambridge Companion to the Roman Republic. 2nd ed. Cambridge: Cambridge University Press, 2014. ISBN 978-1-107-66942-0.', 'https://www.worldcat.org/isbn/9781107669420', 'book'),
(1034, 'Brunt, P.A. Social Conflicts in the Roman Republic. London: Chatto & Windus, 1971. ISBN 978-0-7011-1701-7.', 'https://www.worldcat.org/isbn/9780701117016', 'book'),
(1034, 'Crawford, Michael. The Roman Republic. 2nd ed. London: Fontana Press, 1992. ISBN 978-0-00-686250-8.', 'https://www.worldcat.org/isbn/9780006862505', 'book');

-- ID 265: Estado Novo (Portugal, 1933-1974)
-- ETHICS: Salazar authoritarian regime, colonial wars Angola/Mozambique/Guinea-Bissau, PIDE secret police
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(265, 'Meneses, Filipe Ribeiro de. Salazar: A Political Biography. New York: Enigma Books, 2009. ISBN 978-1-929631-90-2.', 'https://www.worldcat.org/isbn/9781929631902', 'book'),
(265, 'Pinto, António Costa. Salazar''s Dictatorship and European Fascism: Problems of Interpretation. Boulder: Social Science Monographs, 1995. ISBN 978-0-88033-322-2.', 'https://www.worldcat.org/isbn/9780880333221', 'book'),
(265, 'Birmingham, David. A Concise History of Portugal. 3rd ed. Cambridge: Cambridge University Press, 2018. ISBN 978-1-107-49105-2.', 'https://www.worldcat.org/isbn/9781107491052', 'book'),
(265, 'Costa Pinto, António, ed. Contemporary Portugal: Politics, Society, and Culture. 2nd ed. Boulder: Social Science Monographs, 2011. ISBN 978-0-88033-686-5.', 'https://www.worldcat.org/isbn/9780880336864', 'book'),
(265, 'Wheeler, Douglas L. Republican Portugal: A Political History, 1910-1926. Madison: University of Wisconsin Press, 1978. ISBN 978-0-299-07450-6.', 'https://www.worldcat.org/isbn/9780299074500', 'book');

-- ID 253: Kingdom of Saudi Arabia (1932-)
-- ETHICS: Wahhabi-Saudi alliance, oil concession 1933, role in Middle East geopolitics
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(253, 'Vassiliev, Alexei. The History of Saudi Arabia. London: Saqi Books, 2000. ISBN 978-0-86356-399-8.', 'https://www.worldcat.org/isbn/9780863563997', 'book'),
(253, 'Al-Rasheed, Madawi. A History of Saudi Arabia. 2nd ed. Cambridge: Cambridge University Press, 2010. ISBN 978-0-521-74754-7.', 'https://www.worldcat.org/isbn/9780521747547', 'book'),
(253, 'Commins, David. The Wahhabi Mission and Saudi Arabia. London: I.B. Tauris, 2006. ISBN 978-1-84511-080-2.', 'https://www.worldcat.org/isbn/9781845110802', 'book'),
(253, 'Hertog, Steffen. Princes, Brokers, and Bureaucrats: Oil and the State in Saudi Arabia. Ithaca: Cornell University Press, 2010. ISBN 978-0-8014-4781-5.', 'https://www.worldcat.org/isbn/9780801447815', 'book'),
(253, 'Lacroix, Stéphane. Awakening Islam: The Politics of Religious Dissent in Contemporary Saudi Arabia. Cambridge, MA: Harvard University Press, 2011. ISBN 978-0-674-04964-2.', 'https://www.worldcat.org/isbn/9780674049642', 'book');

-- ID 250: Türkiye Cumhuriyeti (Republic of Turkey, 1923-)
-- ETHICS: post-Ottoman; Atatürk reforms; Armenian genocide remembrance contestation;
--         Kurdish issues; 2016 coup attempt; modern AKP era
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(250, 'Zürcher, Erik J. Turkey: A Modern History. 4th ed. London: I.B. Tauris, 2017. ISBN 978-1-78076-401-8.', 'https://www.worldcat.org/isbn/9781780764016', 'book'),
(250, 'Hanioğlu, M. Şükrü. Atatürk: An Intellectual Biography. Princeton: Princeton University Press, 2011. ISBN 978-0-691-15109-7.', 'https://www.worldcat.org/isbn/9780691151090', 'book'),
(250, 'Kasaba, Reşat, ed. The Cambridge History of Turkey, Vol. 4: Turkey in the Modern World. Cambridge: Cambridge University Press, 2008. ISBN 978-0-521-62096-3.', 'https://www.worldcat.org/isbn/9780521620963', 'book'),
(250, 'Yavuz, M. Hakan. Secularism and Muslim Democracy in Turkey. Cambridge: Cambridge University Press, 2009. ISBN 978-0-521-88878-3.', 'https://www.worldcat.org/isbn/9780521888783', 'book'),
(250, 'Findley, Carter Vaughn. Turkey, Islam, Nationalism, and Modernity: A History, 1789-2007. New Haven: Yale University Press, 2010. ISBN 978-0-300-15260-4.', 'https://www.worldcat.org/isbn/9780300152609', 'book');

-- ID 243: Republic of China (中華民國, 1912-)
-- ETHICS: 1911 Xinhai revolution end of Qing, warlord era, Nationalist govt, 1949 retreat to Taiwan
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(243, 'Fenby, Jonathan. The Penguin History of Modern China: The Fall and Rise of a Great Power, 1850 to the Present. 2nd ed. London: Penguin, 2013. ISBN 978-0-14-101975-7.', 'https://www.worldcat.org/isbn/9780141019758', 'book'),
(243, 'Westad, Odd Arne. Restless Empire: China and the World since 1750. London: Bodley Head, 2012. ISBN 978-1-84792-197-2.', 'https://www.worldcat.org/isbn/9781847921970', 'book'),
(243, 'Esherick, Joseph W. and C.X. George Wei, eds. China: How the Empire Fell. London: Routledge, 2014. ISBN 978-0-415-83101-7.', 'https://www.worldcat.org/isbn/9780415831017', 'book'),
(243, 'Taylor, Jay. The Generalissimo: Chiang Kai-shek and the Struggle for Modern China. Cambridge, MA: Harvard University Press, 2009. ISBN 978-0-674-03338-2.', 'https://www.worldcat.org/isbn/9780674033382', 'book'),
(243, 'Mitter, Rana. A Bitter Revolution: China''s Struggle with the Modern World. Oxford: Oxford University Press, 2004. ISBN 978-0-19-280605-5.', 'https://www.worldcat.org/isbn/9780192806055', 'book');

COMMIT;

SELECT 'S42 done. Total sources added: ' || (10 * 5)::text AS status;
