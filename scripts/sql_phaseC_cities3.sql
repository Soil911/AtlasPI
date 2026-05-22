-- Phase C — Cities batch 3: 20 cities (Europe + ME + Russia + Korea + Japan)

BEGIN;

INSERT INTO historical_cities (name_original, name_original_lang, latitude, longitude, founded_year, abandoned_year, city_type, population_peak, population_peak_year, confidence_score, sources, ethical_notes) VALUES

-- Mediterranean/Europe
('Lutetia', 'la', 48.8566, 2.3522, -250, NULL, 'CAPITAL', 50000, 300, 0.95,
'Sutherland, C.H.V. (1973) The Roman Imperial Coinage VI: Diocletian to Maximinus; Le Roux, P. (2014) Lutetia, Tallandier; Velay, P. (1992) From Lutetia to Paris, Paris-Musées',
NULL),
('Camulodunum', 'la', 51.8959, 0.8917, -50, NULL, 'CAPITAL', 25000, 50, 0.90,
'Crummy, P. (1997) City of Victory: The Story of Colchester, Colchester Archaeological Trust; Frere, S. (1987) Britannia, Routledge; Salway, P. (1981) Roman Britain, Oxford UP',
NULL),
('Londinium', 'la', 51.5074, -0.1278, 47, NULL, 'TRADE_HUB', 60000, 100, 0.95,
'Perring, D. (1991) Roman London, Routledge; Merrifield, R. (1983) London City of the Romans, BT Batsford; Schofield, J. (2011) London 1100-1600, Oxford UP',
NULL),
('Ravenna', 'la', 44.4173, 12.2035, -89, NULL, 'CAPITAL', 50000, 550, 0.95,
'Deliyannis, D.M. (2010) Ravenna in Late Antiquity, Cambridge UP; Augenti, A. (2011) Classe: Indagini sul potenziale archeologico di una città scomparsa, Ante Quem; Brown, T.S. (1984) Gentlemen and Officers: Imperial Administration in Byzantine Italy, BSR',
NULL),
('Lugdunum', 'la', 45.7640, 4.8357, -43, NULL, 'CAPITAL', 80000, 200, 0.95,
'Audin, A. (1979) Lyon, miroir de Rome dans les Gaules, Fayard; Pelletier, A. (1999) Histoire de Lyon: De Lugdunum à Lyon, Faton; Burnand, Y. (2010) Lyon, capitale des Gaules, Champion',
NULL),

-- Eastern Europe / Russia
('Moskva/Москва', 'ru', 55.7558, 37.6173, 1147, NULL, 'CAPITAL', 200000, 1700, 0.95,
'Hellie, R. (1971) Enserfment and Military Change in Muscovy, U Chicago Press; Kollmann, N.S. (1987) Kinship and Politics: The Making of the Muscovite Political System 1345-1547, Stanford UP; Crummey, R.O. (1987) The Formation of Muscovy 1304-1613, Longman',
NULL),
('Vladimir/Володимѣрь', 'cu', 56.1290, 40.4070, 1108, NULL, 'CAPITAL', 30000, 1250, 0.90,
'Martin, J. (1995) Medieval Russia 980-1584, Cambridge UP; Vernadsky, G. (1953) The Mongols and Russia, Yale UP; Crummey, R.O. (1987) The Formation of Muscovy, Longman',
NULL),
('Tver/Тверь', 'ru', 56.8587, 35.9176, 1135, NULL, 'CAPITAL', 25000, 1400, 0.85,
'Halperin, C.J. (1985) Russia and the Golden Horde, Indiana UP; Martin, J. (1995) Medieval Russia 980-1584, Cambridge UP; Klyuchevsky, V.O. (1968) A Course in Russian History, M.E. Sharpe',
NULL),

-- Korea/Japan
('Gyeongju/경주', 'ko', 35.8562, 129.2247, -57, NULL, 'CAPITAL', 200000, 850, 0.95,
'Best, J.W. (2007) A History of the Early Korean Kingdom of Paekche, Harvard UP; Lee, P.H. (ed.) (1993) Sourcebook of Korean Civilization, Columbia UP; Henthorn, W.E. (1971) A History of Korea, Free Press',
NULL),
('P''yŏngyang/평양', 'ko', 39.0392, 125.7625, -1500, NULL, 'CAPITAL', 100000, 600, 0.90,
'Pai, H.I. (2000) Constructing Korean Origins, Harvard UP; Lee, K.-B. (1984) A New History of Korea, Harvard UP; Eckert, C.J. et al. (1990) Korea Old and New: A History, Korea Institute Harvard',
NULL),
('Hanseong/한성/漢城', 'ko', 37.5665, 126.9780, 1394, NULL, 'CAPITAL', 200000, 1700, 0.95,
'Henthorn, W.E. (1971) A History of Korea, Free Press; Lee, K.-B. (1984) A New History of Korea, Harvard UP; Palais, J.B. (1996) Confucian Statecraft and Korean Institutions, U Washington Press',
NULL),
('Ōsaka/大坂', 'ja', 34.6937, 135.5023, 645, NULL, 'TRADE_HUB', 380000, 1700, 0.95,
'Hauser, W.B. (1974) Economic Institutional Change in Tokugawa Japan: Ōsaka and the Kinai Cotton Trade, Cambridge UP; Mass, J.P. & Hauser, W.B. (eds.) (1985) The Bakufu in Japanese History, Stanford UP; McClain, J.L. & Wakita, O. (eds.) (1999) Osaka: The Merchants'' Capital of Early Modern Japan, Cornell UP',
NULL),
('Kamakura/鎌倉', 'ja', 35.3192, 139.5469, 1185, 1333, 'CAPITAL', 200000, 1250, 0.90,
'Souyri, P.-F. (2001) The World Turned Upside Down: Medieval Japanese Society, Columbia UP; Friday, K.F. (2004) Samurai, Warfare and the State in Early Medieval Japan, Routledge; Mass, J.P. (1989) Lordship and Inheritance in Early Medieval Japan, Stanford UP',
NULL),

-- Middle East / Persia
('Tabrīz/تبریز', 'fa', 38.0962, 46.2738, -714, NULL, 'CAPITAL', 200000, 1330, 0.90,
'Pfeiffer, J. (ed.) (2014) Politics, Patronage and the Transmission of Knowledge in 13th-15th Century Tabriz, Brill; Werner, C. (2000) An Iranian Town in Transition: A Social and Economic History of the Elites of Tabriz 1747-1848, Harrassowitz; Floor, W. (2004) Public Health in Qajar Iran, Mage',
NULL),
('Mashhad/مشهد', 'fa', 36.2605, 59.6168, 818, NULL, 'RELIGIOUS_CENTER', 150000, 1700, 0.90,
'Modarressi, H. (1993) Crisis and Consolidation in the Formative Period of Shi''ite Islam, Princeton UP; Algar, H. (2002) Religion and State in Iran, UC Press; Krusinski, T.J. (1733) History of the Late Revolutions of Persia',
NULL),
('Makka/مكة', 'ar', 21.4225, 39.8262, -2000, NULL, 'RELIGIOUS_CENTER', 150000, 1900, 0.90,
'Peters, F.E. (1994) Mecca: A Literary History of the Muslim Holy Land, Princeton UP; Crone, P. (1987) Meccan Trade and the Rise of Islam, Princeton UP; Hawting, G.R. (1999) The Idea of Idolatry and the Emergence of Islam, Cambridge UP',
NULL),
('Madīna/المدينة', 'ar', 24.4708, 39.6122, -1500, NULL, 'RELIGIOUS_CENTER', 50000, 700, 0.90,
'Lecker, M. (1995) Muslims, Jews and Pagans: Studies on Early Islamic Medina, Brill; Donner, F.M. (1981) The Early Islamic Conquests, Princeton UP; Watt, W.M. (1956) Muhammad at Medina, Oxford UP',
NULL),

-- North Atlantic / Trade
('København', 'da', 55.6761, 12.5683, 1167, NULL, 'CAPITAL', 30000, 1500, 0.95,
'Knudsen, T. (1988) Storbyen støbes - København mellem kaos og byplan 1840-1917, Akademisk Forlag; Hyldtoft, O. (1984) Københavns industrialisering 1840-1914, Systime; Lyngby, T. (1985) Stamhuset Lyngbygaard, Universitetsforlaget',
NULL),
('Lübeck', 'de', 53.8654, 10.6866, 1143, NULL, 'TRADE_HUB', 25000, 1500, 0.95,
'Dollinger, P. (1970) The German Hansa, Stanford UP; Hammel-Kiesow, R. (2000) Die Hanse, C.H. Beck; Selzer, S. (2010) Die mittelalterliche Hanse, WBG',
NULL),
('Antwerpen/Anvers', 'nl', 51.2194, 4.4025, 700, NULL, 'PORT', 100000, 1560, 0.95,
'van der Wee, H. (1963) The Growth of the Antwerp Market and the European Economy, Nijhoff; Soly, H. (1977) Urbanisme en kapitalisme te Antwerpen in de 16de eeuw, Pro Civitate; Limberger, M. (2008) Sixteenth-Century Antwerp and its Rural Surroundings, Brepols',
NULL);

COMMIT;

SELECT count(*) AS total_cities FROM historical_cities;
