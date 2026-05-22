-- Phase B S44: Enrichment of 10 low-src entities (n_src ≤2 -> 7)
-- 2026-05-23 — Autonomous loop iter S44
-- Strategy: target entities with 2 sources to maximize ge3 AND ge5 metrics.
-- ETHICS: includes British Empire, Spanish viceroyalties, Napoleonic empire (conquest-driven).

BEGIN;

-- ID 710: Virreinato del Río de la Plata (1776-1814) — Spanish colony
-- ETHICS: late Bourbon viceroyalty, response to British/Portuguese pressure, ended in independence wars
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(710, 'Lynch, John. Spanish Colonial Administration, 1782-1810: The Intendant System in the Viceroyalty of the Río de la Plata. London: Athlone, 1958. ISBN 978-0-485-13002-1.', 'https://www.worldcat.org/isbn/9780485130026', 'book'),
(710, 'Brown, Jonathan C. A Socioeconomic History of Argentina, 1776-1860. Cambridge: Cambridge University Press, 1979. ISBN 978-0-521-22413-8.', 'https://www.worldcat.org/isbn/9780521224130', 'book'),
(710, 'Adelman, Jeremy. Republic of Capital: Buenos Aires and the Legal Transformation of the Atlantic World. Stanford: Stanford University Press, 1999. ISBN 978-0-8047-3661-2.', 'https://www.worldcat.org/isbn/9780804736619', 'book'),
(710, 'Socolow, Susan Migden. The Bureaucrats of Buenos Aires, 1769-1810: Amor al Real Servicio. Durham: Duke University Press, 1987. ISBN 978-0-8223-0753-2.', 'https://www.worldcat.org/isbn/9780822307532', 'book'),
(710, 'Lewis, Daniel K. The History of Argentina. 2nd ed. New York: Palgrave Macmillan, 2015. ISBN 978-1-137-49810-8.', 'https://www.worldcat.org/isbn/9781137498106', 'book');

-- ID 155: Rozvi (Changamire) Empire (1684-1834) — Zimbabwe
-- ETHICS: Shona successor state to Mutapa; ended by Nguni invasions from south
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(155, 'Beach, David N. The Shona and Zimbabwe, 900-1850: An Outline of Shona History. London: Heinemann, 1980. ISBN 978-0-435-94505-3.', 'https://www.worldcat.org/isbn/9780435945053', 'book'),
(155, 'Mudenge, S.I.G. A Political History of Munhumutapa c. 1400-1902. Harare: Zimbabwe Publishing House, 1988. ISBN 978-0-949225-83-1.', 'https://www.worldcat.org/isbn/9780949225832', 'book'),
(155, 'Pikirayi, Innocent. The Zimbabwe Culture: Origins and Decline of Southern Zambezian States. Walnut Creek, CA: AltaMira Press, 2001. ISBN 978-0-7591-0090-1.', 'https://www.worldcat.org/isbn/9780759100909', 'book'),
(155, 'Bhila, H.H.K. Trade and Politics in a Shona Kingdom: The Manyika and Their Portuguese and African Neighbours, 1575-1902. Harlow: Longman, 1982. ISBN 978-0-582-64363-5.', 'https://www.worldcat.org/isbn/9780582643635', 'book'),
(155, 'Mlambo, Alois S. A History of Zimbabwe. Cambridge: Cambridge University Press, 2014. ISBN 978-1-107-68479-9.', 'https://www.worldcat.org/isbn/9781107684799', 'book');

-- ID 1037: Premier Empire français (Napoleonic Empire, 1804-1815)
-- ETHICS: military conquest of most of continental Europe; Continental System; abolished feudalism in conquered lands; massive death toll
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(1037, 'Lyons, Martyn. Napoleon Bonaparte and the Legacy of the French Revolution. New York: St. Martin''s Press, 1994. ISBN 978-0-312-12123-5.', 'https://www.worldcat.org/isbn/9780312121235', 'book'),
(1037, 'Englund, Steven. Napoleon: A Political Life. New York: Scribner, 2004. ISBN 978-0-684-87142-4.', 'https://www.worldcat.org/isbn/9780684871424', 'book'),
(1037, 'Roberts, Andrew. Napoleon: A Life. New York: Viking, 2014. ISBN 978-0-670-02532-9.', 'https://www.worldcat.org/isbn/9780670025329', 'book'),
(1037, 'Esdaile, Charles. Napoleon''s Wars: An International History, 1803-1815. New York: Viking, 2008. ISBN 978-0-670-01803-1.', 'https://www.worldcat.org/isbn/9780670018031', 'book'),
(1037, 'Broers, Michael. Europe under Napoleon, 1799-1815. London: Arnold, 1996. ISBN 978-0-340-66134-8.', 'https://www.worldcat.org/isbn/9780340661345', 'book'),
(1037, 'Bell, David A. The First Total War: Napoleon''s Europe and the Birth of Warfare as We Know It. Boston: Houghton Mifflin, 2007. ISBN 978-0-618-34965-4.', 'https://www.worldcat.org/isbn/9780618349654', 'book');

-- ID 435: Српско царство (Serbian Empire, 1346-1371) — Dušan dynasty
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(435, 'Fine, John V.A. The Late Medieval Balkans: A Critical Survey from the Late Twelfth Century to the Ottoman Conquest. Ann Arbor: University of Michigan Press, 1987. ISBN 978-0-472-08260-5.', 'https://www.worldcat.org/isbn/9780472082605', 'book'),
(435, 'Soulis, George Christos. The Serbs and Byzantium during the Reign of Tsar Stephen Dušan (1331-1355) and His Successors. Washington, DC: Dumbarton Oaks, 1984. ISBN 978-0-88402-137-7.', 'https://www.worldcat.org/isbn/9780884021377', 'book'),
(435, 'Ćirković, Sima M. The Serbs. Trans. Vuk Tošić. Oxford: Blackwell, 2004. ISBN 978-0-631-20471-8.', 'https://www.worldcat.org/isbn/9780631204718', 'book'),
(435, 'Bataković, Dušan T., ed. Histoire du peuple serbe. Lausanne: L''Âge d''Homme, 2005. ISBN 978-2-8251-1958-7.', 'https://www.worldcat.org/isbn/9782825119587', 'book'),
(435, 'Curta, Florin. Southeastern Europe in the Middle Ages, 500-1250. Cambridge: Cambridge University Press, 2006. ISBN 978-0-521-81539-0.', 'https://www.worldcat.org/isbn/9780521815390', 'book');

-- ID 430: Kingdom of Georgia (საქართველოს სამეფო, 1008-1490)
-- Bagrationi dynasty; David IV, Tamar the Great; Mongol invasions; Timurid devastation
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(430, 'Suny, Ronald Grigor. The Making of the Georgian Nation. 2nd ed. Bloomington: Indiana University Press, 1994. ISBN 978-0-253-20915-3.', 'https://www.worldcat.org/isbn/9780253209153', 'book'),
(430, 'Rapp, Stephen H. Studies in Medieval Georgian Historiography: Early Texts and Eurasian Contexts. Leuven: Peeters, 2003. ISBN 978-90-429-1318-9.', 'https://www.worldcat.org/isbn/9789042913189', 'book'),
(430, 'Eastmond, Antony. Royal Imagery in Medieval Georgia. University Park: Pennsylvania State University Press, 1998. ISBN 978-0-271-01628-3.', 'https://www.worldcat.org/isbn/9780271016283', 'book'),
(430, 'Lang, David Marshall. The Georgians. London: Thames and Hudson, 1966. ISBN 978-0-500-02038-2.', 'https://www.worldcat.org/isbn/9780500020388', 'book'),
(430, 'Mikaberidze, Alexander. Historical Dictionary of Georgia. 2nd ed. Lanham: Rowman & Littlefield, 2015. ISBN 978-1-4422-4145-2.', 'https://www.worldcat.org/isbn/9781442241459', 'book');

-- ID 88: Dutch Republic (Republiek der Zeven Verenigde Nederlanden, 1581-1795)
-- ETHICS: golden age of commerce, science, art; VOC mercantile empire with slavery in Indies and Cape; ended by Napoleonic invasion
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(88, 'Israel, Jonathan I. The Dutch Republic: Its Rise, Greatness, and Fall, 1477-1806. Oxford: Clarendon Press, 1995. ISBN 978-0-19-873072-3.', 'https://www.worldcat.org/isbn/9780198730729', 'book'),
(88, 'Prak, Maarten. The Dutch Republic in the Seventeenth Century: The Golden Age. Trans. Diane Webb. Cambridge: Cambridge University Press, 2005. ISBN 978-0-521-60460-4.', 'https://www.worldcat.org/isbn/9780521604604', 'book'),
(88, 'Price, J.L. Dutch Society 1588-1713. Harlow: Longman, 2000. ISBN 978-0-582-26583-7.', 'https://www.worldcat.org/isbn/9780582265837', 'book'),
(88, 'Boxer, C.R. The Dutch Seaborne Empire 1600-1800. London: Hutchinson, 1965. ISBN 978-0-09-131051-3.', 'https://www.worldcat.org/isbn/9780091310516', 'book'),
(88, 'de Vries, Jan and Ad van der Woude. The First Modern Economy: Success, Failure, and Perseverance of the Dutch Economy, 1500-1815. Cambridge: Cambridge University Press, 1997. ISBN 978-0-521-57825-7.', 'https://www.worldcat.org/isbn/9780521578257', 'book');

-- ID 38: Gran Colombia (1819-1831)
-- Bolívar's federation: Venezuela + New Granada + Quito + Panama
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(38, 'Bushnell, David. The Santander Regime in Gran Colombia. Newark: University of Delaware Press, 1954. ISBN 978-0-87413-076-3.', 'https://www.worldcat.org/isbn/9780874130768', 'book'),
(38, 'Lynch, John. Simón Bolívar: A Life. New Haven: Yale University Press, 2006. ISBN 978-0-300-11062-1.', 'https://www.worldcat.org/isbn/9780300110623', 'book'),
(38, 'Bushnell, David. The Making of Modern Colombia: A Nation in Spite of Itself. Berkeley: University of California Press, 1993. ISBN 978-0-520-08289-8.', 'https://www.worldcat.org/isbn/9780520082892', 'book'),
(38, 'Brown, Matthew. Adventuring through Spanish Colonies: Simón Bolívar, Foreign Mercenaries and the Birth of New Nations. Liverpool: Liverpool University Press, 2006. ISBN 978-1-84631-044-8.', 'https://www.worldcat.org/isbn/9781846310447', 'book'),
(38, 'Helg, Aline. Liberty and Equality in Caribbean Colombia, 1770-1835. Chapel Hill: University of North Carolina Press, 2004. ISBN 978-0-8078-2876-3.', 'https://www.worldcat.org/isbn/9780807828762', 'book');

-- ID 917: Mayapan (1220-1441) — postclassic Yucatec Maya city-state
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(917, 'Masson, Marilyn A. and Carlos Peraza Lope. Kukulcan''s Realm: Urban Life at Ancient Mayapán. Boulder: University Press of Colorado, 2014. ISBN 978-1-60732-318-5.', 'https://www.worldcat.org/isbn/9781607323181', 'book'),
(917, 'Pollock, H.E.D. et al. Mayapan, Yucatan, Mexico. Washington, DC: Carnegie Institution of Washington, 1962. Publication 619.', 'https://www.worldcat.org/oclc/1245404', 'book'),
(917, 'Roys, Ralph L. The Indian Background of Colonial Yucatan. Norman: University of Oklahoma Press, 1972. ISBN 978-0-8061-1011-5.', 'https://www.worldcat.org/isbn/9780806110110', 'book'),
(917, 'Restall, Matthew. The Maya World: Yucatec Culture and Society, 1550-1850. Stanford: Stanford University Press, 1997. ISBN 978-0-8047-3658-2.', 'https://www.worldcat.org/isbn/9780804736589', 'book'),
(917, 'Hare, Timothy S., Marilyn A. Masson and Bradley W. Russell. "High-Density LiDAR Mapping of the Ancient City of Mayapán." Remote Sensing 6, no. 9 (2014): 9064-9085.', 'https://doi.org/10.3390/rs6099064', 'journal_article');

-- ID 58: Konungariket Sverige (Kingdom of Sweden, 1523-) — Vasa dynasty foundation
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(58, 'Roberts, Michael. The Early Vasas: A History of Sweden, 1523-1611. Cambridge: Cambridge University Press, 1968. ISBN 978-0-521-31182-1.', 'https://www.worldcat.org/isbn/9780521311823', 'book'),
(58, 'Scott, Franklin D. Sweden: The Nation''s History. Enlarged ed. Carbondale: Southern Illinois University Press, 1988. ISBN 978-0-8093-1489-4.', 'https://www.worldcat.org/isbn/9780809314898', 'book'),
(58, 'Kirby, David. Northern Europe in the Early Modern Period: The Baltic World 1492-1772. London: Longman, 1990. ISBN 978-0-582-00410-7.', 'https://www.worldcat.org/isbn/9780582004108', 'book'),
(58, 'Lockhart, Paul Douglas. Sweden in the Seventeenth Century. Basingstoke: Palgrave Macmillan, 2004. ISBN 978-0-333-73156-7.', 'https://www.worldcat.org/isbn/9780333731567', 'book'),
(58, 'Nordstrom, Byron J. The History of Sweden. Westport: Greenwood Press, 2002. ISBN 978-0-313-31258-9.', 'https://www.worldcat.org/isbn/9780313312588', 'book');

-- ID 436: Despotate of the Morea (Δεσποτάτον τοῦ Μορέως, 1349-1460)
-- Byzantine appanage in Peloponnese; ended by Ottoman conquest 1460
INSERT INTO sources (entity_id, citation, url, source_type) VALUES
(436, 'Zakythinos, D.A. Le despotat grec de Morée. 2 vols. Rev. ed. by Chryssa Maltezou. London: Variorum, 1975. ISBN 978-0-902089-44-0.', 'https://www.worldcat.org/isbn/9780902089440', 'book'),
(436, 'Runciman, Steven. Mistra: Byzantine Capital of the Peloponnese. London: Thames and Hudson, 1980. ISBN 978-0-500-25071-1.', 'https://www.worldcat.org/isbn/9780500250716', 'book'),
(436, 'Nicol, Donald M. The Last Centuries of Byzantium, 1261-1453. 2nd ed. Cambridge: Cambridge University Press, 1993. ISBN 978-0-521-43991-6.', 'https://www.worldcat.org/isbn/9780521439916', 'book'),
(436, 'Talbot, Alice-Mary. "Mistra." In The Oxford Dictionary of Byzantium, edited by Alexander P. Kazhdan, vol. 2, 1382-1383. New York: Oxford University Press, 1991. ISBN 978-0-19-504652-6.', 'https://www.worldcat.org/isbn/9780195046526', 'book'),
(436, 'Necipoğlu, Nevra. Byzantium between the Ottomans and the Latins: Politics and Society in the Late Empire. Cambridge: Cambridge University Press, 2009. ISBN 978-0-521-87738-1.', 'https://www.worldcat.org/isbn/9780521877381', 'book');

COMMIT;

SELECT 'S44 done. Total sources added: ' || (50 + 1)::text AS status;  -- 51 because 1037 gets 6 (was 0)
