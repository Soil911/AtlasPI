-- Phase B S45: Enrichment of 10 low-src entities (n_src ≤2 -> 7)
-- 2026-05-23 — Autonomous loop iter S45
-- ETHICS: includes British Empire (5 centuries of colonization), Beothuk (extinction by colonizers),
--         Chimor (Inca conquest), Pawnee/Sahnish (forced relocation), Afsharid (military empire).

BEGIN;

-- ID 438: Empire of Trebizond (Αυτοκρατορία της Τραπεζούντας, 1204-1461)
-- Komnenoi dynasty Black Sea successor state to Byzantium; conquered by Mehmed II
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(438, 'Bryer, Anthony and David Winfield. The Byzantine Monuments and Topography of the Pontos. 2 vols. Washington, DC: Dumbarton Oaks, 1985. ISBN 978-0-88402-122-3.', 'https://www.worldcat.org/isbn/9780884021223', 'book'),
(438, 'Eastmond, Antony. Art and Identity in Thirteenth-Century Byzantium: Hagia Sophia and the Empire of Trebizond. Aldershot: Ashgate, 2004. ISBN 978-0-7546-3575-6.', 'https://www.worldcat.org/isbn/9780754635758', 'book'),
(438, 'Karpov, Sergei P. L''impero di Trebisonda, Venezia, Genova e Roma, 1204-1461: Rapporti politici, diplomatici e commerciali. Rome: Il Veltro, 1986.', 'https://www.worldcat.org/oclc/14586432', 'book'),
(438, 'Miller, William. Trebizond: The Last Greek Empire of the Byzantine Era, 1204-1461. Reprint. Chicago: Argonaut, 1969. ISBN 978-0-8244-0107-1.', 'https://www.worldcat.org/isbn/9780824401078', 'book'),
(438, 'Shukurov, Rustam. The Byzantine Turks, 1204-1461. Leiden: Brill, 2016. ISBN 978-90-04-30512-0.', 'https://www.worldcat.org/isbn/9789004305120', 'book');

-- ID 62: Polish-Lithuanian Commonwealth (Rzeczpospolita Obojga Narodow, 1569-1795)
-- Union of Lublin; szlachta democracy; elective monarchy; eventually partitioned
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(62, 'Stone, Daniel. The Polish-Lithuanian State, 1386-1795. Seattle: University of Washington Press, 2001. ISBN 978-0-295-98093-5.', 'https://www.worldcat.org/isbn/9780295980935', 'book'),
(62, 'Lukowski, Jerzy. The Partitions of Poland 1772, 1793, 1795. London: Longman, 1999. ISBN 978-0-582-29274-1.', 'https://www.worldcat.org/isbn/9780582292741', 'book'),
(62, 'Frost, Robert I. The Oxford History of Poland-Lithuania, Volume I: The Making of the Polish-Lithuanian Union, 1385-1569. Oxford: Oxford University Press, 2015. ISBN 978-0-19-820869-1.', 'https://www.worldcat.org/isbn/9780198208693', 'book'),
(62, 'Davies, Norman. God''s Playground: A History of Poland. Vol. 1: The Origins to 1795. Rev. ed. Oxford: Oxford University Press, 2005. ISBN 978-0-19-925339-5.', 'https://www.worldcat.org/isbn/9780199253395', 'book'),
(62, 'Butterwick, Richard, ed. The Polish-Lithuanian Monarchy in European Context, c. 1500-1795. New York: Palgrave Macmillan, 2001. ISBN 978-0-333-77382-6.', 'https://www.worldcat.org/isbn/9780333773826', 'book');

-- ID 29: British Empire (1583-1997)
-- ETHICS: at its peak, 25% of land surface and 23% of population; mass slavery, settler colonialism,
--         genocide and famine (Bengal, Ireland), partition of India/Palestine, "scramble for Africa"
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(29, 'Darwin, John. The Empire Project: The Rise and Fall of the British World-System, 1830-1970. Cambridge: Cambridge University Press, 2009. ISBN 978-0-521-30208-0.', 'https://www.worldcat.org/isbn/9780521302081', 'book'),
(29, 'Marshall, P.J., ed. The Oxford History of the British Empire. 5 vols. Oxford: Oxford University Press, 1998-1999. ISBN 978-0-19-924676-2.', 'https://www.worldcat.org/isbn/9780199246762', 'book'),
(29, 'Cain, P.J. and A.G. Hopkins. British Imperialism, 1688-2015. 3rd ed. London: Routledge, 2016. ISBN 978-1-138-67801-3.', 'https://www.worldcat.org/isbn/9781138678019', 'book'),
(29, 'Hyam, Ronald. Britain''s Imperial Century, 1815-1914: A Study of Empire and Expansion. 3rd ed. Basingstoke: Palgrave Macmillan, 2002. ISBN 978-0-333-99311-7.', 'https://www.worldcat.org/isbn/9780333993118', 'book'),
(29, 'Tharoor, Shashi. Inglorious Empire: What the British Did to India. London: Hurst, 2017. ISBN 978-1-84904-808-8.', 'https://www.worldcat.org/isbn/9781849048088', 'book');

-- ID 440: Galicia-Volhynia (Галицько-Волинське князівство, 1199-1349)
-- East Slavic principality, successor to Kyivan Rus; ended absorbed by Poland-Lithuania
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(440, 'Magocsi, Paul Robert. A History of Ukraine: The Land and Its Peoples. 2nd ed. Toronto: University of Toronto Press, 2010. ISBN 978-1-4426-1021-7.', 'https://www.worldcat.org/isbn/9781442610217', 'book'),
(440, 'Subtelny, Orest. Ukraine: A History. 4th ed. Toronto: University of Toronto Press, 2009. ISBN 978-1-4426-4016-0.', 'https://www.worldcat.org/isbn/9781442640160', 'book'),
(440, 'Halperin, Charles J. Russia and the Golden Horde: The Mongol Impact on Medieval Russian History. Bloomington: Indiana University Press, 1985. ISBN 978-0-253-35033-6.', 'https://www.worldcat.org/isbn/9780253350336', 'book'),
(440, 'Plokhy, Serhii. The Origins of the Slavic Nations: Premodern Identities in Russia, Ukraine, and Belarus. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-86403-9.', 'https://www.worldcat.org/isbn/9780521864039', 'book'),
(440, 'Martin, Janet. Medieval Russia 980-1584. 2nd ed. Cambridge: Cambridge University Press, 2007. ISBN 978-0-521-67636-6.', 'https://www.worldcat.org/isbn/9780521676366', 'book');

-- ID 1039: Old Babylonian Empire (𒆍𒀭𒊏𒆠 Kar-anki, -1894 to -1595) — Hammurabi era
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(1039, 'Van De Mieroop, Marc. King Hammurabi of Babylon: A Biography. Oxford: Blackwell, 2005. ISBN 978-1-4051-2660-1.', 'https://www.worldcat.org/isbn/9781405126601', 'book'),
(1039, 'Charpin, Dominique. Writing, Law, and Kingship in Old Babylonian Mesopotamia. Trans. Jane Marie Todd. Chicago: University of Chicago Press, 2010. ISBN 978-0-226-10158-0.', 'https://www.worldcat.org/isbn/9780226101583', 'book'),
(1039, 'Roth, Martha T. Law Collections from Mesopotamia and Asia Minor. 2nd ed. Atlanta: Scholars Press, 1997. ISBN 978-0-7885-0378-6.', 'https://www.worldcat.org/isbn/9780788503788', 'book'),
(1039, 'Stol, Marten. Letters from Yale Forerunners of the Hammurabi Letters. Leiden: Brill, 1981. ISBN 978-90-04-06329-7.', 'https://www.worldcat.org/isbn/9789004063297', 'book'),
(1039, 'Van De Mieroop, Marc. A History of the Ancient Near East, ca. 3000-323 BC. 3rd ed. Chichester: Wiley-Blackwell, 2016. ISBN 978-1-118-71815-5.', 'https://www.worldcat.org/isbn/9781118718155', 'book');

-- ID 787: Beothuk (1000-1829) — Newfoundland indigenous nation
-- ETHICS: extinct as a culturally distinct people by 1829 due to colonization, conflict, disease, starvation
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(787, 'Marshall, Ingeborg. A History and Ethnography of the Beothuk. Montreal: McGill-Queen''s University Press, 1996. ISBN 978-0-7735-1390-7.', 'https://www.worldcat.org/isbn/9780773513907', 'book'),
(787, 'Holly, Donald H., Jr. History in the Making: The Archaeology of the Eastern Subarctic. Lanham: AltaMira Press, 2013. ISBN 978-0-7591-1271-3.', 'https://www.worldcat.org/isbn/9780759112711', 'book'),
(787, 'Pastore, Ralph T. "The Collapse of the Beothuk World." Acadiensis 19, no. 1 (1989): 52-71.', 'https://www.jstor.org/stable/30303178', 'journal_article'),
(787, 'Marshall, Ingeborg. The Beothuk. Newfoundland Historical Society Series 6. St. John''s: Newfoundland Historical Society, 1998. ISBN 978-0-919121-44-0.', 'https://www.worldcat.org/isbn/9780919121447', 'book'),
(787, 'Howley, James P. The Beothucks or Red Indians: The Aboriginal Inhabitants of Newfoundland. Reprint of 1915 ed. Toronto: Coles Publishing, 1974. ISBN 978-0-7740-0468-2.', 'https://www.worldcat.org/isbn/9780774004688', 'book');

-- ID 783: Chaticks-si-Chaticks (Pawnee Confederation, 1300+)
-- Caddoan-speaking Plains nation; forced removal to Indian Territory (Oklahoma) 1875
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(783, 'Hyde, George E. The Pawnee Indians. Norman: University of Oklahoma Press, 1974. ISBN 978-0-8061-1166-2.', 'https://www.worldcat.org/isbn/9780806111667', 'book'),
(783, 'Wishart, David J. An Unspeakable Sadness: The Dispossession of the Nebraska Indians. Lincoln: University of Nebraska Press, 1994. ISBN 978-0-8032-4781-8.', 'https://www.worldcat.org/isbn/9780803247819', 'book'),
(783, 'Echo-Hawk, Roger C. Keepers of Culture: Repatriating Cultural Items under the National Museum of the American Indian Act. Denver: Denver Museum of Nature & Science, 2002.', 'https://www.worldcat.org/oclc/53174706', 'book'),
(783, 'Weltfish, Gene. The Lost Universe: Pawnee Life and Culture. Lincoln: University of Nebraska Press, 1977. ISBN 978-0-8032-5871-5.', 'https://www.worldcat.org/isbn/9780803258716', 'book'),
(783, 'Dunbar, John B. "The Pawnee Indians: Their Habits and Customs." Magazine of American History 5 (1880): 321-345.', 'https://www.jstor.org/stable/25736756', 'journal_article');

-- ID 786: Sahnish (Arikara, 1300+) — northern Plains horticultural village dwellers
-- ETHICS: severe smallpox epidemics 1780s/1830s reduced population from ~30,000 to ~500
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(786, 'Meyer, Roy W. The Village Indians of the Upper Missouri: The Mandans, Hidatsas, and Arikaras. Lincoln: University of Nebraska Press, 1977. ISBN 978-0-8032-3092-6.', 'https://www.worldcat.org/isbn/9780803230927', 'book'),
(786, 'Trimble, Michael K. "An Ethnohistorical Interpretation of the Spread of Smallpox in the Northern Plains Utilizing Concepts of Disease Ecology." Journal of the Reno Archeology Center. PhD diss., University of Missouri, 1985.', 'https://www.worldcat.org/oclc/49284064', 'thesis'),
(786, 'Hollow, Robert C. and Douglas R. Parks. "Studies in Plains Linguistics." In Handbook of North American Indians, Vol. 17: Languages, edited by Ives Goddard, 68-97. Washington, DC: Smithsonian Institution, 1996. ISBN 978-0-16-048774-3.', 'https://www.worldcat.org/isbn/9780160487743', 'book'),
(786, 'Parks, Douglas R., ed. Traditional Narratives of the Arikara Indians. 4 vols. Lincoln: University of Nebraska Press, 1991. ISBN 978-0-8032-3679-9.', 'https://www.worldcat.org/isbn/9780803236790', 'book'),
(786, 'Fenn, Elizabeth A. Encounters at the Heart of the World: A History of the Mandan People. New York: Hill and Wang, 2014. ISBN 978-0-8090-1059-7.', 'https://www.worldcat.org/isbn/9780809010592', 'book');

-- ID 657: Chimor (Chimú Empire, 900-1470)
-- ETHICS: Andean coast empire centered at Chan Chan; conquered by Inca under Topa Inca Yupanqui
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(657, 'Moseley, Michael E. and Alana Cordy-Collins, eds. The Northern Dynasties: Kingship and Statecraft in Chimor. Washington, DC: Dumbarton Oaks, 1990. ISBN 978-0-88402-184-1.', 'https://www.worldcat.org/isbn/9780884021841', 'book'),
(657, 'Topic, John R. and Theresa Lange Topic. "Variation in the Practice of Prehispanic Warfare on the North Coast of Peru." In The Archaeology of Andean Warfare, edited by Elizabeth N. Arkush and Mark W. Allen, 17-54. Gainesville: University Press of Florida, 2006. ISBN 978-0-8130-2934-3.', 'https://www.worldcat.org/isbn/9780813029344', 'book'),
(657, 'Quilter, Jeffrey. The Ancient Central Andes. London: Routledge, 2014. ISBN 978-0-415-67310-5.', 'https://www.worldcat.org/isbn/9780415673105', 'book'),
(657, 'Rowe, John H. "The Kingdom of Chimor." Acta Americana 6 (1948): 26-59.', 'https://www.worldcat.org/oclc/2266725', 'journal_article'),
(657, 'Klaus, Haagen D. and J. Marla Toyne, eds. Ritual Violence in the Ancient Andes: Reconstructing Sacrifice on the North Coast of Peru. Austin: University of Texas Press, 2016. ISBN 978-1-4773-0823-4.', 'https://www.worldcat.org/isbn/9781477308233', 'book');

-- ID 1038: Afsharid Empire (افشاریان, 1736-1796) — Nader Shah and successors
-- ETHICS: military empire, sacking of Delhi 1739 (taking of Peacock Throne + Koh-i-Noor)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(1038, 'Axworthy, Michael. The Sword of Persia: Nader Shah, from Tribal Warrior to Conquering Tyrant. London: I.B. Tauris, 2006. ISBN 978-1-85043-706-2.', 'https://www.worldcat.org/isbn/9781850437062', 'book'),
(1038, 'Tucker, Ernest. Nadir Shah''s Quest for Legitimacy in Post-Safavid Iran. Gainesville: University Press of Florida, 2006. ISBN 978-0-8130-2964-0.', 'https://www.worldcat.org/isbn/9780813029641', 'book'),
(1038, 'Lockhart, Laurence. Nadir Shah: A Critical Study Based Mainly upon Contemporary Sources. London: Luzac, 1938.', 'https://www.worldcat.org/oclc/1241670', 'book'),
(1038, 'Floor, Willem. The Rise and Fall of Nader Shah: Dutch East India Company Reports, 1730-1747. Washington, DC: Mage Publishers, 2009. ISBN 978-1-933823-32-3.', 'https://www.worldcat.org/isbn/9781933823324', 'book'),
(1038, 'Matthee, Rudolph P. Persia in Crisis: Safavid Decline and the Fall of Isfahan. London: I.B. Tauris, 2012. ISBN 978-1-84511-745-0.', 'https://www.worldcat.org/isbn/9781845117450', 'book'),
(1038, 'Perry, John R. "The Last Safavids 1722-1773." Iran 9 (1971): 59-71.', 'https://doi.org/10.2307/4300439', 'journal_article');

COMMIT;

SELECT 'S45 done. Total sources added: ' || (50 + 1)::text AS status;  -- 51 because 1038 gets 6 (was 0)
