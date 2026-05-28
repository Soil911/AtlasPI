# Wave 0 / C — Frontend audit

Date: 2026-05-28
Agent: Wave 0 C (general-purpose, background, chrome-devtools-mcp)
Duration: ~4.2 min
Status: completed

---

## Lighthouse scores (desktop, navigation mode)
- **Performance**: not scored in this mode (use trace below). LCP from trace = **307 ms** (excellent).
- **Accessibility**: **94 / 100**
- **Best Practices**: **100 / 100**
- **SEO**: **100 / 100**
- **Agentic Browsing**: 23/100 (low — accessibility tree malformed + missing `llms.txt`)

CWV from Lighthouse trace: **CLS = 0.178** (needs improvement, threshold 0.1), TBT not reported in agentic mode.

## Console
- **0 errors, 0 warnings** across default + year=-1500 + mobile reload. Clean.

## Network
- **Requests (initial default load)**: 69, of which **24 are XHR/fetch to /v1/*** and **21 basemap tiles** from `basemaps.cartocdn.com`.
- **Total transferred (estimate)**: ~**30+ MB** dominated by `/v1/entities` paginated calls (10 × ~2.7 MB = ~27 MB).
- **Top 5 by bytes** (measured live):
  1. `GET /v1/entities?limit=100&offset=0` → **2.75 MB** (×10 sequential pages = ~27 MB)
  2. `unpkg.com/leaflet@1.9.4/dist/leaflet.js` → 147 KB
  3. `/static/app.js` → 119 KB
  4. `/static/style.css` → 96 KB
  5. `unpkg.com/leaflet.markercluster.js` → 34 KB
- **Latency (live curl, no throttling)**: p50 ≈ **210 ms**, p95 ≈ **678 ms** (the 678 ms is the 2.7 MB entities page).
- **4xx/5xx**: **none**. All 197 requests across full session returned 200.
- **Redundant calls**: `/v1/stats` fired 3× per page load. The 10 sequential `/v1/entities` paged calls run after the map has already rendered via `/v1/entities/light?limit=2000` (272 KB) — duplicate dataset.

## Performance trace insight (year=-1500)
1. **LCP 307 ms** is excellent. TTFB 2 ms, render delay 87 ms. Web server is healthy.
2. **CLS 0.178** flagged: font swap (Inter + Playfair load late from `gstatic.com`) shifts header/sidebar text after first paint. Self-host fonts or use `font-display: optional` / preload to fix.
3. **NetworkDependencyTree** chain extends to **~3.95 s** because of the 10 sequential paged `/v1/entities?limit=100&offset=N` requests — they push the "fully loaded" point far beyond LCP. These should be parallelized, switched to a single `limit=1000`, or removed entirely (the `/light` endpoint already covers map markers).

## Visual issues
- `01-default.png`: dark theme renders correctly, sidebar + map + detail panel layout look polished.
- `02-year-minus1500.png`: lapita-era map populated, labels visible on multiple continents. No obvious displaced polygons in the viewport.
- `03-mobile.png` (375×667): header occupies a large vertical share; the "Ask Claude" button is visible but the time slider may collide with sidebar toggle (hard to tell from screenshot).
- `04-mobile-map.png` (full page): map area is present but **sidebar appears not to collapse by default on narrow viewport**, taking ~half the screen width and squeezing the map.

## Mobile
- Sidebar layout not optimised: needs hamburger/drawer pattern under 768 px.
- **Touch targets**: Lighthouse flagged dozens of `.entity-map-label` markers as **only ~13 px tall** (must be ≥24×24 px per WCAG 2.5.5). Each label is `role="button" tabindex="0"` so it counts as interactive.
- Tile requests use `@2x` already — good for retina.

## Top 5 raccomandazioni (prioritised)

1. **Eliminate or batch the 10 sequential `/v1/entities?limit=100&offset=N` calls** (~27 MB total). The `/v1/entities/light?limit=2000` (272 KB) already feeds the map. If the paged calls power the entity table, switch to virtualization + on-demand fetch. **Expected impact: −95% of bytes-on-wire, −3 s on full load.**
2. **Fix CLS 0.178**: preload the 2 used `woff2` font files (Inter regular, Playfair italic) with `<link rel="preload" as="font" crossorigin>`, and use `font-display: optional`. Currently 12+ `gstatic.com` woff2 hits load lazily and shift layout.
3. **Accessibility quick wins** (Lighthouse failures):
   - Remove `aria-label="Caricamento dettagli"` from `<div class="detail-spinner">` (no valid role) or add `role="status"`.
   - Fix `#ask-claude-btn`: visible text is "Ask Claude" but `aria-label="Open Claude with preset prompt"` → mismatch. Set `aria-label` to "Ask Claude" or rely on text only.
   - Increase touch-target size of `entity-map-label` markers to ≥24×24 px on mobile (CSS padding + larger hit-box).
4. **Deduplicate `/v1/stats`** (called 3× per load) and the 8 `/v1/*?limit=1` probe calls (entities, events, rulers, sites, periods, chains, cities, languages). Looks like a feature-discovery probe — collapse into one `/v1/capabilities` endpoint or cache for the session.
5. **Mobile layout pass**: collapse sidebar to drawer under 768 px; ensure timeline + zoom controls don't overlap. Add `llms.txt` per spec to lift Agentic Browsing score (currently 23/100) and improve discoverability for AI agents — perfectly aligned with AtlasPI's stated mission of being "AI-readable".

Screenshots saved at `docs/auto-iter-wave0/frontend/01-default.png`, `02-year-minus1500.png`, `03-mobile.png`, `04-mobile-map.png`.
