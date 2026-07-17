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

### v6.99.85-101 -- Wave 2 hardening + audit + enrichment S51-54 + chain dedup (2026-05-31 → 06-04)
**Versione corrente: v6.99.101** (prod). CI interamente verde (lint+test+js-tests+postgres-migrations+build).
**10/10 HIGH dell'audit chiusi** (con v6.99.93 / audit #7). Poi: discoverability refresh
(llms.txt/landing, v6.99.97), agent-compat routes (#78-81, v6.99.97), enrichment S51-54
(40 entità deployate, ~110 fonti, v6.99.95/98/99/100). Suggestion AI Co-Founder: 5/6 chiuse (#78-82), resta #83.
- **v6.99.101 chain dedup** (struttura): prod aveva 107 catene ma solo 77 nomi distinti — 30
  catene successorie duplicate (doppia-ingestione; root cause in `ingest_chains`, JSON poi
  ripulito ma prod INSERT-only). Rimosse (107→77, orfani invariati 772). Hardening
  `_dedupe_by_name` + fence CI. Vedi `docs/structural-tracks-plan.md`. Prerequisito al linking.

### v6.99.102-108 — tracce strutturali: B1a/B1b, split Babilonia, coerenza deprecati (2026-06-05 → 07-02)
- **v6.99.102/103**: B1a (estensioni catene Iran/Francia/Romania) + B1b (nuove catene
  Brasile + unificazione italiana). Modello unificazioni: linea principale + annessi in note.
- **v6.99.106**: **split Babilonia #171 eseguito** (ETHICS-015 + emendamento): deprecata,
  14 ref ri-homati alle entità-periodo; NUOVA entità #1042 "𒆳𒆍𒀭𒊏𒆠 (Post-Kassite)"
  (−1155..−626, Brinkman/Frame/Beaulieu) per evitare l'anacronismo dell'evento #213.
- **fix CI** (rossa dal 17/06): introspezione route version-proof per FastAPI ≥ 0.139
  (lazy include) — lo startup-audit sicurezza /admin/* era silenziosamente cieco.
- **v6.99.107**: **coerenza deprecati end-to-end** — ADR-005 su ~20 endpoint discovery
  (snapshot/fuzzy/similar/where-was/export...), backport status prod→JSON (66), fix 5
  chain_links + cascata 13 ref JSON alle primary native, guard ingest + 2 fence nuovi,
  follow-up ETHICS-012 #3/#5 chiusi, /v1/where-was documentato in llms.txt.
- **v6.99.108**: rename ETHICS-001 #579 'Fürstentum Walachei' → 'Terra Transalpina'.

---

## Milestone giganti (tesi 2026-07-02 — sessione autonoma)

**Tesi**: i dati sono ormai strutturalmente solidi; il collo di bottiglia del prodotto è
che *nessuno lo trova* (zero canali di acquisizione) e che la differenziazione reale
(where-was, snapshot, metadata epistemici, contesto etico) non è né dimostrata né
misurata. Ordine per leva: M2 > M3 > M1 > M4 > enrichment.

### M1 — Layer catene/entità COMPLETO (residuo)
~~B1c: catene Class-1 rimanenti~~ ✅ **FATTA in v6.99.110** (21 catene nuove + 3
estensioni, ETHICS-017; 2026-07-02). Residuo M1:
- ~~Entità-sblocco~~ ✅ **FATTE in v6.99.120** (ETHICS-020: 8 entità nuove —
  Cambogia post-Angkor, Repubblica Khmer, Serbia 1815-1918 (aggiunta su
  indicazione del cross-check), Regno SHS, Dirʿiyya, Najd, Nepal repubblicano,
  Mthwakazi/Ndebele — più il rename nativo di Lan Xang #128 (era in script thai);
  Mahdiyya e Medri Bahri esistevano GIÀ (#736/#658, coda rename M4). Catene
  34/123/124/125/126/130 estese + 3 nuove per Saudi #253, Gorkha #399,
  Taqali #411 — orfani Class-1 esauriti. Follow-up espliciti in ETHICS-020:
  PRK 1979-89, Eritrea italiana, Serbia moderna.
- ~~Split Sri Lanka #142~~ ✅ **FATTO in v6.99.121** (ETHICS-021: #142→Anuradhapura,
  #386 deprecata, #600→Dambadeniya, +Gampola +Kotte, catena Sinhalese trunk).
- ~~Split Kemet #26~~ ✅ **FATTO in v6.99.122** (ETHICS-022: #26 empire→civilization
  ombrello; 4 entità-periodo tꜣ.wy Old/Middle/New + Πτολεμαϊκὴ βασιλεία; 16 eventi
  ri-organizzati con agentività kushita/persiana aggiunta; catena 3 Regni).
- ~~Ripristino #552 Meroe + follow-up ETHICS-022 (TIP, Periodo Tardo)~~ ✅ **FATTO in
  v6.99.128** (Task 2a, ETHICS-023: 2 entità-fase `tꜣ.wy (Third Intermediate)` +
  `(Late Period)` con conf onesta 0.62/0.82; Meroe #552 un-deprecated come fase
  meroitica; catene 137 e 99 estese; cross-check ChatGPT AGREE).
- ~~Follow-up ETHICS-020: PRK + Stato di Cambogia~~ ✅ **FATTO in v6.99.129** (Task 2b,
  ETHICS-024: 2 entità + catena 126 estesa 4→8 link coi regimi 1970-1993; cross-check
  ChatGPT; split di #256 rinviato per Sihanouk).
- ~~Follow-up ETHICS-020: Serbia moderna~~ ✅ **FATTO in v6.99.130** (Task 2c, ETHICS-025:
  FRY+S&M+Repubblica di Serbia, catena 34 6→10 link; decisione ETHICS-003 = Serbia
  confirmed/0.9 non disputed, Kosovo localizzato; cross-check ChatGPT).
- ~~Follow-up ETHICS-020: Eritrea italiana~~ ✅ **FATTO in v6.99.131** (Task 2d, ETHICS-026:
  Colonia Eritrea + catena COLONIAL Medri Bahri #658 → Colonia Eritrea). **Task 2 CHIUSO.**
- Residuo split/dedup (coda, non bloccante): trunk etiope (#22/#100 + #853 dup di #51);
  Ptolemaico #178/#1059; split #256 Cambogia; Stato di Eritrea 1993- + interregno;
  coda catena montenegrina #130.
- ~~Flag qualità da B1c: rename #534 e verifica #240~~ ✅ **FATTI in v6.99.118**
  (ETHICS-019: #240 → `កម្ពុជាប្រជាធិបតេយ្យ` Kampuchea Democratica + QID Q330988;
  #534 → `Anpi an Ayiti`, entity_type=empire, variante `Empire d'Haïti`).

### M2 — Discoverability (🌍 CUTOVER FATTO: **https://atlaspi.it** live, v6.99.114)
Dominio dedicato registrato da Clirim e cutover eseguito il 2026-07-03: PR #5 mergiata,
cert Let's Encrypt attivo (apex+www), **301 permanente dal vecchio host** (da non
rimuovere mai: wheel PyPI/npm e DOI puntano lì), env/nginx/refactor PUBLIC_BASE_URL.
**Ora eseguibili, UNA volta sola col dominio definitivo**: submission MCP registry,
Google Search Console + Bing (serve login Clirim per la verifica proprietà), backlink
iniziali (awesome-lists MCP/API/DH, Zenodo→repo), Matomo (server + site id da decidere),
release pacchetti (mcp 0.10.0, sdk-py/js 0.3.0 — nuovi default atlaspi.it; rebuild
sdk-js/dist prima di npm publish), upload HF dataset.

**Fatti (v6.99.114-134)**: MCP registry (`io.github.Soil911/atlaspi` 0.10.1), GSC dominio
verificato + sitemap inviata, Bing/IndexNow, Matomo (siteId 2), pacchetti + HF dataset.
**SEO hygiene (v6.99.134, 2026-07-14)**: sitemap `<lastmod>` su tutti gli URL, canonical
mancanti aggiunti (/app /search /timeline /compare /embed), meta description su /embed +
/docs + /redoc (route custom con injection nel `<head>`), metadati /app in EN.
**App UX (v6.99.135, 2026-07-14)**: default lingua → **inglese** (browser-detect, IT
resta per browser italiani); affordance slider anno (fill accent, pulse d'ingresso,
hint "trascina", thumb/traccia più grandi) — l'interazione principale "si vedeva poco".
Le quick-win narrative del design-proposal-stories (era chips, Ask Claude, onboarding,
playback) erano già a bordo; **bottone "Sorprendimi" + banner "Accadde oggi" FATTI in
v6.99.136 (2026-07-17)** → tutte le "alternative leggere" A/B/C del proposal ora a bordo.
Prossimo bivio narrativo: Stories mode completo (grosso), da valutare solo con traffico reale.

**RESIDUO M2 — la leva rimasta**: **backlink** (awesome-lists MCP/API/DH, Zenodo→repo).
Diagnosi 2026-07-14: le pagine sono indicizzabili ma Google ne indicizza 1/14 → dominio
nuovo + zero backlink ("crawled, not indexed"). I backlink sono l'intervento a leva più
alta ancora aperto.

### M3 — Agent-UX dimostrabilmente superiore
Dai gap dell'audit agent-consumer 2026-07-02: (1) zero-result senza hint → suggerire
/v1/search/fuzzy nella risposta vuota; (2) boundary statico silenziosamente anacronistico →
campo machine-readable `boundary_reference_year`; (3) campi machine-facing in italiano
(404, OpenAPI summaries, ethical_notes) → strategia lingua esplicita; (4) on-this-day
payload magro (N+1); (5) freshness release MCP/SDK (dist/ stantii, README con conteggi
vecchi). Più: pagina/benchmark "perché AtlasPI e non Wikidata" con query comparate reali.

### M4 — Riconciliazione totale JSON↔prod (fresh-seed ≡ prod)
**Policy confidence FATTA (ADR-011, v6.99.113)**: 199/286 divergenze chiuse (197
backport JSON:=prod + 2 UPDATE prod batch_32). Coda review manuale poi lavorata a
lotti: 87→72 (v6.99.125, 15 rialzi) → **✅ CHIUSA in v6.99.127** (Task 1 ultracode:
72 entità con verify-agent + refuter avversariale → 11 rialzi prod:=json, 59
backport json:=prod, 2 già convergenti). `conf_review_queue.json` ora VUOTA.
Struttura M4 (rename nativi, ombreggiati, JSON-only) già chiusa in v6.99.124-126
(JSON↔prod name-reconciled 100%). Residuo M4: solo ethical_notes narrative (IT).

### Track continuo — enrichment coda <0.6 (~206 entità, valore marginale calante)

Sessione lunga: audit a freddo (10 dimensioni, workflow `wb4nky8m3` con 29 agenti +
verifica adversariale) → tutte "adequate", 0 critical, **10 HIGH confermati**. Verdetto:
continuare a wave + 1 wave di consolidamento. Chiusi **9/10 HIGH** + analisi traffico
prod + 2 bug-fix:
- **v6.99.85** (2.1) indice GiST `boundary_geom` mai creato in prod (migration 022) — #5
- **v6.99.86** (2.2) rate-limit key = `X-Real-IP` (prima bucket globale dietro nginx) — #3
- **v6.99.87** (2.3) envelope errori unificato (handler `StarletteHTTPException`) — #2
- **v6.99.88** (2.4) `confidence<0.5 ⇒ uncertain` enforced (ETHICS-013) + addendum ETHICS-009 — #4/#9/#10
- **v6.99.89** (2.5) `response_model` su `/light`, `/batch`, `/events` (OpenAPI tipizzato) — #1
- **v6.99.90** (2.6) copertura test frontend (`boundary-cache.js`) + spatial check CI + fix lint — #6/#8
- **v6.99.91** traffic-fix #1: redirect `/v1/entity/{id}` → `/v1/entities/{id}` (agent 404 in prod)
- **v6.99.92** traffic-fix #2: auth admin via token (shell pubbliche + `admin-auth.js`, 401 intermittenti risolti)
- **v6.99.93** (2.7) backport confini JSON↔prod (599 entità: 372 `approximate_circle` +
  227 `historical_approximation`, prima solo-prod) + fence collision attivato (test
  PostGIS-free in SQLite + job Postgres CI) → seed fresco a **0 super-group collision**
  (era 29). Chiude audit **#7** → **10/10 HIGH chiusi**. Vedi ETHICS-012. *Nessun deploy.*

**Rimanenti / prossima sessione** (ordine deciso con Clirim: ~~a~~ → ~~c~~ → b):
- ~~**(a) Backport Phase H JSON↔prod**~~ — ✅ **fatto in v6.99.93** (scope reale 599, non
  372: inclusa la iter-series `historical_approximation`; backportati anche
  confidence+status per coerenza). **Follow-up chiuso in v6.99.94**: riconciliazione
  residua → 6 entità solo-prod aggiunte + 15 `name_original` portati a script nativo
  (ETHICS-001); JSON ora 1038 entità = totale prod. Vedi ETHICS-012 §"#2".
- ~~**(c) orjson** serializzazione globale~~ — ❌ **investigato, NON adottato** (2026-05-31).
  `ORJSONResponse` è **deprecato** in FastAPI ≥0.115 e tutti i `/v1/*` principali
  hanno già `response_model` → FastAPI serializza **nativamente via Pydantic v2**
  (Rust, ≈ velocità orjson), bypassando la response class. Benchmark su payload
  reale (500 entità + boundary, ~10,7 MB): stdlib 315 ms vs orjson 17 ms — ma con
  `response_model` non si usa nessuna delle due, e comunque la serializzazione è
  ≤0,3 s del ~4,5 s. **Il ~4,5 s di `/v1/entities?limit=500` è DB/validazione, NON
  serializzazione** → orjson non aiuta. Change revertato (non committato). Perf reale =
  task separata: profilare query DB / caricamento boundary / validazione Pydantic di
  500 entità (es. `exclude_geometry` di default, indici, paginazione boundary).
- **(b) Enrichment** entità low-confidence (Wave 2 Plan A) — ← IN CORSO (turnkey:
  spec `data/fixes/enrichment_sNN.json` → `scripts/apply_enrichment.py` → SQL+JSON →
  backup+SQL+cra-deploy). **30 entità arricchite + DEPLOYATE** (~90 fonti verificate):
  - **S51 (v6.99.95)** Eurasia classical empires (Umayyad, Maratha, Ghurid, Zagwe, Akkad,
    Neo-Babylon, Mycenae, Saba, Xianbei, Wagadou) — deployato in v6.99.97.
  - **S52 (v6.99.98)** Daju, Tunjur, Sosso, Ngoenyang, Tarumanagara, Kediri, Sogdiana,
    Zunghar, Muisca, Herod — + **chiusa suggestion #82** (Daju/Tunjur geometrie distinte).
  - **S53 (v6.99.99)** Taiping, Zapotec, Mixtec, Gerusalemme ayyubide, Galles, Pipil, Lenca,
    Diaguita, Sunda, Sangam Chola.
  - **Backlog residuo (prod, 2026-06-04)**: **226 entità < 0.6** (di cui 46 < 0.5),
    223 `uncertain`, 84 con < 3 fonti. ≈22 batch da 10 per portare tutto ≥0.6 (i top-30
    ad alta visibilità di brief D sono già fatti). S54+ in corso.
  - **Sotto-tracce aperte**: chain linkage (78% entità orfane da chain_links); gap
    geografici (Pacifico/Siberia/Patagonia); **split-candidate** (Babilonia #171, Sri Lanka
    #142 — super-aggregati da splittare, non arricchire).

### Decisioni/follow-up aperti (non-Wave-2, da Clirim)
- ~~**Suggestion #83** (AI Co-Founder): client esterno → 422 su anni < -4000.~~ **RISOLTO
  v6.99.104** (opzione a): floor allineato a -4000000 su tutti gli endpoint; le 14 entità
  pre-4000 a.C. già nel dataset ora interrogabili/esportabili. Vedi ETHICS-016.
- **Discoverability esterna** (MCP-registry, GSC/Bing, backlink): attende la **decisione dominio**.
- **7 insert solo-prod** + sync `name_original` nativo (ETHICS-001): vedi ETHICS-012 §"#2".

### v6.99.81-83 Wave 1 -- Security, data-fix, perf (2026-05-28)
**(storico — versione corrente ora v6.99.92, sopra.)** Triplo deploy autonomo in 1 sessione
(`auto-iter-wave0` branch, ChatGPT-5.5 cross-check ogni step):
- **v6.99.81** — Admin containment: tutti i 19 endpoint `/admin/*` ora
  richiedono auth (X-Admin-Token header o Basic Auth admin:TOKEN).
  Prima erano security-by-obscurity. 13 nuovi test in
  `tests/test_admin_auth.py`. Vedi CHANGELOG.
- **v6.99.82** — Antimeridian data fix: id 754 Sau o Futuna e id 307
  Lapita avevano polygon bbox 359° (wrap-around). Sostituiti con cerchi
  storicamente realistici. Label mappa rendono ora nel Pacifico, non
  in Atlantico/centro mondo.
- **v6.99.83** — Performance year-aware lazy load: ~27 MB upfront
  ridotto a ~3 MB (single fetch `/v1/entities?year=Y&limit=500`).
  AbortController + cache per anno. Default load -85%.

### v6.99.80 Phase H -- Systematic boundary review + matcher hardening (2026-05-28)
- **340 entità polygon-fixed**: risoluzione di ~100 polygon collisions causate
  da fuzzy matching aourednik/natural_earth con super-gruppi culturali-linguistici
  (Bantou, Polynesians, "minor states", Fatimid Caliphate, Sasanian Empire,
  Kingdom of David and Solomon, ecc.). Vedi [ETHICS-012](docs/ethics/ETHICS-012-phase-h-boundary-review.md).
- **Boot guard** `boundary_collision_guard.py` rileva regression al boot
  (Guard #4 in lifespan, status ok/warning/alarm).
- **CI fence** `test_boundary_collisions_audit.py` (3 test) blocca PR se
  super_group_alerts > 0 o total_groups > 60.
- **Matcher hardening** `aourednik_match.py` + `boundary_match.py`:
  super-group label blacklist (44 entries) + area sanity check (per-entity-type
  ceiling). Tre layer di defense in depth.
- **Lapita label fix** in `static/app.js`: per polygon che attraversano
  antimeridian (lonSpan > 180°), usa `capital.lat/lon` invece di
  bounds-center per il label.
- **Distribuzione boundary_source**: approximate_circle 0 → 280, aourednik
  375 → 195, natural_earth 197 → 91.
- **Final status produzione**: `status: OK, 0 collision groups`.

### v7.0 benchmark closure -- AtlasPI validato come tool-augmented retrieval (2026-04-23)
- 3 esperimenti A/B empirici su agent Claude Sonnet 4.5 per validare
  tesi business "AtlasPI migliora accuracy agenti AI" (vedi
  [ADR-007](docs/adr/ADR-007-agent-tooling-not-prompt.md)).
- **Finding killer**: AtlasPI full (prompt + MCP tools) riduce
  hallucinations LLM del **-67%** su query storiche hard (bank v2
  30 Q trap-designed), da 0.21 a 0.07 avg per Q. Accuracy +4.6pp
  tool-only effect, +2.0pp combined.
- **Prompt standalone e' DANNOSO**: -2.6pp accuracy, +76% hallucinations
  vs baseline. Evitare di distribuire "AtlasPI prompt template" come
  prodotto separato.
- **Bank v1 (100 Q general): ceiling effect** (baseline 92% saturato
  da Wikipedia training di Claude). Benchmark fallito li' per design
  flaw, non per AtlasPI.
- **Pivot strategico positioning**: da "dataset + prompt + MCP" a
  "tool-augmented retrieval, -3x hallucinations". Target: historical
  researchers + AI agent developers, non mass consumer.
- Artefatti riproducibili: `scripts/benchmark/` (runner + 3way +
  rejudge + resume + 3 agents + judge), 3 bank questions (v1 100 Q,
  v2 hard 30 Q, seeds 5 Q), 3 results directories complete.
- Costo totale benchmark: ~$25 API (Anthropic).

### v6.92.0 -- CSP fonts fix + batch deploy (2026-04-22)
- Fix CSP Google Fonts: aggiunto `fonts.googleapis.com` +
  `fonts.gstatic.com` a `style-src`, `font-src`, `connect-src`.
  Risolve 405 POST `/v1/csp-report` noise nei log analytics.
- Batch deploy 8 commit dormienti: Redis cache `/v1/stats`, limit
  cap 100->500 entities, 301 redirect `/v1/trade-routes`, +223
  entities con boundary arricchiti (697K rows JSON), 7 nuovi
  succession chains (SE Asia, NE Africa, Near East, Steppe, India),
  3 fix analyzer (NameVariant check, name_original field).

### v6.91.0 -- Audit cofounder follow-up (2026-04-19)
- P1 fix era-chip active state sync con year slider (Agent A audit
  finding: underline active non renderizzato in prod perche' JS
  applicava `.active` solo su click). Nuova funzione
  `syncActiveEraChip(year)` chiamata su slider input.
- P1 fix CLS-safe pattern docs: aggiunto commento esplicativo sul
  pattern `border-bottom transparent -> accent` in `.sb-section
  .era-chip` (diverso dal v6.67 pseudo-element pattern, ma
  funzionalmente equivalente per CLS-safety).
- P2 fix dead code timeline: rimosso `loadTimeline()`,
  `drawTimeline()` function, `timelineData` var. Canvas eliminato
  in v6.90 ma funzioni rimanevano dead code (~120 righe + fetch
  inutile a `/v1/export/timeline` per ogni init).

### v6.90 -- UI redesign A+ (2026-04-19)
- Completo redesign della pagina /app con palette ambra editoriale
  (`#e8b14a`), tipografia Playfair Display italic per nomi entità, year
  hero in header, sidebar con sezioni collassabili native (`<details>`),
  timeline bar 60px al bottom con era ticks, Leaflet HSL per-entity
  boundary rendering (stateless hash = nessuna gerarchia culturale).
- Preservato `data-section="capital-history"` per 13 entities popolate
  in v6.84 con cronologia capitali editoriale (ADR-004).
- Preservato `dashArray '6,4'` per `status='disputed'` come secondo
  canale visivo (ETHICS-011 transparency-of-uncertainty).
- Event timeline canvas `#timeline-chart` rimosso (regressione UX ~2%
  accettata, endpoint `/v1/events` resta disponibile).
- A11y: focus-visible globale accent + reduced-motion + AAA contrast +
  dual-channel per daltonici.
- Lighthouse CLS 0.00 preservato (v6.67 standard). Accessibility ≥ 95
  target verificato.
- Zero modifiche a backend, API, MCP, SDK, data layer.
- Docs: ADR-006 design system + ETHICS-011 typography/color rationale.

### v0.0.1 -> v0.6.0 -- Fondazione
- Struttura progetto, CLAUDE.md, governance etica, ADR
- FastAPI + SQLAlchemy + SQLite bootstrap
- Modello dati completo: entita', fonti, varianti nome, cambi territoriali
- Pipeline seed da JSON, confidence scoring, status management

### v1.0.0 -> v4.5 -- Prima release e iterazioni
- 16 endpoint REST, mappa Leaflet interattiva
- Dark theme, slider temporale, autocomplete
- Dataset iniziale 40+ entita', test suite 100+
- Export GeoJSON/CSV/Timeline

### v4.6 -> v4.8 -- UX Polish
- Sezioni collassabili, keyboard shortcuts, deep linking URL
- Filtro continente, contemporanei, icone tipo
- Toggle dark/light mode, WCAG migliorato

### v5.0 -> v5.4 -- Feature expansion
- Timeline interattiva, /v1/compare endpoint, confronto UI
- Condivisione, embed mode, meta OG
- /v1/random, developer experience
- Espansione a 55+ entita', diversita' geografica
- 130+ test, security hardening

### v5.5 -> v5.8 -- Scaling massivo
- Espansione da 55 a **746 entita'** con 25 batch files
- 2,200+ fonti accademiche, 2,000+ cambi territoriali
- 21 endpoint API (nearby, snapshot, evolution, aggregation)
- Marker clustering, mini-timeline canvas, filtri avanzati
- 208 test passano, dedup cross-batch automatizzato

### v6.0 -- DEPLOY ONLINE (2026-04-14)
**Criterio di completamento raggiunto**: `curl https://atlaspi.it/health` risponde `200 OK`.

- Dockerfile multi-stage (build + runtime, non-root user)
- Aruba Cloud deploy con HTTPS automatico
- Gunicorn + 2 uvicorn workers, porta 10100
- Variabili ambiente per produzione (DATABASE_URL, SECRET_KEY, etc.)
- CORS configurato, dominio custom **atlaspi.it**
- Health check ottimizzato per monitoring esterno
- Seed automatico al primo deploy
- Repository pubblico Soil911/AtlasPI (account principale)

### v6.1 -- RELIABILITY + DISCOVERABILITY (2026-04-14)
- Sentry SDK integrato, health check esteso (ok/degraded/down)
- Backup/restore scripts con retention, smoke test post-deploy
- Operations runbook, logging rotation
- SEO: robots.txt con AI crawler, sitemap.xml, PUBLIC_BASE_URL
- MCP server Python (`atlaspi-mcp`, 8 tools wrapping REST API)
- Landing page inglese, README killer con badge "Try it live"
- Open Graph image, Twitter card, structured data JSON-LD
- Pipeline Natural Earth + aourednik per boundary import -> **93% coverage**
- ETHICS-005 (confini contestati moderni), ETHICS-006 (guardia geografica
  capital-in-polygon: 133 match displaced corretti, coverage 93% -> **72%**
  per regressione volontaria: correctness > cosmetic coverage)
- CITATION.cff, .zenodo.json, **Zenodo DOI mintato** (10.5281/zenodo.19581784)
- ADR-003: `/app/data` baked nell'immagine via COPY

### v6.2 -- POSTGIS DEEP WORK (2026-04-14)
- `/v1/nearby` riscritto con `ST_DWithin`: da O(n) haversine a indicizzato
  (p95 180 ms -> **20 ms**)
- Re-matching conservativo delle 209 entita' `approximate_generated`:
  solo strategie forti (exact_name, fuzzy_name con geo-guard), MAI NE fuzzy
- Centroid-distance soft check (500 km) come secondo filtro nel fuzzy matcher
- Cleanup 22+7 righe aourednik displaced, coverage 72% -> **73%**
- CI audit: test automatico che blocca regressioni capital-in-polygon
- 281 test

### v6.3 -- EVENTS LAYER (2026-04-15)
**Svolta**: da database di entita' a database di entita' + eventi storici.

- Tre nuove tabelle: `historical_events`, `event_entity_links`, `event_sources`
- EventType enum con 31 valori ETHICS-007 (GENOCIDE, COLONIAL_VIOLENCE,
  ETHNIC_CLEANSING, MASSACRE, DEPORTATION -- nessun eufemismo)
- ETHICS-008: flag `known_silence` per eventi con documentazione soppressa
- 4 endpoint: `/v1/events` (list, detail, types, entity-events)
- Entity expansion 747 -> **846** (+99 entita' in 4 batch tematici)
- Seed iniziale 31 eventi (batch_01) -> espansione a **106 eventi** (batch_02/03/04)
  coprendo Ancient (-2560 -> -216), Medieval (632 -> 1644), Modern (1757 -> 2004)
- PostGIS indici GiST funzionali, bbox filter su `/v1/entities`
- ETHICS-006 CI guardia capital-in-polygon (seconda linea di difesa)
- 308 -> **321 test**

### v6.4 -- CITIES + TRADE ROUTES (2026-04-15)
- HistoricalCity model: **110 citta'** in 3 batch (Mediterraneo/MENA,
  Asia, Americhe/Africa/Europa)
- TradeRoute model: **25 rotte commerciali** (Silk Road, Trans-Saharan,
  Trans-Atlantic, Indian Ocean, etc.)
- ETHICS-009: rinominazioni coloniali documentate con `name_variants`
  (Konstantinoupolis -> Istanbul, Edo -> Tokyo, Tenochtitlan -> Mexico City)
- ETHICS-010: tratta degli esseri umani come categoria di prima classe
  (`involves_slavery=True`, 5 rotte flaggate, ethical_notes con scale/perpetrators)
- 6 nuovi endpoint (cities list/detail/types, routes list/detail/types)
- Alembic migration 005
- 340 test

### v6.5 -- DYNASTY CHAINS + MCP v0.2.0 (2026-04-15)
- DynastyChain + ChainLink models con ChainType e TransitionType enum
- ETHICS-002: conquiste e rivoluzioni non appiattite in "successioni"
- ETHICS-003: tipo IDEOLOGICAL con avvertimento (self-proclaimed continuity)
- 6 catene-archetipo iniziali (Roman, Chinese, Colonial, Ideological, Ottoman, Russian)
- 5 endpoint: chains list/detail/types, predecessors, successors
- MCP server v0.2.0 con 11 nuovi tool (totale 19)
- 355 test

### v6.6 -- EVENT EXPANSION (2026-04-15)
- **+105 eventi** (106 -> 211): Africa, Asia-Pacifico, Americhe, lungo Novecento
- 36 eventi flaggati `known_silence` (ETHICS-008)
- Remap compatibilita' enum (FOUNDATION_STATE -> FOUNDING_STATE, etc.)
- Rispetto integrale ETHICS-007 (niente eufemismi) e ETHICS-008
- 355 test (stabile, solo dati additivi)

### v6.7 -- AGENT-READY INTEGRATION + BOUNDARY HONESTY (2026-04-15)
- `/v1/entities/{id}/timeline` (stream unificato events + territory + chains)
- `/v1/search/fuzzy` (cross-script approximate matching via SequenceMatcher)
- MCP v0.3.0 con 23 tool totali, **pubblicato su PyPI** (`pip install atlaspi-mcp`)
- +16 rotte commerciali (totale **41**): Hanseatic/Baltic + Indian Ocean Maritime
- +3 catene dinastiche (Byzantine->Ottoman, French monarchy->Republic, Iranian)
- Frontend: trade route overlay con outline rossa per rotte schiaviste,
  sidebar catene, detail panel timeline tab
- **Boundary honesty** (v6.7.1/v6.7.2/v6.7.3): tre passate di pulizia
  - v6.7.1: -61 boundary condivisi falsi, -5 placeholder rettangolari,
    cleanup shared polygon via cluster analysis + rapidfuzz
  - v6.7.2: 11 entita' con polygon 10x-200x sovradimensionati corretti
  - v6.7.3: 4 polygon rifiniti con area geodesica reale (pyproj.Geod)
- 371 -> **442 test**

### v6.8 -- ANCIENT EVENTS + ASIAN CHAINS (2026-04-15)
- +24 eventi pre-500 CE (batch_09): Assyria, Grecia, Ellenismo, Maurya, Roma
- +2 catene dinastiche: Giappone (7-link Nara -> Meiji) + India classica (5-link)
- Meiji classificato REVOLUTION (non RESTORATION): colonizzazione Hokkaido/Ainu
- Tutte le transizioni indiane `is_violent=true` (zero successioni pacifiche)
- 486 test

### v6.9 -- MEDIEVAL EVENTS + CHINESE DYNASTY TRUNK (2026-04-15)
- +15 eventi era 500-1000 CE (batch_10): Islam nascente, sintesi carolingia,
  Sui-Tang, persecuzione buddhista Huichang, battesimo della Rus'
- Catena cinese completa (12-link Shang -> PRC, con ETHICS su
  Grande Carestia 15-45M, Rivoluzione Culturale, Tiananmen, Xinjiang)
- 527 test

### v6.10 -- CALIPHATE + KOREAN TRUNKS (2026-04-15)
- Catena islamica sunnita (5-link Rashidun -> Ottoman, con Karbala, Baghdad 1258)
- Catena coreana (5-link Silla -> ROK, con Jeju, Guerra di Corea, Gwangju)
- ETHICS: doppio-chain ad alta densita' etica, ogni transizione un trauma
- 566 test

### v6.11 -- IMPERIAL CONTINUITY TRUNKS (2026-04-15)
- 3 catene: Western Roman imperial (6-link, tipo IDEOLOGICAL: Roma -> Terzo
  Reich come documentazione, NON legittimazione), Eastern Roman/Byzantine
  (2-link), Mongol Yuan branch (3-link)
- +9 eventi (coronazione Ottone I, sacco di Costantinopoli 1204, kurultai 1206,
  Mohi 1241, Ain Jalut 1260, fondazione Yuan 1271, espulsione Yuan 1368,
  dissoluzione SRI 1806, Kaiserproklamation 1871)
- ETHICS: Terzo Reich incluso con ethical_notes piu' denso del progetto (~1100 car.)
- 603+ test

### v6.12 -- API ANALYTICS LAYER (2026-04-16)
- `ApiRequestLog` model + `AnalyticsMiddleware` (logging ogni richiesta API)
- Dashboard HTML interattiva `/admin/analytics` (4 KPI, grafico 30 giorni,
  top endpoint/IP/user agent, ultime 50 richieste, auto-refresh)
- Alembic migration 007
- 670 test

### v6.13 -- PERSIAN & INDIAN CHAINS + EVENT EXPANSION (2026-04-16)
- +4 entita' (Achaemenid Empire, Delhi Sultanate, Mughal Empire, Pakistan)
- +2 catene: Iranian state-formation trunk (6-link Achaemenid -> IRI),
  Indian subcontinent paramount power (4-link Delhi Sultanate -> Republic of India)
- +8 eventi (Gaugamela, Hormozdgan, al-Qadisiyyah, Talikota, Panipat III,
  Delhi Durbar 1877, Jallianwala Bagh 1919, Rivoluzione iraniana 1979)
- **850 entita', 267 eventi, 19 catene**
- 719 test

### v6.14 -- DATE PRECISION LAYER (2026-04-16)
- Nuovo enum DatePrecision (DAY, MONTH, SEASON, YEAR, DECADE, CENTURY)
- 5 nuove colonne su HistoricalEvent e TerritoryChange: month, day,
  date_precision, iso_date, calendar_note
- **138 eventi** con precisione giornaliera, 21 mensile, 4 stagionale
- `/v1/events/on-this-day/{MM-DD}` e `/v1/events/at-date/{YYYY-MM-DD}`
- Alembic migration 008
- 749 test

### v6.15 -- AI CO-FOUNDER INTELLIGENCE LAYER (2026-04-16)
- `/admin/insights` -- analisi traffico (volume, IP, top endpoint, user-agent)
- `/admin/coverage-report` -- report qualita' dati (distribuzione per regione/era,
  confidence, copertura confini/date/catene, punteggio completezza 0-100)
- `/admin/suggestions` -- suggerimenti intelligenti (gap geografici/temporali,
  ricerche fallite, entita' orfane, bassa confidenza)
- Script `generate_daily_brief.py` per brief Markdown giornaliero
- 798 test

### v6.16 -- AI CO-FOUNDER DASHBOARD (2026-04-16)
- Tabella `ai_suggestions` + migrazione Alembic 009
- Dashboard HTML `/admin/brief` con KPI, traffic overview, data quality,
  geographic coverage, confidence distribution, sezione suggerimenti
  con bottoni Accept/Reject/Implement
- Script `ai_cofounder_analyze.py` per generazione suggerimenti automatici
- 6 nuovi endpoint (brief, suggestions CRUD, status)
- 827 test

### v6.17 -- INTERACTIVE TIMELINE (2026-04-16)
- Implementati 3 suggerimenti dal dashboard AI Co-Founder:
  - Alzata confidence per 18 entita', aggiornati status
  - +10 eventi deep antiquity (batch_14, Gobekli Tepe -> Unificazione Egitto)
  - +12 eventi bronze age (batch_15, Sargon di Akkad -> Eruzione di Thera)
- `/v1/timeline-data` -- payload ottimizzato per rendering SVG
- Pagina `/timeline` con timeline SVG pura: barre entita', marker eventi,
  catene collegate, zoom/pan, era quick-jump, layer toggles, ricerca
- **850 entita', 297 eventi**
- 841 test

### v6.18 -- ENTITY COMPARISON TOOL (2026-04-16)
- `GET /v1/compare?ids=1,2,3` -- confronto multi-entita' strutturato (2-4)
  con overlap temporale, eventi condivisi, catene successorie
- Pagina `/compare` interattiva: ricerca con autocomplete, preset rapidi,
  card side-by-side, timeline SVG, tabella dati, deep linking
- 855 test

### v6.19 -- ADVANCED SEARCH + EXPORT (2026-04-16)
- `GET /v1/search/advanced` -- ricerca unificata cross-type con ranking
- `GET /v1/export/entities` e `/v1/export/events` -- export CSV, GeoJSON, JSON
- Pagina `/search` con filtri combinabili, tabs per tipo, card/list view,
  highlight, export integrato, deep linking
- 876 test

### v6.20 -- INTERACTIVE API EXPLORER + DYNASTY CHAINS EXPANSION (2026-04-16)
- Pagina `/docs-ui` -- documentazione API interattiva con "Try it" buttons,
  syntax highlighting, sidebar scroll-spy, dark theme
- +5 nuove catene dinastiche: Ethiopian trunk, Sahel Empire + Kanem-Bornu,
  Andean Civilization, Mesoamerican -> Colonial Mexico
- Totale: **21 catene, 90+ link**
- 883 test

### v6.21 -- REDIS CACHING LAYER (2026-04-16)
- `src/cache.py` con decorator `@cache_response(ttl)`, invalidazione per pattern,
  flush, statistiche (hits/misses/ratio/memory)
- 10 endpoint cached (entities, events, chains, timeline, search, compare, admin)
- Graceful degradation: se Redis non disponibile, handlers funzionano normalmente
- `/admin/cache-stats` e `POST /admin/cache/flush`
- Header `X-Cache: HIT/MISS` + `X-Cache-Key`
- 899 test

### v6.22 -- EMBEDDABLE WIDGETS + MAJOR EVENT EXPANSION (2026-04-16)
**Storico** (NON più versione corrente — superseded dalla serie v6.99.x
in alto; vedi v6.99.81-83 per "Versione corrente").

- **+89 eventi** (312 -> **401**) in 4 batch tematici:
  - batch_17: 38 eventi XX secolo (Trianon, Spanish Civil War, Indian independence, ...)
  - batch_18: 16 eventi Roma/Grecia antica (Peloponnesian War, Punic Wars, Spartacus, ...)
  - batch_19: 18 eventi mondo islamico (Badr, Umayyad founding, Saladin, Suleiman, ...)
  - batch_20: 17 eventi commercio/esplorazione (Vasco da Gama, Magellan, VOC, Suez, ...)
- **Embeddable Widgets**: entity card (`/widget/entity/{id}`),
  timeline (`/widget/timeline`), on this day (`/widget/on-this-day`),
  showcase (`/widgets`) -- tutti con dark/light theme, responsive, self-contained
- **862 entita', 401 eventi, 26 catene, 110 citta', 41 rotte commerciali**
- **917 test**

---

## Roadmap attiva -- Prossime release

> **Nota di sync (v6.99.83, 2026-05-28)**: le entries `v6.23-v6.26` sotto
> in questa sezione sono **storiche/superseded**, in larga parte assorbite
> dalla serie v6.99.x (Phase B-G enrichment + Wave 1 security/perf). Da
> rifattorizzare in una nuova `v7.x` roadmap consolidata. Le 3 priorità
> attive sono: v7.1 (post-benchmark pivot), v7.2 (Zenodo + multi-turn),
> Wave 1.4+ (housekeeping in corso).

### v7.1 -- Post-benchmark pivot (TOP PRIORITY)
**Obiettivo**: implementare le 5 implementation items da ADR-007 dopo
validazione benchmark v7.0 (tool-dominant).

- [ ] Revise `scripts/benchmark/agents/atlaspi_agent.py::SYSTEM_PROMPT`:
      rimuovere "superiority claims" (prefer AtlasPI over training),
      aggiungere "defer to training when tools return empty". Expected:
      prompt-only mode diventa neutrale (da -2.6pp attuale) senza
      impattare full mode +4.6pp.
- [ ] Aggiungere 3 nuovi MCP tools: `get_rulers_at_year(year, region)`,
      `get_events_by_entity(entity_id)`,
      `get_languages_at_year_region(year, region)`.
      Rationale: dry-run ha mostrato gap rulers per Bisanzio moderni
      (solo Justinianus I/II in DB), questi tool danno time-window
      query diretta.
- [ ] Cross-vendor judge validation: rilanciare bank v2 hard con
      GPT-4o o Gemini Flash come judge (same-vendor bias mitigation).
      Costo ~$5. Se risultati simili (+4.6pp tool effect), validation
      extra-solida.
- [ ] Landing page rewrite: hero "Reduce LLM hallucinations 3x on
      historical queries", sezione methodology con link raw data
      benchmark, case studies target ricercatori + dev agent.
- [ ] Production cost/latency doc: tool calls aggiungono ~3x latency
      + ~2x tokens out. Guida integrators su trade-off.

### v7.2 -- Zenodo dataset refresh + multi-turn benchmark
- [ ] Export Zenodo DOI dataset aggiornato post-audit v4 (1038
      entities, 715 QID, capital_history 13 entities, sites 99% linked).
- [ ] Multi-turn agent benchmark: valutare AtlasPI in flow ricerca
      ripetuta (metric: steps-to-solution, total tokens).
- [ ] Bank v3 expansion: 100 Q hard (da 30), copertura bilanciata.

### v6.23 -- EVENTS ON MAP OVERLAY (prossimo)
**Obiettivo**: visualizzare gli eventi direttamente sulla mappa interattiva.

- [ ] Marker eventi sulla mappa Leaflet (icone per event_type)
- [ ] Sincronizzazione con year slider (mostra eventi dell'anno selezionato)
- [ ] Filtro per event_type nella sidebar
- [ ] Clustering eventi per densita' geografica
- [ ] Popup evento con link al detail e alle entita' coinvolte
- [ ] Toggle overlay "Mostra eventi" in sidebar (accanto a trade routes)

### v6.24 -- POSTGIS SPATIAL OPTIMIZATION
**Obiettivo**: query spaziali native ovunque, benchmark sotto 50ms.

- [ ] `/v1/entities` con filtro spaziale `contains` usando ST_Intersects
- [ ] Benchmark: nearby + bbox + contains sotto 50ms con 1000+ entita'
- [ ] Materializzare colonna `boundary_geography` per evitare
  `ST_GeomFromGeoJSON()` runtime su ogni query
- [ ] Audit performance: identificare e risolvere le query lente
- [ ] Valutare indice GiST su eventi (lat/lon)

### v6.25 -- API KEY SYSTEM + RATE LIMITING
**Obiettivo**: monetizzazione e protezione dell'API.

- [ ] Sistema API key (generazione, validazione, revoca)
- [ ] Tier gratuito: 1000 req/giorno, 20 req/minuto
- [ ] Tier premium: 50000 req/giorno, 100 req/minuto
- [ ] Rate limiting reale (Redis-backed, non solo header)
- [ ] Header X-RateLimit-Remaining, X-RateLimit-Reset
- [ ] Dashboard sviluppatore (registrazione, uso, chiave)
- [ ] Stripe integration per upgrade premium

### v6.26 -- DISTRIBUZIONE E LANCIO
**Obiettivo**: il prodotto si vede solo se lo vedono. Lancio coordinato con il
prodotto completo (entita' + eventi + citta' + rotte + catene + widgets + search + caching).

- [ ] Submit a Postman Public Network
- [ ] Submit a RapidAPI Hub
- [ ] Submit a public-apis/public-apis (GitHub)
- [ ] Submit a apilist.fun
- [ ] Show HN ("Show HN: AtlasPI -- Historical geography API + MCP for AI agents")
- [ ] Post su r/datasets, r/GIS, r/MachineLearning, r/history
- [ ] Twitter/X thread, LinkedIn post
- [ ] Blog post di lancio sul nostro dominio
- [ ] Documentazione: "For AI Agent developers" con use case concreti
- [ ] Submit al MCP registry pubblico Anthropic
- [ ] Pubblicazione `atlaspi-mcp` su PyPI registry MCP

---

## Visione post-v6 -- Crescita

### v7.0 -- LANCIO PUBBLICO UFFICIALE
- Product Hunt launch coordinato con HN
- **1,000+ entita'** (attualmente 862, +138 necessari)
- **500+ eventi storici** (attualmente 401, +99 necessari)
- **50+ catene dinastiche** (attualmente 26, +24 necessari)
- **80%+ boundary coverage** (attualmente 72% post ETHICS-006, serve
  re-matching conservativo o nuove fonti boundary per antiche)
- MCP server stabile su PyPI con 23+ tool
- Free tier generoso, premium per volume (v6.25)
- Primo feedback utenti reali
- Metriche utenti tracciate (registrazioni, query/giorno, retention)

### v7.x -- Funzionalita' avanzate
- Playback temporale animato (storia che scorre sulla mappa)
- API GraphQL come alternativa a REST
- Webhook per notifiche su nuove entita'
- Community contribution system (correzioni, nuove entita')
- Integrazioni: Wikidata sync, Natural Earth auto-update
- MCP server con tools avanzati (ragionamento causale, contesto multi-entita')
- Cities layer expansion (100+ -> 500+ citta')
- Trade routes layer expansion (41 -> 100+ rotte)

### v8.0 -- Enterprise
- Multi-tenancy per istituzioni accademiche
- Dataset curati premium ("Colonialismo completo", "Guerre mondiali", "Imperi steppici")
- SLA garantito, supporto dedicato
- Audit log per compliance accademica
- Export bulk per ricerca
- White-label per editori di materiale didattico

---

## Metriche di successo per il lancio (v7.0)

| Metrica | Target v7.0 | Stato attuale (2026-04-16, v6.22.0) |
|---------|-------------|--------------------------------------|
| Uptime | 99.5% | da misurare (UptimeRobot non ancora attivo) |
| Latenza API p95 | < 200ms | ~20ms nearby (PostGIS), ~180ms altri |
| Entita' | 1,000+ | **1,038** (target raggiunto e superato; v6.99.80) |
| Eventi storici | 500+ | **401** (target 300 gia' superato) |
| Catene dinastiche | 50+ | **26** |
| Citta' storiche | 100+ | **110** (target raggiunto) |
| Rotte commerciali | 40+ | **41** (target raggiunto) |
| Boundary coverage | 80%+ | **99.9%** (1037/1038, post Phase H v6.99.80; target ampiamente superato) |
| Test coverage | 500+ test | **917** (target ampiamente superato) |
| Endpoint API | 30+ | **~50** (target superato) |
| Pagine web | 9+ | **9** (app, landing, timeline, compare, search, docs-ui, analytics, brief, widgets) |
| MCP server | PyPI + registry | **PyPI v0.3.0** (23 tool), registry pending |
| Redis caching | attivo | **attivo** (10 endpoint, graceful degradation) |
| Embeddable widgets | 3+ | **3** (entity card, timeline, on-this-day) |
| DOI Zenodo | mintato | **10.5281/zenodo.19581784** |
| Stelle GitHub | 50+ (primo mese) | 0 (repo appena migrato a Soil911) |
| Utenti registrati | 100+ (primo mese) | 0 (no auth ancora, v6.25) |
| Mention in directory API | 5+ | 0 (v6.26) |

---

## Pagine web del progetto

| Pagina | Path | Versione introdotta |
|--------|------|---------------------|
| Mappa interattiva | `/app` | v1.0 |
| Landing page | `/` | v6.1 |
| Timeline SVG | `/timeline` | v6.17 |
| Entity Comparison | `/compare` | v6.18 |
| Advanced Search | `/search` | v6.19 |
| API Explorer | `/docs-ui` | v6.20 |
| Analytics Dashboard | `/admin/analytics` | v6.12 |
| AI Co-Founder Brief | `/admin/brief` | v6.16 |
| Widget Showcase | `/widgets` | v6.22 |

---

## ETHICS records rilevanti per la roadmap

| Record | Tema | Versione |
|--------|------|----------|
| ETHICS-001 | Nome originale come primario | v0.x |
| ETHICS-002 | Conquiste non appiattite in successioni | v6.5 |
| ETHICS-003 | Continuita' IDEOLOGICAL != legittimita' | v6.5 |
| ETHICS-004 | Polygon approximate_generated, confidence cap 0.4 | v6.1 |
| ETHICS-005 | Confini contestati moderni | v6.1 |
| ETHICS-006 | Guardia geografica capital-in-polygon | v6.1.2 |
| ETHICS-007 | Narrativa eventi: no eufemismi | v6.3 |
| ETHICS-008 | known_silence su eventi silenziati | v6.3 |
| ETHICS-009 | Rinominazioni coloniali documentate | v6.4 |
| ETHICS-010 | Tratta esseri umani come categoria | v6.4 |
| ETHICS-011 | Redesign A+ typography + color | v6.90 |
| ETHICS-012 | Phase H boundary review systematica + matcher hardening | v6.99.80 |

---

## Governance etica durante lo sviluppo

Se durante lo sviluppo emerge una scelta che puo' alterare,
semplificare o distorcere la rappresentazione storica, non
procedere in silenzio. In questi casi:

1. aprire o aggiornare un record in `docs/ethics/`
2. descrivere il rischio di distorsione
3. documentare le alternative considerate
4. spiegare la scelta adottata
5. solo dopo procedere con l'implementazione

Regola pratica:
se una decisione tecnica ha impatto sulla verita' storica,
sulla rappresentazione di popoli, confini, nomi o conquiste,
va trattata come decisione etica documentata.

---

## Regola d'oro

Prima di scrivere codice chiedi: "questo dato, in questo formato,
potrebbe essere usato per distorcere la comprensione storica?"
Se la risposta e' si', apri un ETHICS record prima di procedere.
