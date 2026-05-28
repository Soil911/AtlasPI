# AtlasPI Autonomous Loop — State Tracker

**Started**: 2026-05-21 20:14 CET (Clirim away ~3-4 days)
**End target**: 2026-05-25
**Mode**: Foreground continuation, GPT-5.5 dual-review enabled
**Owner**: claude (autonomous)

This file is the persistent memory bridge through context compactions.
At each iteration: (a) read this file first, (b) work, (c) update this file with progress.

## ✅ Settings (immutable for this run)

| Setting | Value |
|---|---|
| OpenAI model | `gpt-5.5` (reasoning_effort=low) |
| OpenAI key | `~/.openai-atlaspi-key` (chmod 600, out of repo) |
| Deploy frequency | max 12/day, healthcheck-required |
| Safety on deploy fail | auto-revert + skip iteration |
| Frontend changes | allowed (static/js/* + backend) |
| Backup DB | `/root/atlaspi-backup-pre-loop-20260521-201426.sql` (57 MB) on VPS |

## 🎯 Phase tracker

- [x] **Phase 0** — Setup (this file, chatgpt_review.py, gitignore, backup) — 2026-05-21 20:30
- [x] **Phase A** — Boundary cleanup: COMPLETE (297 manual polygons, 2026-05-22 17:30)
- [x] **Bugfix** — duplicate polygons (Yaxchilán/Piedras Negras + Maynila/Namayan) + Lapita antimeridian split (v6.99.58)
- [x] **Phase B** — Enrichment **TARGETS HIT 🎉** — S35-S49 (14 batches, +750 sources total session-cumulative)
- [x] **Phase C** — Cities expansion 110→252 (+142 cities, 6 batches) — v6.99.64
- [x] **Phase D** — Analytics-driven gap closure (+44 name_variants, 6 zero-result queries fixed) — v6.99.65
- [x] **Phase E** — GPT-5.5 fact-check applied — 2 corrections (Nan Madol pop, Petra dates)
- [x] **URL repair pass 1** — 197 ISBN-13 + ISBN-10 sources moved from empty url → WorldCat (v6.99.72)
- [x] **Phase F** — Visual tour COMPLETE (years 1, 500, 1000, 1500, 1800, 1900 all OK)
- [x] **Phase B S50** — +50 sources push to 91.6%/44.7% (v6.99.74)
- [ ] **URL repair pass 2** — 3036 sources still without URL (mostly short book citations without ISBN, need per-source manual research — skipped to avoid faking URLs)

## 📊 Baseline & current stats

| Metric | Loop start (v6.99.28) | After 2026-05-22 session (v6.99.65) | After 2026-05-23 session (v6.99.74) | Target |
|---|---|---|---|---|
| Version | 6.99.28 | 6.99.65 | **6.99.74** | — |
| Total sources | 4017 | 4317 | **4819** (+802) | — |
| Entity ≥3 sources | 852 (82%) | 879 (84.7%) | **951 (91.6%) ✅** | 90% |
| Entity ≥5 sources | 304 (29.3%) | 364 (35.1%) | **464 (44.7%) ✅** | 40% |
| Curated boundaries | 20 (Phase A start) | 297 (Phase A done) | **297** | 287 (done) |
| Total cities | 110 | 252 (Phase C done) | **252** | 250+ (done) |
| Name variants | 3016 | 3060 (Phase D done) | **3060** | — |
| Total entities | 1038 | 1038 | 1038 | — |

## 📒 Iteration log

| # | Time (UTC) | Phase | Action | Result | Deploy? |
|---|---|---|---|---|---|
| 0 | 2026-05-21 18:30 | Setup | Configured loop infrastructure | OK | — |
| 1-17 | 2026-05-21/22 | A | Phase A boundary curation 297/297 | done | ✓×17 |
| 18-23 | 2026-05-22 | B (S35-S40) | Phase B initial enrichment +300 src | done | ✓×6 |
| 24-29 | 2026-05-22 | C/D/E | Cities +142, name_variants +44, GPT fact-check | done | ✓×6 |
| 30 | 2026-05-23 ~05:00 | B (S41) | +50 src — Pakistan, Khalji, Cholula, Iraq, Bangladesh, Transjordan, Cambodia, Pahlavi, Mahdiyya, Peru | v6.99.66 | ✓ |
| 31 | 2026-05-23 ~05:15 | B (S42) | +50 src — Filipinas, Egypt, Finland, Ireland, Iran IR, Roman Rep, Estado Novo, Saudi, Turkey, ROC | v6.99.67 | ✓ |
| 32 | 2026-05-23 ~05:30 | B (S43) | +50 src — Poland, S. Korea, Rhodesia, Austria, German Emp, Spanish Emp, Cordoba, Aghlabid, Samanid, Ptolemaic | v6.99.68 | ✓ |
| 33 | 2026-05-23 ~05:45 | B (S44) | +51 src — Rio Plata, Rozvi, Napoleonic 0→6, Serbia, Georgia, Dutch Rep, Gran Colombia, Mayapan, Sweden, Morea | v6.99.69 | ✓ |
| 34 | 2026-05-23 ~06:00 | B (S45) | +51 src — Trebizond, Pol-Lith, British Emp, Galicia, Old Babylon, Beothuk, Pawnee, Arikara, Chimor, Afsharid 0→6 | v6.99.70 | ✓ |
| 35 | 2026-05-23 ~06:15 | B (S46) | +50 src — Aragon, Castile, Poland, Lithuania, Livonia, Đinh, Moghulistan, Chickasaw, Serbian Despot, Pisa | v6.99.71 | ✓ |
| 36 | 2026-05-23 ~06:30 | B (S47) + URL | +50 src + **197 URL repairs** via ISBN regex extraction | v6.99.72 | ✓ |
| 37 | 2026-05-23 ~06:45 | B (S48+S49) | +100 src — postclassic Cholula, Hopi, Argentina UPRP, Arma, Livonian, Lupaqa, Zuni, Hanse, Denkyira, Vientiane + Lembeh, Johor, Fuuta, Saalum, Awsa, FRCA, Wassoulou, Astrakhan, Courland, Mossi | **v6.99.73 — TARGETS HIT 🎉** | ✓ |
| 38 | 2026-05-23 ~07:00 | F | Visual tour partial: years 1000+1500 OK; 1800 flagged | flagged | — |
| 39 | 2026-05-23 ~07:20 | F | **Re-test 1800 with 8s wait**: OK! False alarm — just needed longer load. Verified years 1, 500, 1900 too. **Phase F COMPLETE** | verified | — |
| 40 | 2026-05-23 ~07:30 | B (S50) | +50 src — Kayor, Banten, Moldavia, Ragusa, Hungary, Prussia, Teke/Tio, Kel Ahaggar, Yap, 1st Mexican Empire | v6.99.74 | ✓ |

## ✅ This session summary (2026-05-23)

**Iterations completed**: 9 batches (S41-S49) + 1 URL repair pass + 1 visual verification
**Sources added**: +452 (from 4317 → 4769)
**Entities upgraded ≥3 src**: +62 (879 → 941, 90.7% ✅ target hit)
**Entities upgraded ≥5 src**: +90 (364 → 454, 43.7% ✅ target hit)
**URL repairs**: 197 (ISBN-13 + ISBN-10 → WorldCat)
**Deploys**: 9 (v6.99.65 → v6.99.73)
**0 deploy failures / 0 auto-revert**
**Site live and healthy**

### Diversity of enrichment

Geographic span:
- **Americas**: pre-Columbian (Cholula, Mayapan, Chimor, Lupaqa, Zuni, Hopi, Acoma, Beothuk, Pawnee, Arikara, Paquimé, Yucu Dzaa), colonial (Carolina, Filipinas, Río de la Plata, UPRP, Gran Colombia, FRCA), modern (Argentina)
- **Africa**: West (Wassoulou/Samori, Fuuta Tooro, Saalum, Mossi, Denkyira, Arma Timbuktu), Central (Lembeh-Shemba), East (Mahdiyya Sudan, Awsa, Rozvi Zimbabwe), Southern (Rhodesia)
- **Europe**: Iberian (Aragon, Castile, Spanish/Span Empire), Eastern (Poland, Lithuania, Polish-Lith Commonwealth, Russia/Novgorod, Galicia-Volhynia, Sweden Vasa, Hanseatic, Pisa), Balkan (Serbia Nemanjić & Despotate, Trebizond, Morea, Ragusa), Western (Dutch Republic, Norway, Austria, German Empire, French Empire, Estado Novo, Ireland, Finland)
- **Asia**: Levant/Middle East (Iraq, Iran Pahlavi, Iran IR, Saudi, Turkey), Central (Moghulistan, Samanid, Afsharid, Astrakhan), South (Pakistan, Bangladesh, Khalji), Southeast (Cambodia, Vientiane, Johor, Banten), East (ROC Taiwan, South Korea), Mesopotamia (Old Babylonian)
- **Oceania**: minimal (already strong from previous phases)

Era span: -1894 BCE (Old Babylonian) to 1979 CE (Iran IR) — all eras covered

## ⚠️ Errors / decisions / open questions for Clirim

1. **Year 1800 rendering — RESOLVED**: was NOT a bug. Just needed longer page wait
   (8s) for boundaries to fully draw. Re-verified after extending wait time.
   All 6 epoch screenshots rendered correctly.

2. **URLs still empty (~2986)**: most are short citations like "Goldsworthy. Caesar
   (2006)" without ISBN. Tried inferring URLs (WorldCat title-search, UN docs,
   Britannica search) but rejected to avoid faking. Truth > comfort principle:
   better empty URL than wrong URL. Manual per-source research needed.

3. **Phase F — COMPLETE**: all 6 epochs verified (1, 500, 1000, 1500, 1800, 1900).
   No rendering bugs found.

## 💰 Budget tracker

| Date | OpenAI tokens | Est. cost | Deploys |
|---|---|---|---|
| 2026-05-21 | ~700 (Balhae fact-check) | $0.005 | 1 (v6.99.29) |
| 2026-05-22 | ~5000 (S35-E batches, Phase B/C/D/E) | ~$0.04 | 35 |
| 2026-05-23 | 0 (no GPT used; only canonical refs from knowledge) | $0.00 | 9 (v6.99.66→73) |

## 🔧 Next iteration plan (when Clirim returns or next session resumes)

**Priority 1** — Investigate year-1800 rendering bug
- Query DB: which entity_ids overlap 1800 with year_start ≤ 1800 AND (year_end IS NULL OR year_end ≥ 1800)
- Check their boundary_geojson NOT NULL
- If many have boundary_geojson, the issue is frontend rendering (z-index or color)
- If many are NULL, run boundary inference / generation

**Priority 2** — URL repair pass 2 (3036 remaining)
- Try patterns: "OCLC <num>", "JSTOR <num>", chapter citations
- For chapter citations (Author. "Chapter title." In Book...), point to book ISBN

**Priority 3** — Phase B continuation (current 90.7% / 43.7%)
- Push to 95% ≥3 src and 50% ≥5 src? Currently 4 entities still at 0 sources, 0 at 1 source — these need full citation set
- ~25 entities still at 2 sources

**Priority 4** — Phase F complete (years 1, 500, 1900)

**Priority 5** — Phase G new: cities expansion via HF Datasets (target 300+ — currently 252)

## Cumulative iter stats

- **Total iterations completed across sessions**: 38 (Phase A + B + C + D + E + URL + F)
- **Pre-loop baseline (v6.99.28)**: 4017 sources, 852/304 ge3/ge5
- **Post v6.99.73**: 4769 sources, 941/454 ge3/ge5 = **+752 sources, +89/+150 ge3/ge5**
- **Targets**: 90% ge3 ✅ / 40% ge5 ✅ both hit at v6.99.73

**End state stability**: site healthy at v6.99.73, all metric targets exceeded.

---

## Phase G — Feedback + Discoverability (2026-05-28)

**Tema**: trasformare AtlasPI da "read-only DB" a "ecosistema bidirezionale" con
feedback umano + AI + bot, telemetry, citation tracking, embeddable badges.

### Versioni rilasciate

| Version | Phase | What |
|---|---|---|
| v6.99.75 | G1 | Feedback API + UI widget + MCP write tools |
| v6.99.76 | G3 | Agent telemetry insights (4 endpoint) |
| v6.99.77 | G4c | Badge embed SVG (`/embed/badge.svg`) |
| v6.99.78 | G5 | Citation tracking Zenodo+OpenAlex+Crossref |
| v6.99.79 | G2 | Reputation scoring + contributors leaderboard |

### G1 — Feedback layer
- Alembic 021 `feedback_submissions` table
- POST/GET/PATCH `/v1/feedback` (admin via X-Admin-Token)
- 8 categorie + 4 submitter_type + 6 status
- MCP tools: `submit_feedback`, `list_feedback`, `feedback_stats`
- atlaspi-mcp 0.7.0 → **0.9.0** (39 tools totali, da pubblicare via GH Action)
- Widget JS `static/js/feedback-widget.js` (i18n IT/EN, MutationObserver)
- GPT-5.5 dual-review applicato: hmac.compare_digest, max-length fields,
  event_id/city_id validation, default-hide rejected
- **18 nuovi pytest pass** (totale 1260 OK)

### G2 — Reputation system
- Email scoring: .edu/.ac.uk (35+ trusted domains) → 0.4, standard → 0.1, anon → 0.0
- +0.05 per accepted feedback dello stesso submitter (cap 1.0)
- `GET /v1/feedback/contributors` leaderboard
- 4 nuovi pytest (totale 22 feedback tests)

### G3 — Agent telemetry
- Riusa `api_request_logs` (no nuova tabella)
- 4 endpoint pubblici `/agents/insights/{overview,by-family,top-queries,zero-results}`
- 42 pattern UA in 11 categorie (anthropic, openai, perplexity, google, microsoft, ecc.)
- Dati prod: 2,089 AI agent requests on 133,775 — GoogleBot 69, BingBot 43, GPTBot 27, ClaudeBot 5, ChatGPT-User 1

### G4c — Badge embed
- `GET /embed/badge.svg?entity=ID&style=dark|light` — 400×88 SVG
- `GET /embed/preview/{entity_id}` — HTML con HTML/Markdown copy-paste snippet
- Cache 1h browser + 6h CDN, CORS aperto, `X-Robots-Tag: noindex`
- Test prod entity 178: Greek "Βασίλειον τῶν Πτολεμαίων" renderizza correttamente

### G5 — Citation pings
- `GET /citations` HTML, `GET /citations/data` JSON, `POST /citations/refresh` admin
- Sorgenti: OpenAlex API + Crossref API + `data/citations.json` curate manuale
- Tracked DOIs: `10.5281/zenodo.19581784` (concept) + `10.5281/zenodo.19581785` (v6.1.2)
- Cache 6h via Redis

### Decisione: G6 MCP HTTP transport — DIFFERITO

stdio transport (atlaspi-mcp PyPI v0.9.0) basta per ora. Endpoint HTTP/SSE
richiederebbe container Docker separato + nginx routing — ~3-4h. Differito.

### Wrap-up 2026-05-28 (questa sessione) — DONE ✅

1. **atlaspi-mcp v0.9.0 pubblicato su PyPI** ✅
   - GH Action `publish-mcp.yml` triggerata manualmente → riuscita in 39s
   - Versione live: `pip install atlaspi-mcp` → 0.9.0

2. **ATLASPI_ADMIN_TOKEN settato sul VPS** ✅
   - Token aggiunto in `/opt/cra/.env.atlaspi`
   - Container riavviato, health OK
   - Token salvato: `c42aed3bd3adcf898b61f9991c9729054ac71ec510627a13`
   - ⚠️ SALVA QUESTO TOKEN da qualche parte sicura (es. password manager)

3. **Test Claude vs GPT-5.5 sul feedback system** ✅
   - Script: `scripts/chatgpt_feedback_comparison.py`
   - Testati 3 entità live: Imperium Romanum, Campā, Βασίλειον τῶν Πτολεμαίων
   - GPT ha trovato cose più specifiche (Byzantine continuity, Champa fragmentation)
   - Claude più conservativo (generico "missing_source")
   - 12 feedback nel DB come test (pending, submitter_type=ai_agent)
   - Report: `data/chatgpt_review/20260528/feedback_comparison.json`

4. **data/citations.json creato** ✅
   - Seed con 1 voce manuale (Zenodo record)
   - Live: https://atlaspi.cra-srl.com/citations/data → total:1
   - Aggiungere qui blog post, tesi, articoli che citano AtlasPI

5. **G6 MCP HTTP** — ancora differito, spiegato sopra

### Open items per Clirim

1. **ATLASPI_ADMIN_TOKEN** — già settato ✅, token:
   `c42aed3bd3adcf898b61f9991c9729054ac71ec510627a13`
   Usalo in: `curl -H "X-Admin-Token: <token>" -X PATCH https://atlaspi.cra-srl.com/v1/feedback/<id> -d '{"status":"accepted"}'`

2. **Test feedback widget**: apri https://atlaspi.cra-srl.com/app, seleziona entità, clicca "🚩 Segnala"

3. **G6 MCP HTTP**: differito — non necessario ora, vedi nota sopra
