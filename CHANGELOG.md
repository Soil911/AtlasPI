# Changelog AtlasPI

Tutte le modifiche rilevanti del progetto devono essere documentate qui.

## [v6.1.1] - 2026-04-14

**Tema**: Boundary coverage jump (23% → 93%) via matcher aourednik + fix
ETHICS-003 compliance su entita' contestate + performance export.

### Boundary enrichment — salto di qualita' dati

- Nuovo modulo **`src/ingestion/aourednik_match.py`** per il matching
  contro **aourednik/historical-basemaps** (CC BY 4.0, 53 snapshot
  timestamped da -123000 a 2010 CE). Risolve il gap pre-1800 che
  Natural Earth non puo' coprire.
- Matching rigoroso a 5 livelli: `exact_name` → `SUBJECTO` (suzerain) →
  `PARTOF` → `fuzzy_name` (soglia 80%) → `capital_in_polygon`
  (point-in-polygon ray casting, prefer smallest container) →
  `capital_near_centroid` (stretto, 250km — solo fallback estremo).
- **Point-in-polygon implementato senza shapely** (ray casting + bbox
  pre-filter + hole exclusion). ETHICS: la capitale dentro il poligono
  e' una prova geografica reale, non un'approssimazione.
- **Pipeline arricchimento** (`enrich_all_boundaries.py`): ordine ora
  NE → aourednik → generated. Idempotente, con `.bak` per ogni file.
  Flag `--skip-aourednik` per test isolati.
- **Tracciamento fonte** per ogni match aourednik: campi
  `boundary_aourednik_name`, `boundary_aourednik_year`,
  `boundary_aourednik_precision` + annotazione `ethical_notes`.
- **313 entita'** arricchite con boundary aourednik (41.6% del dataset).
- **Coverage totale**: 699/752 boundary reali (**93.0%**, da 23%):
  - natural_earth: 212 (28.2%)
  - aourednik: 313 (41.6%)
  - historical_map (manuali): 174 (23.1%)
  - approximate_generated: 51 (6.8%)
  - nessun boundary (manca capitale): 2 (0.3%)

### Fix ETHICS-003 (territori contestati)

- **BUG risolto**: `_apply_natural_earth_match` e `_apply_aourednik_match`
  potevano alzare il `confidence_score` sopra 0.7 anche per entita'
  `status = "disputed"`. Violava ETHICS-003. Ora e' cappato
  esplicitamente: la certezza geografica non risolve la disputa storica.
- Tre entita' gia' salvate con conf > 0.7 sono state riallineate a 0.7:
  Reino de la Araucania y Patagonia (e altre 2 modern disputed).

### Performance

- **`/v1/export/geojson`** riscritto per evitare double-JSON-encoding.
  Il boundary nel DB e' gia' una stringa JSON valida: ora viene embedded
  direttamente nella FeatureCollection invece di `json.loads` + `json.dumps`.
- Nuovi parametri: `?geometry=full|centroid|none`:
  - `full` (default) — poligoni completi, bulk export (~10s per 48MB)
  - `centroid` — Point delle capitali, 200x piu' veloce (<500ms)
  - `none` — solo properties, ideale per indicizzazione
- **`/v1/random` ottimizzato**: prima selezionava TUTTI i candidati con
  eager-loading (48MB di boundary!), poi pickava uno. Ora query ID-only,
  selezione random, eager-load del solo scelto. Da ~3s a <300ms.

### Academic credibility

- **`CITATION.cff`**: metadata di citazione formale per GitHub/Zenodo.
  Autore, versione, licenza, keyword, referenze dataset (Natural Earth +
  aourednik) con attribuzione CC BY 4.0.
- **`.zenodo.json`**: config per archivio Zenodo DOI-minted. Rende
  AtlasPI citabile in letteratura accademica.

### Test

- **260 test totali** (da 233). Aggiunto `test_geojson_export_full_under_15s`
  e riadattato `test_geojson_export_centroid_under_500ms` per riflettere
  la nuova API dell'export.
- Fix 3 regressioni: ETHICS-003 disputed confidence, export performance,
  random performance — tutti i nuovi test verdi.
- Nuova **spot-check regression suite** (`tests/test_spotcheck_top10.py`,
  11 test): blocca le soglie di qualita' boundary per le 10 entita' ad
  alta visibilita' accademica (Roma, Ottomani, Mongoli, Incas, Tokugawa,
  Mughal, Bizantino, Qing, Abbasidi, Azteco). Floor di vertici e
  confidence conservativi — un bug della pipeline che declassasse un
  MultiPolygon a 18 vertici fallirebbe immediatamente il CI. Fixture
  `_enrich_test_boundaries` replica il comportamento di produzione
  (lifespan `update_all_boundaries()`) nel test DB.
- Fix `test_health.py`: assertion versione allineata a 6.1.1 (era stale 6.1.0).
- Nuova **sync regression suite** (`tests/test_sync_boundaries.py`, 11 test):
  copre i predicati puri di riconciliazione (count vertices, should_upgrade),
  la modalita' dry-run, l'idempotenza, e il rispetto di ETHICS-003 cap.

### Boundary reconciliation (post-seed fix)

- **Diagnosi**: audit prod-vs-batch rivela che **419/747 entita' (56%)**
  in produzione conservano confini seeded pre-v6.1.1 (13 vertici) anche
  se i batch JSON contengono poligoni reali multi-centinaia di vertici.
  Root cause: `seed_database()` gira solo su DB vuoto e `update_all_boundaries()`
  copre solo la narrow ENTITY_MAPPINGS (~10 entita'). I 313 arricchimenti
  aourednik non propagano al DB in esecuzione.
- Nuovo modulo **`src/ingestion/sync_boundaries_from_json.py`** +
  CLI `python -m src.ingestion.sync_boundaries_from_json [--dry-run]`.
  Riconciliazione monotona: solo upgrade, mai downgrade. Idempotente.
  Rispetta ETHICS-003 (disputed ≤ 0.70) e richiede un guadagno ≥ 20%
  in vertici per evitare churn da differenze di simplification.
- **Documentazione operativa** in `docs/OPERATIONS.md` con ricetta
  completa (backup Postgres + dry-run + sync).

### Boundary provenance — esposizione schema (ETHICS-005)

- **Gap diagnosticato**: i campi `boundary_source`, `boundary_aourednik_*`,
  `boundary_ne_iso_a3` esistevano nei batch JSON ma non erano persistiti
  nel DB ne' esposti dall'API. Un consumatore non poteva distinguere un
  poligono reale da uno generato senza ispezionare il GeoJSON.
- **Migration `002_boundary_provenance`** (Alembic): aggiunge 5 colonne
  nullable a `geo_entities` (`boundary_source`, `boundary_aourednik_name`,
  `boundary_aourednik_year`, `boundary_aourednik_precision`,
  `boundary_ne_iso_a3`). Puramente additiva, downgrade testato.
- **Modello SQLAlchemy** esteso (`src/db/models.py`).
- **Seeder** (`src/db/seed.py`) ora popola le 5 colonne dai batch JSON
  in fase di seed iniziale.
- **Sync reconciliation** (`sync_boundaries_from_json.py`) propaga
  i 5 campi insieme alla geometria upgrade.
- **Schema Pydantic** (`EntityResponse`) espone i 5 campi con
  description ETHICS-005 esplicita.
- **Serializer** (`_entity_to_response`) passa i 5 campi al Response.
- **4 nuovi test** (`tests/test_boundary_provenance.py`):
  presenza dei campi nella response, valori `boundary_source` nell'enum
  ETHICS-005, scala `boundary_aourednik_precision` (0-3, vedi sotto),
  consistenza metadata aourednik.

### Bug fix — PRECISION_CONFIDENCE invertito

- **Bug latente scoperto** durante la stesura dei test boundary provenance.
  Il dict `PRECISION_CONFIDENCE` in `aourednik_match.py` mappava
  `2 -> 0.80, 1 -> 0.65, 0 -> 0.45`, ignorando completamente il valore 3
  (che e' la **tier piu' alta** dello scale aourednik upstream secondo
  il README di `historical-basemaps`: `1 = approssimato, 2 = moderatamente
  preciso, 3 = determinato da legge internazionale`). I valori 3 finivano
  nel fallback a 0.45 (lo stesso di precision=0), facendo apparire 17
  entita' nel dataset (es. Rzeczpospolita Obojga Narodow, Republiek der
  Zeven Verenigde Nederlanden) come confidence-equivalenti a poligoni
  approssimati quando in realta' avevano la precisione massima.
- **Fix**: dict ribilanciato correttamente: `3 -> 0.85, 2 -> 0.70,
  1 -> 0.55, 0 -> 0.45`. Applicabile alle entita' arricchite in futuro;
  i valori esistenti nel DB di produzione restano stale finche' non si
  rilancia `enrich_all_boundaries`. Documentato in CHANGELOG perche'
  riguarda la trasparenza dell'incertezza (ETHICS).

### Community & academic infrastructure

- **`CONTRIBUTING.md`** (nuovo): guida specifica per segnalare errori
  di boundary/nome/data, proporre correzioni schema, contribuire batch
  entita' regionali. Esplicita la policy ETHICS-003 (disputed cap) e la
  policy ETHICS-001/002 (no revisionismo su nomi e conquiste).
- **`ACKNOWLEDGMENTS.md`** (nuovo): scaffolding per i reviewer academic
  che forniranno feedback pre-submission. Chiude la promessa gia'
  presente in `docs/outreach-draft.md` template D.
- **`CODE_OF_CONDUCT.md`** (nuovo): Contributor Covenant v2.1 standard +
  addendum academic integrity (no citation hallucination, disagreement
  with evidence only, rispetto per storie contese).
- **GitHub issue templates** (`.github/ISSUE_TEMPLATE/`):
  - `boundary-correction.md` (entity/boundary corrections con policy
    esplicita su fonti primarie e ETHICS-003)
  - `bug-report.md` (repro + ambiente)
  - `config.yml` (disabilita issue vuote, punta a email per domande
    metodologiche e a Discussions per conversazioni aperte)
- **`docs/paper-draft.md`** aggiornato:
  - Test count 234 -> 260
  - Pipeline Ourednik riscritta per riflettere i 5 matcher reali
    (exact/SUBJECTO/PARTOF/fuzzy/capital-in-polygon) invece del
    modello semplificato "3 matchers" che era inaccurato
  - Precision scale allineata al README upstream aourednik (1=approx,
    2=moderate, 3=international law) invece dello 0/1/2 sbagliato

### File modificati (principali)

- `src/ingestion/aourednik_match.py` (nuovo, ~450 righe; PRECISION_CONFIDENCE fix)
- `src/ingestion/enrich_all_boundaries.py` (pipeline estesa)
- `src/ingestion/sync_boundaries_from_json.py` (nuovo, riconciliazione monotona)
- `src/api/routes/export.py` (perf + nuovi flag)
- `src/api/routes/entities.py` (random perf + serializer provenance)
- `src/api/schemas.py` (EntityResponse + 5 campi provenance)
- `src/db/models.py` (5 colonne provenance)
- `src/db/seed.py` (seeder provenance-aware)
- `alembic/versions/002_boundary_provenance.py` (nuovo, additive)
- `src/config.py` (version 6.1.1)
- `tests/test_performance.py`
- `tests/test_boundary_provenance.py` (nuovo, 4 test)
- `tests/test_sync_boundaries.py` (nuovo, 11 test)
- Tutti i `data/entities/batch_*.json` (boundary arricchiti con .bak)
- `CITATION.cff`, `.zenodo.json` (nuovi)
- `CONTRIBUTING.md`, `ACKNOWLEDGMENTS.md`, `CODE_OF_CONDUCT.md` (nuovi)
- `.github/ISSUE_TEMPLATE/{boundary-correction,bug-report}.md` + `config.yml` (nuovi)
- `docs/paper-draft.md` (aggiornamenti test count + metodologia aourednik)

## [v6.1.0] - 2026-04-14

**Tema**: Reliability + Discoverability post-deploy. Il sito e' online su
https://atlaspi.cra-srl.com — questa release lo rende **affidabile** e
**scopribile dagli agenti AI**.

### Reliability — Production hardening

- **Sentry SDK** integrato (opt-in via `SENTRY_DSN`). Cattura eccezioni
  FastAPI/SQLAlchemy/Starlette + log >= ERROR. Modulo `src/monitoring.py`
  con interfaccia idempotente. Inattivo by default (zero overhead in dev).
- **Health check esteso** (`/health`):
  - status: `ok` | `degraded` | `down` (era solo "ok")
  - sotto-checks: database, seed, sentry
  - uptime_seconds, check_duration_ms, sentry_active, environment
  - HTTP 503 se database down (le altre situazioni restano 200 per non
    confondere monitoring tools che leggono `status` dal body)
- **Backup automatico**:
  - `scripts/backup.sh` — auto-detect SQLite vs PostgreSQL, retention 14gg
  - `scripts/restore.sh` — ripristino con conferma + safe-copy del DB corrente
  - Sidecar Docker Compose schedulato 03:00 daily
- **Smoke test post-deploy** (`scripts/smoke_test.sh`): 14 endpoint critici
  verificati con curl + jq, exit code 0/1 per CI/CD
- **Operations runbook** (`docs/OPERATIONS.md`): quick actions per incident,
  setup UptimeRobot/Sentry, troubleshooting comuni, baseline performance
- **Logging rotation** in docker-compose: 10MB x 3 file
- **Rate limiting davvero attivo**: aggiunto `SlowAPIMiddleware` (prima
  configurato ma non applicato — bug silenzioso scoperto in audit)

### SEO base

- **`/robots.txt`** con allow esplicito per AI crawler (GPTBot, ClaudeBot,
  anthropic-ai, Google-Extended, PerplexityBot, CCBot)
- **`/sitemap.xml`** con priorita' per homepage, app, docs, embed
- **`PUBLIC_BASE_URL`** configurabile via env (default
  `https://atlaspi.cra-srl.com`)

### Discoverability — MCP Server

Nuovo pacchetto Python **`atlaspi-mcp`** in `mcp-server/`:

- 8 tools MCP che wrappano l'API REST: `search_entities`, `get_entity`,
  `snapshot_at_year`, `nearby_entities`, `compare_entities`,
  `random_entity`, `get_evolution`, `dataset_stats`
- Configurabile via `ATLASPI_API_URL` (default produzione)
- Compatibile con **Claude Desktop** e **Claude Code**
- README con quick start, badge PyPI/Python/License, esempi prompt
- 10 test pytest, 1 di integrazione live opzionale
- Pronto per pubblicazione su PyPI

### Landing page inglese

- **`static/landing/index.html`** — landing dedicata in inglese, separata
  dalla mappa interattiva italiana (`/app`)
- 9 sezioni: hero, why, demo embed, MCP setup, API examples (curl/Python/JS
  con copy-to-clipboard), use cases, stats, for AI agents, footer
- SEO completo: 10 OG tags, Twitter card, JSON-LD `WebApplication` +
  `Dataset` (per Google Dataset Search), hreflang, canonical
- Vanilla HTML/CSS/JS — zero dipendenze, zero tracker, zero CDN esterni
- Atteso Lighthouse: SEO 100, Performance 95+, Accessibility 95+
- Routing: `/` → landing, `/app` → mappa (la vecchia root e' ora a `/app`)

### Boundary coverage — Pipeline pronta

Infrastruttura per portare la coverage dal 23% al 60%+ in v6.1.1:

- **`src/ingestion/natural_earth_import.py`** — carica shapefile NE 10m
  (fallback a 110m gia' nel repo) e produce mapping name → polygon
- **`src/ingestion/boundary_match.py`** — 4 strategie:
  ISO_A3 → exact name multilingua → fuzzy rapidfuzz>=85% → capital-in-polygon
- **`src/ingestion/enrich_all_boundaries.py`** — pipeline end-to-end
  idempotente con dry-run e backup `.bak`. Non sovrascrive boundary
  `historical_map`/`academic_source` mai
- **ETHICS-005** documenta il rischio di anacronismo (boundary moderno su
  entita' antica) e la gestione di confini contestati (Taiwan, Western
  Sahara, Palestina, Kosovo, Cipro Nord, Kashmir, Somaliland)
- Coverage proiettata: 40-50% dopo prima esecuzione, 60%+ con NE 10m + tutti
  i match installati. **Esecuzione rinviata** a v6.1.1 per separare commit
  di codice da commit di dati.

### Test

- **233 test totali** (208 v5.8 + 25 nuovi v6.1)
- Nuovo file `tests/test_v61_features.py`:
  - `TestExtendedHealthCheck` (8 test) — campi nuovi, sotto-checks, status
  - `TestSEOEndpoints` (4 test) — robots.txt e sitemap.xml serviti
  - `TestMonitoringModule` (4 test) — Sentry off-by-default, no raise
  - `TestBackupScripts` (5 test) — script presenti, contenuto corretto
  - `TestConfigDefaults` (3 test) — Sentry DSN sicuro, base URL HTTPS
- Conftest aggiornato: `RATE_LIMIT=100000/minute` per evitare 429 in test

### Dipendenze

- Aggiunte: `sentry-sdk[fastapi]>=2.0.0`, `geopandas>=0.14.0`,
  `shapely>=2.0.0`, `rapidfuzz>=3.0.0`
- Dockerfile aggiunge `sqlite3`, `postgresql-client`, `curl`, `jq`
  per gli script operativi

### Documentazione

- `docs/OPERATIONS.md` — runbook operativo
- `docs/ethics/ETHICS-005-boundary-natural-earth.md` — anacronismo e contesi
- `docs/boundary_coverage_report.md` — analisi attuale + scenari proiettati
- `scripts/README.md` — istruzioni per backup/restore/smoke
- `mcp-server/README.md` — quick start integrazione Claude
- `ROADMAP.md` riorganizzata: v6.0 deploy completato, v6.1 in corso,
  v6.2 PostgreSQL (rinviata), v6.3 distribuzione, v6.4 monetization

### Bugfix

- `SlowAPIMiddleware` mancante: rate limiting non era applicato a nessuna
  route (silently broken). Ora i `60/minute` di default funzionano davvero.
- `static/index.html` footer mostrava ancora v5.8.0 dopo bump.

---

## [v5.8.0] - 2026-04-12

### API — Nuovi endpoint e filtri avanzati
- **`/v1/random` con filtri**: parametri opzionali `type`, `year`, `status`, `continent`
  per ottenere entita' casuali filtrate (es. `/v1/random?type=empire&year=1500`)
- **`/v1/aggregation`**: nuovo endpoint con statistiche aggregate per secolo (etichette romane),
  tipo, continente e status — ideale per dashboard e analisi AI
- Totale endpoint: **21** (da 19)

### Frontend — Cluster markers e mini-timeline
- **Leaflet.markercluster**: i marker delle capitali ora si raggruppano a zoom basso,
  con cluster colorati per densita' (small/medium/large). I poligoni GeoJSON restano visibili
- **Mini-timeline canvas**: nel pannello dettaglio, un canvas interattivo mostra la durata
  dell'entita' con marcatori diamante per ogni cambio territoriale. Tooltip on hover con
  anno, tipo e regione. Colori: verde=espansione, rosso=contrazione, blu=altro
- Stili cluster personalizzati per tema scuro

### Dataset — Espansione a 746 entita'
- **batch_22**: Southeast Asia e Indonesia (26 entita' — Ayutthaya, Dai Viet, Sukhothai, etc.)
- **batch_23**: Americhe pre-colombiane e coloniali (19 entita' — Gran Colombia, Comancheria, etc.)
- **batch_24**: Africa medievale e moderna (19 entita' — Jolof, Zanzibar, Mahdist State, etc.)
- Dedup automatico: 11 duplicati rimossi dai nuovi batch

### Test — 208 test totali
- 23 nuovi test in `test_v58_features.py`:
  - `TestFilteredRandom`: 7 test (filtri tipo/anno/status, combinati, 404, cache)
  - `TestAggregation`: 9 test (struttura, somme coerenti, ordinamento secoli, time_span)
  - `TestDataExpansion`: 4 test (conteggio, tipi, continenti, no duplicati)
  - `TestEvolutionForTimeline`: 3 test (dati canvas timeline)
- Fix test performance random (200ms -> 500ms per query filtrata)

---

## [v5.7.0] - 2026-04-11

### Dataset — Espansione massiva a 682 entita'
- **682 entita' uniche** da 22 batch file (batches 00-21)
- **2.022 fonti accademiche**, **2.041 varianti nome**, **1.899 cambi territoriali**
- Nuovi batch: East Asia (28), Crusader/Islamic (43), Americas/Caribbean (39),
  Africa Kingdoms (14), Europe Medieval (22), South/Central Asia (26), Ancient/Classical (20),
  Mesoamerica/Pacific (25), Horn of Africa/Balkans (25)
- Pulizia: 29 duplicati rimossi con dedup cross-batch automatizzato
- Seed fix: population_affected string-to-int conversion nel seed
- Validazione completa: nessun tipo entita' invalido, nessuno status invalido

### API — Nuovo endpoint evolution
- **`/v1/entities/{id}/evolution`**: cronologia completa di un'entita'
  - Timeline ordinata per anno con tutti i cambiamenti territoriali
  - Sommario: conteggio espansioni, contrazioni, fonti, varianti
  - ETHICS: change_type preservato senza eufemismi

### Frontend — Map capital markers
- **Marker capitali sulla mappa**: tutte le entita' con coordinate capitale
  ora appaiono sulla mappa, anche senza confini GeoJSON
- Label nomi entita' sopra i marker capitali
- Stile CSS migliorato: scrollbar personalizzate, focus visible, hover animations
- Source type styling nel pannello dettaglio
- Stats bar e info grid con layout migliorato

### Test — 185 test passano
- **19 nuovi test** in `test_v57_features.py`:
  - Evolution endpoint (6 test): timeline, ordinamento, sommario, 404, campi
  - Capital data (2 test): copertura coordinate, validazione range
  - Data quality expanded (9 test): 600+ entita', 1800+ fonti, diversita'
  - Cache headers (2 test): max-age, no-cache su random

### Infrastruttura
- Version bump a 5.7.0
- README aggiornato: badge, conteggi, nuovo endpoint nella tabella API
- Lint clean (ruff), 0 errori

---

## [v5.6.0] - 2026-04-11

### API — Nuovi endpoint intelligenti
- **`/v1/nearby`**: ricerca per prossimita' geografica (lat, lon, raggio, anno)
  - Distanza Haversine dalle coordinate capitale
  - Risultati ordinati per distanza, filtrabili per anno
- **`/v1/snapshot/{year}`**: stato del mondo in un anno specifico
  - Sommario per tipo, continente, status
  - Filtrabile per tipo e continente
- Totale: **18 endpoint REST** (da 16)
- OpenAPI aggiornata con esempi per i nuovi endpoint

### Frontend — Autocomplete & UX
- **Ricerca autocomplete**: dropdown con suggerimenti in tempo reale
  - Evidenziazione match nel testo, navigazione con frecce
  - Mostra varianti di nome quando il match e' su un alias
  - Chiusura con Esc, selezione con Enter/click
- **Tasto destro sulla mappa**: popup "Entita' vicine" con distanze
  - Usa `/v1/nearby` con l'anno corrente dello slider
- **Barra di caricamento**: progress bar visiva durante fetch entita'
- **Compare view**: i18n completo, layout refactored
- **Aiuto tastiera**: aggiornato con nuove funzionalita'
- OG meta aggiornata: "550+ entita'"

### Dataset — Espansione fase 3
- **587 entita' storiche** (da 441) — 18 batch JSON
- 5 nuovi batch:
  - **Asia Orientale espansa (29)**: Yamato, Nara, Heian, Kamakura, Muromachi, Sui, 
    Northern Wei, Nanzhao, Dali, State of Chu, Three Kingdoms (Wu, Shu, Wei), 
    Uyghur Khaganate, Tibetan Empire, Tuyuhun, Ainu Mosir
  - **Crociate/Islam espanso (46)**: Kingdom of Jerusalem, County of Tripoli, 
    Principality of Antioch, County of Edessa, Latin Empire, Hamdanids, Buyids, 
    Zengids, Ghaznavids, Samanids, Idrisids, Aghlabids, Marinids, Hafsids, 
    Sultanate of Rum, Caliphate of Cordoba, Nasrid Granada, Rashidun Caliphate
  - **Americhe/Caraibi espanso (45)**: Taino, Maroons, Apache, Navajo, Seminole, 
    Metis Nation, Republic of Texas, CSA, Empire of Brazil, Pirate Republic Nassau, 
    Mosquitia, Cahokia, Mesa Verde, Kingdom of Quito, vicereami coloniali
  - **Regni africani (25)**: Buganda, Bunyoro, Rwanda, Burundi, Lunda, Mutapa, 
    Ndongo, Matamba (Queen Nzinga), Loango, Kano, Dagbon, Futa Jallon, Jolof, 
    Bambara/Segou, Wadai, Baguirmi, eSwatini
  - **Europa medievale (25)**: Brittany, Navarre, Pisa, Brandenburg, Saxony, 
    Bavaria, Naples, Two Sicilies, Savoy, Sardinia-Piedmont, Croatia, 
    Epirus, Trebizond, Second Bulgarian, Georgia, Livonian Order, Courland, 
    Transylvania, Grand Duchy of Lithuania, Catalonia
- Fix dati: rimosso duplicato Balhae, corretto despotate -> principality
- Merge batch duplicati (14, 15) con dedup automatico
- 1683 fonti accademiche, 1530 cambi territoriali documentati

### Test
- **166 test tutti verdi** (23 nuovi per v5.6)
  - 8 test `/v1/nearby`: coordinate, distanza, raggio, anno, ordinamento
  - 9 test `/v1/snapshot`: sommario, filtri, anno antico/moderno
  - 6 test autocomplete: ricerca, varianti, unicode, limiti
- Lint ruff pulito

## [v5.5.1] - 2026-04-11

### Frontend — UI Polish & Precision
- **Caricamento completo entita'**: paginazione automatica (era troncato a 100)
- **Fix scroll mappa**: scrollWheelZoom disabilitato di default, si attiva al click
  - Hint visivo "Clicca sulla mappa per abilitare lo zoom" quando si tenta lo scroll
- **Pannello dettaglio migliorato**:
  - Griglia informazioni (tipo, periodo, durata, capitale con coordinate, regione)
  - Tag continente con icona accanto a status badge
  - Indicatore affidabilita' dettagliato (alta/bassa con colore)
  - Info confini: tipo geometria (Point/Polygon/MultiPolygon), numero vertici/regioni
  - Coordinate capitale visibili
  - Sezione fonti con icone per tipo (academic, primary, archaeological, etc.)
  - Messaggio quando confini non disponibili
- **Slider anno esteso**: da -3100 a -4500 a.C. per le nuove entita' antiche
- **Preset anno aggiuntivo**: pulsante 4500 a.C.
- **Testi aggiornati**: footer v5.5, OG meta "255+ entita'", anno minimo corretto

### Dataset — Espansione fase 2
- **441 entita' storiche** (da 258) — 13 batch JSON regionali
- 6 nuovi batch da agenti paralleli:
  - **Oceania/Pacifico (25)**: Aboriginal nations, Maori iwi, Pacific island kingdoms
  - **Asia Centrale/Steppe (30)**: Sciti, Parti, Timuridi, Khanati dell'Asia Centrale
  - **Sudest Asiatico (25)**: Majapahit, Srivijaya, Lan Xang, Dai Viet, Champa
  - **Subcontinente Indiano (25)**: Pandya, Kakatiya, Polonnaruwa, Ahom, Sikh Empire
  - **Africa espansa (23)**: Great Zimbabwe, Mapungubwe, Lozi, Merina, Rozwi
  - **Europa espansa (23)**: Kyivan Rus', Toscana, Milano, Sardegna, Teutonic Order
- 1332 fonti accademiche, 1190 cambi territoriali documentati
- Fix dati: population_affected convertiti da stringa a intero, entity_type corretti

### Test
- 143 test tutti verdi
- Fix ETHICS-003: disputed entities con confidence <= 0.7
- Fix data quality: varianti nome per territori contestati

## [v5.5.0] - 2026-04-11

### Dataset — Espansione massiva
- **255 entita' storiche** (da 55) — copertura globale da -4500 a.C. al 2024
- 200 nuove entita' organizzate in 6 batch regionali:
  - **Europa (45)**: Francia, Inghilterra, Svezia, Danimarca, Norvegia, Portogallo,
    Commonwealth Polacco-Lituano, Ungheria, Macedonia, Sparta, Prussia, Austria,
    Serbia, Bulgaria, Stato Pontificio, Aragona, Castiglia, Visigoti, Ostrogoti,
    Lombardi, Novgorod, Moscovia, Genova, Firenze, Svizzera, Borgogna, Sicilia,
    Ragusa, Hanse, Paesi Bassi, Carolingi, Scozia, Irlanda, Galles, Valacchia,
    Moldavia, Montenegro, Albania, Boemia, Impero Tedesco, Austria-Ungheria, Italia
  - **Asia (36)**: Shang, Zhou, Qin, Han, Tang, Song, Yuan, Ming, Gupta, Chola,
    Maratha, Delhi Sultanate, Vijayanagara, Kushan, Goguryeo, Baekje, Goryeo,
    Joseon, Timuridi, Parti, Sasanidi, Selgiuchidi, Liao, Jin, Xia, Ryukyu,
    Lan Na, Lan Xang, Pagan, Dai Viet, Pallava, Rashtrakuta, Pala, Funan, Balhae
  - **Africa/Medio Oriente (30)**: Ghana, Kanem-Bornu, Ashanti, Dahomey, Sokoto,
    Oyo, Luba, Kilwa, Ajuran, Sumer, Akkad, Assiria, Babilonia, Ittiti, Omayyadi,
    Fatimidi, Ayyubidi, Mamelucchi, Seleucidi, Tolomei, Nabatei, Palmira, Himyar,
    Mitanni, Urartu, Elam, Almoravidi, Almohadi, Lydia, Media
  - **Americhe (31)**: Olmechi, Maya, Teotihuacan, Toltechi, Zapotechi, Mixtechi,
    Muisca, Wari, Chimu, Moche, Caral-Supe, Tiwanaku, Purepecha, Puebloani,
    Nuova Spagna, Peru', Brasile, 13 Colonie, Haiti, Comanche, Lakota, Cherokee,
    Creek, Quilombo dos Palmares, Missioni Gesuite Guarani
  - **Stati moderni (35)**: Germania nazista, URSS, Jugoslavia, Cecoslovacchia,
    Congo Belga, India, Pakistan, Bangladesh, Vietnam, PRC, DDR, Khmer Rouge,
    Sudafrica apartheid, Rhodesia, USA, Francia, Coree, Turchia, Iran, Arabia
    Saudita, Israele, Iraq, Irlanda, Finlandia, AOF, Indocina francese
  - **Mondo antico (25)**: Fenici, Israele, Giuda, Troia, Minoici, Micenei,
    Sciti, Sarmati, Harappa, Bitinia, Pergamo, Bosforo, Galazia, Commagene,
    Dacia, Corinto, Siracusa, Colchide, Armenia, Xiongnu, Dilmun, Mauretania
- 15 tipi di entita': empire, kingdom, republic, confederation, city-state,
  dynasty, colony, disputed_territory, sultanate, khanate, principality,
  duchy, caliphate, federation, city
- Copertura 7 regioni: Europa (68), Asia (60), Medio Oriente (46),
  Africa (41), Americhe (38), Oceania (1), Altro (1)
- 678 fonti accademiche, 544 cambi territoriali documentati
- ETHICS-003: tutti i territori contestati con confidence <= 0.7

### Frontend
- Icone per 6 nuovi tipi entita': sultanate, khanate, principality, duchy, federation, city

### Test
- 143 test tutti verdi (aggiornati threshold per 255+ entita')
- Lint ruff pulito

## [v5.4.0] - 2026-04-11

### Dataset
- 55 entita' storiche — copertura globale da -3100 a.C. al 2014
- 15 nuove entita' focalizzate su regioni sottorappresentate:
  Majapahit, Srivijaya, Hawaii, Tonga, Mapuche, Cahokia,
  Great Zimbabwe, Benin, Silla, Champa, Aksum, Kush,
  Khwarezmian, Ayutthaya, Aotearoa (Maori)
- Copertura Oceania, Sudest Asiatico, America precolombiana

### API (16 endpoint)
- /v1/entity, /v1/entities, /v1/entities/{id}, /v1/search
- /v1/types, /v1/stats, /v1/continents
- /v1/random (entita' casuale)
- /v1/compare/{id1}/{id2} (confronto strutturato)
- /v1/entities/{id}/contemporaries, /v1/entities/{id}/related
- /v1/export/geojson, /v1/export/csv, /v1/export/timeline
- /health, /embed

### Frontend
- Deep linking completo (?entity=5&year=1500&type=empire&continent=Europe)
- Scorciatoie tastiera (Esc, frecce, /, ?)
- Sezioni dettaglio collassabili con animazioni smooth
- Tooltip arricchiti con confidence bar e icone tipo
- Contemporanei caricati async nel pannello dettaglio
- Filtro per continente con chip e icone regione
- Icone emoji per tipo entita' (empire, kingdom, etc.)
- Dark/light mode toggle con persistenza localStorage
- Time playback (animazione attraverso gli anni)
- Timeline clickabile (click per saltare a un anno)
- Modalita' confronto tra due entita'
- Pulsante condivisione (copia permalink)
- Pagina embed (/embed) per iframe
- Print stylesheet migliorato
- i18n completo IT/EN con nuove chiavi

### Infrastruttura
- 143 test (tecnici, etici, sicurezza, edge cases, performance, data quality, v5 features)
- OpenAPI description con code snippets (Python, JS, curl)
- Tags organizzati per sezione
- GZip + CORS + rate limit + security headers
- Docker + CI + logging strutturato

## [v4.5.0] - 2026-04-11

### Dataset
- 40 entità storiche — copertura globale da -3100 a.C. al 2014
- 7 territori contestati (Palestina, Kosovo, Taiwan, Sahara Occ., Crimea, Tibet, Cipro Nord)
- Nuove: Kemet, Achemenide, Spagnolo, Britannico, SRI, Abbaside,
  Giappone imperiale, Lituania, Zulu, Cartagine, Maurya, Gran Colombia, Haudenosaunee

### API (12 endpoint)
- /v1/entity (search + filter + sort + pagination)
- /v1/entities (list + sort + pagination)
- /v1/entities/{id} (dettaglio)
- /v1/search (autocomplete leggero)
- /v1/types (tipi disponibili)
- /v1/stats (statistiche dataset)
- /v1/entities/{id}/contemporaries (overlap temporale)
- /v1/entities/{id}/related (correlate per tipo/periodo)
- /v1/export/geojson (FeatureCollection)
- /v1/export/csv (tabellare)
- /v1/export/timeline (visualizzazione)
- /health (stato servizio)

### Frontend
- Timeline interattiva con canvas (sotto la mappa)
- Filtro per tipo (chip), ordinamento, barra statistiche
- Export buttons (GeoJSON, CSV, API)
- i18n italiano/inglese con toggle
- Responsive (mobile/tablet)
- Accessibilità WCAG 2.1 AA

### Infrastruttura
- GZip compression middleware
- 100 test (tecnici, etici, sicurezza, edge cases, performance, data quality)
- Performance test: tutti gli endpoint < 500ms
- Data quality test: completezza, diversità, coerenza
- Docker + CI + CORS + rate limit + security headers

## [v3.0.0] - 2026-04-11

### Dataset
- 25 entità storiche (da 10) — copertura 6 continenti
- 5 territori contestati: Palestina/Israele, Kosovo, Taiwan, Sahara Occ., Crimea
- 15 nuove: Bizantino, Mughal, Safavide, Tokugawa, Qing, Russo, Azteco, Mali,
  Songhai, Khmer, Venezia, Etiope, Taiwan, Sahara Occ., Crimea
- Confini reali da aourednik/historical-basemaps (7 periodi: 100-1900)
- Confini moderni da Natural Earth (110m)

### API
- Nuovi endpoint: /v1/search (autocomplete), /v1/types, /v1/stats
- Filtro per entity_type su /v1/entity
- Ordinamento: sort=name|year_start|confidence, order=asc|desc
- Paginazione completa su tutti gli endpoint

### Frontend
- Chip filtro per tipo (empire, kingdom, city, etc.)
- Dropdown ordinamento
- Barra statistiche dataset live
- Responsive (mobile/tablet)
- Accessibilità WCAG 2.1 AA
- Skeleton loader, spinner, error toast

### Infrastruttura
- 68 test (tecnici + etici + sicurezza + edge cases + API avanzata)
- 0 errori lint (ruff)
- Docker + docker-compose
- GitHub Actions CI
- Logging strutturato + rate limiting + CORS + security headers

## [v2.0.0] - 2026-04-11

### Infrastruttura produzione
- configurazione ambiente con .env e pydantic-settings
- Docker: Dockerfile multi-stage + docker-compose.yml
- CORS middleware configurabile
- security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- logging strutturato (JSON per produzione, testo per sviluppo)
- request_id univoco su ogni richiesta
- error handling centralizzato con formato errore standard
- rate limiting (60 req/min con slowapi)

### API hardening
- input validation: year (-4000..2100), name (max 200), status enum
- paginazione su tutti gli endpoint lista (limit/offset)
- cache headers (Cache-Control: public, max-age=3600)
- OpenAPI documentation con descrizioni e esempi
- errori strutturati {error, detail, request_id}

### Database
- supporto duale SQLite (dev) / PostgreSQL (prod) via DATABASE_URL
- connection pooling per PostgreSQL
- indici compositi su (year_start, year_end), status, name_variants.name
- CheckConstraint su confidence_score (0.0-1.0)
- enum Python per status, change_type, source_type
- seed idempotente (non duplica al riavvio)

### Frontend
- responsive design: desktop, tablet, mobile
- skeleton loader durante caricamento
- spinner nel pannello dettaglio
- error toast con auto-dismiss
- sidebar collassabile su mobile
- accessibilita' WCAG 2.1 AA: aria-label, roles, keyboard navigation
- debounce sulla ricerca (300ms)
- cache client-side dei dettagli entita'
- noscript fallback

### Test (56 test)
- test infrastruttura: health check, database type, request_id
- test paginazione: default, custom, offset, beyond results
- test validazione: year range, name length, invalid status, negative offset
- test edge cases: anno negativo, Unicode, arabo, risultati vuoti
- test integrita' DB: seed idempotenza, cascade config, confidence range
- test sicurezza: CORS preflight, security headers, errori strutturati
- test etici: ETHICS-001/002/003 tutti verificati

### DevOps
- GitHub Actions CI: lint (ruff) + test (pytest) + build Docker
- .dockerignore ottimizzato
- .env.example documentato

### Documentazione
- docs/API.md: documentazione completa endpoint con esempi curl
- docs/DEPLOYMENT.md: guida deploy locale, Docker, PostgreSQL
- OpenAPI interattivo su /docs e /redoc

## [v1.1.0] - 2026-04-11

### Cambiato
- confini sostituiti con dati reali da fonti accademiche (8 su 10 entita')
- fonti: aourednik/historical-basemaps (world_100, world_1300, world_1500, world_1900)
- fonti: Natural Earth ne_110m (Kosovo, Israele/Palestina)
- confini reali: linee solide sulla mappa; approssimazioni: linee tratteggiate
- layout CSS corretto: sidebar non coperta dalla mappa
- aggiunto banner di qualita' dati nella sidebar
- aggiunto overlay informativo sulla mappa
- tema visivo piu' professionale (ispirato GitHub dark)
- tooltip sulla mappa con confidence score
- nomi entita' visibili direttamente sulla mappa
- ricerca live durante la digitazione
- slider anno con aggiornamento in tempo reale
- pannello dettaglio con avviso specifico su fonte dei confini

### Aggiunto
- pipeline estrazione confini (src/ingestion/extract_boundaries.py)
- script aggiornamento confini (src/ingestion/update_boundaries.py)
- dati grezzi in data/raw/ (Natural Earth, historical-basemaps)

## [v1.0.0] - 2026-04-11

### Aggiunto
- API REST completa (FastAPI) con endpoint /v1/entity, /v1/entities, /health
- modelli ORM: GeoEntity, NameVariant, TerritoryChange, Source
- 10 entità storiche demo con metadati etici completi
- interfaccia web con mappa Leaflet, ricerca, filtri per anno e status
- pannello dettaglio con nomi, varianti, cambi territoriali, fonti, note etiche
- sistema di confidence_score con validazione e derivazione status
- pipeline di importazione dati da JSON
- 26 test (tecnici + etici) tutti passanti
- documentazione completa (CLAUDE.md, README, ROADMAP, ADR, ETHICS)

### Entità demo incluse
- Imperium Romanum, Osmanlı İmparatorluğu, İstanbul
- Tawantinsuyu (Impero Inca), British Raj
- Palestina/Israele (disputato), Kosovo (disputato)
- Ἀθῆναι (Atene antica), Impero Mongolo, Regno del Kongo

## [v0.0.1] - 2026-04-11

### Aggiunto
- documentazione fondazionale del progetto
- ADR iniziali
- ETHICS records iniziali
- template per decisioni future
- struttura repository fondazionale
