-- Phase C — Cities batch 5: 20 cities (Mesopotamia/Persia/N Africa/Central Asia/Russia)

BEGIN;

INSERT INTO historical_cities (name_original, name_original_lang, latitude, longitude, founded_year, abandoned_year, city_type, population_peak, population_peak_year, confidence_score, sources, ethical_notes) VALUES

-- Mesopotamia/Anatolia
('Hattuša', 'hit', 40.0167, 34.6167, -1600, -1180, 'CAPITAL', 50000, -1300, 0.95,
'Bryce, T. (2005) The Kingdom of the Hittites, Oxford UP; Schachner, A. (2009) Hattuscha: Auf der Suche nach dem sagenhaften Großreich der Hethiter, C.H. Beck; Beckman, G. (1999) Hittite Diplomatic Texts, SBL',
NULL),
('Nineveh (alt of Ninua)', 'akk', 36.3598, 43.1525, -6000, -612, 'CAPITAL', 150000, -650, 0.95,
'Russell, J.M. (1991) Sennacherib''s Palace Without Rival at Nineveh, U Chicago Press; Reade, J.E. (1998) Assyrian Sculpture, British Museum; Stronach, D. (1990) The Garden as a Political Statement, BSAI',
NULL),
('Ur', 'sux', 30.9626, 46.1031, -3800, -500, 'CAPITAL', 65000, -2030, 0.95,
'Woolley, L. (1934) Ur Excavations II: The Royal Cemetery, BM/Penn; Crawford, H. (2015) Ur: The City of the Moon God, Bloomsbury; van de Mieroop, M. (1992) Society and Enterprise in Old Babylonian Ur, Reimer',
NULL),
('Susa/شوش (Shushan)', 'elx', 32.1894, 48.2581, -4200, 1218, 'CAPITAL', 40000, -500, 0.95,
'Briant, P. (2002) From Cyrus to Alexander, Eisenbrauns; Potts, D.T. (1999) The Archaeology of Elam, Cambridge UP; Harper, P.O. (1992) The Royal City of Susa, Met Museum',
NULL),
('Ecbatana/همدان', 'fa', 34.7980, 48.5147, -700, NULL, 'CAPITAL', 80000, -500, 0.90,
'Brown, S.C. (1990) Achaemenid Settlement and Reconstruction in the Mehrdad, JESHO 33; Curtis, J. (2013) Ancient Iran from the Air, von Zabern; Shahbazi, A.S. (1980) An Achaemenid Symbol II',
NULL),

-- North Africa
('Kyrēnē/Cyrene', 'grc', 32.8254, 21.8585, -631, 365, 'TRADE_HUB', 100000, -200, 0.90,
'Boardman, J. (1980) The Greeks Overseas, Thames & Hudson; White, D. (1984) The Extramural Sanctuary of Demeter and Persephone at Cyrene, Penn Press; Chamoux, F. (1953) Cyrène sous la monarchie des Battiades, De Boccard',
NULL),
('Leptis Magna', 'la', 32.6383, 14.2920, -1100, 700, 'TRADE_HUB', 100000, 200, 0.90,
'Mattingly, D.J. (1995) Tripolitania, B.T. Batsford; Ward-Perkins, J.B. (1993) The Severan Buildings of Lepcis Magna, Society for Libyan Studies; Birley, A. (1988) Septimius Severus: The African Emperor, Yale UP',
NULL),
('Volubilis', 'la', 34.0741, -5.5550, -300, 800, 'CAPITAL', 20000, 200, 0.90,
'Risse, M. (ed.) (2001) Volubilis: Eine römische Stadt in Marokko, Schnell & Steiner; Akerraz, A. (2009) Volubilis et son territoire, INSAP; Lenoir, E. (2011) Le forum de Volubilis, École française de Rome',
NULL),

-- Central Asia (Silk Road)
('Merv/مرو', 'fa', 37.6450, 62.1939, -550, 1221, 'TRADE_HUB', 200000, 1150, 0.95,
'Hill, J.E. (2009) Through the Jade Gate to Rome, BookSurge; Lerner, J.D. (1999) The Impact of Seleucid Decline on the Eastern Iranian Plateau, Steiner; Williams, T. (2002) Ancient Merv: Queen of the Cities of Khurasan, UCL Press',
NULL),
('Otrar/Отырар', 'kk', 42.8500, 68.3000, 600, 1405, 'TRADE_HUB', 25000, 1200, 0.85,
'Akishev, K.A. & Baipakov, K.M. (1980) Otrar in the Karakhanid Period, Nauka; Frye, R.N. (1996) The Heritage of Central Asia, Markus Wiener; Soucek, S. (2000) A History of Inner Asia, Cambridge UP',
NULL),
('Talas/Тараз', 'kk', 42.9000, 71.3667, 200, NULL, 'TRADE_HUB', 40000, 1150, 0.85,
'Bartol''d, V.V. (1900/1968) Turkestan Down to the Mongol Invasion, Luzac; Frye, R.N. (1996) The Heritage of Central Asia, Markus Wiener; Beckwith, C.I. (1987) The Tibetan Empire in Central Asia, Princeton UP',
NULL),

-- Russia
('Kazan/Казань', 'tt', 55.7961, 49.1064, 1005, NULL, 'CAPITAL', 40000, 1500, 0.90,
'Khodarkovsky, M. (2002) Russia''s Steppe Frontier, Indiana UP; Romaniello, M.P. (2012) The Elusive Empire: Kazan and the Creation of Russia, U Wisconsin Press; Pelenski, J. (1974) Russia and Kazan: Conquest and Imperial Ideology 1438-1560, Mouton',
NULL),
('Astrakhan/Астрахань', 'ru', 46.3497, 48.0408, 1240, NULL, 'TRADE_HUB', 30000, 1700, 0.90,
'Khodarkovsky, M. (2002) Russia''s Steppe Frontier, Indiana UP; Trepavlov, V.V. (2001) The Formation and Early History of the Nogai Horde, Brill; Halperin, C.J. (1985) Russia and the Golden Horde, Indiana UP',
NULL),
('Smolensk/Смоленскъ', 'cu', 54.7818, 32.0401, 863, NULL, 'CAPITAL', 25000, 1500, 0.90,
'Martin, J. (1995) Medieval Russia 980-1584, Cambridge UP; Brückner, A. (1881) Geschichte Polens, Hertz; Avrich, P. (1972) Russian Rebels 1600-1800, Norton',
NULL),

-- East Africa
('Gondär/ጎንደር', 'gez', 12.6090, 37.4671, 1636, NULL, 'CAPITAL', 80000, 1700, 0.95,
'Crummey, D. (1972) Priests and Politicians: Protestant and Catholic Missions in Orthodox Ethiopia 1830-1868, Oxford UP; Pankhurst, R. (1982) History of Ethiopian Towns, Steiner; Berry, L.A. (1976) The Solomonic Monarchy at Gondar, PhD Boston',
NULL),
('Harär/ሐረር', 'om', 9.3137, 42.1280, 1500, NULL, 'TRADE_HUB', 40000, 1850, 0.90,
'Hecht, E.-D. (1982) The City of Harar and the Traditional Harari House, JES 15; Burton, R.F. (1856) First Footsteps in East Africa, Longman; Tareke, G. (1991) Ethiopia: Power and Protest, Cambridge UP',
NULL),

-- Indonesia
('Yogyakarta/ꦔꦪꦺꦴꦒꦾꦏꦂꦠ', 'jv', -7.7956, 110.3695, 1755, NULL, 'CAPITAL', 100000, 1900, 0.95,
'Ricklefs, M.C. (1998) The Seen and Unseen Worlds in Java, U Hawai''i Press; Carey, P. (2008) The Power of Prophecy: Prince Dipanagara and the End of an Old Order in Java, KITLV; Houben, V.J.H. (1994) Kraton and Kumpeni, KITLV',
NULL),
('Banten', 'jv', -6.0376, 106.1683, 1526, 1813, 'PORT', 100000, 1620, 0.90,
'Guillot, C. (1990) The Sultanate of Banten, Gramedia; Ota, A. (2006) Changes of Regime and Social Dynamics in West Java, Brill; Reid, A. (1993) Southeast Asia in the Age of Commerce II: Expansion and Crisis, Yale UP',
NULL),

-- Australia/Pacific (modern colonial)
('Sydney', 'en', -33.8688, 151.2093, 1788, NULL, 'PORT', 500000, 1900, 0.95,
'Karskens, G. (2009) The Colony: A History of Early Sydney, Allen & Unwin; Aplin, G. (1988) A Difficult Infant: Sydney Before Macquarie, NSW UP; Clark, M. (1962) A History of Australia I: From the Earliest Times, MUP',
NULL),
('Wellington/Te Whanganui-a-Tara', 'mi', -41.2865, 174.7762, 1840, NULL, 'CAPITAL', 50000, 1900, 0.95,
'McLean, G. (2000) Wellington: The First Hundred Years, Steele Roberts; Hamer, D. (1990) New Towns in the New World, Columbia UP; King, M. (2003) The Penguin History of New Zealand, Penguin',
NULL);

COMMIT;

SELECT count(*) AS total_cities FROM historical_cities;
