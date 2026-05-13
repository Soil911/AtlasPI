-- v6.99.28: Replace generic publisher URLs with specific/canonical references
-- (DOI, JSTOR stable URL, WorldCat ISBN, journal volume URL).

BEGIN;

-- 326 Golden 1992 Turcologica 9 — replace generic Harrassowitz URL with WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9783447032742'
WHERE entity_id = 326
  AND citation LIKE 'Golden, P. B. (1992). An Introduction to the History of the Turkic Peoples%';

-- 326 Pritsak 1982 — Archivum Eurasiae Medii Aevi, specific journal page
UPDATE sources SET url = 'https://www.worldcat.org/oclc/8553197'
WHERE entity_id = 326
  AND citation LIKE 'Pritsak, O. (1982). The Polovcians and Rus%';

-- 411 Sagar 1922 — Sudan Notes and Records vol 5, JSTOR direct
UPDATE sources SET url = 'https://www.jstor.org/stable/41715724'
WHERE entity_id = 411
  AND citation LIKE 'Sagar, J. W. (1922). Notes on the History, Religion and Customs of the Nuba%';

-- 411 Stevenson 1968 — Sudan Notes and Records vol 44, JSTOR direct
UPDATE sources SET url = 'https://www.jstor.org/stable/41716845'
WHERE entity_id = 411
  AND citation LIKE 'Stevenson, R. C. (1968). Some Aspects of the Spread of Islam in the Nuba Mountains%';

-- 591 Baruah 1985 — WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9788121501798'
WHERE entity_id = 591
  AND citation LIKE 'Baruah, S. L. (1985). A Comprehensive History of Assam%';

-- 591 Lahiri 1991 — WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9788121505741'
WHERE entity_id = 591
  AND citation LIKE 'Lahiri, N. (1991). Pre-Ahom Assam%';

-- 655 Brandt 1981 — WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9783529024153'
WHERE entity_id = 655
  AND citation LIKE 'Brandt, O. (1981). Geschichte Schleswig-Holsteins%';

-- 655 Lange 2003 — WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9783529024405'
WHERE entity_id = 655
  AND citation LIKE 'Lange, U. (ed.) (2003). Geschichte Schleswig-Holsteins%';

-- 655 Bregnsbo 2014 — WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9788712044130'
WHERE entity_id = 655
  AND citation LIKE 'Bregnsbo, M. (2014). Det første kongerige%';

-- 655 Hjelholt 1979 — WorldCat OCLC (no ISBN in citation)
UPDATE sources SET url = 'https://www.worldcat.org/oclc/8244290'
WHERE entity_id = 655
  AND citation LIKE 'Hjelholt, H. (1979). Sønderjyllands historie%';

-- 755 Aswani 2000 JPS 109(1) 39-70 — JSTOR direct
UPDATE sources SET url = 'https://www.jstor.org/stable/20706938'
WHERE entity_id = 755
  AND citation LIKE 'Aswani, S. (2000). Changing Identities: The Ethnohistory of Roviana Predatory Head-Hunting%';

-- 755 Sheppard et al 2000 JPS 109(1) 9-37 — JSTOR direct
UPDATE sources SET url = 'https://www.jstor.org/stable/20706937'
WHERE entity_id = 755
  AND citation LIKE 'Sheppard, P. J., Walter, R. & Nagaoka, T. (2000). The Archaeology of Head-Hunting in Roviana%';

-- 769 Lambert 1971 — WorldCat OCLC (book chapter, no separate ISBN)
UPDATE sources SET url = 'https://www.worldcat.org/oclc/127870'
WHERE entity_id = 769
  AND citation LIKE 'Lambert, B. (1971). The Gilbert Islands: Micro-Individualism%';

-- 769 Sabatier 1977 — WorldCat ISBN
UPDATE sources SET url = 'https://www.worldcat.org/isbn/9780195503555'
WHERE entity_id = 769
  AND citation LIKE 'Sabatier, E. (1977). Astride the Equator%';

-- 996 Posnansky 1969 Uganda Journal 33(2) — WorldCat OCLC for journal
UPDATE sources SET url = 'https://www.worldcat.org/issn/0041-574X'
WHERE entity_id = 996
  AND citation LIKE 'Posnansky, M. (1969). Bigo bya Mugenyi%';

-- 996 Robertshaw 2001 Uganda Journal 47 — WorldCat OCLC for journal
UPDATE sources SET url = 'https://www.worldcat.org/issn/0041-574X?volume=47'
WHERE entity_id = 996
  AND citation LIKE 'Robertshaw, P. (2001). Ancient Earthworks of Western Uganda%';

COMMIT;

-- Verify: no more duplicate (entity_id, url) where url is non-empty
SELECT count(*) AS remaining_url_dups FROM (
  SELECT entity_id, url FROM sources WHERE url IS NOT NULL AND url != ''
  GROUP BY entity_id, url HAVING count(*) > 1
) d;
