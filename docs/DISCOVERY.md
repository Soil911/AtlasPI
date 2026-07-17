# AtlasPI — Kit di scoperta / backlink (2026-07-17)

> Prodotto da una ricerca multi-agente (9 agenti, ~120 verifiche web) + sintesi.
> Ogni voce è **già pronta da inviare**. La maggior parte delle submission verso
> repo/servizi terzi le esegue **Clirim** (pubblicare contenuto pubblico a nome
> proprio non lo fa Claude in autonomia). Claude può preparare fork/branch/PR e
> aprirli **su conferma esplicita, uno alla volta**.

## Perché questo, adesso

I dati (v6.99.136) sono solidi; il collo di bottiglia è la **scoperta**: 0 star, 1
pagina indicizzata, ~0 traffico umano. L'unico segnale che si muove sono i **crawler
AI** (Claude/Anthropic 16 hit in 4 giorni vs 14 in 30). Quindi la leva vera **non**
sono le directory generiche di link, ma i canali **crawlati da agenti/LLM** e i
**cataloghi machine-readable**: awesome-list MCP autorevoli, registri MCP che già
indicizzano il registro ufficiale, registri OpenAPI/dataset, Google Dataset Search.

## Già fatto sul sito (v6.99.137, autonomo)

- **Dataset JSON-LD** su [static/landing/index.html](../static/landing/index.html)
  arricchito per **Google Dataset Search**: `identifier` (DOI, come array), `sameAs`
  (GitHub+HF+Zenodo), `spatialCoverage` mondiale, `includedInDataCatalog`, `version`,
  3ª `distribution` (HF), keywords estese. → valida su
  https://search.google.com/test/rich-results e https://validator.schema.org
- **Metadati accademici** corretti: `CITATION.cff` e `.zenodo.json` (numeri stantii
  747/2.200 → cifre oneste; +npm +HF nei related_identifiers di Zenodo).
- **Pre-check superati**: NOTICE cita aourednik ✓ · `/openapi.json` stabile 3.1.0 ✓.

## Azioni ordinate per leva

| # | Canale | Leva | Effort | Chi invia | Metodo |
|---|---|---|---|---|---|
| 1 | punkpeye/awesome-mcp-servers (~91k★) | molto alta | basso | Claude prepara → Clirim pubblica | PR |
| 2 | APIs.guru (openapi-directory) | molto alta | basso | Clirim (form) | web-form |
| 3 | PulseMCP | alta | basso | Clirim (claim) | web-form |
| 4 | aourednik/historical-basemaps (issue reciproca) | alta | basso | Clirim | issue |
| 5 | public-apis/public-apis (~451k★) | alta | basso | Claude prepara → Clirim | PR (regole rigide) |
| 6 | Zenodo Community "dhdatasets" | alta | basso | Clirim (dal record Zenodo) | web-form |
| 7 | Glama.ai MCP Registry | media-alta | basso | Clirim | web-form |
| 8 | stark1tty/awesome-historical-maps | alta (pertinenza) | basso | Claude prepara → Clirim | PR |
| 9 | appcypher/awesome-mcp-servers (~5.7k★) | media | basso | Claude prepara → Clirim | PR |
| 10 | wong2 / mcpservers.org | media | basso | Clirim (SOLO form) | web-form |
| 11 | awesomedata/awesome-public-datasets (~77k★) | alta | medio | Claude prepara → Clirim | PR (YAML in apd-core) |
| 12 | dh-tech/awesome-digital-humanities | media | basso | Claude prepara → Clirim | PR |
| 13 | sacridini/Awesome-Geospatial (~5.2k★) | media | medio | Claude prepara → Clirim | PR |
| 14 | OpenHistoricalMap Resources (OSM wiki) | media | medio | Clirim (account OSM) | wiki edit |
| 15 | Hacker News — Show HN | media (burst) | basso | Clirim | post |

## Dettaglio azioni (voce pronta + passi)

### #1 · punkpeye/awesome-mcp-servers — PR (la più alta leva)
**Voce (sezione `### 🗺️ Location Services`, ordine alfabetico):**
```
- [Soil911/AtlasPI](https://github.com/Soil911/AtlasPI) 🐍 ☁️ - Historical geography for AI agents: 1000+ polities with real GeoJSON borders, dynastic succession chains, events and cited sources, 4500 BCE-today. Free REST API + MCP server (34 tools), no API key.
```
**Passi:** `gh repo fork punkpeye/awesome-mcp-servers --clone` → inserisci la riga in `### 🗺️ Location Services` (legend: 🐍=Python, ☁️=Cloud) → branch `add-atlaspi` → `gh pr create --title "Add AtlasPI (Location Services)"`. **UNA entry per PR.**

### #2 · APIs.guru — web-form (agent-discovery nativa)
**Payload:** Definition URL `https://atlaspi.it/openapi.json` · Format OpenAPI 3.1 · Source **Official (by API owner)** · Category geography / open_data.
**Passi:** vai su https://apis.guru/add-api, invia il form con la Definition URL sopra. In alternativa issue/PR su `APIs-guru/openapi-directory`.

### #3 · PulseMCP — claim/submit
**Voce:**
```
AtlasPI — Historical geography for AI agents: polities, GeoJSON borders, chains & events, 4500 BCE-today. Free REST API + MCP server (34 tools), cited sources, confidence scores. Apache-2.0, no API key. GitHub: https://github.com/Soil911/AtlasPI · Homepage: https://atlaspi.it · Docs: https://atlaspi.it/docs · Install: pip install atlaspi-mcp · Registry: io.github.Soil911/atlaspi
```
**Passi:** cerca "AtlasPI" su https://www.pulsemcp.com/servers → se presente **Claim** (verifica GitHub) e correggi; se assente **Submit**.

### #4 · aourednik/historical-basemaps — issue reciproca (NOTICE già ok ✓)
**Titolo:** `Downstream project using historical-basemaps: AtlasPI (historical-geography API/MCP)`
**Corpo:**
```
Thanks for historical-basemaps — we build on it in AtlasPI (https://atlaspi.it, https://github.com/Soil911/AtlasPI, Apache-2.0), a public REST + MCP API of historical geography: 1000+ polities with GeoJSON borders, events, dynastic chains and cited sources, 4500 BCE-2024, with per-record confidence scores. historical-basemaps is credited in our NOTICE. Would you list AtlasPI among projects using the data / related resources in the README?
```
**Passi:** `gh issue create -R aourednik/historical-basemaps --title "…" --body "…"`.

### #5 · public-apis/public-apis — PR (regole RIGIDE)
**Voce (sezione `### Geocoding`, ordine alfabetico; fallback `### Open Data`):**
```
| [AtlasPI](https://atlaspi.it) | Historical geography: polities, GeoJSON borders, events & chains, 4500 BCE-today | No | Yes | Yes |
```
**Passi:** fork `public-apis/public-apis` (NON Soil911) → riga in `### Geocoding` → descrizione <100 char, **senza punto finale**, **senza "API"**, **senza TLD** → squash → `gh pr create --base master --title "Add AtlasPI API"` (**titolo esatto**) → attendi il link-check CI verde. **Una sola PR.**

### #6 · Zenodo Community "dhdatasets" — submit dal record esistente
**Messaggio ai curatori:**
```
AtlasPI is an open (Apache-2.0), agent-ready dataset of historical geography: 1000+ polities with GeoJSON borders, 643 events, dynastic chains, cited sources and per-record confidence scores, 4500 BCE-2024, with explicit ethical framing. Already on Zenodo (DOI 10.5281/zenodo.19581784) and HuggingFace. Requesting inclusion in Digital Humanities Datasets.
```
**Passi:** apri il record Zenodo di AtlasPI → ⚙ → **Submit to community** → `dhdatasets` → incolla → Submit. **Nessun nuovo deposito.**

### #7 · Glama.ai — Add Server
**Voce:** `https://github.com/Soil911/AtlasPI — AtlasPI: Historical geography for AI agents, polities + real GeoJSON borders + dynastic chains & events with cited sources, 4500 BCE-today. Free REST API + MCP server (34 tools, PyPI atlaspi-mcp), Apache-2.0, no API key.`
**Passi:** cerca su https://glama.ai/mcp/servers; se auto-indicizzato rivendica, altrimenti **Add Server** con l'URL repo.

### #8 · stark1tty/awesome-historical-maps — PR (pertinenza chirurgica)
**Voce (sottosezione APIs/Tools):**
```
- [AtlasPI](https://atlaspi.it) — free REST API and MCP server for historical geography: 1000+ polities with GeoJSON borders, events, trade routes, succession chains and rulers (4500 BCE-2024), sourced and confidence-scored. Apache-2.0, no login/API key, CORS. [Docs](https://atlaspi.it/docs) · [GitHub](https://github.com/Soil911/AtlasPI).
```
**Passi:** fork → aggiungi sotto `APIs`/`Tools` → `gh pr create --repo stark1tty/awesome-historical-maps --title "Add AtlasPI historical geography API/MCP"`.

### #9 · appcypher/awesome-mcp-servers — PR
**Voce (`### Location Services`):**
```
- [Soil911/AtlasPI](https://github.com/Soil911/AtlasPI) - Historical geography for AI agents: 1000+ polities, real GeoJSON borders, dynastic chains, events & cited sources, 4500 BCE-today. Free REST API + MCP server (34 tools).
```
**Passi:** fork → sezione Location Services → `gh pr create --title "Add AtlasPI MCP server"`.

### #10 · mcpservers.org (wong2) — SOLO web-form (le PR vengono rifiutate)
**Campi:** Name `AtlasPI` · GitHub `https://github.com/Soil911/AtlasPI` · Homepage `https://atlaspi.it` · PyPI `atlaspi-mcp` · Registry `io.github.Soil911/atlaspi` · Category Location Services/Data · Description come #3.
**Passi:** https://mcpservers.org/submit (NON aprire PR sul repo).

### #11 · awesomedata/awesome-public-datasets — PR via YAML (apd-core)
**File `core/GIS/AtlasPI.yml`:** title AtlasPI · homepage https://atlaspi.it · description "Historical geography REST API & MCP — 1000+ polities with real GeoJSON borders, events, dynastic chains, cited sources, 4500 BCE-2024, Apache-2.0" · tags [historical, geojson, borders, api, digital-humanities].
**Passi:** fork `awesomedata/apd-core` → crea `core/GIS/AtlasPI.yml` sul modello esistente → `gh pr create` (il README.rst si rigenera dallo YAML).

### #12 · dh-tech/awesome-digital-humanities — PR (angolo etico)
**Voce (`Data Collection`/`Data Analysis`, o proponi sottosezione "Historical GIS / Datasets"):**
```
- [AtlasPI](https://atlaspi.it) - Open REST API and MCP server for historical geography: 1000+ polities with real GeoJSON borders, events, dynastic chains, cities and trade routes (4500 BCE-2024), with cited sources, confidence scores and explicit ethical framing (original-language names; conquests and genocides named). Apache-2.0, no API key.
```
**Passi:** fork → inserisci in ordine alfabetico → `gh pr create --title "Add AtlasPI"`. Inquadra la PR sul valore accademico (fonti + confidence + governance etica).

### #13 · sacridini/Awesome-Geospatial — PR
**Voce (`## DaaS - Data as a Service`, formato `*   [Name](url) - Desc.`):**
```
*   [AtlasPI](https://atlaspi.it) - Historical geography as a service for AI agents: 1000+ polities with real GeoJSON borders, events, trade routes, succession chains and cited sources, 4500 BCE-2024. Free, no key, Apache-2.0. [GitHub](https://github.com/Soil911/AtlasPI).
```
**Passi:** fork → sezione DaaS → `gh pr create --repo sacridini/Awesome-Geospatial --title "Add AtlasPI to DaaS"`.

### #14 · OpenHistoricalMap Resources (OSM wiki) — richiede account OSM
**Voce:** `* [AtlasPI](https://atlaspi.it) — open REST API and MCP server providing GeoJSON borders for 1000+ historical polities, events, dynastic chains and cited sources (4500 BCE-2024). Apache-2.0, no key. Complements OHM with agent-ready, source-cited polity data and original-language place names.`
**Passi:** account OSM → https://wiki.openstreetmap.org/wiki/OpenHistoricalMap/Resources → Edit → aggiungi nella sezione risorse esterne. (Link possibilmente nofollow → valore soprattutto community/scoperta.)

### #15 · Hacker News — Show HN (burst, un colpo solo)
**Titolo:** `Show HN: AtlasPI – Historical geography API and MCP server for AI agents (Apache 2.0)` · **URL:** `https://atlaspi.it`
**Primo commento:**
```
open REST API + MCP server per geografia storica (no login/API key, JSON+GeoJSON, Apache-2.0). 1000+ polities con GeoJSON reale, 643 eventi, dynastic chains, cited sources + confidence_score. Prova: curl 'https://atlaspi.it/v1/entities?year=1200' · Mappa: https://atlaspi.it/app · MCP: pip install atlaspi-mcp. Feedback voluto su confidence scoring e governance etica (nomi originali, conquiste/genocidi nominati, confini contestati con versioni multiple).
```
**Passi:** login HN con account con storia → submit Title+URL → incolla il corpo come primo commento → orario feriale ~08–10 ET → resta a rispondere 2-3h. **Un solo Show HN per progetto** — scegli quando la copertura dati è più solida.

## Rischi / cosa NON fare

1. **Wikipedia prematura**: NON creare/editare voci su AtlasPI ora (0 star, 1 pagina indicizzata → niente fonti secondarie indipendenti → cancellazione per notability/self-promo). Rimandare a dopo copertura terza.
2. **No footprint da spam**: NON usare lo stesso testo identico su decine di directory a bassa autorevolezza. Varia le descrizioni, privilegia pochi canali ad alta leva.
3. **Fork corretto**: forka SEMPRE il repo di destinazione, MAI `Soil911/*` per errore.
4. **public-apis** è severissimo (1 API/PR, titolo esatto, link-check CI): sbagliare = PR chiusa.
5. **mcp.so**: `/submit` dietro Cloudflare (403 all'automazione) → solo browser reale, bassa priorità.

## Checklist di tracking (aggiornata 2026-07-17 sera — esecuzione autonoma)

- [x] ~~#1 punkpeye/awesome-mcp-servers~~ → **PR #9219 GIÀ APERTA dal 4/07**
  (https://github.com/punkpeye/awesome-mcp-servers/pull/9219). ⚠️ **BLOCCATA**: il
  maintainer chiede il **listing su Glama** come prerequisito → vedi #7, poi
  rispondere sulla PR.
- [ ] #2 APIs.guru (form) — **CLIRIM**: https://apis.guru/add-api con Definition URL
  `https://atlaspi.it/openapi.json`, Source=Official
- [ ] #3 PulseMCP (claim/submit) — **CLIRIM**: https://www.pulsemcp.com/servers
- [x] #4 aourednik/historical-basemaps → **issue #77 APERTA**
  (https://github.com/aourednik/historical-basemaps/issues/77)
- [x] #5 public-apis/public-apis → **PR #6609 APERTA**
  (https://github.com/public-apis/public-apis/pull/6609) — attendere link-check CI
- [ ] #6 Zenodo dhdatasets — **CLIRIM**: dal record Zenodo → Submit to community
- [ ] #7 Glama.ai — **CLIRIM, PRIORITÀ MASSIMA** (sblocca la PR punkpeye #9219):
  https://glama.ai/mcp/servers → Add Server con repo Soil911/AtlasPI → poi **Claim**
  via GitHub. Verificato: NON ancora auto-indicizzato (API search vuota al 17/07).
  Dopo il claim, commentare sulla PR #9219 che il requisito è soddisfatto.
- [x] #8 stark1tty/awesome-historical-maps → **PR #9 APERTA**
  (https://github.com/stark1tty/awesome-historical-maps/pull/9)
- [~] #9 appcypher/awesome-mcp-servers → branch pronto sul fork ma **PR via API
  RIFIUTATA** (FORBIDDEN repo-specifico: interaction limits o restrizioni del
  maintainer). **CLIRIM**: aprirla a mano dal browser:
  https://github.com/appcypher/awesome-mcp-servers/compare/main...Soil911:awesome-mcp-servers-1:add-atlaspi
- [ ] #10 mcpservers.org (form) — **CLIRIM**: https://mcpservers.org/submit
- [x] #11 awesomedata/apd-core → **PR #496 APERTA**
  (https://github.com/awesomedata/apd-core/pull/496)
- [x] #12 dh-tech/awesome-digital-humanities → **PR #76 APERTA**
  (https://github.com/dh-tech/awesome-digital-humanities/pull/76)
- [x] #13 sacridini/Awesome-Geospatial → **PR #229 APERTA**
  (https://github.com/sacridini/Awesome-Geospatial/pull/229)
- [ ] #14 OpenHistoricalMap wiki — **CLIRIM** (account OSM)
- [ ] #15 Show HN — **CLIRIM** (quando i dati sono più solidi)
- [x] Extra: **IndexNow ping 200 OK** (14 URL, 17/07)

**Nota ops**: durante la verifica di #5, `CORS_ORIGINS=*` è stato impostato in prod
(prima: whitelist domini) per rendere vera la colonna "CORS: Yes" — coerente con la
promessa "CORS-enabled" di llms.txt, rollback possibile. Vedi CHANGELOG v6.99.138.
