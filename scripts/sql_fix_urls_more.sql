-- Fix more empty URLs: DOI patterns + ISBN-10 (legacy) + JSTOR stable IDs
-- 2026-05-23 — URL-FIX-2

BEGIN;

-- 1) Sources with DOI in citation: link to https://doi.org/<doi>
SELECT count(*) AS doi_to_fix
FROM sources
WHERE (url IS NULL OR url = '')
  AND citation ~ 'doi:?\s*10\.[0-9]+/[^\s]+';

UPDATE sources
SET url = 'https://doi.org/' || regexp_replace(
    (regexp_match(citation, 'doi:?\s*(10\.[0-9]+/[^\s)\]\.,]+)'))[1],
    '[\.,]$', '', 'g'
)
WHERE (url IS NULL OR url = '')
  AND citation ~ 'doi:?\s*10\.[0-9]+/[^\s]+';

-- 2) Sources with JSTOR stable ID in citation: link to JSTOR
SELECT count(*) AS jstor_to_fix
FROM sources
WHERE (url IS NULL OR url = '')
  AND citation ~ 'jstor.org/stable/[0-9]+';

UPDATE sources
SET url = 'https://www.' || (regexp_match(citation, '(jstor\.org/stable/[0-9]+)'))[1]
WHERE (url IS NULL OR url = '')
  AND citation ~ 'jstor.org/stable/[0-9]+';

-- 3) Sources with ISBN-10 (older format, 10 digits): convert to WorldCat
-- Pattern: ISBN <digits>-<digits>-<digits>-X or 10 consecutive
SELECT count(*) AS isbn10_to_fix
FROM sources
WHERE (url IS NULL OR url = '')
  AND citation ~ 'ISBN[ ]*[0-9][- 0-9]{8,11}[0-9X]'
  AND citation !~ 'ISBN[ ]*97[0-9]';

UPDATE sources
SET url = 'https://www.worldcat.org/isbn/' || regexp_replace(
    (regexp_match(citation, 'ISBN[ ]*([0-9][- 0-9]{8,11}[0-9X])'))[1],
    '[- ]', '', 'g'
)
WHERE (url IS NULL OR url = '')
  AND citation ~ 'ISBN[ ]*[0-9][- 0-9]{8,11}[0-9X]'
  AND citation !~ 'ISBN[ ]*97[0-9]';

-- Final stats
SELECT count(*) AS still_empty,
       (SELECT count(*) FROM sources) AS total_sources,
       (SELECT count(*) FROM sources WHERE url LIKE 'https://%') AS with_https_url
FROM sources WHERE (url IS NULL OR url = '');

COMMIT;
