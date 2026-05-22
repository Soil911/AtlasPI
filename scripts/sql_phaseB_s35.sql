-- Phase B — S35 enrichment batch: 10 entities, +5 academic sources each

BEGIN;

-- 213 Virreinato del Río de la Plata 1776-1814
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(213, 'Lynch, J. (1958). Spanish Colonial Administration, 1782-1810: The Intendant System in the Viceroyalty of the Río de la Plata. Athlone Press / University of London. ISBN 978-0485131048.', 'https://www.bloomsbury.com/9780485131048', 'academic'),
(213, 'Halperín Donghi, T. (1985). Reforma y disolución de los imperios ibéricos, 1750-1850. Alianza Editorial. ISBN 978-8420624365.', 'https://www.alianzaeditorial.es', 'academic'),
(213, 'Lewin, B. (1957). La rebelión de Túpac Amaru y los orígenes de la emancipación americana. Hachette.', 'https://www.worldcat.org/oclc/1402554', 'academic'),
(213, 'Adelman, J. (1999). Republic of Capital: Buenos Aires and the Legal Transformation of the Atlantic World. Stanford University Press. ISBN 978-0804735377.', 'https://www.sup.org/books/title/?id=2129', 'academic'),
(213, 'Lynch, J. (1973). The Spanish American Revolutions, 1808-1826. Norton. ISBN 978-0393007473.', 'https://wwnorton.com/books/9780393007473', 'academic');

-- 831 Rozvi 1684-1866 — Zimbabwe successor state
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(831, 'Beach, D. N. (1980). The Shona and Zimbabwe 900-1850. Heinemann / Mambo Press. ISBN 978-0435947804.', 'https://www.worldcat.org/oclc/6739569', 'academic'),
(831, 'Mudenge, S. I. G. (1988). A Political History of Munhumutapa c. 1400-1902. Zimbabwe Publishing House / James Currey. ISBN 978-0852550878.', 'https://www.jamescurrey.com', 'academic'),
(831, 'Pikirayi, I. (2001). The Zimbabwe Culture: Origins and Decline of Southern Zambezian States. AltaMira Press. ISBN 978-0759101111.', 'https://rowman.com/ISBN/9780759101111', 'academic'),
(831, 'Bhila, H. H. K. (1982). Trade and Politics in a Shona Kingdom: The Manyika and Their African and Portuguese Neighbours 1575-1902. Longman. ISBN 978-0582646476.', 'https://www.routledge.com/9780582646476', 'academic'),
(831, 'Newitt, M. (1995). A History of Mozambique. Indiana University Press. ISBN 978-0253340504.', 'https://iupress.org/9780253340504/a-history-of-mozambique/', 'academic');

-- 737 Wadai 1635-1912
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(737, 'Carbou, H. (1912). La région du Tchad et du Ouadaï. Ernest Leroux.', 'https://gallica.bnf.fr/ark:/12148/bpt6k3041128', 'primary'),
(737, 'Tubiana, M.-J. & Tubiana, J. (1977). The Zaghawa from an Ecological Perspective. Balkema. ISBN 978-9061910107.', 'https://www.worldcat.org/oclc/3327301', 'academic'),
(737, 'Cordell, D. D. (1985). Dar al-Kuti and the Last Years of the Trans-Saharan Slave Trade. University of Wisconsin Press. ISBN 978-0299101947.', 'https://uwpress.wisc.edu/books/0388.htm', 'academic'),
(737, 'O''Fahey, R. S. & Spaulding, J. L. (1974). Kingdoms of the Sudan. Methuen / Africa Studies 9. ISBN 978-0416776201.', 'https://www.routledge.com', 'academic'),
(737, 'Lange, D. (1984). The kingdoms and peoples of Chad. In: D. T. Niane (ed.), General History of Africa, Vol. IV. UNESCO/Heinemann. ISBN 978-9231017100.', 'https://unesdoc.unesco.org/ark:/48223/pf0000184282', 'academic');

-- 572 Regno delle Due Sicilie 1816-1861
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(572, 'Davis, J. A. (2006). Naples and Napoleon: Southern Italy and the European Revolutions, 1780-1860. Oxford University Press. ISBN 978-0199558339.', 'https://global.oup.com/academic/product/naples-and-napoleon-9780199558339', 'academic'),
(572, 'Pinto, C. (2019). La guerra per il Mezzogiorno: Italiani, borbonici e briganti, 1860-1870. Laterza. ISBN 978-8858135365.', 'https://www.laterza.it', 'academic'),
(572, 'Riall, L. (2009). Risorgimento: The History of Italy from Napoleon to Nation-State. Palgrave Macmillan. ISBN 978-0230216709.', 'https://link.springer.com/book/10.1007/978-1-137-09452-6', 'academic'),
(572, 'De Lorenzo, R. (2013). Borbonia felix: Il Regno delle Due Sicilie alla vigilia del crollo. Salerno Editrice. ISBN 978-8884028075.', 'https://www.salernoeditrice.it', 'academic'),
(572, 'Petrusewicz, M. (1996). Latifundium: Moral Economy and Material Life in a European Periphery. University of Michigan Press. ISBN 978-0472106738.', 'https://www.press.umich.edu/9377', 'academic');

-- 151 Oyọ́ (Yoruba Oyo Empire) 1400-1905 — separate from id=851
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(151, 'Law, R. (1977). The Oyo Empire, c.1600-c.1836: A West African Imperialism in the Era of the Atlantic Slave Trade. Clarendon Press / Oxford University Press. ISBN 978-0198227090.', 'https://global.oup.com/academic/product/the-oyo-empire-9780198227090', 'academic'),
(151, 'Ogundiran, A. (2020). The Yoruba: A New History. Indiana University Press. ISBN 978-0253051509.', 'https://iupress.org/9780253051509/the-yoruba/', 'academic'),
(151, 'Akinjogbin, I. A. (ed.) (1998). War and Peace in Yorubaland, 1793-1893. Heinemann Educational Books (Nigeria). ISBN 978-9781294978.', 'https://www.worldcat.org', 'academic'),
(151, 'Falola, T. & Childs, M. D. (eds.) (2004). The Yoruba Diaspora in the Atlantic World. Indiana University Press. ISBN 978-0253344588.', 'https://iupress.org/9780253344588/', 'academic'),
(151, 'Johnson, S. (1921). The History of the Yorubas: From the Earliest Times to the Beginning of the British Protectorate. C.M.S. (Nigeria) Bookshops / Routledge reprint. ISBN 978-0710302083.', 'https://www.worldcat.org/oclc/4180000', 'primary');

-- 232 Československo (Czechoslovakia) 1918-1993
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(232, 'Mamatey, V. S. & Luža, R. (eds.) (1973). A History of the Czechoslovak Republic, 1918-1948. Princeton University Press. ISBN 978-0691052052.', 'https://press.princeton.edu/books/hardcover/9780691052052/', 'academic'),
(232, 'Skilling, H. G. (1976). Czechoslovakia''s Interrupted Revolution. Princeton University Press. ISBN 978-0691051260.', 'https://press.princeton.edu/books/paperback/9780691051260/', 'academic'),
(232, 'Innes, A. (2001). Czechoslovakia: The Short Goodbye. Yale University Press. ISBN 978-0300094978.', 'https://yalebooks.yale.edu/9780300094978', 'academic'),
(232, 'Krejčí, J. (1996). Czechoslovakia at the Crossroads of European History. I. B. Tauris. ISBN 978-1860640032.', 'https://www.bloomsbury.com/uk/czechoslovakia-9781860640032/', 'academic'),
(232, 'Korbel, J. (1959). The Communist Subversion of Czechoslovakia 1938-1948. Princeton University Press. ISBN 978-0691086477.', 'https://press.princeton.edu/books/paperback/9780691086477/', 'academic');

-- 148 Asante 1670-1957
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(148, 'Wilks, I. (1975). Asante in the Nineteenth Century: The Structure and Evolution of a Political Order. Cambridge University Press. ISBN 978-0521099820.', 'https://www.cambridge.org/9780521099820', 'academic'),
(148, 'McCaskie, T. C. (1995). State and Society in Pre-Colonial Asante. Cambridge University Press. ISBN 978-0521410755.', 'https://www.cambridge.org/9780521410755', 'academic'),
(148, 'Wilks, I. (1993). Forests of Gold: Essays on the Akan and the Kingdom of Asante. Ohio University Press. ISBN 978-0821410288.', 'https://www.ohioswallow.com/book/Forests+of+Gold', 'academic'),
(148, 'McCaskie, T. C. (2000). Asante Identities: History and Modernity in an African Village, 1850-1950. Edinburgh University Press. ISBN 978-0748614004.', 'https://edinburghuniversitypress.com', 'academic'),
(148, 'Lewin, T. J. (1978). Asante before the British: The Prempean Years, 1875-1900. Regents Press of Kansas. ISBN 978-0700601592.', 'https://www.worldcat.org/oclc/4137555', 'academic');

-- 422 Ducato di Milano 1395-1797
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(422, 'Black, J. (2009). Absolutism in Renaissance Milan: Plenitude of Power under the Visconti and the Sforza, 1329-1535. Oxford University Press. ISBN 978-0199565290.', 'https://global.oup.com/academic/product/absolutism-in-renaissance-milan-9780199565290', 'academic'),
(422, 'Chittolini, G. (1979). La formazione dello stato regionale e le istituzioni del contado: secoli XIV-XV. Einaudi.', 'https://www.einaudi.it', 'academic'),
(422, 'Cognasso, F. (1955). I Visconti. Dall''Oglio. (Repr. 1992 Corbaccio. ISBN 978-8879720045)', 'https://www.corbaccio.it', 'academic'),
(422, 'Lubkin, G. (1994). A Renaissance Court: Milan under Galeazzo Maria Sforza. University of California Press. ISBN 978-0520081505.', 'https://www.ucpress.edu/book/9780520081505', 'academic'),
(422, 'Mainoni, P. (2003). Milano e la Lombardia: lavoro e produzione fra Quattrocento e Cinquecento. Unicopli. ISBN 978-8840009254.', 'https://www.edizioniunicopli.it', 'academic');

-- 424 Regno di Napoli 1282-1816
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(424, 'Galasso, G. (1992). Alla periferia dell''impero: Il Regno di Napoli nel periodo spagnolo (secoli XVI-XVII). Einaudi. ISBN 978-8806125868.', 'https://www.einaudi.it', 'academic'),
(424, 'Astarita, T. (1992). The Continuity of Feudal Power: The Caracciolo di Brienza in Spanish Naples. Cambridge University Press. ISBN 978-0521410908.', 'https://www.cambridge.org/9780521410908', 'academic'),
(424, 'Calabria, A. (1991). The Cost of Empire: The Finances of the Kingdom of Naples in the Time of Spanish Rule. Cambridge University Press. ISBN 978-0521402330.', 'https://www.cambridge.org/9780521402330', 'academic'),
(424, 'Marino, J. A. (2011). Becoming Neapolitan: Citizen Culture in Baroque Naples. Johns Hopkins University Press. ISBN 978-1421400785.', 'https://www.press.jhu.edu/books/title/9876/becoming-neapolitan', 'academic'),
(424, 'Croce, B. (1925). Storia del Regno di Napoli. Laterza.', 'https://www.laterza.it', 'academic');

-- 441 Regatul Romaniei (Kingdom of Romania) 1881-1947
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(441, 'Hitchins, K. (1994). Rumania 1866-1947. Oxford University Press / Clarendon Press. ISBN 978-0198205852.', 'https://global.oup.com/academic/product/rumania-1866-1947-9780198205852', 'academic'),
(441, 'Boia, L. (2001). Romania: Borderland of Europe. Reaktion Books. ISBN 978-1861891037.', 'https://reaktionbooks.co.uk/work/romania', 'academic'),
(441, 'Heinen, A. (1986). Die Legion ''Erzengel Michael'' in Rumänien. Oldenbourg. ISBN 978-3486529104.', 'https://www.degruyter.com', 'academic'),
(441, 'Hitchins, K. (2014). A Concise History of Romania. Cambridge University Press. ISBN 978-0521872386.', 'https://www.cambridge.org/9780521872386', 'academic'),
(441, 'Iordachi, C. (2019). Liberalism, Constitutional Nationalism, and Minorities: The Making of Romanian Citizenship, c. 1750-1918. Brill. ISBN 978-9004412309.', 'https://brill.com/view/title/53854', 'academic');

COMMIT;

SELECT entity_id, count(*) AS n_src FROM sources WHERE entity_id IN (213, 831, 737, 572, 151, 232, 148, 422, 424, 441) GROUP BY entity_id ORDER BY entity_id;
