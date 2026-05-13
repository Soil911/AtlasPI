# ADR-008 — Policy di versioning per `/v1/` (e quando aprire `/v2/`)

**Status**: Accettato v6.93.0 (2026-05-13)
**Autori**: audit architetturale 2026-05-13 (R9)
**Deciders**: Clirim Ramadani
**Riferimenti**: ADR-002 (REST design), ADR-007 (tool-augmented retrieval)

---

## Contesto

L'API publica e' montata interamente su `/v1/` da v1.0 (2026-04). Oggi
(v6.93.0) ci sono ~50 endpoint sotto `/v1/`. ADR-002 prometteva
"introdurre /v2/ se necessario, non modificare /v1/" ma non ha definito:

- **Cosa** conta come breaking change vs additive
- **Quando** aprire `/v2/`
- **Come** gestire la finestra di compatibilita'
- **Chi** notificare downstream (MCP server, ChatGPT plugin manifest,
  Postman public network, RapidAPI hub — quando attivati)

Senza policy esplicita, abbiamo accumulato breaking di fatto su `/v1/`
(es. v6.32 ha rimosso `top_ips`/`unique_ips` da `/admin/analytics/data`
— vedi 3 test xfailati in v6.92.4). E sono breaking che sfuggivano
perche' i consumer (frontend, MCP) erano sotto il nostro controllo.

Con il lancio post-v7.0 (Postman / RapidAPI / Show HN) i consumer
saranno esterni e impossibilita di rollback retroattivo.

## Decisione

### 1. Classificazione delle change

| Tipo | Esempi | Versione | Comunicazione |
|------|--------|----------|---------------|
| **Additive** | Nuovo endpoint, nuovo campo nella response | minor (`6.92` → `6.93`) | CHANGELOG.md |
| **Soft breaking** | Rimozione campo unused, rinomina alias | minor + deprecation note 1 release prima | CHANGELOG + warning header |
| **Hard breaking** | Cambio shape response, rename endpoint, rimozione field documentato, cambio semantica filter | **richiede `/v2/`** | ADR dedicato + 6 mesi co-esistenza |

Esempi concreti gia' visti in v6.92.x:
- `top_ips` rimosso da `/admin/analytics/data` → **hard breaking** (campo
  documentato in `tests/test_v6120_analytics.py` da v6.12.0). Avrebbe
  dovuto andare in `/v2/admin/analytics/data` se ci fosse stata `/v2/`.
- Aggiunta `boundary_aourednik_year` su `EntityResponse` → **additive**,
  ok in v1.

### 2. Trigger per aprire `/v2/`

Aprire `/v2/` quando una di queste e' vera:

- **≥ 3 hard breaking changes** in coda (giustifica il costo di
  mantenere 2 versioni co-esistenti).
- **Una hard breaking ha urgenza esterna** (es. legal, security,
  conformita' a uno standard emergente come MCP spec major version).
- **Refactor strutturale** che richiede shape diversa (es. PostGIS
  migration R1 — vedi ADR-009 — non richiede di per se' `/v2/` perche'
  la response shape resta GeoJSON, ma se cambiassero le coordinate da
  WGS84 a EPSG:3857 quello sarebbe motivo).

Non aprire `/v2/` per:

- Una singola hard breaking change (preferire deprecation in v1).
- Reorganizzazione interna (database split, modelli rinominati).
- Performance improvement (anche se cambia latency / TTL cache).

### 3. Quando si apre `/v2/`: protocollo

1. **ADR dedicato** che documenta:
   - Quali endpoint cambiano e come
   - Shape diff `/v1/` vs `/v2/` con esempi JSON
   - Migration guide per consumer (Python snippet di "find-replace")
   - Data di sunset di `/v1/`

2. **Co-esistenza minima 6 mesi**. `/v1/` resta funzionante ma:
   - Header `Deprecation: <RFC 7234 date>` su ogni response
   - Header `Sunset: <RFC 7234 date>` con la data di rimozione
   - Header `Link: </v2/path>; rel="successor-version"`
   - Logging in admin dashboard di hit residui su `/v1/`

3. **Sunset di `/v1/`**: dopo la finestra, `/v1/` risponde `410 Gone`
   con body che indica la versione successore. **Non** `404` —
   `410` segnala intenzionale rimozione vs path inesistente.

### 4. Soft breaking: protocollo deprecation in `/v1/`

Per rimuovere un field/parameter senza aprire `/v2/`:

1. **N-1 release**: la response include il field con valore `null` o
   placeholder, e response header `Sunset: <date>`. CHANGELOG marca
   come "DEPRECATED, removal in vN+1".

2. **N release**: field rimosso fisicamente.

3. **Tools update**: i 34 tool del MCP server v0.7.0 vanno sincronizzati
   nella stessa release (un tool che usa field rimosso → empty result).

### 5. Documenti che devono restare sincroni

Ogni breaking touch a `/v1/`:

| Documento | Aggiornamento richiesto |
|-----------|------------------------|
| `static/landing/index.html` | Code examples |
| `static/about.html` | Examples se citati |
| `src/main.py::OPENAPI_DESCRIPTION` | Examples |
| `static/llms.txt` | LLM-readable site map |
| `static/.well-known/ai-plugin.json` | OpenAI plugin schema |
| `mcp-server/src/*` | Tool definitions |
| `CHANGELOG.md` | Breaking note esplicita |

### 6. Esenzioni

I prefissi seguenti **non** seguono la stessa policy:

- `/admin/*` — dashboard interne, breaking ok senza ADR (notifica solo
  in CHANGELOG). Sono per cofounder, non per consumer publici.
- `/v1/csp-report` — endpoint browser-internal, formato dettato da CSP.
- `/_internal/*` (riservato future) — non esiste oggi, ma se introdotto
  segue regola admin.

## Alternative considerate

### Alt 1 — Date-based versioning (`/2026-05-13/`)

**Rejected.** Stile Stripe / GitHub. Funziona bene per API ad alto traffico
con migliaia di consumer. Per AtlasPI (early stage, <100 consumer
identificati) sarebbe over-engineering. Major-number semver e' piu'
intuitivo per developer.

### Alt 2 — Solo bump major del progetto, mai aprire `/v2/`

**Rejected.** Vincolarsi a non avere `/v2/` significa accumulare debt
fino a richiedere rewrite completo. La possibilita' di co-esistenza e'
il valore proprio di REST versioning.

### Alt 3 — Header-based versioning (`Accept: application/vnd.atlaspi.v2+json`)

**Rejected.** Tecnicamente piu' pulito (no path duplication) ma:
- Caching CDN piu' complesso (Vary header).
- Discoverability via OpenAPI peggiore (consumer puo' non sapere che
  esiste v2 senza leggere docs).
- I consumer principali (AI agent + curl-style script) usano path,
  non headers.

### Alt 4 — Path-based versioning con co-esistenza (adopted)

Scelto. Standard largo per REST. Cost mantenere 2 router parallelo per
6 mesi e' accettabile (in pratica copy del router, override solo gli
endpoint che cambiano).

## Conseguenze

### Positive

- **Stabilita' contrattuale**: i consumer esterni post-v7.0 launch
  hanno garanzia che `/v1/` non rompe sotto i loro piedi senza
  preavviso ufficiale.
- **Sblocca refactor di shape**: oggi i 3 test xfail su
  `/admin/analytics/data` indicano un breaking di fatto. La nuova
  policy avrebbe richiesto deprecation prima del cambio, oppure
  `/v2/admin/analytics/data`.
- **Scelta esplicita "no breaking small change"**: blocca la tentazione
  di "ottimizzare API rimuovendo field tanto nessuno lo usa".

### Negative

- **Friction per evoluzioni minori**: un campo "evidentemente unused"
  non puo' essere rimosso silenziosamente. Trade-off accettato.
- **Costo co-esistenza**: aprire `/v2/` richiede mantenimento `/v1/` per
  6 mesi. Stimo 1-2 PR/quarter di sync. Accettabile dato il volume
  attuale.

## Stato implementation

| Componente | Status |
|-----------|--------|
| ADR-008 (questo documento) | ✅ v6.93.0 |
| Update CHANGELOG con sezione "Breaking changes" template | ⏳ TODO v6.93.x |
| Aggiungere CI check su `/v1/` endpoints removed (compare openapi.json) | ⏳ TODO post-v7.0 |
| Tooling per generare migration guide `/v1` → `/v2` quando necessario | ⏳ TODO solo se `/v2/` viene aperto |

## Riapertura

Riapertura prevista quando una delle queste e' vera:
- Si decide di aprire `/v2/` per la prima volta (l'ADR sara' template
  per ADR-XXX dedicato a quella decisione).
- Si raggiungono 1000+ consumer / 1M req/day (forse passare a header-based
  diventa giustificato — re-evaluate Alt 3).
- Standard MCP spec introduce versioning di tools che richiede mirror.
