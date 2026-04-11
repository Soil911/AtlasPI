# Changelog AtlasPI

Tutte le modifiche rilevanti del progetto devono essere documentate qui.

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
