# AtlasPI — Prompt per Claude Code (Sessione "Redesign Mappa A+")

> Copia tutto il blocco seguente e incollalo come **primo messaggio** in Claude Code desktop, aperto sulla cartella del repo AtlasPI.

---

## 📋 Prompt da incollare

```
Ciao. Devi implementare il redesign UI "A+" della pagina mappa di AtlasPI
(static/index.html → la pagina /app).

PRIMA DI TOCCARE QUALUNQUE FILE devi fare una FASE DI VERIFICA PRELIMINARE
e ottenere il mio OK esplicito. Non saltare questa fase.

═══════════════════════════════════════════════════════════════════
FASE 0 — Contesto del progetto
═══════════════════════════════════════════════════════════════════

Leggi nell'ordine:
1. CLAUDE.md (valori fondamentali, convenzioni etiche)
2. ROADMAP.md (dove si inserisce questa modifica)
3. CHANGELOG.md (versione corrente)
4. handoff/01-visual-spec.md (la spec completa del redesign)
5. handoff/prototype/A-plus-prototype.html (riferimento visivo funzionante)
   — apri anche nel browser per vedere comportamento interattivo
6. handoff/prototype/comparison.html (before/after)

Poi leggi i file che modificherai:
- static/index.html
- static/style.css (focus su :root, header, sidebar, timeline, leaflet overrides)
- static/app.js (solo sezioni rendering layer + init Leaflet)
- static/js/theme.js
- static/js/sidebar-toggle.js

═══════════════════════════════════════════════════════════════════
FASE 1 — VERIFICA PRELIMINARE OBBLIGATORIA (stop and confirm)
═══════════════════════════════════════════════════════════════════

Devi verificare e riportarmi in un messaggio strutturato:

A) DATA SAFETY — i rischi ZERO che voglio confermati
   Controlla che il redesign NON:
   - cambi in alcun modo i dati dei confini (boundary_geojson)
   - alteri name_original, confidence_score, status, sources[], acquisition_method
   - tocchi endpoint API (GET /v1/entities, /v1/boundaries, ecc.)
   - modifichi la logica di filtro per year_start/year_end
   - introduca bias visivi che cancellino l'incertezza (es: disputed che
     sembra confirmed per coincidenza di colore)
   - alteri la gerarchia etica dei nomi (original > colonial) definita
     in CLAUDE.md §"Nessun bias geografico"

   Riporta: "DATA SAFETY: ✅ confermato / ⚠️ rischi rilevati: ..."

B) BOUNDARY REALISM — il rischio cartografico
   Il nuovo stile layer Leaflet usa:
   - HSL per-entity con hash(id) → hue stabile ma arbitrario per entità
   - fill alpha 0.28 (tenue)
   - stroke 0.9px (sottile)
   
   Verifica che con questi parametri:
   1. Confini sovrapposti restino leggibili (es: Impero Bizantino dentro
      area dell'Ottomano dopo 1453 — devono essere distinguibili)
   2. Confidence visiva: entità con confidence < 0.5 (status=disputed)
      abbiano un marker visivo distinto (es: stroke dashed, non solo colore)
   3. Hash HSL non generi collisioni in aree dense (Europa medievale,
      India mughal, Asia centrale) — suggerisci salt se trovi collisioni
   4. Il fill alpha 0.28 non renda invisibili le entità piccole (city-states,
      principati) su base mappa dark #0a0d11
   
   Per ogni rischio rilevato proponi una mitigazione e chiedi la mia approvazione
   PRIMA di implementare. Non decidere da solo.

C) ETHICS COMPLIANCE (CLAUDE.md §"Governance etica")
   Se qualsiasi scelta tipografica, coloristica o di layout può alterare
   la rappresentazione storica (esempio: colore warm "premium" a imperi
   coloniali, colore cool "neutro" agli stati indigeni), fermati, scrivi
   un record in docs/ethics/ETHICS-XXX-redesign-aplus.md, e chiedi
   approvazione.

D) TESTING IMPACT
   Lista i test che potrebbero rompersi (es: selettori CSS nei test E2E,
   data-test-id attuali, screenshot diff). Per ognuno proponi: "modifico
   il test", "modifico l'UI per preservare il selettore", o "il test è
   obsoleto, lo rimuovo con motivazione".

E) RIEPILOGO PIANO
   Lista ordinata dei cambi concreti che farai, file per file, senza
   ancora applicarli. Formato:
   
   [ ] static/style.css:12-45 → aggiungi nuovi token palette
   [ ] static/style.css:400-480 → refactor header
   [ ] static/index.html:45-80 → nuovo markup header + year hero
   ...

QUANDO HAI COMPLETATO A-B-C-D-E, FERMATI.
Rispondi con il report e aspetta il mio "OK procedi" o "modifica X".

═══════════════════════════════════════════════════════════════════
FASE 2 — Implementazione (solo dopo il mio OK)
═══════════════════════════════════════════════════════════════════

Segui handoff/01-visual-spec.md alla lettera, sezione per sezione
(§1 tokens → §2 header → §3 sidebar → §4 timeline → §5 layer Leaflet
→ §6 detail panel → §7 interazioni → §10 a11y).

Vincoli di processo:
- Lavora su branch `redesign/aplus-map` (già creato; se non esiste, crealo)
- Un commit per sezione, messaggi tipo:
    feat(ui): new design tokens for A+ redesign (spec §1)
    feat(ui): year hero + simplified header (spec §2)
    feat(ui): collapsible sidebar sections (spec §3)
    feat(ui): timeline with era ticks (spec §4)
    style(map): HSL per-entity boundary rendering (spec §5)
    feat(ui): detail panel editorial typography (spec §6)
    a11y: focus states, reduced-motion, contrast AAA (spec §10)
- NON toccare alcun file fuori dalla whitelist di spec §12
- Aggiorna ROADMAP.md (nuova sezione "v6.8X — UI redesign A+")
- Aggiorna CHANGELOG.md con bullet list dei cambi
- Aggiungi ADR in docs/adr/ADR-XXX-ui-redesign-aplus.md che spiega
  le scelte tipografiche ed etiche

Dopo ogni commit, mostrami il diff principale e aspetta conferma prima
di passare alla sezione successiva. NON fare il redesign intero in una
sola volta.

═══════════════════════════════════════════════════════════════════
FASE 3 — QA locale
═══════════════════════════════════════════════════════════════════

Prima di propormi il deploy:

1. Run backend: `python run.py` → http://127.0.0.1:10100/app
2. Apri affiancato handoff/prototype/A-plus-prototype.html
3. Verifica visivamente:
   - Header (logo amber, year hero serif italic, 4 link, CTA amber)
   - Sidebar (sezioni collassabili, era chips con underline, entity list)
   - Timeline (60px, era ticks sopra slider, anno a destra in serif)
   - Mappa (confini HSL, capital markers, labels)
   - Detail panel (nome in serif, life timeline, K/V rows)
4. Test interattivi:
   - Drag slider → anno header aggiorna live
   - Click empire → detail panel popolato, altri attenuati
   - Hover empire → tooltip, stroke più spesso
   - Toggle theme light/dark → tutto coerente
   - Resize 1280px / 1024px / 768px → niente overflow
5. Run tests: `pytest tests/ -v` e `ruff check src/ tests/`
   — se tests E2E falliscono, applica le mitigation concordate in Fase 1-D
6. Lighthouse locale (Performance, Accessibility) → report score

Mostrami screenshot + output test prima di andare in fase Deploy.

═══════════════════════════════════════════════════════════════════
FASE 4 — Deploy (solo su mio OK finale)
═══════════════════════════════════════════════════════════════════

1. Push branch: `git push origin redesign/aplus-map`
2. Apri PR verso main con descrizione completa (vedi template sotto)
3. Merge solo dopo mia review
4. Deploy: `bash ~/bin/cra-deploy.sh atlaspi`
5. Verifica prod: https://atlaspi.cra-srl.com/app
6. Rollback plan (tienilo pronto):
   - `ssh -i ~/.ssh/cra_vps root@77.81.229.242 "cd /opt/cra && docker compose restart atlaspi"`
   - O revert del commit su main + redeploy

Template PR description:
---
## v6.8X — UI Redesign A+ (mappa)

Redesign UI layer della pagina /app. Solo presentazione, zero cambi
funzionali/API/dati.

### Cambia
- Palette: warm dark (#0f1318), accent ambra (#e8b14a)
- Tipografia: Playfair Display italic per year hero, era attive, nomi entità in detail
- Header: da 7 bottoni a 4 link + year hero + CTA singola
- Sidebar: sezioni collassabili, era chips underline
- Timeline: 60px con era ticks sopra slider
- Mappa: HSL per-entity boundary style, fill tenue, stroke sottile
- Detail panel: editorial typography + life timeline

### Non cambia
- Tutti i dati (boundary_geojson, name_original, confidence_score, ...)
- Tutti gli endpoint API
- MCP server, SDK
- Logica Leaflet (solo stile layer)

### Spec
- handoff/01-visual-spec.md
- handoff/prototype/A-plus-prototype.html (ground truth visiva)

### Test
- pytest ✅ (screenshot attached)
- ruff ✅
- Lighthouse: Perf NN, A11y NN
- Theme light/dark ✅
- Responsive 1280/1024 ✅

### Rollback
`docker compose restart atlaspi` su VPS o revert commit.
---

═══════════════════════════════════════════════════════════════════
REGOLE OPERATIVE RICORDATI SEMPRE
═══════════════════════════════════════════════════════════════════

1. Ferma ogni fase e aspetta il mio OK esplicito prima di procedere
2. Rispetta CLAUDE.md — se scelta tecnica impatta rappresentazione
   storica, ETICS record obbligatorio
3. Whitelist file = spec §12. Tutto il resto = NON TOCCARE
4. I dati sono sacri. L'UI è fluida. Se dubiti, chiedi.
5. Un commit per sezione. Niente mega-commit.
6. Non deployare senza mia approvazione finale.

Inizia dalla FASE 0. Leggi, mappa, poi rispondi con la VERIFICA PRELIMINARE.
```

---

## Note per te (non copiare in Claude Code)

- **Quando Claude Code risponde alla Fase 1**, leggi attentamente il suo report A-B-C-D-E. Se in B (boundary realism) propone mitigazioni, discutile con lui. Comuni:
  - Salt per hashHue se rileva collisioni → OK approvalo
  - Stroke dashed per `status=disputed` → **OK approvalo**, è importante per l'onestà cartografica
  - Alpha > 0.28 per entità piccole → OK se non compromette leggibilità sovrapposizioni
- **Se chiede di scrivere ETHICS-XXX** → lascialo fare. Sono 5 minuti, ti protegge.
- **Durante la Fase 2**, chiedi sempre di vederti il diff prima del commit successivo. Se qualcosa ti suona strano, ferma.
- **Sul deploy**, non fidarti della sua stima di "funziona": apri tu atlaspi.cra-srl.com/app in incognito DOPO il deploy e verifica header + timeline + mappa. Se vedi qualcosa di strano → rollback immediato.
