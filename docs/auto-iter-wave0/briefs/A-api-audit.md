# Wave 0 / A — API audit

Date: 2026-05-28
Agent: Wave 0 A (general-purpose, background, read-only)
Duration: ~2 min
Status: completed

---

## Endpoint inventory

~115 routes across 25 router files. Public REST surface is `/v1/*`; `/admin/*` is dashboard/ops; `/widget/*` and `/embed/*` are iframe-safe. All public read endpoints are GET-only; the write surface is tiny.

| METHOD | path | file:line | auth | rate-limit | response shape |
|---|---|---|---|---|---|
| GET | /health | src/api/routes/health.py:28 | none | 120/min | JSON (typed) |
| GET | /v1/entity, /v1/entities, /v1/entities/light, /v1/entities/batch, /v1/entities/{id} | src/api/routes/entities.py:63,135,281,377,447 | none | 120/min global | Pydantic (EntityResponse + light) |
| GET | /v1/search, /v1/search/fuzzy, /v1/types, /v1/continents, /v1/random, /v1/nearby, /v1/where-was, /v1/snapshot/{year}, /v1/stats, /v1/aggregation | src/api/routes/entities.py:483-1256 | none | 120/min | mixed dict / Pydantic |
| GET | /v1/events*, /v1/events/{id}, /v1/events/types, /v1/events/map, /v1/events/on-this-day/{mm-dd}, /v1/events/at-date/{date}, /v1/events/date-coverage, /v1/entities/{id}/events | src/api/routes/events.py:122-509 | none | 120/min | dict |
| GET | /v1/periods, /types, /regions, /at-year/{year}, /by-slug/{slug}, /{id}, /v1/entities/{id}/periods, /v1/events/{id}/periods | src/api/routes/periods.py:83-318 | none | 120/min | dict |
| GET | /v1/cities*, /v1/routes*, /v1/trade-routes | src/api/routes/cities_routes.py:266-497 | none | 120/min | dict |
| GET | /v1/sites, /sites/types, /sites/unesco, /sites/nearby, /sites/{id} | src/api/routes/sites.py:86-241 | none | 120/min | dict |
| GET | /v1/rulers, /at-year/{year}, /by-entity/{id}, /{id} | src/api/routes/rulers.py:72-206 | none | 120/min | dict |
| GET | /v1/languages, /at-year/{year}, /families, /{id} | src/api/routes/languages.py:58-154 | none | 120/min | dict |
| GET | /v1/chains, /types, /{id}, /v1/entities/{id}/predecessors, /successors | src/api/routes/chains.py:101-316 | none | 120/min | dict |
| GET | /v1/entities/{id}/contemporaries, /related, /similar, /evolution, /timeline; /v1/compare/{id1}/{id2} | src/api/routes/relations.py:33-543 | none | 120/min | dict |
| GET | /v1/snapshot/year/{year} | src/api/routes/snapshot.py:48 | none | 120/min | dict |
| GET | /v1/export/{geojson,csv,timeline,sites.geojson,rulers.geojson,languages.geojson,entities,events} | src/api/routes/export.py:32-334; search.py:342,441 | none | 120/min global (preset 20/min available, not applied) | binary / FeatureCollection |
| GET | /v1/render/snapshot/{year}.png, /v1/render/entity/{id}.png | src/api/routes/render.py:70,150 | none | 120/min | image/png |
| GET | /v1/compare, /v1/search, /v1/timeline-data | search/compare/timeline.py | none | 120/min | dict |
| GET | /embed/badge.svg, /embed/preview/{id} | src/api/routes/embed.py:71,146 | none | 120/min | image/svg+xml |
| GET | /widget, /widget/entity/{id}, /widget/timeline, /widget/on-this-day | src/api/routes/widgets.py:45-63 | none | 120/min | text/html |
| GET | /citations, /citations/data | src/api/routes/citations.py:219,243 | none | 120/min | Pydantic CitationsResponse / HTML |
| POST | /citations/refresh | src/api/routes/citations.py:228 | X-Admin-Token (hmac.compare_digest) | 120/min | Pydantic |
| POST | /v1/feedback | src/api/routes/feedback.py:279 | none (public) | doc says 5/min, but only 120/min global | Pydantic FeedbackResponse |
| GET | /v1/feedback, /stats, /contributors, /{id} | feedback.py:383,439,506,581 | none | 120/min | Pydantic |
| PATCH | /v1/feedback/{id} | feedback.py:596 | X-Admin-Token (hmac.compare_digest) | 120/min | Pydantic |
| GET | /agents/insights/{overview,by-family,top-queries,zero-results} | agents_insights.py:187-349 | none | 120/min | Pydantic |
| **GET, POST, DELETE** | **/admin/cache-stats, /admin/cache/flush, /admin/sync-events** | admin_cache.py:22,41,60 | **NONE** | 120/min | dict |
| **GET, POST** | **/admin/brief, /admin/ai/suggestions, /admin/ai/status; POST /admin/ai/suggestions/{id}/{accept,reject,implement}, /admin/ai/analyze, /admin/ai/implement-accepted** | admin_cofounder.py:38-252 | **NONE** | 120/min | HTML / dict |
| **GET** | **/admin/insights, /admin/coverage-report, /admin/suggestions** | admin_insights.py:137,314,539 | **NONE** | 120/min | dict |
| **POST/GET/DELETE** | **/admin/dev-ips*, /admin/analytics, /admin/analytics/data** | analytics.py:262-945 | **NONE** | 120/min | dict |
| GET | /metrics (Prometheus) | src/api/metrics.py:197 | none | 120/min | text/plain |
| POST | /v1/csp-report | src/middleware/csp_report.py (router) | none | 30/min preset | 204 |

Also non-OpenAPI: `/`, `/app`, `/embed`, `/docs`, `/redoc`, `/openapi.json`, `/v1/openapi.json`, `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/.well-known/ai-plugin.json`, `/.well-known/mcp.json`, `/about`, `/faq`, `/favicon*`, `/og-image.png`, `/docs-ui`.

## OpenAPI status
- Esposto: default FastAPI `/docs`, `/redoc`, `/openapi.json`, plus override `/v1/openapi.json` (src/main.py:606) injecting `servers` based on `ENVIRONMENT`.
- Versione spec: OpenAPI 3.1 (FastAPI default). App version pinned at `6.99.80` (src/config.py:19).
- Description/summary: ricco markdown OPENAPI_DESCRIPTION (~125 line in src/main.py:250). Tag globali italiani (entità, relazioni, esportazione, sistema). La maggior parte degli endpoint ha `summary=` e `description=`; alcuni admin/HTML usano `include_in_schema=False`.
- Pydantic schemas: solo 21 occorrenze di `response_model=` in routes (entities, feedback, citations, agents_insights, health). La maggior parte degli endpoint ritorna `dict`/`JSONResponse` non tipizzati → schema OpenAPI debole, niente validazione di output.

## Auth/security
- Solo 2 endpoint usano auth: `PATCH /v1/feedback/{id}` (feedback.py:611) e `POST /citations/refresh` (citations.py:236). Entrambi verificano header `X-Admin-Token` contro env `ATLASPI_ADMIN_TOKEN` con `hmac.compare_digest` (feedback.py:258-273). Failsafe: se env vuota → tutti negati.
- Nessuna dipendenza FastAPI per auth (nessun `Depends(require_admin)`); auth fatta inline. Nessun ruolo/scope/JWT.
- **Tutti gli endpoint sotto `/admin/*`** (cache flush, sync-events, cofounder AI analyze/implement, insights, dev-ips delete, analytics) **sono completamente non protetti**: `include_in_schema=False` li nasconde da `/docs` ma sono raggiungibili da qualunque IP che conosca l'URL.
- CORS: `src/main.py:406-413` whitelist `https://atlaspi.cra-srl.com,https://www.atlaspi.cra-srl.com` (override env `CORS_ORIGINS`); `allow_credentials=True` solo se non `*`; metodi `GET, POST, OPTIONS` → PATCH e DELETE non sono CORS-preflightabili da browser (per design o omissione).
- Rate limit: slowapi singleton (src/middleware/rate_limit.py) con storage Redis se `REDIS_URL` ping ok, altrimenti memory:// (degrada a per-worker). Default `RATE_LIMIT=60/minute` (config), middleware app `120/minute`. Preset definiti per detail/search/snapshot/export ma **non applicati** (nessun decorator `@limiter.limit()` sui route handlers visti). Header `X-RateLimit-*` automatici.
- Altri middleware: GZip (>500B), SecurityHeaders (HSTS+CSP report-only+nosniff+frame-options+permissions-policy), HeadSupport (HEAD→GET), RequestLogging+analytics, error handlers + Sentry. CSP enforce mode pianificato post-v6.66.

## Top 3 gap/red flag

1. **🚨 `/admin/*` non protetto** (admin_cofounder.py:127-218 POST AI implement/analyze; admin_cache.py:41 cache flush; admin_insights.py traffic logs; analytics.py:262-326 DELETE dev-ips). Sono solo `include_in_schema=False`: security-by-obscurity. Un attaccante può flushare cache, iniettare AI suggestions, cancellare dev-ip filter, leggere insights traffico.
   **Raccomandazione**: estrarre `_check_admin_token` da feedback.py in `src/api/deps.py` come `require_admin = Depends(verify_admin_token)`, applicarlo a tutti i router admin (`APIRouter(dependencies=[Depends(require_admin)])`).

2. **Rate-limit preset non agganciati**: `RATE_LIMIT_EXPORT=20/min`, `_SNAPSHOT=60/min`, `_DETAIL=300/min` definiti (rate_limit.py:102-105) ma nessun handler ha `@limiter.limit(...)`. Solo il default 120/min globale è attivo. Endpoint pesanti come `/v1/export/geojson` e `/v1/render/snapshot/{year}.png` non sono throttlati separatamente.
   **Raccomandazione**: applicare `@limiter.limit(RATE_LIMIT_EXPORT)` a export/*.py e render/*.py; idem `RATE_LIMIT_SNAPSHOT` a snapshot.py:48 e entities.py:1091.

3. **Response models mancanti** su ~80% degli endpoint pubblici (events, periods, sites, cities, chains, rulers, languages, relations, snapshot, render). OpenAPI consumer-side (Claude MCP, client SDK auto-gen) vede solo `application/json` generico.
   **Raccomandazione**: aggiungere `response_model=` con schemi Pydantic per almeno `/v1/snapshot/year/{year}`, `/v1/entities/{id}/similar`, `/v1/events?...`, `/v1/periods/by-slug/{slug}` — sono i 4 endpoint citati nella description OPENAPI come quickstart.

## Files chiave esaminati
- `src/main.py:1-624` (app factory, middleware stack, openapi override)
- `src/config.py:1-94` (CORS/env/rate-limit defaults)
- `src/middleware/rate_limit.py:1-107` (slowapi singleton, preset)
- `src/middleware/security.py:1-146` (CSP report-only, HSTS, headers)
- `src/api/middleware.py:1-84` (re-exports + RateLimitMiddleware stub)
- `src/api/routes/feedback.py:258-612` (only token check pattern)
- `src/api/routes/citations.py:228-240` (token check duplicato)
- `src/api/routes/admin_cache.py:1-75`, `admin_cofounder.py:1-260`, `admin_insights.py:130-545`, `analytics.py:262-945` (admin endpoints NON protetti)
- `src/api/schemas.py:1-60` (Pydantic basics)
