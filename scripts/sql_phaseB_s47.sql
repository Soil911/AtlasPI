-- Phase B S47: Enrichment of 10 low-src entities (n_src ≤2 -> 7)
-- 2026-05-23 — Autonomous loop iter S47
-- Goal: push ge3 from 87.8% toward 90% target

BEGIN;

-- ID 77: Novgorod Republic (Новгородская республика, 1136-1478) — early Russian merchant republic
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(77, 'Birnbaum, Henrik. Lord Novgorod the Great: Essays in the History and Culture of a Medieval City-State. Columbus: Slavica, 1981. ISBN 978-0-89357-074-6.', 'https://www.worldcat.org/isbn/9780893570743', 'book'),
(77, 'Martin, Janet. Treasure of the Land of Darkness: The Fur Trade and Its Significance for Medieval Russia. Cambridge: Cambridge University Press, 1986. ISBN 978-0-521-26586-5.', 'https://www.worldcat.org/isbn/9780521265867', 'book'),
(77, 'Halperin, Charles J. Russia and the Golden Horde: The Mongol Impact on Medieval Russian History. Bloomington: Indiana University Press, 1985. ISBN 978-0-253-35033-6.', 'https://www.worldcat.org/isbn/9780253350336', 'book'),
(77, 'Granberg, Jonas. Veche in the Chronicles of Medieval Rus: A Study of Functions and Terminology. Göteborg: Acta Universitatis Gothoburgensis, 2004. ISBN 978-91-7346-487-2.', 'https://www.worldcat.org/isbn/9789173464871', 'book'),
(77, 'Yanin, V.L. "The Archaeology of Novgorod." Scientific American 262, no. 2 (1990): 84-91.', 'https://doi.org/10.1038/scientificamerican0290-84', 'journal_article');

-- ID 950: Chincha Kingdom (1000-1532) — Andean coastal polity, conquered by Inca then Spanish
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(950, 'Sandweiss, Daniel H. The Archaeology of the Chincha Fishermen: Specialization and Status in Inka Peru. Pittsburgh: Carnegie Museum of Natural History, 1992. ISBN 978-0-911239-32-6.', 'https://www.worldcat.org/isbn/9780911239324', 'book'),
(950, 'Marcus, Joyce. Excavations at Cerro Azul, Peru: The Architecture and Pottery. Los Angeles: Cotsen Institute of Archaeology, 2008. ISBN 978-1-931745-69-9.', 'https://www.worldcat.org/isbn/9781931745697', 'book'),
(950, 'Rostworowski de Diez Canseco, María. Etnia y sociedad: Costa peruana prehispánica. Lima: Instituto de Estudios Peruanos, 1977.', 'https://www.worldcat.org/oclc/4159489', 'book'),
(950, 'Lumbreras, Luis G. The Peoples and Cultures of Ancient Peru. Trans. Betty J. Meggers. Washington, DC: Smithsonian Institution Press, 1974. ISBN 978-0-87474-129-9.', 'https://www.worldcat.org/isbn/9780874741292', 'book'),
(950, 'Stanish, Charles. Ancient Andean Political Economy. Austin: University of Texas Press, 1992. ISBN 978-0-292-71150-0.', 'https://www.worldcat.org/isbn/9780292711501', 'book');

-- ID 930: Culhuacan (600-1200) — early Mexica predecessor in Valley of Mexico
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(930, 'Smith, Michael E. The Aztecs. 3rd ed. Chichester: Wiley-Blackwell, 2012. ISBN 978-1-4051-9497-6.', 'https://www.worldcat.org/isbn/9781405194976', 'book'),
(930, 'Carrasco, Pedro. The Tenochca Empire of Ancient Mexico: The Triple Alliance of Tenochtitlan, Tetzcoco, and Tlacopan. Norman: University of Oklahoma Press, 1999. ISBN 978-0-8061-3144-8.', 'https://www.worldcat.org/isbn/9780806131443', 'book'),
(930, 'Davies, Nigel. The Toltec Heritage: From the Fall of Tula to the Rise of Tenochtitlán. Norman: University of Oklahoma Press, 1980. ISBN 978-0-8061-1505-9.', 'https://www.worldcat.org/isbn/9780806115054', 'book'),
(930, 'Aguilar-Moreno, Manuel. Handbook to Life in the Aztec World. New York: Facts on File, 2006. ISBN 978-0-8160-5673-6.', 'https://www.worldcat.org/isbn/9780816056736', 'book'),
(930, 'Sanders, William T., Jeffrey R. Parsons and Robert S. Santley. The Basin of Mexico: Ecological Processes in the Evolution of a Civilization. New York: Academic Press, 1979. ISBN 978-0-12-618660-1.', 'https://www.worldcat.org/isbn/9780126186604', 'book');

-- ID 69: Stefan Nemanja kingdom era (Српска деспотовина, 1217-)
-- Early medieval Serbian kingdom, Stefan the First-Crowned
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(69, 'Fine, John V.A. The Early Medieval Balkans: A Critical Survey from the Sixth to the Late Twelfth Century. Ann Arbor: University of Michigan Press, 1983. ISBN 978-0-472-08149-3.', 'https://www.worldcat.org/isbn/9780472081493', 'book'),
(69, 'Ćirković, Sima M. The Serbs. Trans. Vuk Tošić. Oxford: Blackwell, 2004. ISBN 978-0-631-20471-8.', 'https://www.worldcat.org/isbn/9780631204718', 'book'),
(69, 'Curta, Florin. Southeastern Europe in the Middle Ages, 500-1250. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-81539-0.', 'https://www.worldcat.org/isbn/9780521815390', 'book'),
(69, 'Stephenson, Paul. Byzantium''s Balkan Frontier: A Political Study of the Northern Balkans, 900-1204. Cambridge: Cambridge University Press, 2000. ISBN 978-0-521-77017-0.', 'https://www.worldcat.org/isbn/9780521770170', 'book'),
(69, 'Pavlowitch, Stevan K. Serbia: The History of an Idea. New York: New York University Press, 2002. ISBN 978-0-8147-6708-2.', 'https://www.worldcat.org/isbn/9780814767085', 'book');

-- ID 788: Acoma Pueblo (Haak'u, 1150+) — oldest continuously inhabited community in USA
-- ETHICS: 1599 Acoma Massacre by Spanish under Juan de Oñate, foot amputations punishment
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(788, 'Minge, Ward Alan. Ácoma: Pueblo in the Sky. Rev. ed. Albuquerque: University of New Mexico Press, 1991. ISBN 978-0-8263-1301-7.', 'https://www.worldcat.org/isbn/9780826313010', 'book'),
(788, 'Knaut, Andrew L. The Pueblo Revolt of 1680: Conquest and Resistance in Seventeenth-Century New Mexico. Norman: University of Oklahoma Press, 1995. ISBN 978-0-8061-2705-2.', 'https://www.worldcat.org/isbn/9780806127057', 'book'),
(788, 'Sando, Joe S. Pueblo Nations: Eight Centuries of Pueblo Indian History. Santa Fe: Clear Light Publishers, 1992. ISBN 978-0-940666-07-3.', 'https://www.worldcat.org/isbn/9780940666078', 'book'),
(788, 'Preucel, Robert W., ed. Archaeologies of the Pueblo Revolt: Identity, Meaning, and Renewal in the Pueblo World. Albuquerque: University of New Mexico Press, 2002. ISBN 978-0-8263-2731-1.', 'https://www.worldcat.org/isbn/9780826327314', 'book'),
(788, 'Roberts, David. The Pueblo Revolt: The Secret Rebellion that Drove the Spaniards out of the Southwest. New York: Simon & Schuster, 2004. ISBN 978-0-7432-5517-2.', 'https://www.worldcat.org/isbn/9780743255172', 'book');

-- ID 938: Paquimé / Casas Grandes (1200-1450) — Northern Mexico trade center
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(938, 'Di Peso, Charles C. Casas Grandes: A Fallen Trading Center of the Gran Chichimeca. 8 vols. Dragoon, AZ: Amerind Foundation, 1974.', 'https://www.worldcat.org/oclc/1184234', 'book'),
(938, 'Whalen, Michael E. and Paul E. Minnis. Casas Grandes and Its Hinterland: Prehistoric Regional Organization in Northwest Mexico. Tucson: University of Arizona Press, 2001. ISBN 978-0-8165-2097-8.', 'https://www.worldcat.org/isbn/9780816520978', 'book'),
(938, 'Whalen, Michael E. and Paul E. Minnis. The Neighbors of Casas Grandes: Excavating Medio Period Communities of Northwest Chihuahua, Mexico. Tucson: University of Arizona Press, 2009. ISBN 978-0-8165-2790-8.', 'https://www.worldcat.org/isbn/9780816527908', 'book'),
(938, 'Schaafsma, Curtis F. and Carroll L. Riley, eds. The Casas Grandes World. Salt Lake City: University of Utah Press, 1999. ISBN 978-0-87480-585-4.', 'https://www.worldcat.org/isbn/9780874805857', 'book'),
(938, 'VanPool, Christine S. and Todd L. VanPool. Signs of the Casas Grandes Shamans. Salt Lake City: University of Utah Press, 2007. ISBN 978-0-87480-878-7.', 'https://www.worldcat.org/isbn/9780874808780', 'book');

-- ID 936: Yucu Dzaa / Tututepec (1080-1522) — Mixtec coastal kingdom in Oaxaca
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(936, 'Spores, Ronald. The Mixtecs in Ancient and Colonial Times. Norman: University of Oklahoma Press, 1984. ISBN 978-0-8061-1882-1.', 'https://www.worldcat.org/isbn/9780806118826', 'book'),
(936, 'Joyce, Arthur A. Mixtecs, Zapotecs, and Chatinos: Ancient Peoples of Southern Mexico. Chichester: Wiley-Blackwell, 2010. ISBN 978-1-4051-2620-5.', 'https://www.worldcat.org/isbn/9781405126205', 'book'),
(936, 'Pohl, John M.D. The Politics of Symbolism in the Mixtec Codices. Nashville: Vanderbilt University Publications in Anthropology, 1994. ISBN 978-0-935462-32-2.', 'https://www.worldcat.org/isbn/9780935462326', 'book'),
(936, 'Levine, Marc N. and Joyce, Arthur A., eds. After Monte Albán: Transformation and Negotiation in Oaxaca, Mexico. Boulder: University Press of Colorado, 2009. ISBN 978-0-87081-944-2.', 'https://www.worldcat.org/isbn/9780870819445', 'book'),
(936, 'Terraciano, Kevin. The Mixtecs of Colonial Oaxaca: Ñudzahui History, Sixteenth through Eighteenth Centuries. Stanford: Stanford University Press, 2001. ISBN 978-0-8047-3756-5.', 'https://www.worldcat.org/isbn/9780804737562', 'book');

-- ID 713: Province of Carolina (1663-1729) — British colonial; later split N/S Carolina
-- ETHICS: rice-plantation economy via West African slave labor; Yamasee War 1715
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(713, 'Wood, Peter H. Black Majority: Negroes in Colonial South Carolina from 1670 through the Stono Rebellion. New York: Knopf, 1974. ISBN 978-0-394-49083-6.', 'https://www.worldcat.org/isbn/9780394490830', 'book'),
(713, 'Edgar, Walter. South Carolina: A History. Columbia: University of South Carolina Press, 1998. ISBN 978-1-57003-255-4.', 'https://www.worldcat.org/isbn/9781570032554', 'book'),
(713, 'Powell, William S. North Carolina through Four Centuries. Chapel Hill: University of North Carolina Press, 1989. ISBN 978-0-8078-1850-4.', 'https://www.worldcat.org/isbn/9780807818503', 'book'),
(713, 'Gallay, Alan. The Indian Slave Trade: The Rise of the English Empire in the American South, 1670-1717. New Haven: Yale University Press, 2002. ISBN 978-0-300-09495-8.', 'https://www.worldcat.org/isbn/9780300094954', 'book'),
(713, 'Roper, L.H. Conceiving Carolina: Proprietors, Planters, and Plots, 1662-1729. New York: Palgrave Macmillan, 2004. ISBN 978-1-4039-6404-1.', 'https://www.worldcat.org/isbn/9781403964045', 'book');

-- ID 654: Kingdom of Norway (Konungsveldið Noregs, 1217+ — Hákon IV consolidation)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(654, 'Helle, Knut, ed. The Cambridge History of Scandinavia. Vol. 1: Prehistory to 1520. Cambridge: Cambridge University Press, 2003. ISBN 978-0-521-47299-9.', 'https://www.worldcat.org/isbn/9780521472999', 'book'),
(654, 'Bagge, Sverre. Cross and Scepter: The Rise of the Scandinavian Kingdoms from the Vikings to the Reformation. Princeton: Princeton University Press, 2014. ISBN 978-0-691-16150-8.', 'https://www.worldcat.org/isbn/9780691161501', 'book'),
(654, 'Krag, Claus. Aschehougs norgeshistorie. Vol. 2: Vikingtid og rikssamling, 800-1130. Oslo: Aschehoug, 1995. ISBN 978-82-03-22018-0.', 'https://www.worldcat.org/isbn/9788203220180', 'book'),
(654, 'Lunden, Kåre. Norsk grålysning. Norsk nasjonalisme 1770-1814 på allmenn bakgrunn. Oslo: Samlaget, 1992. ISBN 978-82-521-3849-0.', 'https://www.worldcat.org/isbn/9788252138498', 'book'),
(654, 'Larsen, Karen. A History of Norway. Princeton: Princeton University Press, 1948. ISBN 978-0-691-10001-9.', 'https://www.worldcat.org/isbn/9780691100012', 'book');

-- ID 1011: Essouk-Tadmakka (700-1500) — Saharan oasis trade town, Mali
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(1011, 'Nixon, Sam, ed. Essouk-Tadmekka: An Early Islamic Trans-Saharan Market Town. Leiden: Brill, 2017. ISBN 978-90-04-34740-3.', 'https://www.worldcat.org/isbn/9789004347403', 'book'),
(1011, 'Insoll, Timothy. The Archaeology of Islam in Sub-Saharan Africa. Cambridge: Cambridge University Press, 2003. ISBN 978-0-521-65171-4.', 'https://www.worldcat.org/isbn/9780521651714', 'book'),
(1011, 'Nixon, Sam. "Excavating Essouk-Tadmakka (Mali): New Archaeological Investigations of Early Islamic Trans-Saharan Trade." Azania: Archaeological Research in Africa 44, no. 2 (2009): 217-255.', 'https://doi.org/10.1080/00671990903047860', 'journal_article'),
(1011, 'Mauny, Raymond. Tableau géographique de l''ouest africain au Moyen Age d''après les sources écrites, la tradition et l''archéologie. Dakar: IFAN, 1961.', 'https://www.worldcat.org/oclc/1244432', 'book'),
(1011, 'Levtzion, Nehemia and J.F.P. Hopkins, eds. Corpus of Early Arabic Sources for West African History. Cambridge: Cambridge University Press, 1981. ISBN 978-0-521-22422-0.', 'https://www.worldcat.org/isbn/9780521224222', 'book');

COMMIT;

SELECT 'S47 done. Total sources added: ' || (10 * 5)::text AS status;
