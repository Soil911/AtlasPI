-- Phase C — Cities batch 2: 20 cities (Asia + Americas + Africa)

BEGIN;

INSERT INTO historical_cities (name_original, name_original_lang, latitude, longitude, founded_year, abandoned_year, city_type, population_peak, population_peak_year, confidence_score, sources, ethical_notes) VALUES

-- Asia
('Sukhōthai', 'th', 17.0125, 99.7036, 1238, 1438, 'CAPITAL', 30000, 1280, 0.90,
'Wyatt, D.K. (2003) Thailand: A Short History, Yale UP; Vickery, M. (1991) The Reign of Sūryavarman I and Royal Factionalism at Angkor, JSEAS 16; Hutchinson, E.W. (1968) 1688 Revolution in Siam',
NULL),
('Thăng Long', 'vi', 21.0285, 105.8542, 1010, NULL, 'CAPITAL', 50000, 1500, 0.90,
'Taylor, K.W. (2013) A History of the Vietnamese, Cambridge UP; Whitmore, J.K. (2010) The Rise of the Coast in Đại Việt, JSEAS 41; Nguyễn Vĩnh Phúc (2009) The Land and the People of Thăng Long-Hà Nội',
NULL),
('Lhasa/ལྷ་ས་', 'bo', 29.6500, 91.1000, 633, NULL, 'CAPITAL', 30000, 1700, 0.90,
'Snellgrove, D.L. & Richardson, H. (1968) A Cultural History of Tibet, Praeger; van Schaik, S. (2011) Tibet: A History, Yale UP; Beckwith, C.I. (1987) The Tibetan Empire in Central Asia, Princeton UP',
NULL),
('Xianyang/咸陽', 'zh', 34.3445, 108.7058, -350, -207, 'CAPITAL', 100000, -220, 0.90,
'Lewis, M.E. (2007) The Early Chinese Empires, Belknap; Bodde, D. (1986) The State and Empire of Ch''in, Cambridge History of China I; Loewe, M. (1986) The Former Han Dynasty, Cambridge History of China I',
NULL),
('Khanbaliq/汗八里', 'mn', 39.9042, 116.4074, 1271, 1368, 'CAPITAL', 600000, 1330, 0.90,
'Allsen, T.T. (2001) Culture and Conquest in Mongol Eurasia, Cambridge UP; Rossabi, M. (1988) Khubilai Khan, UC Press; Steinhardt, N.S. (1990) Chinese Imperial City Planning, U Hawai''i Press',
NULL),
('Borobudur', 'jv', -7.6079, 110.2038, 750, 1000, 'RELIGIOUS_CENTER', 10000, 850, 0.85,
'Miksic, J.N. (1990) Borobudur: Golden Tales of the Buddhas, Periplus; Soekmono, R. (1995) The Javanese Candi, Brill; Kempers, A.J.B. (1976) Ageless Borobudur, Servire',
NULL),

-- Americas (pre-Columbian + colonial)
('Tula', 'nci', 20.0628, -99.3422, 750, 1150, 'CAPITAL', 60000, 950, 0.85,
'Healan, D.M. (1989) Tula of the Toltecs: Excavations and Survey, U Iowa Press; Diehl, R.A. (1983) Tula: The Toltec Capital of Ancient Mexico, Thames & Hudson; Mastache, A.G. (2002) Ancient Tollan: Tula and the Toltec Heartland, U Press of Colorado',
NULL),
('Cholōllān', 'nci', 19.0586, -98.3027, -500, 1519, 'RELIGIOUS_CENTER', 100000, 800, 0.85,
'McCafferty, G.G. (2001) The Postclassic Cholula, Mexicon; Plunket, P. & Uruñuela, G. (2018) Mesoamerican Plazas, U Arizona Press; Lind, M. (2015) Ancient Zapotec Religion, U Press of Colorado',
NULL),
('Monte Albán', 'zap', 17.0438, -96.7677, -500, 850, 'CAPITAL', 25000, 250, 0.90,
'Blanton, R.E. (1978) Monte Albán: Settlement Patterns at the Ancient Zapotec Capital, Academic Press; Marcus, J. & Flannery, K.V. (1996) Zapotec Civilization, Thames & Hudson; Joyce, A.A. (2009) Mixtecs, Zapotecs, and Chatinos, Wiley-Blackwell',
NULL),
('Chan Chan', 'mch', -8.1100, -79.0747, 850, 1470, 'CAPITAL', 60000, 1300, 0.90,
'Moseley, M.E. & Day, K.C. (eds.) (1982) Chan Chan: Andean Desert City, U New Mexico Press; Conrad, G.W. & Demarest, A.A. (1984) Religion and Empire: Andean Heritage, Cambridge UP; Topic, J.R. (1990) Craft Production in the Kingdom of Chimor',
NULL),
('Cahuachi', 'qu', -14.8167, -75.1083, -100, 700, 'RELIGIOUS_CENTER', 6000, 100, 0.85,
'Silverman, H. (1993) Cahuachi in the Ancient Nasca World, U Iowa Press; Orefici, G. (2012) Cahuachi: Capital teocrática Nasca, U San Marcos; Conlee, C.A. (2016) Beyond the Nasca Lines, U Press of Florida',
NULL),
('Lima', 'es', -12.0464, -77.0428, 1535, NULL, 'CAPITAL', 100000, 1700, 0.95,
'Bromley, R.J. (2014) Storia di Lima coloniale, EHESS; Walker, C.F. (2008) Shaky Colonialism, Duke UP; Lockhart, J. (1968) Spanish Peru 1532-1560, U Wisconsin Press',
NULL),
('La Habana', 'es', 23.1136, -82.3666, 1519, NULL, 'PORT', 80000, 1800, 0.95,
'Lobo Montalvo, M.L. (2000) Havana: History and Architecture of a Romantic City, Monacelli Press; Schwartz, R. (1997) Pirates, Pirates, Pirates of the Caribbean, U New Mexico Press; Pérez, L.A. Jr. (2006) Cuba in the American Imagination, UNC Press',
NULL),

-- Africa
('Adulis', 'gez', 15.2667, 39.6500, -1000, 700, 'PORT', 20000, 200, 0.85,
'Munro-Hay, S.C. (1991) Aksum: An African Civilisation of Late Antiquity, Edinburgh UP; Phillipson, D.W. (2012) Foundations of an African Civilisation: Aksum and the Northern Horn 1000 BC-1300 AD, James Currey; Castiglia, G. (2019) Adulis: Archaeological Investigations, Pisa UP',
NULL),
('Napata', 'mer', 18.5167, 31.8333, -750, 350, 'CAPITAL', 15000, -600, 0.85,
'Welsby, D.A. (1996) The Kingdom of Kush, British Museum; Morkot, R.G. (2000) The Black Pharaohs: Egypt''s Nubian Rulers, Rubicon; Edwards, D.N. (2004) The Nubian Past, Routledge',
NULL),
('Marrākuš/مراكش', 'ar', 31.6295, -7.9811, 1062, NULL, 'CAPITAL', 200000, 1150, 0.95,
'Deverdun, G. (1959) Marrakech des origines à 1912, Éditions techniques; Wilbaux, Q. (2001) La médina de Marrakech, Karthala; Pennell, C.R. (2000) Morocco Since 1830, NYU Press',
NULL),
('Lalibela', 'gez', 12.0317, 39.0473, 1137, NULL, 'RELIGIOUS_CENTER', 10000, 1250, 0.90,
'Phillipson, D.W. (2009) Ancient Churches of Ethiopia, Yale UP; Munro-Hay, S.C. (2002) Ethiopia: The Unknown Land, I.B. Tauris; Heldman, M.E. (1992) Architectural Symbolism, JES 25',
NULL),
('Mogadishu', 'so', 2.0469, 45.3182, 900, NULL, 'PORT', 100000, 1500, 0.90,
'Jama, A. (1996) The Origins and Development of Mogadishu AD 1000-1850, Uppsala UP; Mukhtar, M.H. (2003) Historical Dictionary of Somalia, Scarecrow; Cassanelli, L.V. (1982) The Shaping of Somali Society, Penn Press',
NULL),
('Ŋgazargamu', 'kr', 13.6917, 11.6917, 1450, 1808, 'CAPITAL', 50000, 1650, 0.85,
'Hiribarren, V. (2017) A History of Borno, Hurst; Connah, G. (1981) Three Thousand Years in Africa: Man and His Environment in the Lake Chad Region of Nigeria, Cambridge UP; Lange, D. (1987) A Sudanic Chronicle: The Bornu Expeditions of Idrīs Alauma (1564-1576)',
NULL),
('Ouagadougou', 'mos', 12.3686, -1.5275, 1100, NULL, 'CAPITAL', 30000, 1700, 0.85,
'Izard, M. (1985) Gens du pouvoir, gens de la terre, Cambridge UP/MSH; Skinner, E.P. (1989) The Mossi of the Upper Volta, Stanford UP; Wilks, I. (1989) Wa and the Wala: Islam and Polity in Northwestern Ghana, Cambridge UP',
NULL);

COMMIT;

SELECT count(*) AS total_cities FROM historical_cities;
