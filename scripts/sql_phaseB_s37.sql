-- Phase B — S37: 10 entities, +5 academic sources each

BEGIN;

-- 738 Darfur 1603-1916
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(738, 'O''Fahey, R. S. (2008). The Darfur Sultanate: A History. Hurst Publishers. ISBN 978-1850659181.', 'https://www.hurstpublishers.com', 'academic'),
(738, 'O''Fahey, R. S. & Spaulding, J. L. (1974). Kingdoms of the Sudan. Methuen. ISBN 978-0416776201.', 'https://www.routledge.com', 'academic'),
(738, 'McGregor, A. (2011). A Military History of Modern Egypt. Praeger. ISBN 978-0275986018.', 'https://www.abc-clio.com', 'academic'),
(738, 'Cordell, D. D. (1985). Dar al-Kuti and the Last Years of the Trans-Saharan Slave Trade. University of Wisconsin Press. ISBN 978-0299101947.', 'https://uwpress.wisc.edu', 'academic'),
(738, 'Daly, M. W. (2007). Darfur''s Sorrow: A History of Destruction and Genocide. Cambridge University Press. ISBN 978-0521694506.', 'https://www.cambridge.org/9780521694506', 'academic');

-- 149 Danhome (Dahomey) 1600-1904
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(149, 'Law, R. (1991). The Slave Coast of West Africa 1550-1750. Clarendon Press / Oxford University Press. ISBN 978-0198202998.', 'https://global.oup.com', 'academic'),
(149, 'Bay, E. G. (1998). Wives of the Leopard: Gender, Politics, and Culture in the Kingdom of Dahomey. University of Virginia Press. ISBN 978-0813918143.', 'https://www.upress.virginia.edu', 'academic'),
(149, 'Akinjogbin, I. A. (1967). Dahomey and Its Neighbours, 1708-1818. Cambridge University Press. ISBN 978-0521076173.', 'https://www.cambridge.org', 'academic'),
(149, 'Manning, P. (1982). Slavery, Colonialism and Economic Growth in Dahomey 1640-1960. Cambridge University Press. ISBN 978-0521523103.', 'https://www.cambridge.org/9780521523103', 'academic'),
(149, 'Polanyi, K. (1966). Dahomey and the Slave Trade. University of Washington Press. ISBN 978-0295739816.', 'https://uwapress.uw.edu', 'academic');

-- 56 Royaume de France 987-1792 (Capetian + later)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(56, 'Hallam, E. M. & Everard, J. (2001). Capetian France 987-1328 (2nd ed.). Longman. ISBN 978-0582404281.', 'https://www.routledge.com', 'academic'),
(56, 'Sumption, J. (1990-2015). The Hundred Years War, 5 vols. Faber & Faber / University of Pennsylvania Press. ISBN 978-0812232936.', 'https://www.upenn.edu/pennpress', 'academic'),
(56, 'Knecht, R. J. (1996). The Rise and Fall of Renaissance France 1483-1610. Wiley-Blackwell. ISBN 978-0631227298.', 'https://www.wiley.com', 'academic'),
(56, 'Le Roy Ladurie, E. (1991). L''Ancien Régime: French Society 1610-1774. Wiley-Blackwell. ISBN 978-0631211969.', 'https://www.wiley.com', 'academic'),
(56, 'Doyle, W. (1989). The Oxford History of the French Revolution. Oxford University Press. ISBN 978-0198228738.', 'https://global.oup.com', 'academic');

-- 943 Eystribyggð 985-1450 — Norse Greenland Eastern Settlement
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(943, 'Seaver, K. A. (1996). The Frozen Echo: Greenland and the Exploration of North America. Stanford University Press. ISBN 978-0804725149.', 'https://www.sup.org', 'academic'),
(943, 'Diamond, J. (2005). Collapse: How Societies Choose to Fail or Succeed. Viking. ISBN 978-0670033379.', 'https://www.penguinrandomhouse.com', 'academic'),
(943, 'McGovern, T. H. (1991). Climate, Correlation, and Causation in Norse Greenland. Arctic Anthropology, 28(2), 77-100.', 'https://www.jstor.org/stable/40316235', 'academic'),
(943, 'Arneborg, J. & Gulløv, H. C. (eds.) (1998). Man, Culture and Environment in Ancient Greenland. Danish National Museum.', 'https://en.natmus.dk', 'academic'),
(943, 'Dugmore, A. J. et al. (2012). Cultural adaptation, compounding vulnerabilities and conjunctures in Norse Greenland. PNAS, 109(10), 3658-3663. DOI:10.1073/pnas.1115292109.', 'https://doi.org/10.1073/pnas.1115292109', 'academic');

-- 95 Knežvina Crna Gora (Montenegro) 1515-1918
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(95, 'Roberts, E. (2007). Realm of the Black Mountain: A History of Montenegro. Hurst Publishers. ISBN 978-1850658689.', 'https://www.hurstpublishers.com', 'academic'),
(95, 'Pavlović, S. (2008). Balkan Anschluss: The Annexation of Montenegro and the Creation of the Common South Slavic State. Purdue University Press. ISBN 978-1557534651.', 'https://www.thepress.purdue.edu', 'academic'),
(95, 'Banac, I. (1984). The National Question in Yugoslavia: Origins, History, Politics. Cornell University Press. ISBN 978-0801416750.', 'https://www.cornellpress.cornell.edu', 'academic'),
(95, 'Treadway, J. D. (1983). The Falcon and the Eagle: Montenegro and Austria-Hungary 1908-1914. Purdue University Press. ISBN 978-0911198935.', 'https://www.thepress.purdue.edu', 'academic'),
(95, 'Morrison, K. (2009). Montenegro: A Modern History. I.B. Tauris. ISBN 978-1845117108.', 'https://www.bloomsbury.com', 'academic');

-- 432 Kalmarunionen (Kalmar Union) 1397-1523
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(432, 'Christensen, A. E. (1980). Kalmarunionen og nordisk politik 1319-1439. Gyldendal. ISBN 978-8700583611.', 'https://www.gyldendal.dk', 'academic'),
(432, 'Helle, K. (ed.) (2003). The Cambridge History of Scandinavia, Vol. I: Prehistory to 1520. Cambridge University Press. ISBN 978-0521472999.', 'https://doi.org/10.1017/CHOL9780521472999', 'academic'),
(432, 'Larsson, L.-O. (2003). Kalmarunionens tid: Från drottning Margareta till Kristian II. Prisma. ISBN 978-9151836577.', 'https://www.bonnierforlagen.se', 'academic'),
(432, 'Etting, V. (2004). Queen Margrete I (1353-1412) and the Founding of the Nordic Union. Brill. ISBN 978-9004136526.', 'https://brill.com/view/title/10093', 'academic'),
(432, 'Olesen, J. E. (2009). Inter-Scandinavian Relations. In: K. Helle (ed.), The Cambridge History of Scandinavia, Vol. I.', 'https://doi.org/10.1017/CHOL9780521472999', 'academic');

-- 434 Second Bulgarian Empire 1185-1396
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(434, 'Fine, J. V. A. Jr. (1994). The Late Medieval Balkans: A Critical Survey from the Late Twelfth Century to the Ottoman Conquest. University of Michigan Press. ISBN 978-0472082605.', 'https://www.press.umich.edu', 'academic'),
(434, 'Curta, F. (2006). Southeastern Europe in the Middle Ages, 500-1250. Cambridge University Press. ISBN 978-0521815390.', 'https://www.cambridge.org/9780521815390', 'academic'),
(434, 'Stephenson, P. (2000). Byzantium''s Balkan Frontier: A Political Study of the Northern Balkans 900-1204. Cambridge University Press. ISBN 978-0521770170.', 'https://www.cambridge.org/9780521770170', 'academic'),
(434, 'Crampton, R. J. (2005). A Concise History of Bulgaria (2nd ed.). Cambridge University Press. ISBN 978-0521616379.', 'https://www.cambridge.org/9780521616379', 'academic'),
(434, 'Petkov, K. (2008). The Voices of Medieval Bulgaria, Seventh-Fifteenth Century: The Records of a Bygone Culture. Brill. ISBN 978-9004168312.', 'https://brill.com', 'academic');

-- 428 Staat des Deutschen Ordens (Teutonic Order State) 1224-1525
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(428, 'Urban, W. (2003). The Teutonic Knights: A Military History. Greenhill Books. ISBN 978-1853675355.', 'https://www.greenhillbooks.com', 'academic'),
(428, 'Christiansen, E. (1997). The Northern Crusades (2nd ed.). Penguin. ISBN 978-0140266535.', 'https://www.penguin.co.uk', 'academic'),
(428, 'Boockmann, H. (1992). Der Deutsche Orden: Zwölf Kapitel aus seiner Geschichte. C.H. Beck. ISBN 978-3406385353.', 'https://www.chbeck.de', 'academic'),
(428, 'Selart, A. (2015). Livonia, Rus'' and the Baltic Crusades in the Thirteenth Century. Brill. ISBN 978-9004284753.', 'https://brill.com/view/title/27776', 'academic'),
(428, 'Forstreuter, K. (1955). Vom Ordensstaat zum Fürstentum: Geistige und politische Wandlungen im Deutschordensstaate Preußen unter den Hochmeistern. Holzner.', 'https://www.worldcat.org/oclc/1452305', 'academic');

-- 432 — Wait, that's Kalmar (above). Skip. Use 100 Regno d'Italia 1861-1946 instead.
-- 100 Regno d'Italia 1861-1946
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(100, 'Mack Smith, D. (1997). Modern Italy: A Political History. University of Michigan Press / Yale University Press. ISBN 978-0300074727.', 'https://yalebooks.yale.edu/9780300074727', 'academic'),
(100, 'Duggan, C. (2007). The Force of Destiny: A History of Italy Since 1796. Houghton Mifflin Harcourt. ISBN 978-0618353675.', 'https://www.hmhbooks.com', 'academic'),
(100, 'Clark, M. (2008). Modern Italy 1871 to the Present (3rd ed.). Routledge. ISBN 978-1405823524.', 'https://www.routledge.com', 'academic'),
(100, 'Bosworth, R. J. B. (2002). Mussolini''s Italy: Life Under the Fascist Dictatorship. Allen Lane / Penguin. ISBN 978-0713996975.', 'https://www.penguin.co.uk', 'academic'),
(100, 'Lyttelton, A. (1973). The Seizure of Power: Fascism in Italy 1919-1929. Routledge. ISBN 978-0415139717.', 'https://www.routledge.com', 'academic');

-- 85 Regnum Siciliae 1130-1816 (Kingdom of Sicily)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(85, 'Norwich, J. J. (1970). The Kingdom in the Sun, 1130-1194. Longman. ISBN 978-0582127135.', 'https://www.routledge.com', 'academic'),
(85, 'Houben, H. (2002). Roger II of Sicily: A Ruler Between East and West. Cambridge University Press. ISBN 978-0521653329.', 'https://www.cambridge.org/9780521653329', 'academic'),
(85, 'Abulafia, D. (1988). Frederick II: A Medieval Emperor. Oxford University Press. ISBN 978-0195080407.', 'https://global.oup.com', 'academic'),
(85, 'Matthew, D. (1992). The Norman Kingdom of Sicily. Cambridge University Press. ISBN 978-0521269117.', 'https://www.cambridge.org/9780521269117', 'academic'),
(85, 'Mack Smith, D. (1968). A History of Sicily: Medieval Sicily 800-1713. Chatto & Windus. ISBN 978-0701144265.', 'https://www.penguin.co.uk', 'academic');

COMMIT;

SELECT entity_id, count(*) AS n_src FROM sources WHERE entity_id IN (738, 149, 56, 943, 95, 432, 434, 428, 100, 85) GROUP BY entity_id ORDER BY entity_id;
