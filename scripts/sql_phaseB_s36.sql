-- Phase B — S36: 10 entities, +5 academic sources each

BEGIN;

-- 212 Virreinato de Nueva Granada 1717-1819
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(212, 'McFarlane, A. (1993). Colombia Before Independence: Economy, Society, and Politics under Bourbon Rule. Cambridge University Press. ISBN 978-0521416412.', 'https://www.cambridge.org/9780521416412', 'academic'),
(212, 'Phelan, J. L. (1978). The People and the King: The Comunero Revolution in Colombia, 1781. University of Wisconsin Press. ISBN 978-0299074609.', 'https://uwpress.wisc.edu/books/0167.htm', 'academic'),
(212, 'Lynch, J. (1973). The Spanish American Revolutions, 1808-1826. Norton. ISBN 978-0393007473.', 'https://wwnorton.com/books/9780393007473', 'academic'),
(212, 'Earle, R. (2000). Spain and the Independence of Colombia 1810-1825. University of Exeter Press. ISBN 978-0859895125.', 'https://www.exeter.ac.uk/press', 'academic'),
(212, 'Bushnell, D. (1993). The Making of Modern Colombia: A Nation in Spite of Itself. University of California Press. ISBN 978-0520082892.', 'https://www.ucpress.edu/book/9780520082892', 'academic');

-- 32 Empire of Japan 1868-1947
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(32, 'Jansen, M. B. (2000). The Making of Modern Japan. Belknap Press of Harvard University Press. ISBN 978-0674003347.', 'https://www.hup.harvard.edu/catalog.php?isbn=9780674003347', 'academic'),
(32, 'Beasley, W. G. (1987). Japanese Imperialism, 1894-1945. Oxford University Press. ISBN 978-0198221685.', 'https://global.oup.com', 'academic'),
(32, 'Gluck, C. (1985). Japan''s Modern Myths: Ideology in the Late Meiji Period. Princeton University Press. ISBN 978-0691008127.', 'https://press.princeton.edu/books/paperback/9780691008127/', 'academic'),
(32, 'Pyle, K. B. (2007). Japan Rising: The Resurgence of Japanese Power and Purpose. PublicAffairs. ISBN 978-1586484171.', 'https://www.publicaffairsbooks.com', 'academic'),
(32, 'Dower, J. W. (1999). Embracing Defeat: Japan in the Wake of World War II. W. W. Norton. ISBN 978-0393046861.', 'https://wwnorton.com', 'academic');

-- 423 Regno di Sardegna 1720-1861
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(423, 'Mack Smith, D. (1971). Italy: A Modern History. University of Michigan Press. ISBN 978-0472071999.', 'https://www.press.umich.edu', 'academic'),
(423, 'Romeo, R. (1969). Cavour e il suo tempo, 3 vols. Laterza. ISBN 978-8842002772.', 'https://www.laterza.it', 'academic'),
(423, 'Hearder, H. (1983). Cavour. Longman. ISBN 978-0582490703.', 'https://www.routledge.com', 'academic'),
(423, 'Riall, L. (2009). Risorgimento: The History of Italy from Napoleon to Nation-State. Palgrave Macmillan. ISBN 978-0230216709.', 'https://link.springer.com', 'academic'),
(423, 'Beales, D. & Biagini, E. F. (2002). The Risorgimento and the Unification of Italy. Longman. ISBN 978-0582369580.', 'https://www.routledge.com', 'academic');

-- 421 Granducato di Toscana 1569-1859
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(421, 'Diaz, F. (1976). Il Granducato di Toscana: I Medici. UTET. ISBN 978-8802027012.', 'https://www.utet.com', 'academic'),
(421, 'Pesendorfer, F. (1989). Il Granducato di Toscana sotto i Lorena. Le Lettere. ISBN 978-8871661124.', 'https://www.lelettere.it', 'academic'),
(421, 'Litchfield, R. B. (1986). Emergence of a Bureaucracy: The Florentine Patricians, 1530-1790. Princeton University Press. ISBN 978-0691054360.', 'https://press.princeton.edu', 'academic'),
(421, 'Brown, J. (1989). In the Shadow of Florence: Provincial Society in Renaissance Pescia. Oxford University Press. ISBN 978-0195059199.', 'https://global.oup.com', 'academic'),
(421, 'Wandruszka, A. (1987). Pietro Leopoldo: Un grande riformatore. Edizioni Sansoni.', 'https://www.giuntieditore.it', 'academic');

-- 523 Império do Brasil 1822-1889
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(523, 'Barman, R. J. (1988). Brazil: The Forging of a Nation, 1798-1852. Stanford University Press. ISBN 978-0804714372.', 'https://www.sup.org', 'academic'),
(523, 'Barman, R. J. (1999). Citizen Emperor: Pedro II and the Making of Brazil, 1825-91. Stanford University Press. ISBN 978-0804735100.', 'https://www.sup.org', 'academic'),
(523, 'Skidmore, T. E. (1999). Brazil: Five Centuries of Change. Oxford University Press. ISBN 978-0195058093.', 'https://global.oup.com', 'academic'),
(523, 'Bethell, L. (ed.) (1989). Brazil: Empire and Republic, 1822-1930. Cambridge University Press. ISBN 978-0521369930.', 'https://www.cambridge.org/9780521369930', 'academic'),
(523, 'Levine, R. M. (1999). The History of Brazil. Greenwood Press. ISBN 978-0313305849.', 'https://www.abc-clio.com', 'academic');

-- 407 Al-Dawla al-Alawiyya (Alaouite dynasty Morocco) 1631-present
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(407, 'Pennell, C. R. (2000). Morocco Since 1830: A History. New York University Press. ISBN 978-0814766774.', 'https://nyupress.org', 'academic'),
(407, 'Park, T. K. & Boum, A. (2006). Historical Dictionary of Morocco (2nd ed.). Scarecrow Press. ISBN 978-0810853416.', 'https://rowman.com/ISBN/9780810853416', 'academic'),
(407, 'Laroui, A. (1977). Les origines sociales et culturelles du nationalisme marocain (1830-1912). Maspero. ISBN 978-2707109071.', 'https://www.editionsladecouverte.fr', 'academic'),
(407, 'El Mansour, M. (1990). Morocco in the Reign of Mawlay Sulayman. Middle East and North African Studies Press. ISBN 978-0906559239.', 'https://www.worldcat.org/oclc/22310007', 'academic'),
(407, 'Maghraoui, D. (ed.) (2013). Revisiting the Colonial Past in Morocco. Routledge. ISBN 978-0415638470.', 'https://www.routledge.com/9780415638470', 'academic');

-- 361 Rattanakosin (Siam/Thailand 1782-1932)
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(361, 'Wyatt, D. K. (2003). Thailand: A Short History (2nd ed.). Yale University Press. ISBN 978-0300084757.', 'https://yalebooks.yale.edu/9780300084757', 'academic'),
(361, 'Terwiel, B. J. (2005). Thailand''s Political History: From the Fall of Ayutthaya to Recent Times. River Books. ISBN 978-9749863084.', 'https://www.riverbooksbk.com', 'academic'),
(361, 'Baker, C. & Phongpaichit, P. (2014). A History of Thailand (3rd ed.). Cambridge University Press. ISBN 978-1316007334.', 'https://www.cambridge.org/9781316007334', 'academic'),
(361, 'Mead, K. K. (2004). The Rise and Decline of Thai Absolutism. RoutledgeCurzon. ISBN 978-0415404594.', 'https://www.routledge.com', 'academic'),
(361, 'Mishra, P. K. (2010). A Contemporary History of Thailand. Concept Publishing. ISBN 978-8180696121.', 'https://www.conceptpub.com', 'academic');

-- 847 Achaemenid هخامنشیان -550/-330
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(847, 'Briant, P. (2002). From Cyrus to Alexander: A History of the Persian Empire. Eisenbrauns. ISBN 978-1575060316.', 'https://www.eisenbrauns.com', 'academic'),
(847, 'Wiesehöfer, J. (2001). Ancient Persia: From 550 BC to 650 AD. I.B. Tauris. ISBN 978-1860646751.', 'https://www.bloomsbury.com', 'academic'),
(847, 'Olmstead, A. T. (1948). History of the Persian Empire. University of Chicago Press. ISBN 978-0226627755.', 'https://press.uchicago.edu', 'academic'),
(847, 'Kuhrt, A. (2007). The Persian Empire: A Corpus of Sources from the Achaemenid Period. Routledge. ISBN 978-0415436281.', 'https://www.routledge.com/9780415436281', 'academic'),
(847, 'Llewellyn-Jones, L. (2013). King and Court in Ancient Persia 559 to 331 BCE. Edinburgh University Press. ISBN 978-0748641253.', 'https://edinburghuniversitypress.com', 'academic');

-- 521 Republic of Texas 1836-1845
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(521, 'Campbell, R. B. (2003). Gone to Texas: A History of the Lone Star State. Oxford University Press. ISBN 978-0195149648.', 'https://global.oup.com', 'academic'),
(521, 'Fehrenbach, T. R. (2000). Lone Star: A History of Texas and the Texans. Da Capo Press. ISBN 978-0306809422.', 'https://www.hachettebookgroup.com', 'academic'),
(521, 'Henderson, S. (1942). The Texas Republic: A Social and Economic History. University of Oklahoma Press. ISBN 978-0806118970.', 'https://www.oupress.com', 'academic'),
(521, 'Calvert, R. A., De León, A. & Cantrell, G. (2007). The History of Texas (4th ed.). Wiley-Blackwell. ISBN 978-0882952161.', 'https://www.wiley.com', 'academic'),
(521, 'Vázquez, J. Z. & Meyer, L. (1985). The United States and Mexico. University of Chicago Press. ISBN 978-0226852089.', 'https://press.uchicago.edu', 'academic');

-- 5 British Raj 1858-1947
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(5, 'Metcalf, B. D. & Metcalf, T. R. (2012). A Concise History of Modern India (3rd ed.). Cambridge University Press. ISBN 978-1107672185.', 'https://www.cambridge.org/9781107672185', 'academic'),
(5, 'Bayly, C. A. (1988). Indian Society and the Making of the British Empire. Cambridge University Press. ISBN 978-0521386500.', 'https://www.cambridge.org/9780521386500', 'academic'),
(5, 'Tomlinson, B. R. (1993). The Economy of Modern India, 1860-1970. Cambridge University Press. ISBN 978-0521360234.', 'https://www.cambridge.org', 'academic'),
(5, 'Brown, J. M. (1994). Modern India: The Origins of an Asian Democracy (2nd ed.). Oxford University Press. ISBN 978-0198731139.', 'https://global.oup.com', 'academic'),
(5, 'Stein, B. (2010). A History of India (2nd ed.). Wiley-Blackwell. ISBN 978-1405195096.', 'https://www.wiley.com', 'academic');

COMMIT;

SELECT entity_id, count(*) AS n_src FROM sources WHERE entity_id IN (212, 32, 423, 421, 523, 407, 361, 847, 521, 5) GROUP BY entity_id ORDER BY entity_id;
