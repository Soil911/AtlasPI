# ADR-010 — `external_source_records` come pattern polymorphic per JSON-blob sources

**Status**: Accettato v6.98.0 (2026-05-13)
**Autori**: audit architetturale 2026-05-13 (R8)
**Deciders**: Clirim Ramadani
**Riferimenti**: ETHICS-005 (boundary provenance), ADR-007 (tool-augmented retrieval)

---

## Contesto

L'audit R8 ha identificato un'inconsistenza nello schema dati:

- `GeoEntity` (entità geopolitiche) ha **tabella relazionale** `sources` (FK
  su `geo_entities.id`). Citazioni queryabili, type-safe, JOIN-friendly.
- 6 altre tabelle hanno **JSON-blob Text** per le citazioni:
  `HistoricalCity`, `TradeRoute`, `DynastyChain`, `ArchaeologicalSite`,
  `HistoricalRuler`, `HistoricalLanguage`.

Limitazione del pattern JSON-blob:

```sql
-- Impossibile da fare oggi:
SELECT COUNT(*) FROM (
    SELECT 'city' AS type, id FROM historical_cities WHERE sources LIKE '%Cambridge History%'
    UNION ALL
    SELECT 'route' AS type, id FROM trade_routes WHERE sources LIKE '%Cambridge History%'
    ...
);
```

- LIKE su JSON Text è lento + fragile (matchi "Cambridge History" anche se citato
  come "Cambridge Hist." o "The Cambridge Encyclopedia").
- Nessun indice possibile su un campo dentro JSON serializzato.
- Nessuna FK / integrity check / cascade.
- Cross-resource attribution impossibile ("quali risorse citano X?").

## Decisione

Introdurre una tabella **polymorphic** `external_source_records`:

```sql
CREATE TABLE external_source_records (
    id          SERIAL PRIMARY KEY,
    parent_type VARCHAR(50)  NOT NULL,   -- 'city' | 'route' | 'chain' | 'site' | 'ruler' | 'language'
    parent_id   INTEGER      NOT NULL,
    citation    VARCHAR(1000) NOT NULL,
    url         VARCHAR(2000) NULL,
    source_type VARCHAR(30)  NOT NULL DEFAULT 'secondary',
    created_at  VARCHAR(50)  NOT NULL,   -- ISO 8601 timestamp del backfill
    UNIQUE(parent_type, parent_id, citation)
);

CREATE INDEX ix_source_records_parent ON external_source_records(parent_type, parent_id);
CREATE INDEX ix_source_records_citation ON external_source_records(citation);
CREATE INDEX ix_source_records_source_type ON external_source_records(source_type);
```

### Caratteristiche

- **Polymorphic** via `(parent_type, parent_id)` invece di FK foreach
  tabella (evita 6 FK e 6 cascade-delete trigger).
- **`source_type` ENUM** allineato al `SourceType` Python (vedi
  `src/db/enums.py`): primary | secondary | academic | oral_tradition |
  archaeological | indirect_reference.
- **UNIQUE constraint** `(parent_type, parent_id, citation)`: una stessa
  fonte non puo' essere duplicata sulla stessa risorsa.
- **`created_at`** tracking quando il record e' stato sincronizzato
  dal JSON.

### Strategia: source-of-truth vs mirror

**Il JSON-blob su ogni tabella resta CANONICO.** `external_source_records`
e' un **mirror queryable** popolato via script idempotente.

Motivazione:

1. **Backward compat assoluta**: tutti gli endpoint che oggi serializzano
   `sources` come JSON nel response (cities, routes, chains, ecc.)
   continuano a funzionare invariati.
2. **Migrazione incrementale**: il JSON e' fonte di verita' durante la
   transizione. Lo script di sync e' idempotente, ri-eseguibile.
3. **Riducibile a relazionale puro in futuro**: quando tutti i
   consumer downstream useranno `external_source_records` come fonte
   primaria, il JSON puo' essere droppato in v7.x (breaking change
   gated da ADR-008 deprecation protocol).

### Script `scripts/sync_source_records.py`

Backfill manuale (NON al boot — overhead non giustificato):

```bash
# Sincronizza tutto
docker exec cra-atlaspi python -m scripts.sync_source_records

# Solo un tipo (rebuild dopo dataset update)
docker exec cra-atlaspi python -m scripts.sync_source_records --only cities

# Dry-run
docker exec cra-atlaspi python -m scripts.sync_source_records --dry-run
```

Logica per ogni tabella:
1. Carica tutti i record con `sources != NULL`.
2. Parse JSON (lista di dict `{citation, url, source_type}`).
3. Insert in `external_source_records` con UPSERT su
   `(parent_type, parent_id, citation)` — duplicati skippati.

Tempo stimato: ~5s su 1500 totali (110 cities + 41 routes + ~30
chains + 1249 sites + 105 rulers + 29 languages).

## Alternative considerate

### Alt 1 — Replace JSON con relazionale per ogni tabella (6 tabelle dedicate)

```sql
CREATE TABLE city_sources (city_id, citation, url, source_type, ...);
CREATE TABLE route_sources (route_id, citation, url, source_type, ...);
-- ... 6 tabelle totali
```

**Rejected.** Beneficio modesto (cross-table query impossibile lo
stesso senza UNION 6 volte). Replicazione schema. Migration breaking
per tutti i consumer downstream che serializzano JSON nel response.

### Alt 2 — Tabella unica polymorphic + sync mirror (adopted)

**Adopted.** Pattern Discriminator-Single-Table (gia' usato in altri
sistemi come Stripe `events`, GitHub `subscriptions`).

Trade-off:
- (+) 1 indice per tutte le query cross-source.
- (+) Backward compat 100%.
- (+) Future-proof: il JSON puo' essere droppato dopo deprecation.
- (−) `parent_id` non e' FK a single tabella → no DB-level integrity
  per orfani (es. una citazione per una `city_id` che non esiste piu').
  Mitigato dal sync periodico che riazzera `parent_type`-specific
  records prima del repopulate.

### Alt 3 — JSON-LD / RDF triplestore

**Rejected.** Pattern molto piu' potente (sources con vocabolari
controllati: Schema.org `Citation`, Dublin Core), ma overkill per
AtlasPI scale. Aggiunge dep su rdflib + complessita' query SPARQL.

## Conseguenze

### Positive

- **Query cross-source**: "quali risorse citano 'Cambridge Histories'?"
  diventa una SELECT con LIKE su indice.
- **Citation analytics**: "le 20 fonti piu' citate nel dataset" via
  GROUP BY + COUNT.
- **Source-type aggregato**: "quante fonti primary vs academic in
  totale?".
- **Foundation per future endpoint** `/v1/sources/search?q=...` e
  `/v1/sources/{citation}/citers` (additive, non-breaking).

### Negative

- **Doppia rappresentazione**: JSON canonical + mirror relational.
  Storage ~+0.5MB (1500 records × ~300 byte avg).
- **Sync overhead**: backfill manuale required dopo modifica JSON.
  Mitigato con script idempotente + futuro hook al lifespan.
- **No DB-level orfani protection**: parent_type/parent_id potrebbero
  riferire a record cancellati. Lo script di sync ri-pulisce ogni run.

## Stato implementation

| Componente | Status |
|-----------|--------|
| ADR-010 (questo documento) | ✅ v6.98.0 |
| Alembic migration 020 (create table + indici + unique) | ✅ v6.98.0 |
| `scripts/sync_source_records.py` | ✅ v6.98.0 |
| Endpoint `/v1/sources/search` | ⏳ TODO v7.x (additive) |
| Endpoint `/v1/sources/{citation}/citers` | ⏳ TODO v7.x (additive) |
| Auto-sync al boot (se justified) | ⏳ valutare post-launch |
| Drop JSON sources columns (breaking) | ⏳ post-v7.0 deprecation cycle |

## Riapertura

Riapertura prevista quando:
- Un consumer chiede esplicitamente cross-source query → priorità
  endpoint `/v1/sources/search`.
- Le citazioni superano 10000 records (oggi ~5000 stimati) → potrebbe
  giustificare full text search via PostgreSQL `tsvector` + GIN index.
- Si decide di droppare le colonne `sources` JSON (breaking) →
  ADR dedicato + ADR-008 deprecation cycle.
