# AtlasPI auto-iteration log

Branch: `auto-iter-wave0`
Started: 2026-05-28
DB backup: `/root/atlaspi-backup-AUTOITER-START-20260528-194958.sql` (production VPS, 43MB)
Driver: Claude Code (autonomous mode, with user oversight)
Cross-check: ChatGPT API (when key available) + Claude sub-agents

## Stop conditions (require user OK)
- Contratto API cambia
- Migration Alembic nuova
- DROP / dati persi
- ETHICS record nuovo
- Decisione architetturale (ADR)
- ChatGPT solleva issue grave che condivido
- `cra-deploy` fallisce 2x

## Wave 0 — Reconnaissance (started 2026-05-28)

5 agenti in parallelo background. Tutti read-only sul codice/DB.

| Agent | Mandato | Status |
|---|---|---|
| A | API audit (endpoint, OpenAPI, auth, CORS) | launched |
| B | Data quality (7 analyzers + geometric) | launched |
| C | Frontend audit (lighthouse, console, network, screenshots) | launched |
| D | Enrichment backlog (S35+ priorities, gaps) | launched |
| E | Docs sync (ROADMAP/CHANGELOG/ETHICS) | launched |

## Activity log

- 2026-05-28 19:49 UTC — DB backup completato (43M)
- 2026-05-28 19:50 UTC — Branch `auto-iter-wave0` creato
- 2026-05-28 19:50 UTC — OpenAI key NOT in `.env.atlaspi` (good, would leak to prod) — TROVATA in `$env:OPENAI_API_KEY` locale (Windows env var) + ALSO in `~/.openai-atlaspi-key`
- 2026-05-28 19:51 UTC — Wave 0 lanciato (5 agenti background, read-only)
- 2026-05-28 19:52 UTC — Scoperto: `scripts/chatgpt_review.py` GIÀ ESISTENTE (gpt-5.5 + fallback gpt-5.4, gpt-4-turbo). Self-test ping ok. Mio Write fallito correttamente; userò esistente.
- 2026-05-28 19:54 UTC — Tutti i 5 agenti completati. Brief salvati in `docs/auto-iter-wave0/briefs/{A,B,C,D,E}-*.md`.

## Wave 0 — RISULTATI SINTETICI

| Agent | Durata | Stato | Brief |
|---|---|---|---|
| A | 2.0 min | done | A-api-audit.md |
| B | 5.5 min | done | B-data-quality.md |
| C | 4.2 min | done | C-frontend-audit.md |
| D | 4.2 min | done | D-enrichment-backlog.md |
| E | 2.2 min | done | E-docs-sync.md |

### Top 15 findings cross-categoria

**🚨 Sicurezza**
1. 10+ endpoint `/admin/*` non protetti (cache flush, AI implement/accept, dev-ips DELETE, analytics) — solo `include_in_schema=False`

**⚡ Performance/UX**
2. 27 MB scaricati per default load (10× `/v1/entities?limit=100&offset=N` quando `/v1/entities/light?limit=2000` già copre la mappa)
3. CLS 0.178 (sopra threshold 0.1) da font swap gstatic
4. `/v1/stats` 3× per page + 8 probe `/v1/*?limit=1`
5. Agentic Browsing 23/100 (manca `/llms.txt`)
6. Mobile sidebar non collassa <768px, touch targets <24px

**🗺️ Dati / geometric**
7. 2 antimeridian crossers: id=754 Sau o Futuna, id=307 Lapita (auto-fix esistente)
8. 7-10 mismatch `entity_type`/size: Harappa `city-state` 1.5M km², Lituania `principality` 1.5M km², Finlandia `duchy` 762k km²
9. 78.6% entità ORFANI da chain_links (sotto soglia 85% analyzer → invisibile)

**📚 Docs/Process**
10. ROADMAP dichiara "v6.22" come corrente, realtà è v6.99.80 (gap 77 release)
11. Tag git fermi a `v6.92.0` (8+ versioni non-taggate)
12. ETHICS-010 mismatch: file dice "wikidata-cross-reference", ROADMAP dice "tratta esseri umani"
13. Phase G (v6.99.75-79: feedback/reputation/citation/telemetry) senza ADR

**📈 Backlog**
14. Enrichment a S50 reale (memoria utente diceva S34 — stale)
15. 280 eventi unlinked (43%) — ETHICS-007 backlog. Top 30 priority list pronta (D brief).

### Buone notizie
- Metadata "verde" (5/7 analyzer silenziosi)
- 0 entità senza fonti (100%)
- 100% boundary coverage
- 91k API requests, 99.97% 2xx
- Lighthouse: Acc 94, BP 100, SEO 100, LCP 307ms
- `chatgpt_review.py` già funzionante (gpt-5.5)

## ChatGPT-5.5 cross-check su Wave 1 plan (2026-05-28 19:58 UTC)

Logged: `data/chatgpt_review/20260528/ask.jsonl`

**Verdict**: "directionally good but underweights admin exposure, overweights housekeeping. Reorder containment-first."

**Punti accettati** (alta convergenza):
1. Admin auth è URGENZA #1, va in Wave 1.1, non in Wave 1b
2. Antimeridian fix è MEDIUM data risk (muta prod), non LOW → serve backup specifico + verifica `ST_IsValid` + bbox sanity + render smoke
3. "Drop v6.23-v6.26 as absorbed" → rischio cancellare history → MARK AS SUPERSEDED
4. ETHICS-010: investigare PRIMA se rename/dupe/wrong, non scegliere arbitrariamente
5. Quick containment: middleware block `/admin/*` (token o IP allowlist) BEFORE refactor router-level
6. Considerare DISABILITARE endpoint admin alto rischio (AI implement, cache flush, dev-ips DELETE) se non usati
7. Definizione smoke ESPLICITA: homepage + map markers + /entities/light + /stats + entity detail + admin 401/403 + admin auth 200
8. NO MIXED BUNDLE (docs+security+data+frontend insieme) → 1 sub-wave 1 release
9. Tag git: verificare commit hash prod = HEAD prima di taggare (per evitare tag su commit non deployato)
10. Default page web NON dovrebbe chiamare `/v1/entities` se `/light` basta
11. Auth admin: identificare PRIMA caller legittimi, POI applicare auth + audit logging

**Disaccordo parziale (judgment Claude)**:
- gpt: "/llms.txt not material enough to outrank security/perf" → vero che impatto immediato score è limitato, MA resta strategico per pitch "AI-readable database" (mission AtlasPI). Lo sposto in Wave 1.4 (housekeeping), non escludo.

## Wave 1 — PIANO REVISTO (post cross-check)

| Sub-wave | Versione | Focus | Tempo stimato | Rischio |
|---|---|---|---|---|
| 1.1 | v6.99.81 | CONTAINMENT `/admin/*` | 60-90 min | medio (verify-then-implement) |
| 1.2 | v6.99.82 | DATA FIX antimeridian | 30-45 min | medio (backup + verify) |
| 1.3 | v6.99.83 | PERF (27 MB regression) | 60-90 min | medio (analisi prima) |
| 1.4 | v6.99.84 | HOUSEKEEPING (docs, llms.txt, a11y, tag) | 45-60 min | basso |

Ogni sub-wave: 1 sub-release deploy autonomo. NO bundle misti.

## Wave 1.1 — Admin containment (2026-05-28)

Status: implementato, pytest pass, pronto per deploy v6.99.81.

### Decisione finale (post 2 cross-check ChatGPT-5.5)

- **Token-only auth** (X-Admin-Token header OR Basic Auth admin:TOKEN)
- **NO IP allowlist** (critical fix: bypass via reverse proxy)
- **Failsafe** se ATLASPI_ADMIN_TOKEN env unset → tutti 401
- **Basic Auth username constraint**: deve essere esattamente `admin`
- **WWW-Authenticate Basic** header → browser prompt
- **Cron hardened**: source env + fail-fast se token mancante + header sempre presente
- **Docs-ui cleanup**: rimossa intera sezione Admin & Insights pubblica
- **Startup audit loud**: log ERROR se trovo /admin/* senza verify_admin dep

### Test result (locale)

```
1291 passed, 36 skipped, 10 xfailed, 0 failed in 97.6s
tests/test_admin_auth.py: 13/13 pass (1 per username constraint)
```

### File toccati (Wave 1.1)

| File | Type | Change |
|---|---|---|
| src/api/deps.py | NEW | verify_admin dependency |
| src/main.py | MODIFIED | Depends import + 4 admin includes + startup audit |
| static/docs-ui/index.html | MODIFIED | -82 LOC (admin section rimossa) |
| scripts/daily_ai_check.sh | MODIFIED | +19 LOC env load + token + header |
| tests/conftest.py | MODIFIED | TEST_ADMIN_TOKEN + client header + unauth_client |
| tests/test_admin_auth.py | NEW | 13 test (unauth/auth/failsafe/edge) |

### Stop conditions non-trigger

- Nessun caller pubblico legittimo di /admin/* trovato (UI admin/brief è privato Clirim)
- Nessun POST/DELETE distruttivo da IP esterno nei log nginx
- Cra-agent integration (`/api/admin/agent/*` 500) è separata, fuori scope

### Cross-check ChatGPT-5.5 (round 1 e 2)

Log: `data/chatgpt_review/20260528/ask.jsonl` (round 1 piano + round 2 design + round 3 implement review).

**Critici applicati**:
- Round 1 → reorder containment-first (era #4, è diventato #1)
- Round 2 → rimossa IP allowlist (bypass reverse proxy)
- Round 3 → enforce Basic Auth username == admin

**Disaccordi documentati**:
- gpt: "llms.txt not material" → mantenuto in Wave 1.4 (strategicamente importante per "AI-readable" mission)

### Deploy outcome (2026-05-28 18:46 UTC)

- `cra-deploy atlaspi` → build + recreate container + healthcheck OK
- Commit hash deployed: `7f3006857f7040ee55eab3c0776dad7be23fad3f` (verified match local HEAD)
- Tag annotato `v6.99.81` creato e pushato

### Smoke prod result (9 check + cron WET run)

| # | Test | Expected | Got | OK |
|---|---|---|---|---|
| 1 | /health public | 200 | 200 | ✓ |
| 2 | /v1/entities/light?limit=5 | 200 | 200 | ✓ |
| 3 | /admin/cache-stats UNAUTH | 401 + WWW-Authenticate Basic | 401 + correct header | ✓ |
| 4 | /admin/cache-stats + X-Admin-Token | 200 | 200 + valid JSON body | ✓ |
| 5 | /admin/cache-stats + Basic admin:TOKEN | 200 | 200 | ✓ |
| 6 | /admin/cache-stats + Basic foo:TOKEN | 401 | 401 | ✓ |
| 7 | /admin/cache-stats + wrong token | 401 | 401 | ✓ |
| 8 | /admin/coverage-report UNAUTH (era esposto via docs-ui) | 401 | 401 | ✓ |
| 9 | Cron daily_ai_check.sh WET run | exit 0 + 52/52 smoke pass | exit 0 + 52/52 + 1 briefing | ✓ |

**Wave 1.1: COMPLETE. v6.99.81 in produzione, validato.**

## Wave 1.2 — Antimeridian data fix (2026-05-28)

Status: COMPLETE. v6.99.82 deployato. id 754 + id 307 fixati.

### Bug root cause

Boundaries Polygon singoli con vertici a ±179.98 → bbox lon_span 359°.
- `_normalize_antimeridian` script salta perché agisce solo su MultiPolygon
- Entrambi sono in `MANUALLY_CURATED_IDS` (skip aggiuntivo)

### Fix design (post ChatGPT-5.5 cross-check)

**id 754 Sau o Futuna**: cerchio 10km attorno a Sigave/Alo (Futuna island)
- bbox: lon [-178.25, -178.07] = 0.19° span, area 313 km²

**id 307 Lapita**: cerchio 1000km attorno a Vanuatu (Efate)
- bbox: lon [158.86, 177.77] = 18.92° span, area 3.12M km²
- Core Bismarcks-Solomon-Vanuatu-Fiji (Tonga/Samoa esclusi: doc esplicito)

### ChatGPT critiche applicate

- `ST_SetSRID(_, 4326)` wrapper
- WHERE clause idempotency guard
- "WESTERN/CORE PROXY" wording per Lapita
- `CASE WHEN ethical_notes empty` per cleanliness

### Verifica produzione

| | id 754 | id 307 |
|---|---|---|
| lon_span pre | 359.97° | 358.50° |
| lon_span post | 0.19° | 18.92° |
| area pre | 124,879 km² | 6,187,246 km² |
| area post | 313 km² | 3,124,123 km² |
| ST_IsValid | t | t |
| boundary_source | historical_approximation | historical_approximation |
| bbox center | Pacific (Futuna) | Pacific (Vanuatu) |

### Files

- NEW: `scripts/fix_anti_754_307.py`
- NEW: `data/fixes/v6.99.82_antimeridian.sql`
- NEW: `data/fixes/backups/v6.99.82_pre_fix_754_307.jsonl`
- NEW: `docs/auto-iter-wave0/wave-1-2/inventory-and-design.md` (skipped, design in CHANGELOG)
- NEW: `docs/auto-iter-wave0/wave-1-2/screenshots/{01,02}*.png`

Nessuna code change runtime → no migration, no breaking change.
Tag `v6.99.82` da pushare dopo cra-deploy.

**Wave 1.2: COMPLETE.**

## Wave 1.3 — Year-aware lazy boundary load (2026-05-28)

Status: IMPLEMENTED, awaiting deploy + visual verify.

### Bug

`loadEntityBoundariesInBackground` (v6.68) faceva 10 fetch sequenziali
a `/v1/entities?limit=100&offset=N` (~27 MB totali) per pre-caricare TUTTI
i boundary_geojson, indipendentemente dall'anno visualizzato.

### Fix design (post ChatGPT-5.5 cross-check, 12+ critiche applicate)

- Phase 1 invariata: `/v1/entities/light?limit=2000` (272 KB)
- Phase 2 NEW: `/v1/entities?year=Y&limit=500` solo on year change
- Cache Map<year, {status, promise, ...}>
- AbortController per stale race
- Paginate defensive (future-proof se anno > 500 entità)
- Merge solo boundary_geojson + opzionali (no overwrite name/status)

### Trade-offs (verificati)

- Default load: 272 KB + ~3 MB = ~85% reduction vs 27 MB
- Year change: 0.5-5 MB single fetch (cached dopo)
- Peak active year (1500=331): ben sotto limit=500
- Rate-limit: AbortController evita pressure su slider drag

### File toccati

- MODIFIED: `static/app.js` (~+30 LOC net)
- JS syntax OK (`node --check`)
- Backend pytest: 1292 pass, 0 failed

Pronto per cra-deploy + verifica network panel + tag v6.99.83.


