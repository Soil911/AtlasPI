-- Phase B S41: Enrichment of 10 entities (conf 0.85, n_src=3 -> 8)
-- 2026-05-22 — Autonomous loop iter S41
-- ETHICS: includes colonial states (Virreinato del Peru, Filipinas, Transjordan)
--         and decolonization republics (Pakistan, Bangladesh, Cambodia, Iran).
--         Sources include both metropolitan and indigenous perspectives where available.

BEGIN;

-- ID 850: Islamic Republic of Pakistan (1947-)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(850, 'Talbot, Ian. Pakistan: A Modern History. New York: St. Martin''s Press, 2009. ISBN 978-0-230-62304-0.', 'https://www.worldcat.org/isbn/9780230623040', 'book'),
(850, 'Jalal, Ayesha. The Struggle for Pakistan: A Muslim Homeland and Global Politics. Cambridge, MA: Harvard University Press, 2014. ISBN 978-0-674-05289-5.', 'https://www.worldcat.org/isbn/9780674052895', 'book'),
(850, 'Khan, Yasmin. The Great Partition: The Making of India and Pakistan. New Haven: Yale University Press, 2017. ISBN 978-0-300-23036-4.', 'https://www.worldcat.org/isbn/9780300230364', 'book'),
(850, 'Cohen, Stephen P. The Idea of Pakistan. Washington, DC: Brookings Institution Press, 2004. ISBN 978-0-8157-1502-3.', 'https://www.worldcat.org/isbn/9780815715023', 'book'),
(850, 'Bose, Sugata and Ayesha Jalal. Modern South Asia: History, Culture, Political Economy. 4th ed. New York: Routledge, 2017. ISBN 978-1-138-24368-0.', 'https://www.worldcat.org/isbn/9781138243680', 'book');

-- ID 390: Khalji sultanate of Delhi (1290-1320)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(390, 'Jackson, Peter. The Delhi Sultanate: A Political and Military History. Cambridge: Cambridge University Press, 1999. ISBN 978-0-521-54329-3.', 'https://www.worldcat.org/isbn/9780521543293', 'book'),
(390, 'Kumar, Sunil. The Emergence of the Delhi Sultanate, 1192-1286. Delhi: Permanent Black, 2007. ISBN 978-81-7824-159-2.', 'https://www.worldcat.org/isbn/9788178241592', 'book'),
(390, 'Eaton, Richard M. India in the Persianate Age, 1000-1765. Berkeley: University of California Press, 2019. ISBN 978-0-520-32505-3.', 'https://www.worldcat.org/isbn/9780520325053', 'book'),
(390, 'Lal, Kishori Saran. History of the Khaljis, A.D. 1290-1320. Rev. ed. New Delhi: Munshiram Manoharlal, 1980. ISBN 978-0-83646-027-4.', 'https://www.worldcat.org/isbn/9780836460274', 'book'),
(390, 'Asher, Catherine B. and Cynthia Talbot. India before Europe. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-80904-7.', 'https://www.worldcat.org/isbn/9780521809047', 'book');

-- ID 928: Cholōllān / Cholula (-500 to 1519 CE)
-- ETHICS: pre-Hispanic city-state, includes 1519 Cholula massacre by Cortés
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(928, 'McCafferty, Geoffrey G. The Ceramics of Postclassic Cholula, Mexico. Los Angeles: Cotsen Institute of Archaeology, UCLA, 2001. ISBN 978-1-931745-04-0.', 'https://www.worldcat.org/isbn/9781931745040', 'book'),
(928, 'Plunket, Patricia and Gabriela Uruñuela. "Mountain of Sustenance, Mountain of Destruction: The Prehispanic Experience with Popocatépetl Volcano." Journal of Volcanology and Geothermal Research 170 (2008): 111-120.', 'https://doi.org/10.1016/j.jvolgeores.2007.09.005', 'journal_article'),
(928, 'Carrasco, Davíd. Quetzalcoatl and the Irony of Empire: Myths and Prophecies in the Aztec Tradition. Rev. ed. Boulder: University Press of Colorado, 2000. ISBN 978-0-87081-558-1.', 'https://www.worldcat.org/isbn/9780870815581', 'book'),
(928, 'Solís, Felipe et al. Cholula: La gran pirámide. México: Instituto Nacional de Antropología e Historia, 2006. ISBN 978-968-03-0205-2.', 'https://www.worldcat.org/isbn/9789680302052', 'book'),
(928, 'Restall, Matthew. When Montezuma Met Cortés: The True Story of the Meeting That Changed History. New York: Ecco, 2018. ISBN 978-0-06-242726-7.', 'https://www.worldcat.org/isbn/9780062427267', 'book');

-- ID 255: Republic of Iraq (1932-)
-- ETHICS: post-Mandate Iraq, includes Ba'athist regime, 2003 invasion, ongoing reconstruction
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(255, 'Tripp, Charles. A History of Iraq. 3rd ed. Cambridge: Cambridge University Press, 2007. ISBN 978-0-521-87823-4.', 'https://www.worldcat.org/isbn/9780521878234', 'book'),
(255, 'Marr, Phebe and Ibrahim Al-Marashi. The Modern History of Iraq. 4th ed. Boulder: Westview Press, 2017. ISBN 978-0-8133-5006-7.', 'https://www.worldcat.org/isbn/9780813350067', 'book'),
(255, 'Dodge, Toby. Inventing Iraq: The Failure of Nation Building and a History Denied. New York: Columbia University Press, 2003. ISBN 978-0-231-13166-0.', 'https://www.worldcat.org/isbn/9780231131660', 'book'),
(255, 'Sluglett, Peter. Britain in Iraq: Contriving King and Country. New York: Columbia University Press, 2007. ISBN 978-0-231-14201-7.', 'https://www.worldcat.org/isbn/9780231142017', 'book'),
(255, 'Bashkin, Orit. The Other Iraq: Pluralism and Culture in Hashemite Iraq. Stanford: Stanford University Press, 2009. ISBN 978-0-8047-6065-5.', 'https://www.worldcat.org/isbn/9780804760655', 'book');

-- ID 236: People's Republic of Bangladesh (1971-)
-- ETHICS: 1971 Liberation War / Bangladesh genocide by Pakistani military (3 million dead by Bangladesh govt estimates)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(236, 'Bose, Sarmila. Dead Reckoning: Memories of the 1971 Bangladesh War. New York: Columbia University Press, 2011. ISBN 978-0-231-70164-8.', 'https://www.worldcat.org/isbn/9780231701648', 'book'),
(236, 'Raghavan, Srinath. 1971: A Global History of the Creation of Bangladesh. Cambridge, MA: Harvard University Press, 2013. ISBN 978-0-674-72864-6.', 'https://www.worldcat.org/isbn/9780674728646', 'book'),
(236, 'Schendel, Willem van. A History of Bangladesh. 2nd ed. Cambridge: Cambridge University Press, 2020. ISBN 978-1-108-46774-8.', 'https://www.worldcat.org/isbn/9781108467748', 'book'),
(236, 'Ludden, David. "The Politics of Independence in Bangladesh." Economic and Political Weekly 46, no. 35 (2011): 79-85.', 'https://www.jstor.org/stable/23017921', 'journal_article'),
(236, 'Riaz, Ali. Bangladesh: A Political History since Independence. London: I.B. Tauris, 2016. ISBN 978-1-78453-318-7.', 'https://www.worldcat.org/isbn/9781784533187', 'book');

-- ID 501: Emirate of Transjordan (1921-1946) — British Mandate
-- ETHICS: British-imposed political construct carved from Mandate Palestine; Hashemite import from Hejaz
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(501, 'Wilson, Mary C. King Abdullah, Britain and the Making of Jordan. Cambridge: Cambridge University Press, 1987. ISBN 978-0-521-32421-0.', 'https://www.worldcat.org/isbn/9780521324210', 'book'),
(501, 'Salibi, Kamal. The Modern History of Jordan. London: I.B. Tauris, 1993. ISBN 978-1-86064-331-6.', 'https://www.worldcat.org/isbn/9781860643316', 'book'),
(501, 'Alon, Yoav. The Making of Jordan: Tribes, Colonialism and the Modern State. London: I.B. Tauris, 2007. ISBN 978-1-84511-138-0.', 'https://www.worldcat.org/isbn/9781845111380', 'book'),
(501, 'Robins, Philip. A History of Jordan. Cambridge: Cambridge University Press, 2004. ISBN 978-0-521-59895-8.', 'https://www.worldcat.org/isbn/9780521598958', 'book'),
(501, 'Massad, Joseph A. Colonial Effects: The Making of National Identity in Jordan. New York: Columbia University Press, 2001. ISBN 978-0-231-12323-8.', 'https://www.worldcat.org/isbn/9780231123238', 'book');

-- ID 256: Kingdom of Cambodia (1953-)
-- ETHICS: independence 1953, Khmer Rouge genocide 1975-1979 (1.7M dead), modern restoration
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(256, 'Chandler, David P. A History of Cambodia. 4th ed. Boulder: Westview Press, 2007. ISBN 978-0-8133-4363-2.', 'https://www.worldcat.org/isbn/9780813343631', 'book'),
(256, 'Kiernan, Ben. The Pol Pot Regime: Race, Power, and Genocide in Cambodia under the Khmer Rouge, 1975-79. 3rd ed. New Haven: Yale University Press, 2008. ISBN 978-0-300-14434-0.', 'https://www.worldcat.org/isbn/9780300144345', 'book'),
(256, 'Tully, John. A Short History of Cambodia: From Empire to Survival. Crows Nest, NSW: Allen & Unwin, 2005. ISBN 978-1-74114-763-9.', 'https://www.worldcat.org/isbn/9781741147636', 'book'),
(256, 'Strangio, Sebastian. Hun Sen''s Cambodia. New Haven: Yale University Press, 2014. ISBN 978-0-300-19072-9.', 'https://www.worldcat.org/isbn/9780300190724', 'book'),
(256, 'Edwards, Penny. Cambodge: The Cultivation of a Nation, 1860-1945. Honolulu: University of Hawai''i Press, 2007. ISBN 978-0-8248-2923-0.', 'https://www.worldcat.org/isbn/9780824829230', 'book');

-- ID 251: Imperial State of Iran (1925-1979) — Pahlavi dynasty
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(251, 'Abrahamian, Ervand. A History of Modern Iran. 2nd ed. Cambridge: Cambridge University Press, 2018. ISBN 978-1-316-62578-7.', 'https://www.worldcat.org/isbn/9781316625781', 'book'),
(251, 'Katouzian, Homa. The Persians: Ancient, Mediaeval and Modern Iran. New Haven: Yale University Press, 2009. ISBN 978-0-300-12118-1.', 'https://www.worldcat.org/isbn/9780300121186', 'book'),
(251, 'Ansari, Ali M. Modern Iran since 1797: Reform and Revolution. 3rd ed. London: Routledge, 2019. ISBN 978-1-138-89719-4.', 'https://www.worldcat.org/isbn/9781138897199', 'book'),
(251, 'Cronin, Stephanie, ed. The Making of Modern Iran: State and Society under Riza Shah, 1921-1941. London: Routledge, 2003. ISBN 978-0-415-30284-7.', 'https://www.worldcat.org/isbn/9780415302845', 'book'),
(251, 'Milani, Abbas. The Shah. New York: Palgrave Macmillan, 2011. ISBN 978-0-230-11562-9.', 'https://www.worldcat.org/isbn/9780230115620', 'book');

-- ID 736: Mahdiyya / Mahdist State (Sudan, 1885-1898)
-- ETHICS: anti-colonial Islamic revolt against Ottoman-Egyptian and British rule; ended by Battle of Omdurman 1898
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(736, 'Holt, P.M. The Mahdist State in the Sudan, 1881-1898: A Study of Its Origins, Development and Overthrow. 2nd ed. Oxford: Clarendon Press, 1970. ISBN 978-0-19-821648-1.', 'https://www.worldcat.org/isbn/9780198216483', 'book'),
(736, 'Searcy, Kim. The Formation of the Sudanese Mahdist State: Ceremony and Symbols of Authority, 1882-1898. Leiden: Brill, 2011. ISBN 978-90-04-18599-9.', 'https://www.worldcat.org/isbn/9789004185999', 'book'),
(736, 'Daly, M.W. Empire on the Nile: The Anglo-Egyptian Sudan, 1898-1934. Cambridge: Cambridge University Press, 1986. ISBN 978-0-521-32664-1.', 'https://www.worldcat.org/isbn/9780521326643', 'book'),
(736, 'Voll, John O. "The Sudanese Mahdi: Frontier Fundamentalist." International Journal of Middle East Studies 10, no. 2 (1979): 145-166.', 'https://doi.org/10.1017/S0020743800034796', 'journal_article'),
(736, 'Warburg, Gabriel. Islam, Sectarianism and Politics in Sudan since the Mahdiyya. London: Hurst, 2003. ISBN 978-1-85065-588-2.', 'https://www.worldcat.org/isbn/9781850655886', 'book');

-- ID 709: Viceroyalty of Peru (1542-1824)
-- ETHICS: Spanish colonial regime over Andean indigenous peoples; mita labor, encomienda, mass demographic collapse
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(709, 'Andrien, Kenneth J. Andean Worlds: Indigenous History, Culture, and Consciousness under Spanish Rule, 1532-1825. Albuquerque: University of New Mexico Press, 2001. ISBN 978-0-8263-2358-0.', 'https://www.worldcat.org/isbn/9780826323583', 'book'),
(709, 'Lockhart, James. Spanish Peru, 1532-1560: A Social History. 2nd ed. Madison: University of Wisconsin Press, 1994. ISBN 978-0-299-14180-2.', 'https://www.worldcat.org/isbn/9780299141806', 'book'),
(709, 'Cahill, David. From Rebellion to Independence in the Andes: Soundings from Southern Peru, 1750-1830. Amsterdam: Aksant, 2002. ISBN 978-90-5260-027-1.', 'https://www.worldcat.org/isbn/9789052600277', 'book'),
(709, 'Mumford, Jeremy Ravi. Vertical Empire: The General Resettlement of Indians in the Colonial Andes. Durham, NC: Duke University Press, 2012. ISBN 978-0-8223-5310-2.', 'https://www.worldcat.org/isbn/9780822353102', 'book'),
(709, 'Klarén, Peter Flindell. Peru: Society and Nationhood in the Andes. New York: Oxford University Press, 2000. ISBN 978-0-19-506928-3.', 'https://www.worldcat.org/isbn/9780195069280', 'book');

COMMIT;

SELECT 'S41 done. Total sources added: ' || (10 * 5)::text AS status;
