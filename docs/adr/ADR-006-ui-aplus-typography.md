# ADR-006 — UI A+ typography & color system (v6.90)

**Status**: Adopted v6.90.0 (2026-04-19)
**Authors**: Claude Code (redesign session full-autonomy)
**Reviewers**: Clirim Ramadani (cofounder audit)
**Related ETHICS**: [ETHICS-011](../ethics/ETHICS-011-redesign-aplus-typography-and-color.md)

---

## Contesto

La pagina `/app` di AtlasPI (1038 entità, mappa Leaflet interattiva, sidebar
filtri, detail panel, timeline) era stata iterata senza un design system
unificato. Palette blu GitHub (`#58a6ff`) e font system stack funzionavano
ma non trasmettevano il carattere editoriale/accademico del dataset.

Questa ADR documenta il nuovo design system introdotto in v6.90 (Round 1-9
del redesign A+), le scelte tecniche, e come mantenerlo.

---

## Decisione

### Palette (tokens CSS)

```css
/* Dark theme (default) */
--bg:         #0f1318;  /* warm dark, era #0d1117 */
--panel:      #151a21;  /* sidebar, header */
--panel-2:    #1b2028;  /* hover/selected states */
--border:     #242a34;
--text:       #e9edf2;
--text-muted: #8a93a0;
--text-dim:   #6b7380;
--accent:     #e8b14a;  /* ambra editoriale */
--accent-ink: #1a1208;  /* ink su accent (AAA su giallo) */
--confirmed:  #6eb58a;  /* verde attenuato */
--uncertain:  #d4a13a;  /* ambra neutrale */
--disputed:   #d57770;  /* rosso attenuato */
```

Legacy tokens (`--bg-dark`, `--accent-warm`, `--shadow`, `--leaflet-filter`)
preservati come **alias** per backward-compat dei ~3000 righe CSS preesistenti.

Light theme usa palette parchment-like (`--bg: #faf8f3`, `--accent: #b38420`)
per AAA contrast su sfondo crema.

### Tipografia

**Font stacks**:
- `--font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
  Helvetica, Arial, sans-serif` — UI generale
- `--font-serif: 'Playfair Display', Georgia, 'Times New Roman', serif` —
  nomi entità, anno hero, era chip attiva, era ticks attivi

**Caricati via Google Fonts**:
- Inter: 400, 500, 600, 700
- Playfair Display: 0,600 / 1,400 / 1,600 / 1,700 (italic weights)
- `display=swap` per evitare FOIT (conserva CLS 0)

**Regole di uso**:
- `font-serif` + italic: riservato a nomi entità, anno hero, era chip
  attiva, era tick attiva, capital-history nome. Segnala "editoriale/classico".
- `font-ui`: tutto il resto. Segnala "interfaccia utile".
- `font-variant-numeric: tabular-nums`: su qualsiasi numero (year, count,
  percentuale, coordinate) per allineamento vertical-align preciso.

### Spacing scale

```css
--s-1: 4px;   --s-2: 8px;   --s-3: 12px;
--s-4: 16px;  --s-5: 22px;  --s-6: 32px;
```

Non applicata in massa (rischio regressione visiva su 3000 righe CSS).
Usata esplicitamente solo in nuove regole v6.90 (timeline bar, header,
sidebar sections).

### Rendering mappa (Leaflet layer HSL)

```js
// Per ogni entità con boundary_geojson polygon:
const hue = hashHue(e.id);  // djb2 stateless, 0-359
const selected = e.id === _selectedEntityId;
const hovered  = ...;       // from mouseover/mouseout
const fillAlpha = 0.28 * (selected ? 1.4 : hovered ? 1.2 : 1);
style: {
  fillColor: `hsla(${hue}, 55%, 55%, ${fillAlpha})`,
  fillOpacity: 1,
  color:      `hsl(${hue}, 55%, ${selected ? 70 : 62}%)`,
  weight:     selected ? 2 : hovered ? 1.3 : 0.9,
  lineJoin:   'round',
  opacity:    (someoneSelected && !selected && !hovered) ? 0.55 : 1,
  dashArray:  e.status === 'disputed' ? '6,4' :
              !isReal(e) ? '4,3' : null  // ETHICS-011 #2
}
```

**Hash function**:
```js
function hashHue(id) {
  let h = 0;
  const s = String(id);
  for (let i = 0; i < s.length; i++)
    h = ((h << 5) - h) + s.charCodeAt(i);
  return Math.abs(h) % 360;
}
```

### Architettura layout

**Flex column vertical**:
1. `#header` 52px fisso
2. `#app` flex:1 (sidebar + map + detail + timeline-bar absolute)
3. `footer` auto height

**#app padding-bottom: 60px** per riservare spazio alla
`.timeline-bar` (position:absolute bottom:0).

**Sidebar** `#sidebar`: 320px width fissa (spec dice 280 ma v6.67+
layout usa 320 e il cambio rischia reflow — decision: lasciare 320).

**Detail panel**: 400px destra, position absolute, transform
translateX(100%) per hidden.

**Timeline bar**: 60px, absolute bottom, flexbox con play-btn
circle + year-slider con era-ticks overlay + year-display serif
italic.

### Componenti principali

**Header**:
- Brand block (Atlas**PI** in accent + subtitle HISTORICAL GEOGRAPHY)
- Separator 1×26px
- Year hero (32px Playfair italic tabular-nums)
- Era label (10.5px Playfair italic accent uppercase)
- Nav: 4 link → More ▾ dropdown (Embed, API Docs, OpenAPI, Language, Theme)
- Counter pill (10.5px tabular-nums con dot verde)
- Sidebar toggle + Ask Claude CTA

**Sidebar collassabile** `<details>` nativo:
- Era (aperto)
- Status (aperto) — rows 12×12 checkbox-like con fill colore
- Region (chiuso) — continent chips
- Type (chiuso) — type chips
- Overlay (chiuso) — events + trade routes
- Sort select + Reset btn
- On map section (live count)

**Timeline bar**: [▶] [4500 BCE] [slider+era-ticks] [2025] [input|era|go] [speed▾] [year italic]

**Detail panel**: h2 Playfair italic 22px + Latin variant 11px
italic + life timeline 2px + tabbed sections (overview/timeline)
+ K/V info grid 80/1fr + capital-history editorial + sources +
ethics notes.

---

## Alternatives considerate

### Alt 1 — Palette categorica per continent
**Rejected**: ETHICS-011 §1. Rinforzerebbe gerarchie culturali.

### Alt 2 — Monocroma con variazioni di luminosità
**Rejected**: impossibile distinguere entità sovrapposte.

### Alt 3 — Material Design 3 system
**Rejected**: ML-industrial aesthetic contraddice il positioning
"editoriale/accademico" target.

### Alt 4 — Editorial HSL per-entity (chosen)
**Adopted**. Stateless hash, saturation/lightness uniformi, ogni
entità distinguibile, nessuna gerarchia implicita.

---

## Implicazioni

### Performance
- 2 preconnect + 2 stylesheet Google Fonts = ~45KB woff2 cached
- Lighthouse Performance: target ≥ 85 (era ~80 baseline)
- LCP invariato (tile Leaflet LCP, non font)
- CLS mantenuto a 0 via `display:swap` + `contain:layout` su header + fixed
  heights su sidebar sections

### A11y
- Contrast AAA per `--text` su `--bg` (13.2:1)
- Focus-visible globale 2px accent
- Reduced-motion full compliance
- Dual-channel status (color + dashArray) per daltonici

### Backward compat
- API endpoints invariati (Agent C contract verification)
- SDK python/js invariati (no frontend coupling)
- MCP server invariato (stdio-only, no HTTP frontend)
- Zenodo DOI stabile (entity count non cambia)

### Maintainability
- Token layer `:root` in un unico blocco (35 righe)
- Legacy alias mappati per bridge durante transition
- Nuove regole CSS sempre in coda al file (3400+ righe)
- ETHICS record per ogni scelta visiva non-banale

---

## Filing & riferimenti

- Spec design: [handoff/01-visual-spec.md](../../handoff/01-visual-spec.md)
- Prototipo: [handoff/prototype/A-plus-prototype.html](../../handoff/prototype/A-plus-prototype.html)
- Phase 1 verification: [handoff/cofounder-review/PHASE-1-VERIFICATION.md](../../handoff/cofounder-review/PHASE-1-VERIFICATION.md)
- Related: [ETHICS-011](../ethics/ETHICS-011-redesign-aplus-typography-and-color.md),
  [ADR-004](./ADR-004-capital-history-schema.md),
  [ADR-005](./ADR-005-deprecated-entity-merge-policy.md)

## Stato implementation (v6.90.0)

| Componente | Status |
|-----------|--------|
| Tokens + font imports (spec §1) | ✅ commit 40ef173 |
| Header A+ (spec §2) | ✅ commit bf47a66 |
| Sidebar collapsible (spec §3) | ✅ commit 1a4d359 |
| Timeline bar (spec §4) | ✅ commit 716e92c |
| Leaflet HSL (spec §5) | ✅ commit 06cf5f8 |
| Detail panel editorial (spec §6) | ✅ commit 007ff73 |
| A11y + reduced-motion (spec §7 + §10) | ✅ commit ce9cdef |
| i18n keys IT/EN | ✅ commit 4817361 |
| ETHICS-011 + ADR-006 | ✅ this commit |
| capital_history preservation (addendum B) | ✅ integrato in commit 007ff73 |
| CLS preservation (addendum C) | ✅ tutti i commit |
| Deprecated filter (addendum E) | ✅ già in v6.87 (upstream) |
