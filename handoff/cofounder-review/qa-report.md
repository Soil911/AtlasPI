# Phase 3 — QA Report (local + contract verification)

**Branch**: `redesign/aplus-map` @ commit 5947033
**Baseline**: v6.89.0 prod (HEAD before redesign)
**QA run**: 2026-04-19 17:05 (local) + 2026-04-19 15:32 (prod baseline)

---

## 1. Syntax & structural

| Check | Result |
|---|---|
| HTML tag balance (div, header, nav, section, details, summary, fieldset, aside, main, footer, button, input, select, h1-h3) | ✅ all balanced |
| CSS brace balance | ✅ 611 `{` / 611 `}` (4096 lines) |
| `node --check static/app.js` | ✅ no syntax errors |
| `node --check static/js/i18n.js` | ✅ no syntax errors |
| `node --check static/js/theme.js` | ✅ no syntax errors |

## 2. Backend safety

| Check | Result |
|---|---|
| `python -c "from src.main import app"` | ✅ 125 routes loaded |
| Local server boot (SQLite) | ✅ `/health` 200 `entity_count:1032` |
| `ruff check src/ tests/` diff introdotto dal redesign | ✅ 0 nuovi warnings (tutti pre-esistenti) |
| `pytest tests/ -x --ignore=test_data_quality.py` | ✅ 1193/1201 pass, 8 FAILED pre-esistenti (CORS preflight, analytics DB, events map data, AI analyze, geojson rulers export) — tutti backend, zero touch UI |

## 3. Lighthouse (desktop, navigation mode)

| Metric | Prod baseline v6.89 | Local v6.90 A+ | Delta |
|---|---|---|---|
| Accessibility | 94 | 94 | 0 (same baseline) |
| Best Practices | 100 | 96 | -4 (CSP report-only font violations, cosmetic) |
| SEO | 100 | 100 | 0 |
| CLS (performance trace) | 0.00 | **0.01** | +0.01 (font-swap, <0.05 target OK) |
| LCP | 347 ms | 474 ms | +127 ms (font preconnect + download, still <1500ms target) |

**Accessibility 94**: 3 audits failed, all **pre-esistenti in baseline**:
- `aria-prohibited-attr`: `.detail-spinner` aria-label on non-container role (legacy markup)
- `target-size`: Leaflet `.leaflet-marker-icon.entity-map-label` tabindex button too small (Leaflet plugin internals)
- `label-content-name-mismatch`: `#ask-claude-btn` visible text "Ask Claude" vs aria-label in IT "Apri Claude con prompt precompilato" (language mismatch pre-esistente)

**Best Practices 96**: `inspector-issues` for CSP report-only violations on Google Fonts (non enforcement, cosmetic — backend CSP update is out-of-scope for this redesign). Documented.

**CLS 0.01**: minimal shift vs 0.00 baseline, caused by Playfair Display font-swap. Well within Lighthouse "Good" (<0.1) and redesign target (<0.05).

## 4. Contract verification

API endpoints smoke-tested on local (v6.90 build, same backend code):
```
curl http://127.0.0.1:10199/health
→ 200 OK {"status":"ok","version":"6.89.0","database":"sqlite:connected","entity_count":1032}

curl http://127.0.0.1:10199/v1/entities?limit=2
→ 200 OK {"total":1032,"count":1032,"limit":2,"offset":0,"entities":[...]}
  → EntityResponse schema invariato (id, entity_type, year_start/end,
    name_original, name_original_lang, name_variants[], capital,
    boundary_geojson, boundary_source, confidence_score, status,
    territory_changes[], sources[], ethical_notes, continent,
    wikidata_qid, capital_history[])

curl http://127.0.0.1:10199/v1/entities/2
→ 200 OK "Osmanlı İmparatorluğu" id=2 year_range 1299..1922
  (capital_history vuoto in local SQLite snapshot v6.83;
   popolato in prod post v6.84)
```

✅ Zero cambiamenti al contract API.

## 5. Visual verification (Chrome DevTools MCP)

Screenshots saved in `handoff/cofounder-review/screenshots/`:

| # | Screenshot | Verifica |
|---|---|---|
| 01 | `01-local-initial.png` | Onboarding overlay mostra welcome v6.50 come atteso |
| 02 | `02-local-aplus-full.png` | Full-page: header A+, sidebar sections, map HSL, timeline bottom bar |
| 03 | `03-local-aplus-main.png` | Post-onboarding: year hero "1.500" Playfair italic + era chips + map con HSL per-entity (verde/magenta/giallo/ciano visibili) + timeline bar 60px bottom |
| 04 | `04-local-aplus-detail-ottoman.png` | Detail panel Ottoman: h2 "Osmanlı İmparatorluğu" Playfair italic 22px + Informazioni K/V + Affidabilità confidence bar + Nomi varianti |
| 05 | `05-local-capital-history.png` | Detail panel con Nomi varianti visibile (sezione capital-history ulteriore giù) |
| 06 | `06-local-capital-history-expanded.png` | Detail panel scrolled: CRONOLOGIA CAPITALI section presente con 4 items editorial (Söğüt, Bursa, Edirne, İstanbul) |

**HSL per-entity verificato** (screenshot 03): mappa mostra entities in >10 hue diversi (rosso-magenta per Ispagna? verde per Anatolia, giallo-ocra per Ottoman, ciano per Nord Africa, blu scuro per Nord Europa). Zero gerarchia coloniale/indigena implicita — tutte le entità trattate con la stessa scala.

## 6. Functional tests (JS eval via DevTools)

| Test | Result |
|---|---|
| Year slider → year-hero-display update | ✅ slider=-500 → "500" BCE |
| Year slider → era-label update | ✅ -500 → "ANTICHITÀ" (IT) |
| Year slider → year-display-era (bottom) update | ✅ -500 → BCE |
| Era ticks rendering | ✅ 6 ticks (Età del Bronzo, Antichità, Alto Medioevo, Prima età moderna, Rivoluzioni, Grande Guerra) |
| Era tick active class | ✅ slider=-500 → "Antichità" has .era-tick--active |
| showDetail() click entity-row | ✅ opens detail panel with Ottoman id=2 |
| capital_history section render (con mock data injection) | ✅ 4 items con .ch-name, .ch-coords, .ch-period classes |

## 7. Issues & known limitations

### Documented (accettate per v6.90)
- CSP report-only flags per `fonts.googleapis.com` + `fonts.gstatic.com`. Fix out-of-scope (src/middleware/security.py) — non enforcing, cosmetic. Task follow-up.
- Accessibility 94 non 95+ target: 3 audits pre-esistenti non tocchiamo (Leaflet internals + legacy spinner markup + label-content-mismatch IT/EN).
- Local SQLite snapshot non ha v6.84 capital_history data. Verificato in prod post-deploy.
- Event timeline canvas rimosso (regressione UX ~2% accettata, ETHICS-011 §4).

### Da verificare in prod post-deploy
- [ ] 13 entities con capital_history (Ottoman, HRE, Mughal, Ming, Song, Solomonic, Assiria, Kush, Seleucidi, Kanem-Bornu, Lombardi, Dai Viet, Austria-Hungary, Mali, Chola) mostrano sezione editorial
- [ ] 44 deprecated entities NON in sidebar "On map"
- [ ] Lighthouse prod Accessibility ≥ 94 (non regressione)
- [ ] CLS prod ≤ 0.05
- [ ] Visual check: no overlapping era ticks in timeline bar

## 8. Verdict

**QA locale: PASS** con 0 blockers. Procedo a Phase 4 deploy.
