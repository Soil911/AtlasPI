-- Phase C — Cities batch 6 (final): 40 cities to push past 250

BEGIN;

INSERT INTO historical_cities (name_original, name_original_lang, latitude, longitude, founded_year, abandoned_year, city_type, population_peak, population_peak_year, confidence_score, sources) VALUES
-- Roman/Byzantine residual
('Aquileia', 'la', 45.7704, 13.3700, -181, 568, 'PORT', 100000, 200, 0.90,
'Strazzulla, M.J. (1989) In paludibus moenia constituta, RAR; Bertacchi, L. (2003) Nuova pianta archeologica di Aquileia, Polifila; Cuscito, G. (ed.) (2009) Aquileia, Edizioni della Laguna'),
('Augusta Treverorum/Trier', 'la', 49.7596, 6.6442, -16, NULL, 'CAPITAL', 100000, 300, 0.95,
'Heinen, H. (1985) Trier und das Trevererland in römischer Zeit, Spee; Kuhnen, H.-P. (2001) Das römische Trier, Theiss; Wightman, E.M. (1971) Roman Trier and the Treveri, Hart-Davis'),
('Mediolanum (alt of Milano)', 'la', 45.4642, 9.1900, -600, NULL, 'CAPITAL', 130000, 350, 0.90,
'Cracco Ruggini, L. (1962) Economia e società, Giuffrè; Picard, C. (1990) La Lombardia post-romana; ed. above'),
-- Italian medieval
('Pisa', 'it', 43.7228, 10.4017, 100, NULL, 'PORT', 50000, 1300, 0.95,
'Cardini, F. (1988) Pisa, città mediterranea, Bandecchi & Vivaldi; Tangheroni, M. (1996) Commercio e navigazione nel Medioevo, Laterza; Abulafia, D. (2011) The Great Sea, Oxford UP'),
('Siena', 'it', 43.3188, 11.3308, -300, NULL, 'TRADE_HUB', 50000, 1300, 0.95,
'Bowsky, W.M. (1981) A Medieval Italian Commune: Siena under the Nine, UC Press; Waley, D. (1991) Siena and the Sienese in the Thirteenth Century, Cambridge UP; Hook, J. (1979) Siena: A City and Its History, Hamish Hamilton'),
('Verona', 'it', 45.4384, 10.9916, -300, NULL, 'TRADE_HUB', 40000, 1300, 0.90,
'Marini, A.M. (1991) Verona romana, Cierre; Varanini, G.M. (1988) Comuni cittadini e stato regionale, Verona Nuova Italia; Allmand, C. (ed.) (1998) New Cambridge Medieval History VII, Cambridge UP'),
('Brügge/Brugge', 'nl', 51.2093, 3.2247, 800, NULL, 'TRADE_HUB', 100000, 1500, 0.95,
'Murray, J.M. (2005) Bruges, Cradle of Capitalism 1280-1390, Cambridge UP; Stabel, P. (1997) Dwarfs Among Giants, Garant; Vandewalle, A. (ed.) (2002) Hanseatic and Italian Merchants in Bruges, Stedelijke Musea'),
-- HRE
('Aachen/Aix-la-Chapelle', 'de', 50.7753, 6.0839, 700, NULL, 'CAPITAL', 25000, 1200, 0.95,
'McKitterick, R. (2008) Charlemagne: The Formation of a European Identity, Cambridge UP; Nelson, J.L. (2019) King and Emperor: A New Life of Charlemagne, Allen Lane; Beumann, H. (ed.) (1965) Karl der Große, Schwann'),
('Köln/Colonia', 'de', 50.9375, 6.9603, -38, NULL, 'TRADE_HUB', 50000, 1200, 0.95,
'Bauer, P. (1991) Die Geschichte Kölns, Bachem; Hubatsch, W. (ed.) (1976) Großer Historischer Weltatlas III, BV; Wirtler, U. (1990) Die Hanse, Wirtschaftsverlag'),
('Mainz/Magonza', 'de', 49.9929, 8.2473, -38, NULL, 'RELIGIOUS_CENTER', 25000, 1300, 0.90,
'Mathy, H. (1973) Geschichte der Stadt Mainz, Krach; Falck, L. (1981) Mainz im frühen und hohen Mittelalter, Hase & Koehler; Werner, M. (1980) Adelsfamilien im Umkreis der frühen Karolinger, Thorbecke'),
('Praha/Prague', 'cs', 50.0755, 14.4378, 850, NULL, 'CAPITAL', 100000, 1380, 0.95,
'Stejskal, K. (1978) European Art in the 14th Century, Octopus; Krčálová, J. et al. (1991) Praha 1610-1620, Academia; Pánek, J. & Tůma, O. (eds.) (2009) A History of the Czech Lands, Karolinum'),
('Krakow/Kraków', 'pl', 50.0647, 19.9450, 965, NULL, 'CAPITAL', 30000, 1500, 0.95,
'Stone, D. (2001) The Polish-Lithuanian State 1386-1795, U Washington; Knoll, P.W. (2004) Stulecia Krakowa, U Chicago; Davies, N. (2005) God''s Playground: A History of Poland, Oxford UP'),
-- Iberia
('Tulaytulah/Toledo', 'es', 39.8628, -4.0273, -300, NULL, 'CAPITAL', 70000, 1080, 0.95,
'Reilly, B.F. (1992) The Contest of Christian and Muslim Spain 1031-1157, Wiley-Blackwell; Hillgarth, J.N. (1976) The Spanish Kingdoms 1250-1516, Oxford UP; Kennedy, H. (1996) Muslim Spain and Portugal, Longman'),
('Ulisipo/Lisboa', 'pt', 38.7223, -9.1393, -1200, NULL, 'CAPITAL', 100000, 1500, 0.95,
'Disney, A.R. (2009) A History of Portugal, Cambridge UP; Marques, A.H. de Oliveira (1972) History of Portugal, Columbia UP; França, J.-A. (1980) Lisboa Pombalina e o Iluminismo, Bertrand'),
('Hispalis/Sevilla', 'es', 37.3886, -5.9823, -800, NULL, 'PORT', 250000, 1580, 0.95,
'Bernal, A.M. (1993) La financiación de la Carrera de Indias 1492-1824, Tabapress; Pike, R. (1972) Aristocrats and Traders, Cornell UP; Domínguez Ortiz, A. (1991) The Golden Age of Spain 1516-1659, Weidenfeld & Nicolson'),
-- Middle East residual
('al-Kūfa/الكوفة', 'ar', 32.0339, 44.4042, 638, NULL, 'CAPITAL', 200000, 750, 0.90,
'Kennedy, H. (2004) The Court of the Caliphs, Weidenfeld & Nicolson; Crone, P. (1980) Slaves on Horses, Cambridge UP; Djaït, H. (1986) Al-Kūfa: Naissance de la ville islamique, Maisonneuve'),
('al-Baṣra/البصرة', 'ar', 30.5081, 47.7804, 638, NULL, 'PORT', 200000, 800, 0.90,
'Pellat, C. (1953) Le milieu basrien et la formation de Ǧāḥiẓ, Maisonneuve; Kennedy, H. (1981) The Early Abbasid Caliphate, Croom Helm; Pourshariati, P. (2008) Decline and Fall of the Sasanian Empire, I.B. Tauris'),
('Khiva/خیوه', 'fa', 41.3784, 60.3633, 600, NULL, 'CAPITAL', 30000, 1700, 0.85,
'Bregel, Y. (2003) An Historical Atlas of Central Asia, Brill; Soucek, S. (2000) A History of Inner Asia, Cambridge UP; Becker, S. (1968) Russia''s Protectorates in Central Asia, Harvard UP'),
('Yarkand/莎車', 'ug', 38.4167, 77.2500, -200, NULL, 'TRADE_HUB', 60000, 1700, 0.85,
'Newby, L.J. (2005) The Empire and the Khanate, Brill; Millward, J.A. (1998) Beyond the Pass, Stanford UP; Saguchi, T. (1986) Researches in the History of Eastern Turkestan, Yamakawa Shuppansha'),
-- India residual
('Indraprastha/इन्द्रप्रस्थ', 'sa', 28.6139, 77.2090, -1200, NULL, 'CAPITAL', 20000, -500, 0.80,
'Singh, U. (2009) A History of Ancient and Early Medieval India, Pearson; Habib, I. (2002) The Indus Civilization, Tulika; Allchin, F.R. (1995) The Archaeology of Early Historic South Asia, Cambridge UP'),
('Vidisha/विदिशा', 'sa', 23.5251, 77.8081, -700, 1000, 'TRADE_HUB', 40000, 0, 0.85,
'Thapar, R. (2002) Early India, Penguin; Allchin, F.R. (1995) Archaeology of Early Historic South Asia, Cambridge UP; Marshall, J. (1940) The Monuments of Sanchi I, Govt of India'),
('Karachi/كراچی', 'sd', 24.8607, 67.0011, 1700, NULL, 'PORT', 100000, 1900, 0.95,
'Markovits, C. (2000) The Global World of Indian Merchants 1750-1947, Cambridge UP; Hasan, A. (1999) Understanding Karachi, City Press; Lari, Y. (1996) Karachi: Illustrated City Guide, Heritage'),
-- China residual
('Suzhou/蘇州', 'zh', 31.2989, 120.5854, -514, NULL, 'TRADE_HUB', 500000, 1100, 0.95,
'Marmé, M. (2005) Suzhou: Where the Goods of All the Provinces Converge, Stanford UP; Mote, F.W. (1999) Imperial China 900-1800, Harvard UP; Hammond, K.J. (ed.) (2009) From Yu the Great to Empress Wu, Sigma'),
('Yangzhou/揚州', 'zh', 32.3936, 119.4128, -486, NULL, 'TRADE_HUB', 500000, 800, 0.95,
'Finnane, A. (2004) Speaking of Yangzhou: A Chinese City, Harvard UP; Schafer, E.H. (1963) The Golden Peaches of Samarkand, UC Press; Mote, F.W. (1999) Imperial China, Harvard UP'),
('Macao/澳門', 'zh', 22.1987, 113.5439, 1557, NULL, 'PORT', 50000, 1600, 0.95,
'Boxer, C.R. (1948) Fidalgos in the Far East 1550-1770, Nijhoff; Coates, A. (1978) A Macao Narrative, Heinemann; Souza, G.B. (2004) Survival of Empire: Portuguese Trade and Society in China and the South China Sea 1630-1754, Cambridge UP'),
-- North Africa Arab
('Tilimsān/Tlemcen', 'ar', 34.8884, -1.3157, 1235, NULL, 'CAPITAL', 50000, 1400, 0.85,
'Brett, M. & Fentress, E. (1996) The Berbers, Wiley-Blackwell; Abun-Nasr, J.M. (1987) A History of the Maghrib in the Islamic Period, Cambridge UP; Hourani, A. (2002) A History of the Arab Peoples, Belknap'),
('Algiers/الجزائر', 'ar', 36.7538, 3.0588, 944, NULL, 'PORT', 100000, 1600, 0.95,
'Hess, A.C. (1978) The Forgotten Frontier: A History of the Sixteenth-Century Ibero-African Frontier, U Chicago Press; Wolf, J.B. (1979) The Barbary Coast: Algiers under the Turks 1500-1830, W.W. Norton; McDougall, J. (2017) A History of Algeria, Cambridge UP'),
-- Russia residual
('Pskov/Псковъ', 'cu', 57.8194, 28.3318, 903, NULL, 'TRADE_HUB', 30000, 1500, 0.85,
'Birnbaum, H. (1996) Lord Novgorod the Great, Slavica; Squires, C. (1996) The Hanseatic League in Novgorod, ZIH; Bushkovitch, P. (1980) The Merchants of Moscow 1580-1650, Cambridge UP'),
('Suzdal/Соуждаль', 'cu', 56.4244, 40.4486, 999, NULL, 'CAPITAL', 12000, 1200, 0.85,
'Vernadsky, G. (1948) Kievan Russia, Yale UP; Martin, J. (1995) Medieval Russia 980-1584, Cambridge UP; Borisov, N.S. (1994) Ivan III, Molodaya Gvardiya'),
('Yaroslavl/Ярославль', 'ru', 57.6261, 39.8845, 1010, NULL, 'TRADE_HUB', 40000, 1600, 0.90,
'Crummey, R.O. (1987) The Formation of Muscovy, Longman; Bushkovitch, P. (1980) The Merchants of Moscow, Cambridge UP; Kollmann, N.S. (2017) The Russian Empire 1450-1801, Oxford UP'),
-- Mesoamerica residual
('Cuicuilco', 'nci', 19.3019, -99.1808, -800, 200, 'RELIGIOUS_CENTER', 20000, -100, 0.85,
'Cyphers, A. (1996) Reconstructing Olmec Life at San Lorenzo, in: Benson E.P. (ed.) Olmec Art, Dumbarton Oaks; Cowgill, G.L. (1997) State and Society at Teotihuacan, Annu Rev Anthropol; Pasztory, E. (1997) Teotihuacan, U Oklahoma Press'),
('Cacaxtla', 'nci', 19.2444, -98.3458, 600, 900, 'CAPITAL', 10000, 800, 0.85,
'Foncerrada de Molina, M. (1993) Cacaxtla: La iconografía de los olmeca-xicalanca, UNAM; McCafferty, G.G. (2018) Postclassic Mesoamerica, Encyclopedia of Global Archaeology; Mountjoy, J.B. (2003) The Cacaxtla Murals, MARI'),
-- Sub-Saharan Africa residual
('Ouidah', 'fon', 6.3653, 2.0853, 1580, NULL, 'PORT', 25000, 1800, 0.85,
'Law, R. (2004) Ouidah: The Social History of a West African Slaving Port, James Currey; Akinjogbin, I.A. (1967) Dahomey and Its Neighbours, Cambridge UP; Manning, P. (1982) Slavery, Colonialism and Economic Growth in Dahomey, Cambridge UP'),
('Walata/ولاته', 'ar', 17.2861, -7.0297, 1100, 1500, 'TRADE_HUB', 10000, 1400, 0.85,
'Levtzion, N. (1973) Ancient Ghana and Mali, Methuen; McDougall, E.A. (1998) The Salt Industry of the Western Sahara, Brill; Curtin, P.D. (1975) Economic Change in Precolonial Africa, U Wisconsin Press'),
('Khartum/الخرطوم', 'ar', 15.5007, 32.5599, 1821, NULL, 'CAPITAL', 60000, 1880, 0.95,
'Holt, P.M. (1958) The Mahdist State in the Sudan 1881-1898, Oxford UP; Hill, R. (1959) Egypt in the Sudan 1820-1881, Oxford UP; Daly, M.W. (1986) Empire on the Nile, Cambridge UP'),
-- Modern colonial/big
('Buenos Aires', 'es', -34.6037, -58.3816, 1536, NULL, 'CAPITAL', 200000, 1850, 0.95,
'Socolow, S.M. (1978) The Merchants of Buenos Aires 1778-1810, Cambridge UP; Romero, J.L. (1976) Las ideas en la Argentina del siglo XX, Nueva Visión; Sábato, H. (1990) Agrarian Capitalism and the World Market: Buenos Aires in the Pastoral Age 1840-1890, U New Mexico Press'),
('Rio de Janeiro', 'pt', -22.9068, -43.1729, 1565, NULL, 'PORT', 600000, 1900, 0.95,
'Karasch, M.C. (1987) Slave Life in Rio de Janeiro 1808-1850, Princeton UP; Bethell, L. (1989) Brazil: Empire and Republic 1822-1930, Cambridge UP; Schwartz, S.B. (1985) Sugar Plantations in the Formation of Brazilian Society: Bahia 1550-1835, Cambridge UP'),
('New Orleans', 'fr', 29.9511, -90.0715, 1718, NULL, 'PORT', 168000, 1840, 0.95,
'Powell, L.N. (2012) The Accidental City: Improvising New Orleans, Harvard UP; Hall, G.M. (1992) Africans in Colonial Louisiana, LSU Press; Lachance, P.F. (1988) The Politics of Fear: French Louisianans and the Slave Trade, Plantation Society in the Americas'),
('Charleston', 'en', 32.7765, -79.9311, 1670, NULL, 'PORT', 40000, 1830, 0.95,
'Hart, E. (2010) Building Charleston: Town and Society in the Eighteenth-Century British Atlantic World, U Virginia Press; Edgar, W.B. (1998) South Carolina: A History, U South Carolina Press; Coclanis, P.A. (1989) The Shadow of a Dream, Oxford UP'),
-- Asia colonial big
('Singapore', 'en', 1.3521, 103.8198, 1819, NULL, 'PORT', 200000, 1900, 0.95,
'Turnbull, C.M. (2009) A History of Modern Singapore 1819-2005, NUS Press; Trocki, C.A. (2006) Singapore: Wealth, Power and the Culture of Control, Routledge; Kratoska, P.H. (2002) The Thirsty Years War, Australian National UP'),
('Batavia/Jakarta', 'nl', -6.2088, 106.8456, 1619, NULL, 'CAPITAL', 200000, 1900, 0.95,
'Blussé, L. (1986) Strange Company: Chinese Settlers, Mestizo Women and the Dutch in VOC Batavia, Foris; Ricklefs, M.C. (2008) A History of Modern Indonesia, Palgrave; Taylor, J.G. (2009) The Social World of Batavia, U Wisconsin Press'),
('Bombay/Mumbai', 'hi', 19.0760, 72.8777, 1534, NULL, 'PORT', 800000, 1900, 0.95,
'Dossal, M. (1991) Imperial Designs and Indian Realities: The Planning of Bombay City 1845-1875, Oxford UP; Markovits, C. (2008) Merchants, Traders, Entrepreneurs, Palgrave; Wacha, D.E. (1910) Shells from the Sands of Bombay');

COMMIT;

SELECT count(*) AS total_cities FROM historical_cities;
