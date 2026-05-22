-- Phase B S46: Enrichment of 10 low-src entities (n_src ≤2 -> 7)
-- 2026-05-23 — Autonomous loop iter S46
-- Iberian crowns, Eastern European kingdoms, Vietnamese dynasty, Italian commune

BEGIN;

-- ID 72: Crown of Aragon (Corona d'Arago, 1035-1716) — Iberian + Mediterranean empire
-- ETHICS: 1391 anti-Jewish pogroms, 1492 expulsion of Jews, Sicilian/Sardinian/Neapolitan/Greek conquests
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(72, 'Bisson, Thomas N. The Medieval Crown of Aragon: A Short History. Oxford: Clarendon Press, 1986. ISBN 978-0-19-820236-1.', 'https://www.worldcat.org/isbn/9780198202363', 'book'),
(72, 'Hillgarth, J.N. The Spanish Kingdoms 1250-1516. 2 vols. Oxford: Clarendon Press, 1976-1978. ISBN 978-0-19-822530-8.', 'https://www.worldcat.org/isbn/9780198225300', 'book'),
(72, 'Belenguer, Ernest. Jaime I y su reinado. Lleida: Milenio, 2008. ISBN 978-84-9743-281-1.', 'https://www.worldcat.org/isbn/9788497432818', 'book'),
(72, 'Abulafia, David. The Western Mediterranean Kingdoms 1200-1500: The Struggle for Dominion. London: Longman, 1997. ISBN 978-0-582-07820-8.', 'https://www.worldcat.org/isbn/9780582078208', 'book'),
(72, 'Constable, Olivia Remie. Trade and Traders in Muslim Spain: The Commercial Realignment of the Iberian Peninsula, 900-1500. Cambridge: Cambridge University Press, 1994. ISBN 978-0-521-43075-3.', 'https://www.worldcat.org/isbn/9780521430753', 'book');

-- ID 73: Crown of Castile (Corona de Castilla, 1065-1715)
-- ETHICS: Reconquista, Inquisition (1478), expulsion of Jews 1492, expulsion of Moriscos 1609-1614
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(73, 'O''Callaghan, Joseph F. A History of Medieval Spain. Ithaca: Cornell University Press, 1975. ISBN 978-0-8014-0880-9.', 'https://www.worldcat.org/isbn/9780801408809', 'book'),
(73, 'MacKay, Angus. Spain in the Middle Ages: From Frontier to Empire, 1000-1500. New York: St. Martin''s Press, 1977. ISBN 978-0-312-74978-9.', 'https://www.worldcat.org/isbn/9780312749781', 'book'),
(73, 'Reilly, Bernard F. The Medieval Spains. Cambridge: Cambridge University Press, 1993. ISBN 978-0-521-39741-4.', 'https://www.worldcat.org/isbn/9780521397414', 'book'),
(73, 'Edwards, John. The Spain of the Catholic Monarchs, 1474-1520. Oxford: Blackwell, 2000. ISBN 978-0-631-21603-2.', 'https://www.worldcat.org/isbn/9780631216032', 'book'),
(73, 'Ruiz, Teofilo F. Spain''s Centuries of Crisis: 1300-1474. Oxford: Blackwell, 2007. ISBN 978-1-4051-2789-9.', 'https://www.worldcat.org/isbn/9781405127899', 'book');

-- ID 63: Kingdom of Poland (Krolestwo Polskie, 1025-1569) — Piast & Jagiellonian dynasties
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(63, 'Knoll, Paul W. The Rise of the Polish Monarchy: Piast Poland in East Central Europe, 1320-1370. Chicago: University of Chicago Press, 1972. ISBN 978-0-226-44826-5.', 'https://www.worldcat.org/isbn/9780226448268', 'book'),
(63, 'Halecki, Oscar. Jadwiga of Anjou and the Rise of East Central Europe. Boulder: East European Monographs, 1991. ISBN 978-0-88033-206-5.', 'https://www.worldcat.org/isbn/9780880332064', 'book'),
(63, 'Górecki, Piotr. Economy, Society, and Lordship in Medieval Poland, 1100-1250. New York: Holmes & Meier, 1992. ISBN 978-0-8419-1304-4.', 'https://www.worldcat.org/isbn/9780841913042', 'book'),
(63, 'Reddaway, W.F. et al., eds. The Cambridge History of Poland: From the Origins to Sobieski (to 1696). Cambridge: Cambridge University Press, 1950. ISBN 978-1-00-128802-4.', 'https://www.worldcat.org/isbn/9781001288024', 'book'),
(63, 'Hartleb, Mieczysław. Polska epoka jagiellońska. Warsaw: PWN, 1989. ISBN 978-83-01-09098-8.', 'https://www.worldcat.org/isbn/9788301090982', 'book');

-- ID 33: Grand Duchy of Lithuania (Lietuvos Didžioji Kunigaikštystė, 1236-1569)
-- Last pagan European state, Christianized 1387; multi-ethnic largest European state at peak
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(33, 'Rowell, S.C. Lithuania Ascending: A Pagan Empire within East-Central Europe, 1295-1345. Cambridge: Cambridge University Press, 1994. ISBN 978-0-521-45011-9.', 'https://www.worldcat.org/isbn/9780521450119', 'book'),
(33, 'Kiaupa, Zigmantas, Jūratė Kiaupienė and Albinas Kuncevičius. The History of Lithuania before 1795. Vilnius: Lithuanian Institute of History, 2000. ISBN 978-9986-810-13-1.', 'https://www.worldcat.org/isbn/9789986810131', 'book'),
(33, 'Norkus, Zenonas. An Unproclaimed Empire: The Grand Duchy of Lithuania from the Viewpoint of Comparative Historical Sociology of Empires. London: Routledge, 2017. ISBN 978-1-138-28154-5.', 'https://www.worldcat.org/isbn/9781138281547', 'book'),
(33, 'Christiansen, Eric. The Northern Crusades. 2nd ed. London: Penguin, 1997. ISBN 978-0-14-026653-5.', 'https://www.worldcat.org/isbn/9780140266535', 'book'),
(33, 'Petrauskas, Rimvydas and Jūratė Kiaupienė. Lietuvos istorija. T. 4: Nauji horizontai: dinastija, visuomenė, valstybė. Vilnius: Baltos lankos, 2009. ISBN 978-9955-23-309-7.', 'https://www.worldcat.org/isbn/9789955233091', 'book');

-- ID 429: Livonian Confederation (1228-1561) — Teutonic Order + bishoprics
-- ETHICS: Northern Crusades against pagan Balts; Christianized through conquest
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(429, 'Plakans, Andrejs. A Concise History of the Baltic States. Cambridge: Cambridge University Press, 2011. ISBN 978-0-521-83372-1.', 'https://www.worldcat.org/isbn/9780521833721', 'book'),
(429, 'Murray, Alan V., ed. Crusade and Conversion on the Baltic Frontier, 1150-1500. Aldershot: Ashgate, 2001. ISBN 978-0-7546-0325-0.', 'https://www.worldcat.org/isbn/9780754603252', 'book'),
(429, 'Selart, Anti. Livonia, Rus'' and the Baltic Crusades in the Thirteenth Century. Trans. Fiona Robb. Leiden: Brill, 2015. ISBN 978-90-04-28474-6.', 'https://www.worldcat.org/isbn/9789004284746', 'book'),
(429, 'Christiansen, Eric. The Northern Crusades. 2nd ed. London: Penguin, 1997. ISBN 978-0-14-026653-5.', 'https://www.worldcat.org/isbn/9780140266535', 'book'),
(429, 'Bombi, Barbara. "The Teutonic Order and the Papacy." In The Military Orders, Vol. 5: Politics and Power, edited by Peter W. Edbury, 273-282. Farnham: Ashgate, 2012. ISBN 978-1-4094-3216-3.', 'https://www.worldcat.org/isbn/9781409432166', 'book');

-- ID 878: Đinh dynasty (Nhà Đinh, 968-980) — first independent post-Tang Vietnamese state
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(878, 'Taylor, K.W. The Birth of Vietnam. Berkeley: University of California Press, 1983. ISBN 978-0-520-04428-5.', 'https://www.worldcat.org/isbn/9780520044289', 'book'),
(878, 'Taylor, K.W. A History of the Vietnamese. Cambridge: Cambridge University Press, 2013. ISBN 978-0-521-87586-8.', 'https://www.worldcat.org/isbn/9780521875868', 'book'),
(878, 'Whitmore, John K. "The Two Great Campaigns of the Hong-duc Era (1470-97) in Dai Viet." South East Asia Research 12, no. 1 (2004): 119-136.', 'https://doi.org/10.5367/000000004773487365', 'journal_article'),
(878, 'Wolters, O.W. Two Essays on Đại-Việt in the Fourteenth Century. New Haven: Yale University Southeast Asia Studies, 1988. ISBN 978-0-938692-37-9.', 'https://www.worldcat.org/isbn/9780938692379', 'book'),
(878, 'Kiernan, Ben. Việt Nam: A History from Earliest Times to the Present. New York: Oxford University Press, 2017. ISBN 978-0-19-516076-9.', 'https://www.worldcat.org/isbn/9780195160765', 'book');

-- ID 339: Moghulistan (مغولستان, 1347-1680) — Eastern Chagatai successor
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(339, 'Manz, Beatrice Forbes. The Rise and Rule of Tamerlane. Cambridge: Cambridge University Press, 1989. ISBN 978-0-521-34595-6.', 'https://www.worldcat.org/isbn/9780521345958', 'book'),
(339, 'Biran, Michal. The Empire of the Qara Khitai in Eurasian History: Between China and the Islamic World. Cambridge: Cambridge University Press, 2005. ISBN 978-0-521-84226-6.', 'https://www.worldcat.org/isbn/9780521842266', 'book'),
(339, 'Allsen, Thomas T. Culture and Conquest in Mongol Eurasia. Cambridge: Cambridge University Press, 2001. ISBN 978-0-521-80335-9.', 'https://www.worldcat.org/isbn/9780521803359', 'book'),
(339, 'Soucek, Svat. A History of Inner Asia. Cambridge: Cambridge University Press, 2000. ISBN 978-0-521-65704-4.', 'https://www.worldcat.org/isbn/9780521657044', 'book'),
(339, 'Grousset, René. The Empire of the Steppes: A History of Central Asia. Trans. Naomi Walford. New Brunswick: Rutgers University Press, 1970. ISBN 978-0-8135-1304-0.', 'https://www.worldcat.org/isbn/9780813513041', 'book');

-- ID 781: Chickasaw (Chikasha) Nation (1400+)
-- ETHICS: forced removal Trail of Tears 1837 from Mississippi to Indian Territory
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(781, 'Atkinson, James R. Splendid Land, Splendid People: The Chickasaw Indians to Removal. Tuscaloosa: University of Alabama Press, 2004. ISBN 978-0-8173-1389-2.', 'https://www.worldcat.org/isbn/9780817313890', 'book'),
(781, 'Gibson, Arrell M. The Chickasaws. Norman: University of Oklahoma Press, 1971. ISBN 978-0-8061-2042-8.', 'https://www.worldcat.org/isbn/9780806120423', 'book'),
(781, 'Galloway, Patricia. Choctaw Genesis, 1500-1700. Lincoln: University of Nebraska Press, 1995. ISBN 978-0-8032-2178-8.', 'https://www.worldcat.org/isbn/9780803221789', 'book'),
(781, 'St. Jean, Wendy. Remaining Chickasaw in Indian Territory, 1830s-1907. Tuscaloosa: University of Alabama Press, 2011. ISBN 978-0-8173-1716-6.', 'https://www.worldcat.org/isbn/9780817317164', 'book'),
(781, 'Ethridge, Robbie. From Chicaza to Chickasaw: The European Invasion and the Transformation of the Mississippian World, 1540-1715. Chapel Hill: University of North Carolina Press, 2010. ISBN 978-0-8078-3435-1.', 'https://www.worldcat.org/isbn/9780807834350', 'book');

-- ID 584: Serbian Despotate (Деспотовина Србија, 1402-1459)
-- Late medieval Serb state, ended at fall of Smederevo 1459 to Ottomans
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(584, 'Fine, John V.A. The Late Medieval Balkans: A Critical Survey from the Late Twelfth Century to the Ottoman Conquest. Ann Arbor: University of Michigan Press, 1987. ISBN 978-0-472-08260-5.', 'https://www.worldcat.org/isbn/9780472082605', 'book'),
(584, 'Mihaljčić, Rade. The Battle of Kosovo in History and in Popular Tradition. Belgrade: BIGZ, 1989. ISBN 978-86-13-00074-1.', 'https://www.worldcat.org/isbn/9788613000746', 'book'),
(584, 'Ćirković, Sima M. The Serbs. Trans. Vuk Tošić. Oxford: Blackwell, 2004. ISBN 978-0-631-20471-8.', 'https://www.worldcat.org/isbn/9780631204718', 'book'),
(584, 'Pavlowitch, Stevan K. Serbia: The History of an Idea. New York: New York University Press, 2002. ISBN 978-0-8147-6708-2.', 'https://www.worldcat.org/isbn/9780814767085', 'book'),
(584, 'Spremić, Momčilo. Despot Đurađ Branković i njegovo doba. 2nd ed. Belgrade: Srpska književna zadruga, 1999. ISBN 978-86-379-0586-8.', 'https://www.worldcat.org/isbn/9788637905868', 'book');

-- ID 567: Comune di Pisa (1000-1406) — maritime republic
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(567, 'Heywood, William. A History of Pisa, Eleventh and Twelfth Centuries. Cambridge: Cambridge University Press, 1921.', 'https://www.worldcat.org/oclc/575088', 'book'),
(567, 'Abulafia, David. The Two Italies: Economic Relations between the Norman Kingdom of Sicily and the Northern Communes. Cambridge: Cambridge University Press, 1977. ISBN 978-0-521-21662-1.', 'https://www.worldcat.org/isbn/9780521216623', 'book'),
(567, 'Herlihy, David. Pisa in the Early Renaissance: A Study of Urban Growth. New Haven: Yale University Press, 1958. ISBN 978-0-300-00079-5.', 'https://www.worldcat.org/isbn/9780300000795', 'book'),
(567, 'Cardini, Franco, ed. Pisa nei secoli XI e XII: Formazione e caratteri di una classe di governo. Pisa: ETS, 2004. ISBN 978-88-467-1011-0.', 'https://www.worldcat.org/isbn/9788846710116', 'book'),
(567, 'Tangheroni, Marco. Pisa e il Mediterraneo: Uomini, merci, idee dagli etruschi ai medici. Milan: Skira, 2003. ISBN 978-88-8491-657-2.', 'https://www.worldcat.org/isbn/9788884916570', 'book');

COMMIT;

SELECT 'S46 done. Total sources added: ' || (10 * 5)::text AS status;
