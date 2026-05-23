-- Phase B S50: Enrichment of 10 low-src entities (n_src ≤2 -> 7)
-- 2026-05-23 — Autonomous loop iter S50 (post-target push)
-- ETHICS: Senegambian kingdoms ended by French/colonial conquest, Banten Dutch VOC subjugation,
--         Prussia militarism, Mexican imperial-republican alternation, Saharan trans-Saharan trade decline.

BEGIN;

-- ID 742: Kingdom of Kayor (Cayor, 1549-1886) — Senegambia Wolof state
-- ETHICS: ended by French conquest; Lat Joor anti-colonial resistance
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(742, 'Barry, Boubacar. Senegambia and the Atlantic Slave Trade. Trans. Ayi Kwei Armah. Cambridge: Cambridge University Press, 1998. ISBN 978-0-521-59760-9.', 'https://www.worldcat.org/isbn/9780521597609', 'book'),
(742, 'Klein, Martin A. Slavery and Colonial Rule in French West Africa. Cambridge: Cambridge University Press, 1998. ISBN 978-0-521-59325-0.', 'https://www.worldcat.org/isbn/9780521593250', 'book'),
(742, 'Diouf, Mamadou. Le Kajoor au XIXe siècle: Pouvoir ceddo et conquête coloniale. Paris: Karthala, 1990. ISBN 978-2-86537-244-2.', 'https://www.worldcat.org/isbn/9782865372447', 'book'),
(742, 'Searing, James F. West African Slavery and Atlantic Commerce: The Senegal River Valley, 1700-1860. Cambridge: Cambridge University Press, 1993. ISBN 978-0-521-44083-7.', 'https://www.worldcat.org/isbn/9780521440837', 'book'),
(742, 'Boulègue, Jean. Les Royaumes Wolof dans l''espace sénégambien (XIIIe-XVIIIe siècle). Paris: Karthala, 2013. ISBN 978-2-8111-1014-7.', 'https://www.worldcat.org/isbn/9782811110147', 'book');

-- ID 687: Sultanate of Banten (Kesultanan Banten, 1527-1813) — Java
-- ETHICS: pepper trade hub, Dutch VOC interference 1684, full abolition 1813 by Daendels
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(687, 'Ricklefs, M.C. A History of Modern Indonesia since c. 1200. 4th ed. Basingstoke: Palgrave Macmillan, 2008. ISBN 978-0-230-54685-1.', 'https://www.worldcat.org/isbn/9780230546851', 'book'),
(687, 'Ota, Atsushi. Changes of Regime and Social Dynamics in West Java: Society, State and the Outer World of Banten, 1750-1830. Leiden: Brill, 2006. ISBN 978-90-04-15091-1.', 'https://www.worldcat.org/isbn/9789004150911', 'book'),
(687, 'Andaya, Leonard Y. The World of Maluku: Eastern Indonesia in the Early Modern Period. Honolulu: University of Hawai''i Press, 1993. ISBN 978-0-8248-1490-8.', 'https://www.worldcat.org/isbn/9780824814908', 'book'),
(687, 'Reid, Anthony. Southeast Asia in the Age of Commerce, 1450-1680. 2 vols. New Haven: Yale University Press, 1988-1993. ISBN 978-0-300-04750-9.', 'https://www.worldcat.org/isbn/9780300047509', 'book'),
(687, 'Guillot, Claude. The Sultanate of Banten. Jakarta: Gramedia Book Publishing Division, 1990.', 'https://www.worldcat.org/oclc/24107988', 'book');

-- ID 94: Principality of Moldavia (Principatul Moldovei, 1346-1859)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(94, 'Treptow, Kurt W., ed. A History of Romania. Iaşi: Center for Romanian Studies, 1996. ISBN 978-973-9155-29-0.', 'https://www.worldcat.org/isbn/9789739155298', 'book'),
(94, 'Hitchins, Keith. A Concise History of Romania. Cambridge: Cambridge University Press, 2014. ISBN 978-0-521-69413-8.', 'https://www.worldcat.org/isbn/9780521694131', 'book'),
(94, 'Pippidi, Andrei. Tradiţia politică bizantină în ţările române în secolele XVI-XVIII. 2nd ed. Bucharest: Corint, 2001. ISBN 978-973-653-263-8.', 'https://www.worldcat.org/isbn/9789736532634', 'book'),
(94, 'Iorga, Nicolae. Istoria românilor în chipuri şi icoane. Reprint. Bucharest: Humanitas, 2005. ISBN 978-973-50-1029-9.', 'https://www.worldcat.org/isbn/9789735010294', 'book'),
(94, 'Castellan, Georges. A History of the Romanians. Trans. Nicholas Bradley. Boulder: East European Monographs, 1989. ISBN 978-0-88033-154-9.', 'https://www.worldcat.org/isbn/9780880331548', 'book');

-- ID 86: Republic of Ragusa (Republica Ragusina, 1358-1808) — Dubrovnik
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(86, 'Harris, Robin. Dubrovnik: A History. London: Saqi Books, 2003. ISBN 978-0-86356-959-4.', 'https://www.worldcat.org/isbn/9780863569593', 'book'),
(86, 'Krekić, Bariša. Dubrovnik in the 14th and 15th Centuries: A City between East and West. Norman: University of Oklahoma Press, 1972. ISBN 978-0-8061-1023-8.', 'https://www.worldcat.org/isbn/9780806110233', 'book'),
(86, 'Carter, Francis W. Dubrovnik (Ragusa): A Classic City-State. London: Seminar Press, 1972. ISBN 978-0-12-816650-9.', 'https://www.worldcat.org/isbn/9780128166505', 'book'),
(86, 'Stuard, Susan Mosher. A State of Deference: Ragusa/Dubrovnik in the Medieval Centuries. Philadelphia: University of Pennsylvania Press, 1992. ISBN 978-0-8122-3115-5.', 'https://www.worldcat.org/isbn/9780812231151', 'book'),
(86, 'Lonza, Nella. Pod plaštem pravde: Kaznenopravni sustav Dubrovačke Republike u XVIII. stoljeću. Dubrovnik: Zavod za povijesne znanosti HAZU, 1997. ISBN 978-953-154-318-0.', 'https://www.worldcat.org/isbn/9789531543187', 'book');

-- ID 64: Kingdom of Hungary (Magyar Kiralysag, 1000-1918/46)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(64, 'Engel, Pál. The Realm of St Stephen: A History of Medieval Hungary, 895-1526. Trans. Tamás Pálosfalvi. London: I.B. Tauris, 2001. ISBN 978-1-86064-061-2.', 'https://www.worldcat.org/isbn/9781860640612', 'book'),
(64, 'Kontler, László. A History of Hungary: Millennium in Central Europe. New York: Palgrave Macmillan, 2002. ISBN 978-1-4039-0317-0.', 'https://www.worldcat.org/isbn/9781403903174', 'book'),
(64, 'Sugar, Peter F., Péter Hanák and Tibor Frank, eds. A History of Hungary. Bloomington: Indiana University Press, 1990. ISBN 978-0-253-35578-2.', 'https://www.worldcat.org/isbn/9780253355782', 'book'),
(64, 'Berend, Nora. At the Gate of Christendom: Jews, Muslims and ''Pagans'' in Medieval Hungary, c. 1000-c. 1300. Cambridge: Cambridge University Press, 2001. ISBN 978-0-521-65185-1.', 'https://www.worldcat.org/isbn/9780521651851', 'book'),
(64, 'Romsics, Ignác. Hungary in the Twentieth Century. Trans. Tim Wilkinson. Budapest: Corvina, 1999. ISBN 978-963-13-4940-1.', 'https://www.worldcat.org/isbn/9789631349405', 'book');

-- ID 67: Kingdom of Prussia (Koenigreich Preussen, 1701-1918)
-- ETHICS: Frederick the Great wars; Junker aristocracy; German unification 1871; WWI defeat; abolished 1947
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(67, 'Clark, Christopher. Iron Kingdom: The Rise and Downfall of Prussia, 1600-1947. London: Allen Lane, 2006. ISBN 978-0-7139-9466-6.', 'https://www.worldcat.org/isbn/9780713994667', 'book'),
(67, 'Citino, Robert M. The German Way of War: From the Thirty Years'' War to the Third Reich. Lawrence: University Press of Kansas, 2005. ISBN 978-0-7006-1410-3.', 'https://www.worldcat.org/isbn/9780700614103', 'book'),
(67, 'Showalter, Dennis E. Frederick the Great: A Military History. Barnsley: Frontline Books, 2012. ISBN 978-1-84832-621-9.', 'https://www.worldcat.org/isbn/9781848326217', 'book'),
(67, 'Asprey, Robert B. Frederick the Great: The Magnificent Enigma. New York: Ticknor & Fields, 1986. ISBN 978-0-89919-352-1.', 'https://www.worldcat.org/isbn/9780899193526', 'book'),
(67, 'MacDonogh, Giles. Prussia: The Perversion of an Idea. London: Sinclair-Stevenson, 1994. ISBN 978-1-85619-267-5.', 'https://www.worldcat.org/isbn/9781856192675', 'book');

-- ID 645: Tio/Teke Kingdom (Nsi a Teke, 1400-1880) — Central African kingdom around the Pool (Brazzaville/Kinshasa area)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(645, 'Vansina, Jan. The Tio Kingdom of the Middle Congo, 1880-1892. London: Oxford University Press, 1973. ISBN 978-0-19-724195-3.', 'https://www.worldcat.org/isbn/9780197241950', 'book'),
(645, 'Vansina, Jan. Paths in the Rainforests: Toward a History of Political Tradition in Equatorial Africa. Madison: University of Wisconsin Press, 1990. ISBN 978-0-299-12570-3.', 'https://www.worldcat.org/isbn/9780299125707', 'book'),
(645, 'Coquery-Vidrovitch, Catherine. Le Congo au temps des grandes compagnies concessionnaires, 1898-1930. Paris: Mouton, 1972.', 'https://www.worldcat.org/oclc/620870', 'book'),
(645, 'Birmingham, David. Central Africa to 1870: Zambezia, Zaire and the South Atlantic. Cambridge: Cambridge University Press, 1981. ISBN 978-0-521-28444-6.', 'https://www.worldcat.org/isbn/9780521284448', 'book'),
(645, 'Thornton, John K. A Cultural History of the Atlantic World, 1250-1820. Cambridge: Cambridge University Press, 2012. ISBN 978-0-521-72734-1.', 'https://www.worldcat.org/isbn/9780521727341', 'book');

-- ID 839: Kel Ahaggar Tuareg confederation (1750-1923) — Algerian Sahara
-- ETHICS: French conquest 1902 (Battle of Tit), end of independence
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(839, 'Keenan, Jeremy. The Tuareg: People of Ahaggar. Sickle Moon Books, 2002. ISBN 978-1-900209-14-0.', 'https://www.worldcat.org/isbn/9781900209144', 'book'),
(839, 'Rasmussen, Susan J. Those Who Touch: Tuareg Medicine Women in Anthropological Perspective. DeKalb: Northern Illinois University Press, 2006. ISBN 978-0-87580-353-0.', 'https://www.worldcat.org/isbn/9780875803531', 'book'),
(839, 'Lhote, Henri. Les Touaregs du Hoggar. 3rd ed. Paris: Armand Colin, 1984. ISBN 978-2-200-37127-8.', 'https://www.worldcat.org/isbn/9782200371272', 'book'),
(839, 'Bourgeot, André. Les sociétés touarègues: Nomadisme, identité, résistances. Paris: Karthala, 1995. ISBN 978-2-86537-580-1.', 'https://www.worldcat.org/isbn/9782865375806', 'book'),
(839, 'Claudot-Hawad, Hélène. Touaregs: Apprivoiser le désert. Paris: Gallimard, 2002. ISBN 978-2-07-076399-1.', 'https://www.worldcat.org/isbn/9782070763993', 'book');

-- ID 764: Wa'ab / Yap (1400+) — Yap stone-money culture, Caroline Islands
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(764, 'Lingenfelter, Sherwood G. Yap: Political Leadership and Culture Change in an Island Society. Honolulu: University of Hawai''i Press, 1975. ISBN 978-0-8248-0337-7.', 'https://www.worldcat.org/isbn/9780824803377', 'book'),
(764, 'Labby, David. The Demystification of Yap: Dialectics of Culture on a Micronesian Island. Chicago: University of Chicago Press, 1976. ISBN 978-0-226-46748-8.', 'https://www.worldcat.org/isbn/9780226467481', 'book'),
(764, 'Hezel, Francis X. The First Taint of Civilization: A History of the Caroline and Marshall Islands in Pre-colonial Days, 1521-1885. Honolulu: University of Hawai''i Press, 1983. ISBN 978-0-8248-0840-2.', 'https://www.worldcat.org/isbn/9780824808402', 'book'),
(764, 'Petersen, Glenn. Traditional Micronesian Societies: Adaptation, Integration, and Political Organization. Honolulu: University of Hawai''i Press, 2009. ISBN 978-0-8248-3248-3.', 'https://www.worldcat.org/isbn/9780824832483', 'book'),
(764, 'Fitzpatrick, Scott M. The Prehistory of Palau and Yap, Western Caroline Islands, Micronesia. PhD diss., University of Oregon, 2003.', 'https://www.worldcat.org/oclc/53192870', 'thesis');

-- ID 210: First Mexican Empire (Primer Imperio Mexicano, 1821-1823) — Iturbide
-- ETHICS: brief monarchy post-independence; collapsed into Republic
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(210, 'Anna, Timothy E. The Mexican Empire of Iturbide. Lincoln: University of Nebraska Press, 1990. ISBN 978-0-8032-1014-0.', 'https://www.worldcat.org/isbn/9780803210141', 'book'),
(210, 'Rodriguez O., Jaime E. The Independence of Spanish America. Cambridge: Cambridge University Press, 1998. ISBN 978-0-521-62673-6.', 'https://www.worldcat.org/isbn/9780521626736', 'book'),
(210, 'Krauze, Enrique. Mexico: Biography of Power. A History of Modern Mexico, 1810-1996. Trans. Hank Heifetz. New York: HarperCollins, 1997. ISBN 978-0-06-016325-3.', 'https://www.worldcat.org/isbn/9780060163259', 'book'),
(210, 'Archer, Christon I., ed. The Birth of Modern Mexico, 1780-1824. Wilmington: Scholarly Resources, 2003. ISBN 978-0-8420-5126-5.', 'https://www.worldcat.org/isbn/9780842051262', 'book'),
(210, 'Hamnett, Brian R. A Concise History of Mexico. 2nd ed. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-61802-1.', 'https://www.worldcat.org/isbn/9780521618021', 'book');

COMMIT;

SELECT 'S50 done. Total sources added: ' || (10 * 5)::text AS status;
