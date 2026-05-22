-- Phase C — Cities batch 4: 20 cities (India + SE Asia + Pre-Columbian + colonial)

BEGIN;

INSERT INTO historical_cities (name_original, name_original_lang, latitude, longitude, founded_year, abandoned_year, city_type, population_peak, population_peak_year, confidence_score, sources, ethical_notes) VALUES

-- India
('Hampi/ಹಂಪೆ', 'kn', 15.3350, 76.4600, 1336, 1565, 'CAPITAL', 500000, 1500, 0.95,
'Stein, B. (1989) Vijayanagara, Cambridge UP; Verghese, A. (1995) Religious Traditions at Vijayanagara, Manohar; Fritz, J.M. & Michell, G. (2003) Hampi Vijayanagara, India Book House',
NULL),
('Thanjāvūr/தஞ்சாவூர்', 'ta', 10.7870, 79.1378, 850, NULL, 'CAPITAL', 200000, 1010, 0.90,
'Stein, B. (1980) Peasant State and Society in Medieval South India, Oxford UP; Sastri, K.A.N. (1955) The Cōḷas, U Madras; Veluthat, K. (1993) The Political Structure of Early Medieval South India, Orient Longman',
NULL),
('Kanchipuram/காஞ்சிபுரம்', 'ta', 12.8342, 79.7036, 200, NULL, 'RELIGIOUS_CENTER', 80000, 700, 0.90,
'Hari Rao, V.N. (1976) The Śrīrangam Temple, Sri Venkateswara UP; Mahalingam, T.V. (1969) Kāñcīpuram in Early South Indian History, Asia Publishing; Hudson, D.D. (2008) The Body of God: An Emperor''s Palace for Krishna in Eighth-Century Kanchipuram, Oxford UP',
NULL),
('Jaipur/जयपुर', 'hi', 26.9124, 75.7873, 1727, NULL, 'CAPITAL', 200000, 1820, 0.95,
'Sachdev, V. & Tillotson, G. (2002) Building Jaipur: The Making of an Indian City, Reaktion; Asher, C.B. (1992) Architecture of Mughal India, Cambridge UP; Roy, A. (2011) The Making of a Princely State: Jaipur in the 18th Century, Cambridge UP',
NULL),
('Murshidabad/মুর্শিদাবাদ', 'bn', 24.1817, 88.2685, 1704, NULL, 'CAPITAL', 700000, 1750, 0.90,
'Marshall, P.J. (1976) East Indian Fortunes: The British in Bengal in the Eighteenth Century, Oxford UP; Datta, K.K. (1948) Studies in the History of Bengal Subah, Calcutta UP; Sinha, N.K. (1956) The Economic History of Bengal, Firma KLM',
NULL),

-- SE Asia
('Pegu/ပဲခူး', 'my', 17.3299, 96.4810, 825, NULL, 'CAPITAL', 150000, 1500, 0.85,
'Lieberman, V. (2003) Strange Parallels: SE Asia in Global Context, Cambridge UP; Aung-Thwin, M. (2005) The Mists of Rāmañña, U Hawai''i Press; Charney, M.W. (2006) Powerful Learning, U Michigan',
NULL),
('Phnom Penh', 'km', 11.5564, 104.9282, 1372, NULL, 'CAPITAL', 100000, 1600, 0.95,
'Chandler, D.P. (2018) A History of Cambodia, Westview; Edwards, P. (2007) Cambodge: The Cultivation of a Nation, U Hawai''i Press; Tully, J. (2002) France on the Mekong, U Press of America',
NULL),
('Manila', 'es', 14.5995, 120.9842, 1571, NULL, 'CAPITAL', 200000, 1800, 0.95,
'Reed, R.R. (1978) Colonial Manila: The Context of Hispanic Urbanism, UC Press; Doeppers, D.F. (1984) Manila 1900-1941, Yale UP; Phelan, J.L. (1959) The Hispanization of the Philippines, U Wisconsin Press',
NULL),
('Hue/Huế', 'vi', 16.4637, 107.5909, 1306, NULL, 'CAPITAL', 100000, 1830, 0.90,
'Woodside, A. (1971) Vietnam and the Chinese Model, Harvard UP; Choi, B.W. (2004) Southern Vietnam under the Reign of Minh Mạng, Cornell SEAP; Vu, H.T.M. (2017) The Origins of the Vietnam War, U North Carolina Press',
NULL),

-- Africa (Sub-Saharan + Sahel)
('Great Zimbabwe', 'sn', -20.2667, 30.9333, 1100, 1450, 'CAPITAL', 18000, 1300, 0.95,
'Huffman, T.N. (2007) Handbook to the Iron Age, U KwaZulu-Natal Press; Pikirayi, I. (2001) The Zimbabwe Culture, AltaMira; Beach, D.N. (1980) The Shona and Zimbabwe 900-1850, Mambo',
NULL),
('Mapungubwe', 'sn', -22.2089, 29.3958, 1075, 1300, 'CAPITAL', 5000, 1250, 0.90,
'Huffman, T.N. (2005) Mapungubwe: Ancient African Civilisation on the Limpopo, Wits UP; Calabrese, J.A. (2007) The Emergence of Social and Political Complexity, BAR; Manyanga, M. (2007) Resilient Landscapes: Socio-Environmental Dynamics in the Shashi-Limpopo Basin, Uppsala UP',
NULL),
('Ife/Ilé-Ifẹ̀ (Yoruba)', 'yo', 7.4905, 4.5521, 800, NULL, 'RELIGIOUS_CENTER', 30000, 1300, 0.90,
'Ogundiran, A. (2020) The Yoruba: A New History, Indiana UP; Drewal, H.J. & Pemberton, J. (1989) Yoruba: Nine Centuries of African Art and Thought, Abrams; Bascom, W.R. (1969) The Yoruba of Southwestern Nigeria, Holt Rinehart',
NULL),
('Kumasi', 'tw', 6.6885, -1.6244, 1700, NULL, 'CAPITAL', 25000, 1820, 0.90,
'Wilks, I. (1975) Asante in the Nineteenth Century, Cambridge UP; McCaskie, T.C. (1995) State and Society in Pre-Colonial Asante, Cambridge UP; Wilks, I. (1993) Forests of Gold, Ohio UP',
NULL),
('Abomey', 'fon', 7.1859, 1.9911, 1610, 1894, 'CAPITAL', 30000, 1850, 0.90,
'Law, R. (1991) The Slave Coast of West Africa 1550-1750, Oxford UP; Bay, E.G. (1998) Wives of the Leopard, Virginia UP; Manning, P. (1982) Slavery, Colonialism and Economic Growth in Dahomey, Cambridge UP',
NULL),

-- North America (colonial-era)
('New Amsterdam', 'nl', 40.7128, -74.0060, 1626, 1664, 'TRADE_HUB', 1500, 1660, 0.95,
'Shorto, R. (2004) The Island at the Center of the World, Doubleday; Rink, O.A. (1986) Holland on the Hudson, Cornell UP; Jacobs, J. (2009) The Colony of New Netherland, Cornell UP',
NULL),
('Mexico City (post-conquest)', 'es', 19.4326, -99.1332, 1521, NULL, 'CAPITAL', 200000, 1800, 0.95,
'Lockhart, J. (1992) The Nahuas After the Conquest, Stanford UP; Boyer, R. (1973) La Gran Inundación de México 1629-1638, SEP; Hoberman, L.S. (1991) Mexico''s Merchant Elite 1590-1660, Duke UP',
NULL),
('Boston', 'en', 42.3601, -71.0589, 1630, NULL, 'PORT', 80000, 1800, 0.95,
'Bailyn, B. (1955) The New England Merchants in the Seventeenth Century, Harvard UP; Nash, G.B. (1979) The Urban Crucible: Social Change, Political Consciousness, and the Origins of the American Revolution, Harvard UP; Vickers, D. (1994) Farmers and Fishermen, UNC Press',
NULL),

-- Pacific
('Honoruru/Honolulu', 'haw', 21.3099, -157.8581, 1200, NULL, 'PORT', 14000, 1850, 0.85,
'Kamakau, S.M. (1992) Ruling Chiefs of Hawaii, Kamehameha Schools; Kirch, P.V. (2010) How Chiefs Became Kings, UC Press; Sahlins, M. (1992) Historical Ethnography I: Anahulu, U Chicago Press',
NULL),
('Lapita village (Talasea/Watom)', 'mh', -5.0500, 150.7500, -1500, -500, 'OTHER', 1000, -1000, 0.80,
'Kirch, P.V. (1997) The Lapita Peoples, Wiley-Blackwell; Specht, J. & Anson, D. (1988) Excavations on Watom Island, RAMP; Sand, C. (2010) Lapita Calédonien, Société des Océanistes',
NULL),
('Nan Madol', 'pon', 6.8425, 158.3331, 1100, 1628, 'CAPITAL', 25000, 1450, 0.90,
'Ayres, W.S. (1990) Nan Madol Pohnpei Stone Cities, in: Davidson, J. et al. (eds.) Oceanic Culture History; McCoy, M.D. & Athens, J.S. (2011) Sourcing the Stones, Asian Perspectives; Hanlon, D. (1988) Upon a Stone Altar, U Hawai''i Press',
NULL);

COMMIT;

SELECT count(*) AS total_cities FROM historical_cities;
