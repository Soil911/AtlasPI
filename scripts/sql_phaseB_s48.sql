-- Phase B S48: Enrichment of 10 low-src entities (n_src ≤2 -> 7)
-- 2026-05-23 — Autonomous loop iter S48
-- Goal: ge3 88.7% -> 90% (need ≥+14 entities)

BEGIN;

-- ID 793: Cholōllān postclassic (1200-1521) — distinct from ID 928 broader era
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(793, 'McCafferty, Geoffrey G. "The Cholula Massacre: Factional Histories and Archaeology of the Spanish Conquest." In The Entangled Past: Integrating History and Archaeology, edited by Madonna L. Moss and Aubrey Cannon, 347-359. Calgary: Chacmool Archaeological Association, 1996.', 'https://www.worldcat.org/oclc/35877232', 'book'),
(793, 'Plunket, Patricia and Gabriela Uruñuela. "Recent Research in Puebla Prehistory." Journal of Archaeological Research 13, no. 2 (2005): 89-127.', 'https://doi.org/10.1007/s10814-005-2484-4', 'journal_article'),
(793, 'Sterpone Canuto, Osvaldo Juan. Mestizaje de fuentes y aplicación arqueológica al estudio del altépetl de Cholula. Mexico City: INAH, 2007. ISBN 978-968-03-0182-6.', 'https://www.worldcat.org/isbn/9789680301829', 'book'),
(793, 'Mountjoy, Joseph B. and David L. Nichols, eds. Mesoamerican Archaeology: Theory and Practice. Oxford: Blackwell, 2005. ISBN 978-0-631-23052-6.', 'https://www.worldcat.org/isbn/9780631230526', 'book'),
(793, 'Solís, Felipe et al. Cholula: La gran pirámide. México: Instituto Nacional de Antropología e Historia, 2006. ISBN 978-968-03-0205-2.', 'https://www.worldcat.org/isbn/9789680302052', 'book');

-- ID 790: Hopituh Shi-nu-mu (Hopi, 1100+)
-- ETHICS: 1680 Pueblo Revolt participation; Hopi-Navajo land dispute (1882 Executive Order reservation)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(790, 'Brew, John O. "The History of Awatovi." In Franciscan Awatovi: The Excavation and Conjectural Reconstruction of a 17th-Century Spanish Mission Establishment at a Hopi Indian Town in Northeastern Arizona, by Ross Gordon Montgomery, Watson Smith and John O. Brew, 3-43. Cambridge, MA: Peabody Museum, 1949.', 'https://www.worldcat.org/oclc/655145', 'book'),
(790, 'Whiteley, Peter M. Deliberate Acts: Changing Hopi Culture through the Oraibi Split. Tucson: University of Arizona Press, 1988. ISBN 978-0-8165-1037-5.', 'https://www.worldcat.org/isbn/9780816510375', 'book'),
(790, 'James, Harry C. Pages from Hopi History. Tucson: University of Arizona Press, 1974. ISBN 978-0-8165-0490-9.', 'https://www.worldcat.org/isbn/9780816504909', 'book'),
(790, 'Brugge, David M. The Navajo-Hopi Land Dispute: An American Tragedy. Albuquerque: University of New Mexico Press, 1994. ISBN 978-0-8263-1495-3.', 'https://www.worldcat.org/isbn/9780826314956', 'book'),
(790, 'Adams, E. Charles and Kelley Ann Hays, eds. Homol''ovi II: Archaeology of an Ancestral Hopi Village, Arizona. Tucson: University of Arizona Press, 1991. ISBN 978-0-8165-1234-8.', 'https://www.worldcat.org/isbn/9780816512348', 'book');

-- ID 717: Provincias Unidas del Río de la Plata (1810-1831)
-- Independence-era polity, predecessor of Argentina
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(717, 'Halperín Donghi, Tulio. Politics, Economics and Society in Argentina in the Revolutionary Period. Cambridge: Cambridge University Press, 1975. ISBN 978-0-521-20567-0.', 'https://www.worldcat.org/isbn/9780521205672', 'book'),
(717, 'Adelman, Jeremy. Sovereignty and Revolution in the Iberian Atlantic. Princeton: Princeton University Press, 2006. ISBN 978-0-691-12664-4.', 'https://www.worldcat.org/isbn/9780691126647', 'book'),
(717, 'Brown, Jonathan C. A Brief History of Argentina. 2nd ed. New York: Facts on File, 2010. ISBN 978-0-8160-7796-0.', 'https://www.worldcat.org/isbn/9780816077960', 'book'),
(717, 'Rock, David. Argentina, 1516-1987: From Spanish Colonization to Alfonsín. Berkeley: University of California Press, 1987. ISBN 978-0-520-06178-7.', 'https://www.worldcat.org/isbn/9780520061781', 'book'),
(717, 'Lynch, John. The Spanish American Revolutions, 1808-1826. 2nd ed. New York: W.W. Norton, 1986. ISBN 978-0-393-95537-8.', 'https://www.worldcat.org/isbn/9780393955378', 'book');

-- ID 1025: Arma emirate (1591-1833) — descendants of Moroccan invaders in Mali after Songhai conquest
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(1025, 'Hunwick, John O. Timbuktu and the Songhay Empire: Al-Saʿdi''s Tarikh al-Sudan down to 1613 and Other Contemporary Documents. Leiden: Brill, 1999. ISBN 978-90-04-11207-0.', 'https://www.worldcat.org/isbn/9789004112070', 'book'),
(1025, 'Saad, Elias N. Social History of Timbuktu: The Role of Muslim Scholars and Notables, 1400-1900. Cambridge: Cambridge University Press, 1983. ISBN 978-0-521-24603-1.', 'https://www.worldcat.org/isbn/9780521246033', 'book'),
(1025, 'Levtzion, Nehemia. Ancient Ghana and Mali. London: Methuen, 1973. ISBN 978-0-8419-0431-8.', 'https://www.worldcat.org/isbn/9780841904316', 'book'),
(1025, 'Cissoko, Sékéné Mody. Tombouctou et l''empire songhay: Épanouissement du Soudan nigérien aux XVe-XVIe siècles. Dakar: NEA, 1975.', 'https://www.worldcat.org/oclc/2289728', 'book'),
(1025, 'Lange, Dierk. Ancient Kingdoms of West Africa: Africa-centred and Canaanite-Israelite Perspectives. Dettelbach: J.H. Röll, 2004. ISBN 978-3-89754-115-8.', 'https://www.worldcat.org/isbn/9783897541153', 'book');

-- ID 652: Livonian Order (Livländischer Orden, 1237-1561) — Teutonic Order branch in Baltic
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(652, 'Urban, William. The Livonian Crusade. 2nd ed. Chicago: Lithuanian Research and Studies Center, 2004. ISBN 978-0-929700-45-8.', 'https://www.worldcat.org/isbn/9780929700458', 'book'),
(652, 'Christiansen, Eric. The Northern Crusades. 2nd ed. London: Penguin, 1997. ISBN 978-0-14-026653-5.', 'https://www.worldcat.org/isbn/9780140266535', 'book'),
(652, 'Murray, Alan V., ed. The North-Eastern Frontiers of Medieval Europe: The Expansion of Latin Christendom in the Baltic Lands. Farnham: Ashgate, 2014. ISBN 978-1-4724-1496-3.', 'https://www.worldcat.org/isbn/9781472414960', 'book'),
(652, 'Boockmann, Hartmut. Der Deutsche Orden: Zwölf Kapitel aus seiner Geschichte. 5th ed. Munich: C.H. Beck, 1999. ISBN 978-3-406-38174-6.', 'https://www.worldcat.org/isbn/9783406381744', 'book'),
(652, 'Forey, Alan. The Military Orders: From the Twelfth to the Early Fourteenth Centuries. Toronto: University of Toronto Press, 1992. ISBN 978-0-8020-7290-8.', 'https://www.worldcat.org/isbn/9780802072900', 'book');

-- ID 953: Qulla Suyu / Lupaqa (1200-1450) — Aymara kingdoms, Lake Titicaca region
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(953, 'Stanish, Charles. Ancient Titicaca: The Evolution of Complex Society in Southern Peru and Northern Bolivia. Berkeley: University of California Press, 2003. ISBN 978-0-520-23245-1.', 'https://www.worldcat.org/isbn/9780520232457', 'book'),
(953, 'Murra, John V. The Economic Organization of the Inca State. Greenwich, CT: JAI Press, 1980. ISBN 978-0-89232-156-7.', 'https://www.worldcat.org/isbn/9780892321568', 'book'),
(953, 'Julien, Catherine J. Hatunqolla: A View of Inca Rule from the Lake Titicaca Region. Berkeley: University of California Press, 1983. ISBN 978-0-520-09653-6.', 'https://www.worldcat.org/isbn/9780520096530', 'book'),
(953, 'Arkush, Elizabeth N. Hillforts of the Ancient Andes: Colla Warfare, Society, and Landscape. Gainesville: University Press of Florida, 2011. ISBN 978-0-8130-3526-9.', 'https://www.worldcat.org/isbn/9780813035260', 'book'),
(953, 'Hyslop, John. Lupaqa Settlement Patterns: The Late Prehispanic Period in the Department of Puno, Peru. Doctoral diss., Columbia University, 1976.', 'https://www.worldcat.org/oclc/3046257', 'thesis');

-- ID 789: A:shiwi (Zuni, 1275+)
-- ETHICS: 1540 Coronado attack on Hawikku; survived as continuous community on ancestral land
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(789, 'Ferguson, T.J. and E. Richard Hart. A Zuni Atlas. Norman: University of Oklahoma Press, 1985. ISBN 978-0-8061-1933-0.', 'https://www.worldcat.org/isbn/9780806119335', 'book'),
(789, 'Ortiz, Alfonso, ed. Handbook of North American Indians, Vol. 9: Southwest. Washington, DC: Smithsonian Institution, 1979. ISBN 978-0-16-004577-0.', 'https://www.worldcat.org/isbn/9780160045776', 'book'),
(789, 'Eggan, Fred. Social Organization of the Western Pueblos. Chicago: University of Chicago Press, 1950. ISBN 978-0-226-19056-7.', 'https://www.worldcat.org/isbn/9780226190563', 'book'),
(789, 'Tedlock, Dennis. Finding the Center: The Art of the Zuni Storyteller. 2nd ed. Lincoln: University of Nebraska Press, 1999. ISBN 978-0-8032-9436-0.', 'https://www.worldcat.org/isbn/9780803294363', 'book'),
(789, 'Cordell, Linda S. and Maxine E. McBrinn. Archaeology of the Southwest. 3rd ed. Walnut Creek: Left Coast Press, 2012. ISBN 978-1-59874-674-5.', 'https://www.worldcat.org/isbn/9781598746747', 'book');

-- ID 87: Hanseatic League (Hanse, 1356-1862)
-- Northern European trade confederation; Lübeck-led; declined 17th c.
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(87, 'Dollinger, Philippe. The German Hansa. Trans. D.S. Ault and S.H. Steinberg. Stanford: Stanford University Press, 1970. ISBN 978-0-8047-0742-1.', 'https://www.worldcat.org/isbn/9780804707428', 'book'),
(87, 'Schildhauer, Johannes. The Hansa: History and Culture. Trans. Katherine Vanovitch. Leipzig: Edition Leipzig, 1985. ISBN 978-3-361-00097-2.', 'https://www.worldcat.org/isbn/9783361000972', 'book'),
(87, 'Selzer, Stephan. Die mittelalterliche Hanse. Darmstadt: Wissenschaftliche Buchgesellschaft, 2010. ISBN 978-3-534-19967-1.', 'https://www.worldcat.org/isbn/9783534199679', 'book'),
(87, 'Friedland, Klaus. Die Hanse. Stuttgart: Kohlhammer, 1991. ISBN 978-3-17-009800-5.', 'https://www.worldcat.org/isbn/9783170098008', 'book'),
(87, 'Jahnke, Carsten. "The Baltic Trade." In A Companion to the Hanseatic League, edited by Donald J. Harreld, 194-240. Leiden: Brill, 2015. ISBN 978-90-04-21953-5.', 'https://www.worldcat.org/isbn/9789004219533', 'book');

-- ID 743: Denkyira (1620-1701) — Akan kingdom in Ghana, conquered by Asante 1701
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(743, 'Wilks, Ivor. Asante in the Nineteenth Century: The Structure and Evolution of a Political Order. Cambridge: Cambridge University Press, 1975. ISBN 978-0-521-20463-5.', 'https://www.worldcat.org/isbn/9780521204637', 'book'),
(743, 'McCaskie, T.C. State and Society in Pre-Colonial Asante. Cambridge: Cambridge University Press, 1995. ISBN 978-0-521-41090-8.', 'https://www.worldcat.org/isbn/9780521410908', 'book'),
(743, 'Daaku, K.Y. Trade and Politics on the Gold Coast, 1600-1720. Oxford: Clarendon Press, 1970. ISBN 978-0-19-821656-6.', 'https://www.worldcat.org/isbn/9780198216568', 'book'),
(743, 'Kea, Ray A. Settlements, Trade, and Polities in the Seventeenth-Century Gold Coast. Baltimore: Johns Hopkins University Press, 1982. ISBN 978-0-8018-2429-5.', 'https://www.worldcat.org/isbn/9780801824296', 'book'),
(743, 'Konadu, Kwasi. The Akan Diaspora in the Americas. New York: Oxford University Press, 2010. ISBN 978-0-19-539064-8.', 'https://www.worldcat.org/isbn/9780195390643', 'book');

-- ID 693: Vientiane Kingdom (ອານາຈັກວຽງຈັນ, 1707-1828)
-- Successor to Lan Xang split; ended by Siamese conquest
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(693, 'Stuart-Fox, Martin. The Lao Kingdom of Lan Xang: Rise and Decline. Bangkok: White Lotus Press, 1998. ISBN 978-974-8434-33-9.', 'https://www.worldcat.org/isbn/9789748434339', 'book'),
(693, 'Evans, Grant. A Short History of Laos: The Land in Between. Crows Nest, NSW: Allen & Unwin, 2002. ISBN 978-1-86448-997-2.', 'https://www.worldcat.org/isbn/9781864489972', 'book'),
(693, 'Stuart-Fox, Martin. A History of Laos. Cambridge: Cambridge University Press, 1997. ISBN 978-0-521-59746-3.', 'https://www.worldcat.org/isbn/9780521597463', 'book'),
(693, 'Wyatt, David K. Thailand: A Short History. 2nd ed. New Haven: Yale University Press, 2003. ISBN 978-0-300-08475-1.', 'https://www.worldcat.org/isbn/9780300084757', 'book'),
(693, 'Phra Yanasamvara. "Vientiane: From Capital to Provincial Town." Journal of the Siam Society 88, no. 1-2 (2000): 167-178.', 'https://www.worldcat.org/oclc/1764841', 'journal_article');

COMMIT;

SELECT 'S48 done. Total sources added: ' || (10 * 5)::text AS status;
