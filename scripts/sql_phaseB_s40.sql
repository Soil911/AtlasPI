-- Phase B — S40: 10 major imperial/national entities, +5 academic sources each

BEGIN;

-- 2 Ottoman Empire 1299-1922
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(2, 'Inalcik, H. & Quataert, D. (eds.) (1994). An Economic and Social History of the Ottoman Empire, 1300-1914. Cambridge University Press. ISBN 978-0521574556.', 'https://www.cambridge.org/9780521574556', 'academic'),
(2, 'Faroqhi, S. N. (ed.) (2006). The Cambridge History of Turkey, Vol. 3: The Later Ottoman Empire, 1603-1839. Cambridge University Press. ISBN 978-0521620956.', 'https://www.cambridge.org', 'academic'),
(2, 'Finkel, C. (2005). Osman''s Dream: The History of the Ottoman Empire. Basic Books. ISBN 978-0465023967.', 'https://www.basicbooks.com', 'academic'),
(2, 'Quataert, D. (2005). The Ottoman Empire, 1700-1922 (2nd ed.). Cambridge University Press. ISBN 978-0521547826.', 'https://www.cambridge.org/9780521547826', 'academic'),
(2, 'Imber, C. (2009). The Ottoman Empire, 1300-1650: The Structure of Power (2nd ed.). Palgrave Macmillan. ISBN 978-0230574519.', 'https://link.springer.com', 'academic');

-- 15 Qing Empire 1636-1912
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(15, 'Rowe, W. T. (2009). China''s Last Empire: The Great Qing. Belknap Press of Harvard University Press. ISBN 978-0674036123.', 'https://www.hup.harvard.edu', 'academic'),
(15, 'Crossley, P. K. (1999). A Translucent Mirror: History and Identity in Qing Imperial Ideology. University of California Press. ISBN 978-0520234246.', 'https://www.ucpress.edu', 'academic'),
(15, 'Rawski, E. S. (1998). The Last Emperors: A Social History of Qing Imperial Institutions. University of California Press. ISBN 978-0520228375.', 'https://www.ucpress.edu', 'academic'),
(15, 'Spence, J. D. (1990). The Search for Modern China. W. W. Norton. ISBN 978-0393027082.', 'https://wwnorton.com', 'academic'),
(15, 'Perdue, P. C. (2005). China Marches West: The Qing Conquest of Central Eurasia. Harvard University Press. ISBN 978-0674016842.', 'https://www.hup.harvard.edu', 'academic');

-- 16 Russian Empire 1721-1917
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(16, 'Lieven, D. (2000). Empire: The Russian Empire and Its Rivals. Yale University Press. ISBN 978-0300088052.', 'https://yalebooks.yale.edu', 'academic'),
(16, 'Hosking, G. (1997). Russia: People and Empire, 1552-1917. Harvard University Press. ISBN 978-0674781191.', 'https://www.hup.harvard.edu', 'academic'),
(16, 'Kappeler, A. (2001). The Russian Empire: A Multi-Ethnic History. Pearson. ISBN 978-0582234154.', 'https://www.pearson.com', 'academic'),
(16, 'Pipes, R. (1974). Russia under the Old Regime. Charles Scribner''s Sons. ISBN 978-0684140414.', 'https://www.simonandschuster.com', 'academic'),
(16, 'Wortman, R. S. (2006). Scenarios of Power: Myth and Ceremony in Russian Monarchy from Peter the Great to the Abdication of Nicholas II. Princeton University Press. ISBN 978-0691123745.', 'https://press.princeton.edu', 'academic');

-- 138 Đại Nam (Nguyễn dynasty) 1802-1945
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(138, 'Woodside, A. (1971). Vietnam and the Chinese Model. Harvard University Press. ISBN 978-0674937215.', 'https://www.hup.harvard.edu', 'academic'),
(138, 'Choi, B. W. (2004). Southern Vietnam under the Reign of Minh Mạng (1820-1841). Cornell Southeast Asia Program. ISBN 978-0877277835.', 'https://www.cornellpress.cornell.edu', 'academic'),
(138, 'Taylor, K. W. (2013). A History of the Vietnamese. Cambridge University Press. ISBN 978-0521699150.', 'https://www.cambridge.org', 'academic'),
(138, 'Goscha, C. E. (2016). Vietnam: A New History. Basic Books. ISBN 978-0465094363.', 'https://www.basicbooks.com', 'academic'),
(138, 'Brocheux, P. & Hémery, D. (2009). Indochina: An Ambiguous Colonization 1858-1954. University of California Press. ISBN 978-0520245396.', 'https://www.ucpress.edu', 'academic');

-- 156 Buganda 1300-1894
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(156, 'Kiwanuka, M. S. M. (1971). A History of Buganda: From the Foundation of the Kingdom to 1900. Africana Publishing. ISBN 978-0841902077.', 'https://www.worldcat.org', 'academic'),
(156, 'Reid, R. J. (2002). Political Power in Pre-Colonial Buganda: Economy, Society and Warfare in the Nineteenth Century. James Currey. ISBN 978-0852554999.', 'https://www.jamescurrey.com', 'academic'),
(156, 'Wrigley, C. (1996). Kingship and State: The Buganda Dynasty. Cambridge University Press. ISBN 978-0521894357.', 'https://www.cambridge.org', 'academic'),
(156, 'Hanson, H. E. (2003). Landed Obligation: The Practice of Power in Buganda. Heinemann. ISBN 978-0325070995.', 'https://www.worldcat.org', 'academic'),
(156, 'Reid, R. (2017). A History of Modern Uganda. Cambridge University Press. ISBN 978-1107067202.', 'https://www.cambridge.org/9781107067202', 'academic');

-- 162 Imerina (Madagascar) 1540-1897
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(162, 'Brown, M. (1995). A History of Madagascar. Damien Tunnacliffe. ISBN 978-0908377169.', 'https://www.worldcat.org', 'academic'),
(162, 'Campbell, G. (2005). An Economic History of Imperial Madagascar, 1750-1895. Cambridge University Press. ISBN 978-0521839358.', 'https://www.cambridge.org/9780521839358', 'academic'),
(162, 'Larson, P. M. (2000). History and Memory in the Age of Enslavement: Becoming Merina in Highland Madagascar, 1770-1822. Heinemann. ISBN 978-0325002171.', 'https://www.worldcat.org', 'academic'),
(162, 'Ellis, S. (1985). The Rising of the Red Shawls: A Revolt in Madagascar, 1895-1899. Cambridge University Press. ISBN 978-0521307048.', 'https://www.cambridge.org', 'academic'),
(162, 'Raison-Jourde, F. (1991). Bible et pouvoir à Madagascar au XIXe siècle. Karthala. ISBN 978-2865372805.', 'https://www.karthala.com', 'academic');

-- 215 Capitanía General de Chile 1541-1818
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(215, 'Collier, S. & Sater, W. F. (2004). A History of Chile, 1808-2002 (2nd ed.). Cambridge University Press. ISBN 978-0521534840.', 'https://www.cambridge.org/9780521534840', 'academic'),
(215, 'Loveman, B. (2001). Chile: The Legacy of Hispanic Capitalism (3rd ed.). Oxford University Press. ISBN 978-0195128727.', 'https://global.oup.com', 'academic'),
(215, 'Méndez Beltrán, L. M. (2004). La exportación minera en Chile, 1800-1840. Editorial Universitaria. ISBN 978-9561115729.', 'https://www.editorialuniversitaria.cl', 'academic'),
(215, 'Bauer, A. J. (1975). Chilean Rural Society from the Spanish Conquest to 1930. Cambridge University Press. ISBN 978-0521208673.', 'https://www.cambridge.org', 'academic'),
(215, 'Salazar, G. & Pinto, J. (1999-2002). Historia contemporánea de Chile, 5 vols. LOM Ediciones. ISBN 978-9562821605.', 'https://www.lom.cl', 'academic');

-- 224 Estado Oriental del Uruguay 1828-present
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(224, 'Caetano, G. & Rilla, J. (1994). Historia contemporánea del Uruguay: de la Colonia al Siglo XXI. Editorial Fin de Siglo. ISBN 978-9974491588.', 'https://www.findesiglo.com.uy', 'academic'),
(224, 'Finch, M. H. J. (1981). A Political Economy of Uruguay since 1870. St. Martin''s Press. ISBN 978-0312623036.', 'https://us.macmillan.com', 'academic'),
(224, 'Frega, A. (ed.) (2008). Historia del Uruguay en el siglo XX (1890-2005). Ediciones de la Banda Oriental. ISBN 978-9974104310.', 'https://www.bandaoriental.com.uy', 'academic'),
(224, 'Williman, J. C. (1984). El Departamento de Lavalleja, 1857-1980. Ediciones de la Banda Oriental.', 'https://www.bandaoriental.com.uy', 'academic'),
(224, 'Reyes Abadie, W. & Vázquez Romero, A. (1998). Crónica general del Uruguay. Banda Oriental. ISBN 978-9974102934.', 'https://www.bandaoriental.com.uy', 'academic');

-- 234 Republic of India 1947-present
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(234, 'Guha, R. (2007). India After Gandhi: The History of the World''s Largest Democracy. Ecco/HarperCollins. ISBN 978-0060958589.', 'https://www.harpercollins.com', 'academic'),
(234, 'Khilnani, S. (1997). The Idea of India. Hamish Hamilton / Penguin. ISBN 978-0241135969.', 'https://www.penguin.co.uk', 'academic'),
(234, 'Sarkar, S. (1983). Modern India 1885-1947. Macmillan. ISBN 978-0333904251.', 'https://www.macmillan.com', 'academic'),
(234, 'Roy, T. (2014). India in the World Economy from Antiquity to the Present. Cambridge University Press. ISBN 978-1107656055.', 'https://www.cambridge.org', 'academic'),
(234, 'Talbot, I. (2016). A History of Modern South Asia: Politics, States, Diasporas. Yale University Press. ISBN 978-0300196948.', 'https://yalebooks.yale.edu', 'academic');

-- 244 Weimar Republic 1919-1933
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(244, 'Kolb, E. (2004). The Weimar Republic (2nd ed.). Routledge. ISBN 978-0415344418.', 'https://www.routledge.com', 'academic'),
(244, 'Peukert, D. J. K. (1991). The Weimar Republic: The Crisis of Classical Modernity. Hill and Wang. ISBN 978-0809015566.', 'https://us.macmillan.com', 'academic'),
(244, 'Mommsen, H. (1996). The Rise and Fall of Weimar Democracy. University of North Carolina Press. ISBN 978-0807845974.', 'https://uncpress.org', 'academic'),
(244, 'Eyck, E. (1962-1963). A History of the Weimar Republic, 2 vols. Harvard University Press. ISBN 978-0689101227.', 'https://www.hup.harvard.edu', 'academic'),
(244, 'Weitz, E. D. (2007). Weimar Germany: Promise and Tragedy. Princeton University Press. ISBN 978-0691016955.', 'https://press.princeton.edu', 'academic');

COMMIT;

SELECT entity_id, count(*) AS n_src FROM sources WHERE entity_id IN (2, 15, 16, 138, 156, 162, 215, 224, 234, 244) GROUP BY entity_id ORDER BY entity_id;
