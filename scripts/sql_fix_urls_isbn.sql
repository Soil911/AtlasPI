-- Fix empty URLs by extracting ISBN from citation and pointing to WorldCat
-- 2026-05-23 — Autonomous loop iter URL-FIX-1
-- Strategy: Sources with NULL or empty url AND citation containing "ISBN 97x-..."
--           extract the ISBN, normalize (strip hyphens), build worldcat.org/isbn/<13-digit> URL.

BEGIN;

-- Preview how many would be affected (informational query, no DML)
SELECT count(*) AS to_fix
FROM sources
WHERE (url IS NULL OR url = '')
  AND citation ~ 'ISBN[ ]*97[0-9][- 0-9]+[0-9X]';

-- Update: extract first ISBN-13 from citation, build WorldCat URL
UPDATE sources
SET url = 'https://www.worldcat.org/isbn/' || regexp_replace(
    (regexp_match(citation, 'ISBN[ ]*(97[0-9][- 0-9]+[0-9X])'))[1],
    '[- ]', '', 'g'
)
WHERE (url IS NULL OR url = '')
  AND citation ~ 'ISBN[ ]*97[0-9][- 0-9]+[0-9X]';

-- Verify result
SELECT count(*) AS still_empty_url
FROM sources
WHERE (url IS NULL OR url = '')
  AND citation ~ 'ISBN[ ]*97[0-9][- 0-9]+[0-9X]';

COMMIT;

-- Show 5 sample fixes
SELECT id, left(citation, 80) AS citation_preview, url
FROM sources
WHERE url LIKE 'https://www.worldcat.org/isbn/%'
ORDER BY id DESC
LIMIT 5;
