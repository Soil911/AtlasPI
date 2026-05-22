-- Phase C — Cities batch 1: 20 historically major cities
-- 2026-05-22 v6.99.64

BEGIN;

INSERT INTO historical_cities (name_original, name_original_lang, latitude, longitude, founded_year, abandoned_year, city_type, population_peak, population_peak_year, confidence_score, sources, ethical_notes) VALUES

-- 1. Eridu (Sumerian first city, religious center)
('Eridu', 'sux', 30.8160, 45.9931, -5400, -600, 'RELIGIOUS_CENTER', 4000, -2900, 0.85,
'Crawford, H. (2004) Sumer and the Sumerians, Cambridge UP; Postgate, J.N. (1992) Early Mesopotamia, Routledge; Safar, F. et al. (1981) Eridu, Iraqi Government',
'Earliest known Sumerian city per cuneiform tradition; archaeologically attested from Ubaid 0 ca. 5400 BCE.'),

-- 2. Lagash (Sumerian)
('Lagaš', 'sux', 31.4156, 46.4081, -2700, -200, 'CAPITAL', 80000, -2400, 0.85,
'Maisels, C.K. (1990) The Emergence of Civilization, Routledge; Bauer, J. (1998) Early Dynastic IIIa-IIIb in: OBO 160/1; Hansen, D.P. (1992) Royal Building Activity at Sumerian Lagash, BA 55',
NULL),

-- 3. Mari (NE Syria, Bronze Age)
('Mari', 'akk', 34.5497, 40.8919, -2900, -1759, 'CAPITAL', 30000, -1800, 0.85,
'Margueron, J.-C. (2004) Mari: métropole de l''Euphrate, Picard; Heimpel, W. (2003) Letters to the King of Mari, Eisenbrauns; Charpin, D. (2008) Mari et le Proche-Orient, Académie des inscriptions',
NULL),

-- 4. Ebla (Bronze Age N Syria)
('Ebla', 'sem', 35.7975, 36.7958, -3500, -1600, 'CAPITAL', 30000, -2300, 0.85,
'Matthiae, P. (2010) Ebla: La città del trono, Einaudi; Pettinato, G. (1991) Ebla: A New Look at History, Johns Hopkins UP; Archi, A. (2015) Ebla and Its Archives, De Gruyter',
NULL),

-- 5. Knossos (Minoan Crete)
('Knōsós', 'grc', 35.2978, 25.1633, -3000, -1100, 'CAPITAL', 18000, -1700, 0.85,
'Cadogan, G. (1976) Palaces of Minoan Crete, Methuen; MacGillivray, J.A. (2000) Minotaur: Sir Arthur Evans and the Archaeology of the Minoan Myth, Hill and Wang; Driessen, J. (2018) An Archaeology of Forced Migration, Aegis 15',
NULL),

-- 6. Mycenae (Mycenaean Greek Bronze Age)
('Mukēnai', 'grc', 37.7308, 22.7556, -1700, -1100, 'CAPITAL', 30000, -1300, 0.85,
'Mylonas, G.E. (1966) Mycenae and the Mycenaean Age, Princeton UP; Wace, A.J.B. (1949) Mycenae: An Archaeological History and Guide; Shelmerdine, C.W. (2008) Cambridge Companion to Aegean Bronze Age',
NULL),

-- 7. Sparta (Greek city-state, military)
('Spartē', 'grc', 37.0810, 22.4239, -900, -396, 'CAPITAL', 35000, -480, 0.85,
'Cartledge, P. (2002) Sparta and Lakonia 1300-362 BC, Routledge; Kennell, N.M. (2010) Spartans: A New History, Wiley-Blackwell; Hodkinson, S. (2000) Property and Wealth in Classical Sparta, Duckworth',
NULL),

-- 8. Thēbai (Greek Thebes, Boeotia)
('Thēbai', 'grc', 38.3265, 23.3210, -1400, NULL, 'CAPITAL', 30000, -371, 0.85,
'Buck, R.J. (1979) A History of Boeotia, U Alberta Press; Demand, N. (1982) Thebes in the Fifth Century, Routledge; Symeonoglou, S. (1985) The Topography of Thebes, Princeton UP',
NULL),

-- 9. Mohenjo-Daro (Indus Valley)
('Mohenjo-Daro', 'snd', 27.3289, 68.1356, -2500, -1700, 'CAPITAL', 40000, -2300, 0.90,
'Mackay, E.J.H. (1938) Further Excavations at Mohenjo-Daro; Possehl, G.L. (2002) The Indus Civilization, AltaMira; Kenoyer, J.M. (1998) Ancient Cities of the Indus Valley, Oxford UP Karachi',
NULL),

-- 10. Harappa (Indus Valley)
('Harappa', 'snd', 30.6285, 72.8643, -2600, -1700, 'CAPITAL', 25000, -2200, 0.85,
'Kenoyer, J.M. (1998) Ancient Cities of the Indus Valley, Oxford UP; Wright, R.P. (2010) The Ancient Indus, Cambridge UP; Vats, M.S. (1940) Excavations at Harappa, Government of India',
NULL),

-- 11. Ujjain (ancient India, Avanti capital)
('Ujjayinī', 'sa', 23.1793, 75.7849, -700, NULL, 'CAPITAL', 80000, -400, 0.85,
'Thapar, R. (2002) Early India, Penguin; Chakrabarti, D.K. (1995) The Archaeology of Ancient Indian Cities, Oxford UP; Allchin, F.R. (1995) The Archaeology of Early Historic South Asia, Cambridge UP',
NULL),

-- 12. Mathura (Kushan + Hindu sacred)
('Mathurā', 'sa', 27.4924, 77.6737, -600, NULL, 'RELIGIOUS_CENTER', 200000, 200, 0.85,
'Sharma, R.C. (1976) Mathura Museum and Art; Dhavalikar, M.K. (2002) Mathura: Cult and Culture, Aryan Books; Srinivasan, D.M. (ed.) (1989) Mathurā: The Cultural Heritage, AIIS',
NULL),

-- 13. Pompeii (Roman city, volcanic preservation)
('Pompeii', 'la', 40.7497, 14.4863, -700, 79, 'MULTI_PURPOSE', 11000, 79, 0.95,
'Beard, M. (2008) The Fires of Vesuvius: Pompeii Lost and Found, Profile Books; Wallace-Hadrill, A. (1994) Houses and Society in Pompeii and Herculaneum, Princeton UP; Cooley, A. (2014) Pompeii and Herculaneum: A Sourcebook, Routledge',
NULL),

-- 14. Mediolanum/Milano (Roman + medieval Italian)
('Mediolanum', 'la', 45.4642, 9.1900, -600, NULL, 'CAPITAL', 130000, 300, 0.90,
'Cracco Ruggini, L. (1962) Economia e società nell''Italia annonaria, Giuffrè; Picard, C. (1990) La Lombardia post-romana, Hachette; Lubkin, G. (1994) A Renaissance Court: Milan under Galeazzo Maria Sforza, UC Press',
NULL),

-- 15. Petra (Nabataean rock-cut city)
('Reqem', 'nab', 30.3285, 35.4444, -300, 663, 'CAPITAL', 30000, 100, 0.90,
'Bowersock, G.W. (1983) Roman Arabia, Harvard UP; Markoe, G. (ed.) (2003) Petra Rediscovered, Abrams; Schmid, S.G. (2008) Petra and the Nabataeans, in: J.M. Tubb (ed.) Excavations in Jordan, BMP',
NULL),

-- 16. Tadmor/Palmyra (Syrian desert oasis)
('Tadmor', 'sem', 34.5519, 38.2683, -1900, 273, 'TRADE_HUB', 200000, 200, 0.90,
'Smith, A.M. II (2013) Roman Palmyra: Identity, Community, and State Formation, Oxford UP; Sartre, M. (2005) The Middle East under Rome, Belknap/Harvard; Edwell, P.M. (2008) Between Rome and Persia, Routledge',
NULL),

-- 17. Halab/Aleppo (Yamhad/Hittite/Seleucid/Hamdanid)
('Ḫalab', 'sem', 36.2021, 37.1343, -3000, NULL, 'CAPITAL', 200000, 1000, 0.90,
'Burns, R. (1999) Monuments of Syria: An Historical Guide, I.B. Tauris; Kennedy, H. (2007) The Great Arab Conquests, Da Capo; Marcus, A. (1989) The Middle East on the Eve of Modernity: Aleppo in the Eighteenth Century, Columbia UP',
NULL),

-- 18. Antiochia (Antioch on the Orontes, Seleucid + Byzantine)
('Antiókheia', 'grc', 36.2061, 36.1611, -300, 1268, 'CAPITAL', 500000, 100, 0.95,
'Downey, G. (1961) A History of Antioch in Syria, Princeton UP; Sandwell, I. (2007) Religious Identity in Late Antiquity, Cambridge UP; De Giorgi, A.U. (2016) Ancient Antioch, Cambridge UP',
NULL),

-- 19. Meroe (Kush capital, Nile)
('Meroe', 'mer', 16.9347, 33.7242, -800, 350, 'CAPITAL', 25000, -200, 0.90,
'Welsby, D.A. (1996) The Kingdom of Kush, British Museum; Shinnie, P.L. (1967) Meroe: A Civilization of the Sudan, Thames & Hudson; Edwards, D.N. (2004) The Nubian Past, Routledge',
NULL),

-- 20. Carthago Nova (Punic + Roman, modern Cartagena Spain)
('Qart-Ḥadašt', 'phn', 37.6087, -0.9863, -227, NULL, 'PORT', 30000, 50, 0.85,
'Carrasco, J. (2017) Cartagena en la antigüedad: Una ciudad portuaria, Universidad de Murcia; Mate, S.J. (1990) Carthage and the Iberian Peninsula, Iberian Archaeology Press; Ramallo Asensio, S. (2003) Carthago Nova, U Murcia',
NULL);

COMMIT;

SELECT count(*) AS total_cities FROM historical_cities;
