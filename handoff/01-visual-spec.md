# AtlasPI — Design Spec: Mappa A+

**Versione**: 1.0 (apr 2026)
**Scope**: solo UI layer di `/app` (static/index.html, static/style.css, static/app.js)
**Target**: preservare ogni comportamento esistente, cambiare solo tipografia, palette, layout header/sidebar/timeline.

---

## 1. Design tokens

Aggiungere/modificare le CSS custom properties dentro `:root` in `static/style.css` (tema dark — default).

```css
:root {
  /* ── Backgrounds ── */
  --bg:         #0f1318;   /* era #0d1117 — più caldo */
  --panel:      #151a21;   /* sidebar, header */
  --panel-2:    #1b2028;   /* stati hover / selected */
  --border:     #242a34;   /* separatori sottili */

  /* ── Text ── */
  --text:       #e9edf2;
  --text-muted: #8a93a0;
  --text-dim:   #6b7380;

  /* ── Accent (UNICO — brand) ── */
  --accent:     #e8b14a;   /* ambra editoriale — sostituisce rosso e amber dispersi */
  --accent-ink: #1a1208;   /* testo sopra accent */

  /* ── Status semantici ── */
  --confirmed:  #6eb58a;
  --uncertain:  #d4a13a;
  --disputed:   #d57770;

  /* ── Tipografia ── */
  --font-ui:     'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-serif:  'Playfair Display', Georgia, 'Times New Roman', serif;

  /* ── Spacing scale ── */
  --s-1: 4px;
  --s-2: 8px;
  --s-3: 12px;
  --s-4: 16px;
  --s-5: 22px;
  --s-6: 32px;
}

[data-theme="light"] {
  --bg:         #faf8f3;
  --panel:      #ffffff;
  --panel-2:    #f3efe6;
  --border:     #e3dcc9;
  --text:       #1a1a1a;
  --text-muted: #6b6b6b;
  --text-dim:   #9a9a9a;
  --accent:     #b38420;
  --accent-ink: #ffffff;
}
```

**Importa Playfair Display** (una volta sola, in `static/index.html` head):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;1,400;1,600;1,700&display=swap" rel="stylesheet">
```

---

## 2. Header (da 7 bottoni a 4 link + anno hero)

### Prima (attuale)
```
[AtlasPI] [sub] ........ [🟡 IT] [Search] [Timeline] [Compare] [Embed] [API Docs] [OpenAPI] [🔴 Ask Claude] 31/194
```

### Dopo (A+)
```
[AtlasPI] [Historical Geography] | 1500 CE · Age of Discovery .. Search Timeline Compare More⌄ ● 31 on map [🟠 Ask Claude]
```

### Cambiamenti puntuali
- **Logo**: "PI" in `var(--accent)` (non più `#58a6ff`)
- **Subtitle**: `Historical Geography` — stile piccolo `11px`, `letter-spacing: 1.2px`, uppercase, `var(--text-muted)`
- **Separator**: linea verticale 1×26px `var(--border)`
- **Year hero**: `font-family: var(--font-serif); font-style: italic; font-weight: 700; font-size: 32px; letter-spacing: -0.6px; font-variant-numeric: tabular-nums;`
- **Era label**: stessa serif italic ma `10.5px`, `var(--accent)`, uppercase, letter-spacing 1px, solo nome dell'era corrente
- **Nav**: 4 link testuali (Search, Timeline, Compare, More) — **no più bottoni bordati**. Sono `<span>` con `font-size: 11.5px; color: var(--text-muted); cursor: pointer;` — hover: `color: var(--text)`
- **"More ⌄"** dropdown contiene: Embed, API Docs, OpenAPI, Language (IT/EN/...)
- **Counter pill**: `padding: 3px 9px; border: 1px solid var(--border); border-radius: 3px; font-size: 10.5px;` — pallino verde `var(--confirmed)` 6×6px + testo `N on map`
- **CTA "Ask Claude"**: `background: var(--accent); color: var(--accent-ink); padding: 5px 12px; font-size: 11.5px; font-weight: 500; border-radius: 3px;` — **no più rosso**

### Altezza header
`52px` (da `48px` attuali). Gli extra 4px accomodano il year hero in serif.

---

## 3. Sidebar

### Comportamento
- **Sezioni collassabili** con chevron ▾/▸
- Default aperte: `Era`, `Status`
- Default chiuse: `Region`, `Overlay`, `Type`
- Ultimo blocco fisso: **On map (N)** — lista live delle entità filtrate, scrollabile

### Era chips — stile editoriale
```html
<span class="era-chip">Bronze</span>
<span class="era-chip era-chip--active">Discovery</span>
```
- **Non attivo**: `font-size: 10.5px; color: var(--text-muted); padding: 4px 8px 6px; border-bottom: 1.5px solid transparent;`
- **Attivo**: `color: var(--accent); font-weight: 600; font-style: italic; font-family: var(--font-serif); border-bottom: 1.5px solid var(--accent); letter-spacing: 0.3px;`
- **NO background fill** sui chip — solo underline per attivo

### Status rows
Lista verticale con checkbox-like square (12×12, fill di colore se attivo):
- Confirmed — `var(--confirmed)`
- Uncertain — `var(--uncertain)`
- Disputed — `var(--disputed)`
Il conteggio a destra, `var(--text-muted)`, tabular-nums.

### Entity list (blocco "On map")
```css
.entity-row {
  padding: 8px 10px;
  font-size: 12px;
  display: flex; align-items: center; gap: 8px;
  border-radius: 3px;
  cursor: pointer;
}
.entity-row:hover { background: var(--panel-2); }
.entity-row--selected {
  background: var(--panel-2);
  border: 1px solid var(--border);
}
.entity-row .swatch {
  width: 3px; height: 14px; border-radius: 2px;
  /* color = HSL per-entity (vedi §5) */
}
.entity-row .range {
  font-size: 10px; color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}
```

### Larghezza sidebar
`280px` (invariata). Con `overflow-y: auto` sul container flex per evitare clip su viewport corto.

---

## 4. Timeline (bottom bar)

### Altezza
`60px` (era 44px).

### Struttura
```
[▶] [4500 BCE] ──tick tick tick── [2025] [speed ⌄] [1500 CE]
```

### Tick delle ere sopra il cursore
Posizionati assolutamente lungo la barra, ogni tick è il nome dell'era:
```css
.era-tick {
  position: absolute; top: -2px; transform: translateX(-50%);
  font-size: 9px; color: var(--text-muted); letter-spacing: 0.4px;
  white-space: nowrap;
}
.era-tick--active {
  color: var(--accent); font-weight: 600;
  font-style: italic; font-family: var(--font-serif);
}
```

### Play button
Cerchio 30px, `background: var(--accent); color: var(--accent-ink);` — ▶ / ❚❚ a seconda dello stato.

### Slider thumb
```css
input[type=range]::-webkit-slider-thumb {
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 0 3px var(--panel), 0 0 0 4px rgba(232,177,74,0.3);
}
input[type=range]::-webkit-slider-runnable-track {
  height: 4px; background: var(--border); border-radius: 2px;
}
```

### Year display a destra
`font-family: var(--font-serif); font-style: italic; font-weight: 600; color: var(--accent); font-size: 15px; font-variant-numeric: tabular-nums;` — seguito da piccolo "CE" o "BCE" in Inter `9px var(--text-muted)`.

---

## 5. Rendering confini mappa (Leaflet layer style)

**NON toccare la logica Leaflet, i dati GeoJSON, le coordinate.** Solo lo stile del layer.

### Prima
```js
// app.js attuale (es.)
style: {
  fillColor: '#58a6ff', fillOpacity: 0.25,
  color: '#58a6ff', weight: 1
}
```

### Dopo
```js
// HSL per entità — hue fisso dal campo entity.color_hue o hash(entity.id)
// Ogni entità ha un hue stabile; saturation/lightness uniformi → palette coerente.
const hue = entity.color_hue ?? (hashHue(entity.id));
const selected = entity.id === selectedId;
const hovered  = entity.id === hoveredId;

const fillAlpha = 0.28 * (selected ? 1.4 : hovered ? 1.2 : 1);
style: {
  fillColor: `hsla(${hue}, 55%, 55%, ${fillAlpha})`,
  fillOpacity: 1,  // alpha is in color
  color:       `hsl(${hue}, 55%, ${selected ? 70 : 62}%)`,
  weight:      selected ? 2 : hovered ? 1.3 : 0.9,
  lineJoin:    'round',
  opacity:     (selectedId && !selected && !hovered) ? 0.55 : 1,
}
```

### hashHue helper
```js
function hashHue(id) {
  let h = 0;
  const s = String(id);
  for (let i = 0; i < s.length; i++) h = ((h << 5) - h) + s.charCodeAt(i);
  return Math.abs(h) % 360;
}
```

### Capital marker
Cerchio SVG nel layer:
- Non selezionato: `r=2.2; fill=#c0cad6; stroke=#0a0d11; stroke-width=1`
- Selezionato: `r=3.5; fill=var(--accent); stroke=#0a0d11; stroke-width=1`

### Label entità (testo sulla mappa)
`fontFamily: Inter; fontSize: selected ? 11 : 8.5; fill: selected ? #fff : #a0a9b5; fontWeight: selected ? 600 : 400; letterSpacing: 0.4px`. Text in uppercase con `.toUpperCase()` (comportamento invariato se già così).

---

## 6. Detail panel (entità selezionata)

### Struttura
```
ENTITY
Holy Roman Empire          ← Playfair italic 22px
Sacrum Imperium Romanum    ← Playfair italic 11px, muted

─────────────────────────
[====●========] 962—1806   ← life timeline
 4500 BCE         2025

─────────────────────────
PERIOD      962 — 1806
CAPITAL     Wien
CONFIDENCE  0.94 ● confirmed
SOURCE      aourednik/basemaps

[GeoJSON]  [Sources]  [API]
```

### Life timeline
Barra orizzontale 2px che rappresenta l'intera timeline del progetto (-4500 → 2025). Segmento colorato = vita dell'entità. Pallino `var(--accent)` = anno corrente.

### Labels K/V
`text-transform: uppercase; letter-spacing: 0.4px; font-size: 9.5px; color: var(--text-muted);` per la chiave; `font-size: 11.5px; color: var(--text); font-variant-numeric: tabular-nums;` per il valore.

---

## 7. Interazioni

**Tutte invariate rispetto ad ora.** Solo questi micro-tocchi:

- **Hover empire** → stroke leggermente più spesso (1.3px) + fill +20% alpha + tooltip in alto a sinistra con nome, periodo, capitale
- **Click empire** → selected state (vedi §5) + detail panel a destra si apre/aggiorna
- **Hover entity row** in sidebar → background `var(--panel-2)`
- **Drag timeline slider** → aggiorna anno in header + mappa + detail panel in tempo reale (debounce 50ms su render Leaflet se già esiste; altrimenti debounce richiesto)

---

## 8. Responsive

- `>= 1280px`: layout full come descritto
- `768-1279px`: sidebar collassa a 0 con un toggle button in header; detail panel scompare, si apre come modal
- `< 768px`: header stacked (logo + year in riga 1, nav in riga 2), timeline bar in fondo, map full screen, sidebar come drawer

**Non parte del handoff 1** — A+ desktop prima. Mobile è un handoff successivo.

---

## 9. Cosa NON toccare

- **Qualunque file Python** in `src/`
- **Dati GeoJSON** — qualunque cosa in `data/`, `research_output/`, `hf-dataset/`
- **Chiamate API**: `fetch('/v1/entities/...')`, `fetch('/v1/boundaries/...')`, ecc. — le URL, i parametri, la struttura payload rimangono identiche
- **Leaflet init**: `L.map('map', {...})` con opzioni di viewport, zoom min/max, tileLayer → non toccare
- **MCP server** (`mcp-server/`) — fuori scope
- **File backend**: `Dockerfile`, `requirements.txt`, `docker-compose.yml`
- **Confidence scoring, status, boundary data** — sono dati, non stile
- **Naming convention delle entità** — `name_original` resta primary come da CLAUDE.md

---

## 10. Accessibilità

- Contrasto testo normale AAA (4.5:1 minimo) — tutti i `var(--text)` su `var(--bg)` e `var(--panel)` sono verificati
- Focus visible: `outline: 2px solid var(--accent); outline-offset: 2px` su tutti gli elementi interattivi
- Era chip attivo: non solo colore, ma anche underline (due segnali = daltonici compatibili)
- `prefers-reduced-motion`: disabilita transizioni su empire hover

---

## 11. Backward compatibility

- Tutti i selettori CSS esistenti che non vengono ridefiniti continuano a funzionare
- Le class `.leaflet-*` overrides restano come sono
- Light theme tokens vengono aggiornati ma il toggle continua a funzionare
- Tema preferito utente (localStorage) rispettato

---

## 12. File coinvolti (whitelist)

Solo questi file possono essere modificati:

- ✅ `static/index.html` — header markup, font import
- ✅ `static/style.css` — tokens, header, sidebar, timeline, entity rows, detail panel, leaflet overrides esistenti
- ✅ `static/app.js` — SOLO stile layer Leaflet (oggetto `style` / `setStyle`) e creazione label. **Non toccare** fetch, init Leaflet, event handlers, state management, filters logic
- ✅ `static/js/theme.js` — può aggiungere il nuovo accent al toggle light/dark
- ✅ `static/js/sidebar-toggle.js` — può aggiungere behavior collassabile sezioni

Tutto il resto: **blacklist**.

---

## 13. File di riferimento visivo

Nel pacchetto handoff trovi:
- `prototype/A-plus-prototype.html` — prototipo React funzionante (slider, hover, Tweaks)
- `prototype/comparison.html` — before/after side by side
- Screenshot statici in `prototype/screens/`

Claude Code deve aprire `prototype/A-plus-prototype.html` come ground truth visivo e confrontare ogni suo output con quello.
