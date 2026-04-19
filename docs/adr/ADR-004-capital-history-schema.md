# ADR-004 — Capital History schema (capital_history table)

**Status**: Adopted v6.84.0 (2026-04-19)
**Authors**: Audit v4 Round 13 (Fase C closure)
**Deciders**: Clirim Ramadani

---

## Contesto

Audit v2 Agent 04 + audit v4 Round 5 hanno identificato un pattern sistemico:
**polities long-duration con capitali multiple non-rappresentate dal singolo
campo `geo_entities.capital_*`**.

Esempi flaggati con drift Wikidata HIGH e/o MED:

| Entity | year_start..end | Capital "iconica" | Realtà |
|--------|-----------------|-------------------|--------|
| Ottoman (id 2) | 1299-1922 | İstanbul | Söğüt (1299-1335) → Bursa → Edirne → İstanbul (1453+) |
| HRE (id 30) | 800-1806 | Wien | Aachen → Frankfurt → Regensburg → Wien (de facto Asburgo) |
| Mughal (id 12) | 1526-1857 | Delhi | Agra (1526-1648) → Delhi → Aurangabad |
| Ming (id 108) | 1368-1644 | Beijing | Nanjing (1368-1421) → Beijing |
| Song (id 106) | 960-1279 | Kaifeng | Kaifeng (Northern) → Lin'an/Hangzhou (Southern) |
| Solomonic Ethiopia (id 24) | 1270-1974 | Addis Abeba | Tegulet → itinerant → Gondar → Mekelle → Addis Abeba (1886+) |
| Assiria (id 170) | -2025 to -612 | Nineveh | Aššur (~1320y) → Kalhu → Nineveh (93y) |
| Kush (id 52) | -1070 to 350 | Meroë | Kerma → Napata → Meroë (-590+) |
| Seleucidi (id 177) | -312 to -63 | Antioch | Seleucia (-312 to -240) → Antioch |
| Kanem-Bornu (id 147) | 700-1893 | Njimi | Njimi (Kanem) → Ngazargamu (Bornu) → Kukawa |
| Lombardi (id 76) | 568-774 | Pavia | itinerant Verona/Cividale (568-572) → Pavia |
| Austria-Hungary (id 99) | 1867-1918 | Wien | Wien + Budapest (binational) |
| Mali (id 18) | 1235-1600 | Niani (disputed) | court itinerant (Green 2022 hypothesis) |

**Problema specifico**: un agente AI che chiede `GET /v1/entities/2?year=1400`
riceve `capital: {"name": "İstanbul"}` — historically falso (era Edirne).

## Decisione

Adottata schema `capital_history` table (v6.84.0 migration 016):

```sql
CREATE TABLE capital_history (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES geo_entities(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    lat DOUBLE PRECISION NULL,
    lon DOUBLE PRECISION NULL,
    year_start INTEGER NOT NULL,
    year_end INTEGER NULL,
    ordering INTEGER NOT NULL DEFAULT 0,
    notes TEXT NULL
);
```

### Razionale schema

- **`year_start NOT NULL, year_end NULLABLE`**: stesso pattern di `geo_entities`. NULL = capitale ancora attuale o ultima.
- **`lat/lon NULLABLE`**: per polities con corte itinerante (Mali medieval, Solomonic 1400-1636). Si usa `name='court itinerant'` + coords NULL.
- **`ordering`**: per casi con periodi sovrapposti (es. Austria-Hungary aveva Wien E Budapest pari grado nello stesso periodo). Sort secondario quando year ranges si sovrappongono.
- **`notes` TEXT**: spiegazione del ruolo (es. "sede incoronazioni" vs "sede de facto" vs "capitale di una metà del dual monarchy").
- **`ON DELETE CASCADE`**: capital_history cancellata se entity rimossa (consistency).

### Decisione conservata: `geo_entities.capital_*` rimangono

Il campo `geo_entities.capital_name/lat/lon` continua a esistere e contiene la **capitale "iconica"** (più nota, più duratura, o convenzionalmente associata). Backward compat per consumer esistenti.

`capital_history` è **complementare**, non sostituiva. Permette query come:
- "What was the capital of Ottoman Empire in year Y?" → fai join su capital_history WHERE year_start <= Y AND (year_end IS NULL OR year_end >= Y)
- "Show me all capitals of HRE" → SELECT FROM capital_history WHERE entity_id = 30 ORDER BY year_start

### Population

13 entities popolate in v6.84 (47 capital records totali). Pattern: ogni entity con drift HIGH coord da Wikidata + entities flaggate in audit v2 Agent 04.

Future entries da popolare: tutte le polities con ethical_notes contenente "[v6.65 audit]", "[v6.66 audit]", "[v6.75 audit v4]" che documentano capital anachronism.

## Alternative considerate

### Alt 1 — Aggiungi `capital_alt_name1`, `capital_alt_name2`, `capital_alt_name3` a geo_entities

**Rejected**: arbitrary cap on number of capitals (HRE ne ha 4, Solomonic 5). Ottoman ne ha 4 ma con date diverse, non sovrapposte → schema flat non lo cattura.

### Alt 2 — `geo_entities.capital_history JSON` field

**Rejected**: queries più difficili (no index su JSON path semplice), no cascade delete, no enforcement schema.

### Alt 3 — Separate field `geo_entities.capital_chronology TEXT`

**Rejected**: campo testuale free-form non queryable per AI agents. Stessa limitazione di ethical_notes (che già copre il caso ma non strutturalmente).

### Alt 4 — Schema relational (chosen)

**Adopted**. Scalable (qualunque numero capitals), queryable (JOIN by year), cascade-delete safe, indici utilizzabili.

## Implicazioni

- `EntityResponse` Pydantic schema dovrebbe esporre `capital_history` come array di oggetti. **TODO** in v6.87+: aggiornare `src/api/schemas.py` + `src/api/routes/entities.py::_entity_to_response()`.
- Drift detection (v6.69+ scripts) può ora confrontare AtlasPI capital_history vs Wikidata P36 timeline (es. P39 hold position from-to ranges).
- Frontend `static/app.js` può mostrare timeline capitali nella sidebar detail.

## Stato implementation

| Componente | Status |
|-----------|--------|
| Migration 016_capital_history.py | ✅ |
| `CapitalHistory` model | ✅ |
| `GeoEntity.capital_history` relationship | ✅ |
| Populate 13 entities | ✅ (47 records) |
| `EntityResponse` schema expose | ⏳ TODO v6.87 |
| Frontend rendering | ⏳ TODO v6.88 |
| Wikidata drift incorporation | ⏳ TODO v6.89+ |
