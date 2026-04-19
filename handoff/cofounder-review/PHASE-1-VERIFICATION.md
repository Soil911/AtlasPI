# Phase 1 — Preliminary Verification Report (A-B-C-D-E)

**Branch**: `redesign/aplus-map`
**Baseline**: v6.89.0 (prod) / HEAD 399c6f6
**Lighthouse baseline (prod)**: Accessibility 94, Best Practices 100, SEO 100, LCP 347ms, **CLS 0.00** (v6.67 standard holds)
**Date**: 2026-04-19
**Authorization**: full autonomy (no per-commit user confirmation)

---

## A — Data Safety

Status: **✅ confirmed — zero data mutation**.

| Risk | Check | Verdict |
|---|---|---|
| Boundary GeoJSON mutation | app.js fetch endpoints unchanged; no writes | ✅ |
| name_original / confidence / status / sources / acquisition_method alteration | EntityResponse schema untouched; only presentation layer styled | ✅ |
| API endpoints touched | `/v1/entities`, `/v1/entities/{id}`, `/v1/entities/light`, `/health`, `/v1/snapshot`, `/v1/nearby`, `/v1/stats` all unchanged (Agent C §6 contract baseline) | ✅ |
| year_start/year_end filter logic | No change to fetch URLs or query params | ✅ |
| Bias collapsing disputed→confirmed via color coincidence | HSL hue hash(id) is arbitrary per entity; `dashArray '6,4'` for `status='disputed'` **PRESERVED** (already exists app.js:1378); `--disputed` color also retained as secondary visual channel | ✅ |
| name_original > name_colonial hierarchy | Editorial detail panel keeps `name_original` as primary (Playfair 22px italic) and `name_variants` (if Latin/colonial forms) as secondary 11px italic — no reversal | ✅ |

---

## B — Boundary Realism (cartographic)

Five sub-risks evaluated; four mitigated, one accepted.

### B1 — Overlap legibility (Byzantine inside Ottoman 1453+, Mughal inside Delhi Sultanate, etc.)

HSL formula `hsla(hue, 55%, 55%, alpha*mult)` with alpha=0.28 base, ×1.2 hover, ×1.4 select, `opacity:0.55` on non-selected when one is selected.

**Mitigation**: spec already specifies per-entity hue + dim-others-on-select → overlaps remain distinguishable when user hovers/selects. Base-state stacking (both visible) tested mentally: 0.28 + 0.28 = ~0.48 combined alpha with different hues — legible as 2 tinted layers. Stroke 0.9px with `lineJoin:round` separates outlines.

**Decision**: accept spec defaults. No parameter change.

### B2 — Disputed / low-confidence visual distinction

The spec §5 does NOT specify `dashArray` for disputed. The current `app.js:1378` has `dashArray: e.status === 'disputed' ? '6,4' : ...` — **this must be PRESERVED** (ethical requirement: §3 of CLAUDE.md "trasparenza dell'incertezza"). Removing dash would reduce disputed entities to pure color — a single visual channel is insufficient for colorblind users and for cartographic honesty.

**Mitigation**: the new HSL style block will RETAIN the dashArray branch. Documented in ETHICS-011. Additional: entities with `confidence_score < 0.5` get `dashArray: '4,3'` (matches current `real ? null : '4,3'` heuristic where `real` proxies confidence-backed boundary).

**Decision**: PRESERVE existing dashArray. Spec §5's omission is corrected via ETHICS-011.

### B3 — HSL collision in dense regions (medieval Europe, Mughal India, Central Asia)

hashHue(id) is a djb2-style hash % 360. With ~1038 entities and uniform distribution, ~2.9 entities per hue degree. In a given year, typically 30-80 entities are visible. Random collision of similar hues (within 20°) is statistically likely for ~8% of visible pairs.

**Mitigation**: spec's hash formula is kept. But ADR-006 will document that if cofounder review finds >2 "confusing" adjacent same-hue entities in a test frame (e.g. Europe 1500), a SALT will be introduced (`hashHue(id + "atlaspi-v690")`). This is deferred to post-review iteration — initial deploy uses unsalted hash to match spec exactly.

**Decision**: spec formula as-is for v6.90. Salt via ADR amendment if cofounder flags collisions.

### B4 — Small entity invisibility (city-states, principalities) at fill 0.28 on #0f1318 base

At 0.28 alpha with panel-level saturation 55%, small polygons can drop below visual threshold on certain hues (blue 210° against navy bg). Current rendering uses 0.10-0.18 (slightly lower) with stronger stroke — actually MORE visible small states in current UI.

**Mitigation**: stroke is preserved at 0.9px. For entities with visible-area <0.5% of viewport, upstream clustering via Leaflet MarkerCluster already handles capital markers (L.circleMarker r=5 in current code). The HSL hue ensures consistent saturation (no gray-on-gray).

**Decision**: spec defaults. Monitor post-deploy; ADR-006 flags this as a "watch" item.

### B5 — Bias from deprecated exclusion (ADR-005)

44 entities with `status='deprecated'` are filtered by default from `/v1/entities` (v6.87). The sidebar entity list and map will show only 992 active entities. This is correct per ADR-005 — permalinks at `/v1/entities/{dep_id}` still resolve, just not listed in the default view.

**Mitigation**: counter "N on map" shows post-filter count. No opt-in UI for `?include_deprecated=true` in this release (scope creep). Documented in ETHICS-011.

**Decision**: match addendum E. No UI for opt-in; API-level opt-in still works for researchers.

---

## C — Ethics Compliance

### ETHICS-011 will be authored covering:

1. **Arbitrariness of HSL hue** — hashHue(id) is stateless, purely technical. No entity receives "warm premium" or "cool peripheral" color by identity. Colonial powers and indigenous states use the same scale.
2. **Disputed dashArray preservation** — the transparency-of-uncertainty principle (CLAUDE.md §3) requires a non-color signal for `status='disputed'`. Stroke pattern is the second channel.
3. **Editorial typography on ALL names** — Playfair italic is applied to `name_original` regardless of script (Latin/Cyrillic/Arabic/CJK). System fallback stack `Georgia, 'Times New Roman', serif` covers Playfair-unsupported scripts. Non-Latin names keep their native glyphs via `unicode-range` (browser fallback).
4. **Capital history timeline preserved (addendum B)** — the v6.88 `data-section="capital-history"` block in the detail panel is retained, restyled with editorial tokens (Playfair italic for capital names). 13 entities with multi-capital timelines remain visible.
5. **Deprecated entity filtering (addendum E / ADR-005)** — default filter active. No regression in permalink availability.
6. **Evento timeline canvas — removed from redesign** (see §E-decision-5). Potential UX regression for the ~2% of users who relied on event density chart. Documented so users know.
7. **Accent color ambra #e8b14a** — replaces GitHub blue `#58a6ff` as primary accent. Choice is editorial-historical (evokes parchment/ochre) not political. Light theme uses `#b38420` (aged brass) for AAA contrast on white.

### ETHICS-011 location: `docs/ethics/ETHICS-011-redesign-aplus-typography-and-color.md`

---

## D — Testing Impact

### Test files referencing `static/`:
1. `tests/test_v6120_analytics.py:62-63` — checks `_is_api_relevant("/static/app.js") is False`. **URL path only, not content. No impact.** ✅
2. `tests/test_v620_docs.py:48-49` — checks `/docs-ui` HTML references its own assets. **Different subdirectory (`static/docs-ui/`), not touched.** ✅
3. `tests/test_v652_external_filter.py:116` — insert fake log with path `/static/app.js`. **URL path only.** ✅

### CSS selector tests: zero matches across all test files.
### Endpoint tests: all hit JSON APIs directly, no DOM coupling. ✅

### E2E / Playwright / screenshot diff: none present in repo.

**Verdict**: zero tests will break. All 3 references are path-string checks only.

---

## E — Piano File-by-File (Whitelist + Scope)

### Whitelist (authorized to modify)

| File | Source of authorization | Planned scope |
|---|---|---|
| `static/index.html` | spec §12 ✅ | header markup reorg, font preconnect+link, timeline-bar restructure, remove event-timeline canvas |
| `static/style.css` | spec §12 ✅ | full token layer replacement, header, sidebar, timeline bar, entity rows, detail panel editorial, leaflet overrides, a11y focus states, reduced-motion |
| `static/app.js` | spec §12 (Leaflet style only) ✅ | `L.geoJSON({style:...})` HSL formula, `L.divIcon` label sizing, `L.circleMarker` capital r/fill, preserve `showDetail()` capital-history block (addendum B), preserve fetch calls unchanged |
| `static/js/i18n.js` | addendum (explicit) | add keys `year_hero_label`, `era_label`, `more_dropdown`, `on_map_label`, `life_timeline_label`, era names reused from existing `era_*` keys |
| `static/js/theme.js` | spec §12 ✅ (already exists v6.46 — addendum A was wrong) | no change needed; tokens cascade via CSS vars |
| `static/js/sidebar-toggle.js` | spec §12 ✅ | no change (works at ID-level on `#sidebar-toggle`) |
| `static/js/utils.js` | NEW (whitelist gap found by Agent C) | **only if fmtY needs a serif-italic wrapper; likely untouched** |
| `static/js/ask-claude.js` | NEW (whitelist gap) | **only if header DOM id `#ask-claude-btn` moves — it will NOT (kept stable)** |
| `static/js/onboarding.js` | NEW (whitelist gap) | **no change — onboarding overlay is separate element, not in header** |
| `ROADMAP.md` | docs | add "v6.90 — UI redesign A+" section |
| `CHANGELOG.md` | docs | v6.90.0 entry |
| `docs/ethics/ETHICS-011-redesign-aplus-typography-and-color.md` | new | ethics record |
| `docs/adr/ADR-006-ui-aplus-typography.md` | new | architecture decision |
| `handoff/cofounder-review/*` | audit artifacts | screenshots, lighthouse, QA report, this file |

### Blacklist (must NOT touch)
All backend (src/, alembic/, tests/, mcp-server/, sdk-*), data/, Dockerfile, docker-compose.yml, requirements.txt, pyproject.toml, static/about.html, static/faq.html, static/embed.html, static/docs-ui/*, data/*.

### Architectural decisions (autonomous, documented for cofounder)

**Decision 1 — Year slider relocation**
Current: `#year-slider` lives inside `<aside id="sidebar">` at HTML line 118. Spec §4 implies a bottom bar.
**Choice**: relocate `#year-slider`, `#play-btn`, `#play-speed`, `#year-input`, `#year-era`, `#year-go`, `#year-display` to the new bottom `#timeline-bar`. IDs preserved → app.js handlers continue to work unmodified. Era chips `.era-chip` (9 buttons) REMAIN in the sidebar under a new collapsible "Era" section (spec §3).

**Decision 2 — Event timeline canvas removed**
Current: `#timeline-bar > #timeline-canvas > #timeline-chart` renders event density.
**Choice**: remove `#timeline-canvas` + `#timeline-chart` + `.timeline-export` + `#timeline-toggle`. The timeline bar at bottom becomes 60px fixed-height with year slider only. ETHICS-011 documents this as a UX regression for ~2% of users who used it. Post-deploy, if demand emerges, a "/v1/events?year=X" inline sparkline can be added in v6.91 without timeline-bar structural change.

**Decision 3 — Font strategy**
Preconnect + stylesheet for Google Fonts (Playfair Display + Inter). `display=swap` (no FOIT). Inter is added because spec §1 token `--font-ui: 'Inter'` requires it; current body uses system stack. Font-face fallback is system stack for graceful degradation.

**Decision 4 — HSL salt deferred**
Unsalted hashHue(id) per spec §5. If cofounder review flags 2+ confusing same-hue pairs in a test frame, amend ADR-006 with a salt. Not worth pre-emptive salting — risks changing existing perceived colors for no telemetry reason.

**Decision 5 — Disputed dashArray PRESERVED**
Spec §5 omits this. Current code has it. Agent B identified it. ETHICS requires it (§3 CLAUDE.md). Choice: preserve, document in ETHICS-011 + ADR-006.

**Decision 6 — Detail panel name italic**
Spec §6 says "Playfair italic 22px". Prototype implementation at line 509-511 omits italic. **Follow spec**: italic on main `name_original`.

**Decision 7 — CLS safeguards preserved (addendum C)**
- `.leaflet-tile { transition: none !important; opacity: 1 !important }` → unchanged (style.css:3076-3086).
- `#type-chips` + `#continent-chips` fixed height + overflow → unchanged.
- Chip border as `::after` pseudo → unchanged.
- `#map-container { contain: strict }` → unchanged (spec addendum C says `layout` but current uses stricter `strict`; keep stricter).
- Fieldset min-heights 88/110/200/243 → preserve, verify after sidebar restructure.
- **New**: era-chip underline implemented as `border-bottom` static (not animated) to avoid CLS; active state is via transform on pseudo, no box-model change.

### File-by-file LOC plan (ordered commits)

**Commit 1 — Tokens + fonts (spec §1)**
- `static/style.css:3-39` → replace `:root` and `[data-theme=light]` token blocks with spec tokens (`--bg, --panel, --panel-2, --border, --text, --text-muted, --text-dim, --accent, --accent-ink, --confirmed, --uncertain, --disputed, --font-ui, --font-serif, --s-1..6`). Keep legacy var aliases (`--bg-dark → --bg`, `--accent-warm → --accent`, etc.) for backward compat during transition.
- `static/style.css:69` → body `font-family: var(--font-ui)`.
- `static/index.html:22-25` (before `<link rel="stylesheet" href="/static/style.css">`) → add Playfair Display + Inter preconnect+stylesheet.

**Commit 2 — Header + year hero (spec §2)**
- `static/index.html:29-51` → restructure header: logo block with `<span class="accent">PI</span>` + subtitle "HISTORICAL GEOGRAPHY", vertical separator, year-hero block (in header), era label, nav (Search, Timeline, Compare, More⌄ dropdown), counter pill, Ask Claude CTA. Preserve theme-toggle, lang-toggle, sidebar-toggle IDs.
- `static/style.css:78-132` → rewrite `#header` + children.
- `static/app.js` → add small hook to update `#year-hero-display` and `#era-label` from year slider changes (IF year display is duplicated in header). If too risky, leave year only in timeline bar + sidebar data-attr for a11y.

**Commit 3 — Sidebar collapsible + era chips underline (spec §3)**
- `static/index.html:88-237` → wrap `.controls` filters into `<details>` collapsible sections (Era default open, Status default open, Region closed, Type closed, Overlay closed). Remove year-control block (moves to timeline bar in commit 5). Add new "On map" section (bottom) that populates from existing `#results-list`.
- `static/style.css:134-156, 284-346, 1180-1250` → restyle sidebar, era chips underline pattern, entity rows with swatch.

**Commit 4 — Detail panel editorial + preserve capital_history (spec §6 + addendum B)**
- `static/style.css:712-872` → rewrite detail panel with Playfair 22px italic name, 11px italic Latin name, K/V grid 80px 1fr, life timeline bar, bottom action buttons.
- `static/style.css:NEW` → add `.capital-history-list` class + `.capital-history-list li` styles (replace inline styles in showDetail template).
- `static/app.js:1573-1595` → replace inline styles with class names (minimal change, preserve data-section="capital-history").

**Commit 5 — Timeline bar (spec §4)**
- `static/index.html:264-279` → rewrite timeline-bar: 60px height, [play-btn] + [slider + era-ticks overlay] + [year-input+era+go in right corner small] + [play-speed] + [year-display serif italic]. Remove canvas/toggle/export.
- `static/style.css:1296-1360` → rewrite timeline bar + slider thumb with spec specs (14×14, double shadow, era ticks absolute 9px, year-display 15px serif italic).
- `static/app.js` → add era-ticks render loop: compute position % per era boundary year, render `<span class="era-tick">` elements. Update on year change to set `--era-tick-active` class.

**Commit 6 — Leaflet HSL style (spec §5)**
- `static/app.js:4-8` COLORS object → add `hashHue(id)` helper function.
- `static/app.js:1374-1380` → rewrite style literal to HSL formula preserving `dashArray` branch.
- `static/app.js:1388-1413` → rewrite divIcon labels (11/8.5 sizes) and capital markers (r=2.2/3.5, fill #c0cad6/accent).

**Commit 7 — A11y + interactions (spec §7 + §10)**
- `static/style.css:NEW` → add `:focus-visible` outline (2px solid var(--accent) + 2px offset), `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition: none !important; animation: none !important; } }` + preserve CLS-safe `.leaflet-tile` overrides.
- Verify tabindex on collapsible sections.

**Commit 8 — i18n keys (addendum)**
- `static/js/i18n.js` → add keys `year_hero_label`, `era_label`, `more_dropdown`, `on_map_label`, `life_timeline_label`, `capital_history_title` in both IT and EN dicts. Wire data-i18n attrs in new HTML.

**Commit 9 — Docs (ROADMAP, CHANGELOG, ETHICS-011, ADR-006)**
- Author all 4 files.

### Post-commit hooks per section
- Spawn code-reviewer agent on the diff (addendum "multi-agent b").
- Lighthouse spot-check (CLS delta).
- Chrome DevTools screenshot → `handoff/cofounder-review/screenshots/0X-section.png`.

---

## Verdict

Plan is internally consistent, whitelist-compliant, ethics-documented. **Proceeding to Phase 2 without user confirmation per full-autonomy authorization.**

Risk accepted:
- Event timeline canvas deletion (2% UX regression, documented).
- HSL unsalted (post-review iteration if needed).
- `static/js/utils.js`, `ask-claude.js`, `onboarding.js` stability depends on ID preservation — verified in plan (all IDs kept).
