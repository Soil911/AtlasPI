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

### v0.0.1 → v0.6.0 — Fondazione (completate)
- Struttura progetto, CLAUDE.md, governance etica, ADR
- FastAPI + SQLAlchemy + SQLite bootstrap
- Modello dati completo: entita', fonti, varianti nome, cambi territoriali
- Pipeline seed da JSON, confidence scoring, status management

### v1.0.0 → v4.5 — Prima release e iterazioni (completate)
- 16 endpoint REST, mappa Leaflet interattiva
- Dark theme, slider temporale, autocomplete
- Dataset iniziale 40+ entita', test suite 100+
- Export GeoJSON/CSV/Timeline

### v4.6 → v4.8 — UX Polish (completate)
- Sezioni collassabili, keyboard shortcuts, deep linking URL
- Filtro continente, contemporanei, icone tipo
- Toggle dark/light mode, WCAG migliorato

### v5.0 → v5.4 — Feature expansion (completate)
- Timeline interattiva, /v1/compare endpoint, confronto UI
- Condivisione, embed mode, meta OG
- /v1/random, developer experience
- Espansione a 55+ entita', diversita' geografica
- 130+ test, security hardening

### v5.5 → v5.8 — Scaling massivo (completate)
- Espansione da 55 a **746 entita'** con 25 batch files
- 2,200+ fonti accademiche, 2,000+ cambi territoriali
- 21 endpoint API (nearby, snapshot, evolution, aggregation)
- Marker clustering, mini-timeline canvas, filtri avanzati
- **208 test** passano, dedup cross-batch automatizzato

---

## Roadmap attiva — Verso il lancio pubblico

### v6.0 — DEPLOY ONLINE (priorita' assoluta)
Come co-fondatore: "Se non e' online, non esiste come prodotto"

**Obiettivo**: AtlasPI accessibile da qualsiasi browser nel mondo.

- [ ] Dockerfile multi-stage (build + runtime)
- [ ] Configurazione Railway/Render con PostgreSQL
- [ ] Gunicorn/Uvicorn production server
- [ ] Variabili ambiente per produzione (DATABASE_URL, SECRET_KEY, etc.)
- [ ] CORS configurato per dominio reale
- [ ] Health check endpoint ottimizzato per monitoring
- [ ] Dominio personalizzato (atlaspi.dev o simile)
- [ ] HTTPS automatico
- [ ] Seed automatico al primo deploy
- [ ] README con "Try it live" badge

**Criterio di completamento**: `curl https://atlaspi.dev/health` risponde `200 OK`.

### v6.1 — POSTGRESQL + POSTGIS
Come CTO: "SQLite non scala e non fa query spaziali"

**Obiettivo**: database di produzione con query geospaziali native.

- [ ] Migrazione schema a PostgreSQL (Alembic)
- [ ] PostGIS per query spaziali (ST_Contains, ST_DWithin, ST_Distance)
- [ ] /v1/nearby riscitto con PostGIS (da O(n) a O(log n))
- [ ] Indici GiST su boundary_geojson
- [ ] Connection pooling (SQLAlchemy pool + pgbouncer)
- [ ] Seed compatibile PostgreSQL
- [ ] SQLite mantenuto per sviluppo locale
- [ ] Benchmark: nearby sotto 50ms con 1000+ entita'

### v6.2 — BOUNDARY COVERAGE
Come utente: "La mappa e' piena di puntini, dov'e' la geografia?"

**Obiettivo**: almeno 60% delle entita' con confini poligonali reali.

Stato attuale: solo 174/746 (23%) hanno boundary Polygon.

- [ ] Pipeline import da Natural Earth (paesi moderni → entita' corrispondenti)
- [ ] Simplified GeoJSON per entita' storiche (da fonti OSM/wikimedia)
- [ ] Tool semi-automatico: dato un'entita', genera boundary approssimato
- [ ] Validazione: ogni boundary deve avere fonte e confidence
- [ ] Target: 450+ entita' con Polygon (60%+)
- [ ] ETHICS: i confini contestati mantengono versioni multiple

### v6.3 — API AUTHENTICATION
Come business: "Per il modello open core serve il gate"

- [ ] Sistema API key (generazione, validazione, revoca)
- [ ] Tier gratuito: 1000 req/giorno, 20 req/minuto
- [ ] Tier premium: 50000 req/giorno, 100 req/minuto
- [ ] Rate limiting reale (Redis-backed, non solo header)
- [ ] Dashboard sviluppatore (registrazione, uso, chiave)
- [ ] Header X-RateLimit-Remaining, X-RateLimit-Reset
- [ ] Documentazione per sviluppatori AI

### v6.4 — LANDING PAGE & DOCS
Come marketing: "Il prodotto si vende se lo vedono"

- [ ] Landing page statica con demo interattiva embed
- [ ] Documentazione API (non solo Swagger, ma guida narrativa)
- [ ] Esempi codice: Python, JavaScript, curl
- [ ] Sezione "For AI Agents" con use case specifici
- [ ] Blog/changelog pubblico
- [ ] SEO per "historical geographic API"

---

## Visione post-v6 — Crescita

### v7.0 — LANCIO PUBBLICO
- Product Hunt / Hacker News launch
- 1000+ entita', 80%+ con boundary
- Free tier generoso, premium per volume
- Primo feedback utenti reali

### v7.x — Funzionalita' avanzate
- Playback temporale animato (storia che scorre sulla mappa)
- API GraphQL come alternativa a REST
- Webhook per notifiche su nuove entita'
- Community contribution system (correzioni, nuove entita')
- Integrazioni: Wikidata sync, Natural Earth auto-update

### v8.0 — Enterprise
- Multi-tenancy per istituzioni accademiche
- Dataset curati premium (es. "Colonialismo completo", "Guerre mondiali")
- SLA garantito, supporto dedicato
- Audit log per compliance accademica

---

## Metriche di successo per il lancio (v7.0)

| Metrica | Target |
|---------|--------|
| Entita' | 1,000+ |
| Boundary coverage | 80%+ |
| Uptime | 99.5% |
| Latenza API p95 | < 200ms |
| Test coverage | 250+ test |
| Endpoint | 25+ |
| Utenti registrati | 100+ (primo mese) |
| Stelle GitHub | 50+ (primo mese) |
