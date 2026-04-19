# ADR-005 — Deprecated Entity Merge Policy

**Status**: Adopted v6.85.0 (2026-04-19)
**Authors**: Audit v4 Round 14 (Fase C closure)

---

## Contesto

Audit v4 Fase A bootstrap ha rivelato **42+44 = 86 entità che condividono Wikidata Q-ID** (44 dopo Round 3 collision fix). La maggioranza sono **duplicate plain**: stessa polity con due `name_original` differenti per script/lingua diversa.

Esempi:
- 12 مغلیہ سلطنت + 849 سلطنت مغلیہ (entrambi Mughal Empire Q33296)
- 27 Xšāça + 847 هخامنشیان (entrambi Achaemenid Q389688)
- 90 Rioghachd na h-Alba + 585 Kongerike Skottland (Scotland Q230791)
- 218 ᏣᎳᎩ + 859 Tsalagi (Cherokee Q105405, native vs Latin transliteration)

Queste duplicate sono tecnicamente errori di seed dataset (probabilmente da merge incompleti o ingestion plurime). La domanda: come risolverle senza rompere il dato?

## Decisione: status='deprecated' + FK redirect, NO DELETE

Adottata strategia conservativa applicata in v6.85.0:

1. **Identifica primary entity** per ogni QID duplicato
   - Default: `id` minore (versione stabile, non duplicato recente)
   - Eccezione: per QID che descrive un sub-set semantico, primary = entity che corrisponde più precisamente
     (es. Q1537016 Kanem Empire → primary 647 Kanem, not 147 Kanem-Bornu aggregate)

2. **Redirect FK** delle secondary entities ai primary:
   - `historical_rulers.entity_id`
   - `archaeological_sites.entity_id`
   - `historical_cities.entity_id`
   - `chain_links.entity_id` (con dedup se primary già presente nello stesso chain)

3. **Marca secondary** con:
   - `status = 'deprecated'`
   - `ethical_notes` appended con pointer alla primary

4. **NO DELETE** — preserva permalink `/v1/entities/{secondary_id}` per backward compat.

### Motivazioni

#### Pro DELETE (rejected)

- DB più pulito (no entries inutili)
- Less ambiguity in future queries
- Reduces total entity_count to a more accurate number

#### Pro deprecate-only (chosen)

- **Permalink stability**: chiunque ha bookmarked `/v1/entities/849` (sec. مغلیہ) continua a funzionare (status=deprecated visibile, dati FK puntano correttamente)
- **Dataset stability**: AtlasPI è pubblicato su Zenodo con DOI; cambiare `entity_count` rompe la riproducibilità dei research papers che citano "1034 entities"
- **Soft transition**: consumer possono migrare al primary via il pointer in ethical_notes senza errore 404
- **Reversibilità**: se la decisione "primary X" si rivela sbagliata, possiamo riconsiderare semplicemente cambiando status, non re-creando l'entity

### Trade-off

- **Total entity_count include deprecated**: 1036 totali, 992 confirmed/active, 44 deprecated. Endpoint `/v1/entities` dovrebbe filtrare deprecated by default (vedi implementazione).
- **Stat reportate** (es. landing page) dovrebbero usare `WHERE status != 'deprecated'`.

## Filtering convention

Endpoint pubblici dovrebbero applicare filter `status != 'deprecated'` di default. Override esplicito via `?include_deprecated=true` per analisi DB-level.

```python
# Esempio in src/api/routes/entities.py
def list_entities(include_deprecated: bool = False, ...):
    q = db.query(GeoEntity)
    if not include_deprecated:
        q = q.filter(GeoEntity.status != 'deprecated')
    ...
```

**TODO** v6.87+: implementare filter explicit (currently endpoint ritorna tutti).

## Stato implementazione

| Componente | Status |
|-----------|--------|
| 44 secondary entities marcate deprecated | ✅ v6.85.0 |
| FK redirect (rulers/sites/cities/chains) | ✅ v6.85.0 |
| `/v1/entities` filter `?include_deprecated` | ⏳ TODO v6.87 |
| `/v1/stats` exclude deprecated | ⏳ TODO v6.87 |
| Landing/docs aggiornare conteggio (1036 → 992 active) | ⏳ TODO v6.87 |
| README.md aggiornare badge | ⏳ TODO v6.87 |

## Reversal procedure

Se in futuro si decidesse che un entity X (currently deprecated) dovrebbe essere riattivato:

```sql
-- Step 1: revert status
UPDATE geo_entities SET status = 'confirmed' WHERE id = X;

-- Step 2: rimuovi pointer da ethical_notes
UPDATE geo_entities SET
  ethical_notes = REGEXP_REPLACE(ethical_notes, ' \[v6\.85 audit v4 Round 14\].*', '')
WHERE id = X;

-- Step 3 (manual): valuta se i FK redirected (rulers/sites/cities/chains)
-- vanno spostati di nuovo a X o lasciati al primary
```
