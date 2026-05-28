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


