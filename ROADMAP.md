# Roadmap AtlasPI

## Principi di roadmap

- sviluppo incrementale
- versionamento esplicito
- scope limitato per ogni release
- prima la base etica e architetturale, poi il codice applicativo
- nessuna feature fuori roadmap senza aggiornamento esplicito di questo file
- "se non e' online, non esiste"

---

## Versioni completate

### v0.0.1 → v0.6.0 — Fondazione
- Struttura progetto, CLAUDE.md, governance etica, ADR
- FastAPI + SQLAlchemy + SQLite bootstrap
- Modello dati completo: entita', fonti, varianti nome, cambi territoriali
- Pipeline seed da JSON, confidence scoring, status management

### v1.0.0 → v4.5 — Prima release e iterazioni
- 16 endpoint REST, mappa Leaflet interattiva
- Dark theme, slider temporale, autocomplete
- Dataset iniziale 40+ entita', test suite 100+
- Export GeoJSON/CSV/Timeline

### v4.6 → v4.8 — UX Polish
- Sezioni collassabili, keyboard shortcuts, deep linking URL
- Filtro continente, contemporanei, icone tipo
- Toggle dark/light mode, WCAG migliorato

### v5.0 → v5.4 — Feature expansion
- Timeline interattiva, /v1/compare endpoint, confronto UI
- Condivisione, embed mode, meta OG
- /v1/random, developer experience
- Espansione a 55+ entita', diversita' geografica
- 130+ test, security hardening

### v5.5 → v5.8 — Scaling massivo
- Espansione da 55 a **746 entita'** con 25 batch files
- 2,200+ fonti accademiche, 2,000+ cambi territoriali
- 21 endpoint API (nearby, snapshot, evolution, aggregation)
- Marker clustering, mini-timeline canvas, filtri avanzati
- 208 test passano, dedup cross-batch automatizzato

### v6.0 — DEPLOY ONLINE (completata 2026-04-14)
**Criterio di completamento raggiunto**: `curl https://atlaspi.cra-srl.com/health` risponde `200 OK`.

- Dockerfile multi-stage (build + runtime, non-root user)
- Aruba Cloud deploy con HTTPS automatico
- Gunicorn + 2 uvicorn workers, porta 10100
- Variabili ambiente per produzione (DATABASE_URL, SECRET_KEY, etc.)
- CORS configurato, dominio custom **atlaspi.cra-srl.com**
- Health check ottimizzato per monitoring esterno
- Seed automatico al primo deploy
- Repository pubblico Soil911/AtlasPI (account principale)

---

## Roadmap attiva — Crescita post-deploy

### v6.1 — RELIABILITY + DISCOVERABILITY (in corso)
**Filosofia**: ora che siamo online, "affidabile" viene prima di "ricco di feature".
Nessuno si fida di un servizio che si rompe silenziosamente.

#### Reliability stack
- [x] Sentry SDK integrato (opt-in via SENTRY_DSN)
- [x] Health check esteso: status ok/degraded/down, sotto-checks, uptime, sentry status
- [x] Backup script con retention (SQLite + PostgreSQL auto-detect)
- [x] Restore script con conferma + safe-copy del DB corrente
- [x] Smoke test post-deploy (14 endpoint critici)
- [x] Operations runbook (`docs/OPERATIONS.md`)
- [x] Backup sidecar in docker-compose (cron-style 03:00)
- [x] Logging rotation (10MB x 3 file)

#### SEO base
- [x] `/robots.txt` con allow esplicito per AI crawler (GPTBot, ClaudeBot, anthropic-ai, ecc)
- [x] `/sitemap.xml` con route canoniche
- [x] PUBLIC_BASE_URL configurabile per domini di staging

#### Discoverability per agenti AI
- [x] **MCP server Python** (`atlaspi-mcp` package, 8 tools wrapping REST API)
- [x] Documentazione Claude Desktop / Claude Code config
- [ ] Pubblicazione su PyPI come `atlaspi-mcp`
- [ ] Submit al MCP registry pubblico Anthropic

#### Landing & marketing prep
- [x] Landing page inglese statica (separata dall'app italiana)
- [x] README killer con badge "Try it live"
- [x] Open Graph image, Twitter card, structured data JSON-LD
- [ ] Routing: `/` → landing, `/app` → mappa interattiva (vecchia root)

#### Data quality
- [x] Pipeline Natural Earth → boundary import per stati moderni
- [x] Tool semi-automatico per boundary approssimato (entita' antiche)
- [x] ETHICS-005 per gestione confini contestati moderni
- [x] Esecuzione pipeline su tutto il dataset → **93.0% real boundary coverage** (v6.1.1)
- [x] Matcher aourednik/historical-basemaps per entita' pre-1800 (v6.1.1)
- [x] **ETHICS-006** — guardia geografica (capital-in-polygon) sul fuzzy
      matcher NE. Cleanup di 133 match displaced (Garenganze→RUS, CSA→ITA,
      Mapuche→AUS, ...). Coverage 93% → 72% (regressione volontaria:
      correctness > cosmetic coverage). (v6.1.2)

#### Academic credibility
- [x] CITATION.cff per citazione formale (v6.1.1)
- [x] .zenodo.json per DOI mint (v6.1.1)
- [x] **Zenodo DOI mintato** (v6.1.2) — concept `10.5281/zenodo.19581784`,
      version v6.1.2 `10.5281/zenodo.19581785`. Repo pubblico +
      webhook Zenodo attivo + GitHub Release v6.1.2 → mint automatico.

#### Ops hardening
- [x] **ADR-003** — `/app/data` non e' piu' un named volume, bakata
      nell'immagine via `COPY data/` nel Dockerfile. Previene il bug del
      volume-masks-fresh-image emerso durante il sync v6.1.1. (v6.1.2)

### v6.2 — POSTGIS DEEP WORK + RE-MATCHING POST ETHICS-006
**Quando**: dopo v6.1.2 stabilizzato in produzione.

PostgreSQL + PostGIS e' ufficialmente il backend di produzione da v6.1.1.
I task PostGIS-native (query spaziali, indici GiST) possono ora procedere
direttamente senza la migrazione SQLite → PG.

#### Query spatial native
- [x] Migrazione schema completata via Alembic (v6.1.1)
- [x] PostGIS abilitato (postgis/postgis:16-3.4 image) (v6.1.1)
- [ ] /v1/nearby riscritto con ST_DWithin (da O(n) a indicizzato)
- [ ] /v1/entities con filtro spaziale (bbox, contains) usando ST_Intersects
- [ ] Indici GiST su `ST_GeomFromGeoJSON(boundary_geojson)` materializzata
- [ ] Benchmark: nearby sotto 50ms con 1000+ entita'

#### Data quality — seconda iterazione post ETHICS-006
- [ ] **Centroid-distance soft check** come secondo filtro nel fuzzy
      matcher: oltre a capital-in-polygon, richiedere che `|capital −
      centroid_poligono|` ≤ 500 km. Riduce falsi positivi dove NE ha
      poligoni enormi e la capitale e' per caso dentro il bordo.
- [ ] **Re-matching conservativo** delle 209 entita' in
      `approximate_generated`: tentare nuova passata SOLO con strategie
      non-fuzzy (exact name, alias ISO espliciti, aourednik), senza
      riaprire la strada al pattern-matching dei token generici.
- [ ] **Audit automatico nel CI**: test che fallisce se alcuna entita'
      con `boundary_source != "approximate_generated"` ha capitale fuori
      dal poligono. Blocca regressioni simili a ETHICS-006.
- [ ] Valutare se estendere la guardia anche al matching aourednik
      (attualmente aourednik usa capital-in-polygon come strategia
      esplicita, ma non come guardia per exact/fuzzy name).

### v6.3 — DISTRIBUZIONE E LANCIO
**Obiettivo**: il prodotto si vende solo se lo vedono.

- [ ] Submit a Postman Public Network
- [ ] Submit a RapidAPI Hub
- [ ] Submit a public-apis/public-apis (GitHub)
- [ ] Submit a apilist.fun
- [ ] Show HN ("Show HN: AtlasPI — Historical geography API + MCP for AI agents")
- [ ] Post su r/datasets, r/GIS, r/MachineLearning
- [ ] Twitter/X thread, LinkedIn post
- [ ] Blog post di lancio sul nostro dominio
- [ ] Documentazione: "For AI Agent developers" con use case concreti

### v6.4 — API AUTHENTICATION + MONETIZATION
**Quando**: dopo aver dimostrato che esiste domanda d'uso.

- [ ] Sistema API key (generazione, validazione, revoca)
- [ ] Tier gratuito: 1000 req/giorno, 20 req/minuto
- [ ] Tier premium: 50000 req/giorno, 100 req/minuto
- [ ] Rate limiting reale (Redis-backed, non solo header)
- [ ] Dashboard sviluppatore (registrazione, uso, chiave)
- [ ] Header X-RateLimit-Remaining, X-RateLimit-Reset
- [ ] Stripe integration per upgrade premium
- [ ] Documentazione narrativa (non solo Swagger)

---

## Visione post-v6 — Crescita

### v7.0 — LANCIO PUBBLICO UFFICIALE
- Product Hunt launch coordinato con HN
- 1000+ entita', 80%+ con boundary
- MCP server stabile, pubblicato su PyPI
- Free tier generoso, premium per volume
- Primo feedback utenti reali
- Metriche utenti tracciate (registrazioni, query/giorno, retention)

### v7.x — Funzionalita' avanzate
- Playback temporale animato (storia che scorre sulla mappa)
- API GraphQL come alternativa a REST
- Webhook per notifiche su nuove entita'
- Community contribution system (correzioni, nuove entita')
- Integrazioni: Wikidata sync, Natural Earth auto-update
- MCP server con tools avanzati (ragionamento causale, contesto multi-entita')

### v8.0 — Enterprise
- Multi-tenancy per istituzioni accademiche
- Dataset curati premium ("Colonialismo completo", "Guerre mondiali", "Imperi steppici")
- SLA garantito, supporto dedicato
- Audit log per compliance accademica
- Export bulk per ricerca
- White-label per editori di materiale didattico

---

## Metriche di successo per il lancio (v7.0)

| Metrica | Target | Stato attuale (2026-04-14) |
|---------|--------|---------------------------|
| Uptime | 99.5% | da misurare (UptimeRobot non ancora attivo) |
| Latenza API p95 | < 200ms | ~180ms (verificato live) |
| Entita' | 1,000+ | 747 |
| Boundary coverage | 80%+ | **93.0%** (NE 28% + aourednik 42% + historical 23%) ✓ superato |
| Test coverage | 250+ test | **260 ✓** (208 v5.8 + 25 v6.1 + 1 v6.1.1 + 11 spot-check top-10 + 11 sync reconciliation + 4 boundary provenance) |
| Endpoint | 25+ | 21 + 2 SEO |
| MCP server | pubblicato su PyPI | pacchetto pronto, da pubblicare |
| Stelle GitHub | 50+ (primo mese) | 0 (repo appena migrato a Soil911) |
| Utenti registrati | 100+ (primo mese) | 0 (no auth ancora) |
| Mention in directory API | 5+ | 0 |
