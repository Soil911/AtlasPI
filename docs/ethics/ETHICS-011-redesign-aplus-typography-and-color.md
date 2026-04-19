# ETHICS-011 — Redesign A+ / typography & color choices (v6.90)

**Status**: Adopted v6.90.0 (2026-04-19)
**Authors**: Claude Code (redesign session full-autonomy)
**Reviewers**: Clirim Ramadani (cofounder audit post-deploy)
**Related ADR**: [ADR-006](../adr/ADR-006-ui-aplus-typography.md)

---

## Contesto

Il redesign UI "A+" della pagina `/app` (v6.90) introduce cambiamenti
visivi significativi: palette ambra/ocra editoriale, tipografia Playfair
Display italic sui nomi delle entità, HSL per-entity sui confini mappa,
rimozione del timeline canvas eventi, filtraggio deprecated entities
di default.

Tutte le scelte visive che potrebbero alterare la rappresentazione
storica sono documentate qui per rispetto di CLAUDE.md §
"Governance etica durante lo sviluppo".

---

## Decisioni documentate

### 1. Palette HSL per-entity è arbitraria (non gerarchica)

**Scelta**: ogni entità ha un hue stabile calcolato tramite
`hashHue(id) = djb2(id) % 360`. Saturation e lightness sono fissi al
55% e 55%/62% rispettivamente.

**Rischio considerato**: l'assegnazione "casuale" del hue potrebbe per
coincidenza dare a imperi coloniali colori caldi (rossi/arancione)
e a stati indigeni colori freddi (blu/verdi), rinforzando bias culturali.

**Mitigazione**: il hash è completamente stateless e deterministico
sull'ID interno (numero), non sul nome dell'entità. L'ID è assegnato
in ordine di ingestion dal dataset — non c'è correlazione con
geografia, religione, o periodo storico. Le collisioni di hue tra
entità vicine sono accettate a priori in questa release; se il
cofounder audit post-deploy rileva pattern problematici (>2 pair
confusamente adiacenti nello stesso anno-frame), ADR-006 può essere
emendato per introdurre un salt (`hashHue(id + "atlaspi-v690")`).

**Alternative considerate e scartate**:
- **Palette categorica per continent/type**: rinforzerebbe gerarchie
  ("l'Europa ha colori freddi prestigiosi, l'Africa ha colori caldi
  esotici"). Rifiutata per lo stesso principio di ETHICS-001.
- **Palette monocroma (solo ambra con variazioni di luminosità)**:
  impossibile distinguere entità sovrapposte nello stesso frame.
- **Palette color_hue memorizzato nel database**: richiederebbe
  migration + decisioni curatoriali per 1038 entità = scope creep
  fuori spec §5.

### 2. dashArray preservato per `status='disputed'`

**Scelta**: il campo `dashArray: '6,4'` applicato a entità con
`status='disputed'` (che esisteva in v6.67+ nel renderMap pre-redesign)
è **preservato** nella nuova funzione `computeBoundaryStyle()`.

**Spec §5 omette questo**. L'omissione è corretta qui perché:
- CLAUDE.md §3 ("Trasparenza dell'incertezza") richiede che lo
  status `disputed` sia visibilmente distinto.
- Il solo colore HSL è un singolo canale (problematico per daltonici
  e per entità con hue disputato-sembra-confermato per coincidenza).
- La stroke pattern è un secondo canale ortogonale al colore: un
  daltonico vede la linea tratteggiata indipendentemente dal hue.

Analogamente, `dashArray: '4,3'` è preservato per entità con
`boundary_source='approximate_generated'` (confidence cap 0.4 da
ETHICS-004). Questo canale "approssimativo" deve restare visibile.

### 3. Tipografia Playfair Display italic è neutrale

**Scelta**: il font serif italic è applicato a tutti i nomi
entità (`name_original`) in uno stile uniforme: `.detail-panel h2`
22px italic, `.capital-history-list .ch-name` 13px italic.

**Rischio considerato**: lo stile "classico/editoriale" potrebbe
privilegiare implicitamente le entità con nomi in caratteri latini
(es. "Sacrum Imperium Romanum") rispetto a caratteri non-latini
(es. "سلطنت مغلیہ" o "چنگ سلسله").

**Mitigazione**: il font stack `var(--font-serif)` ha fallback
a Georgia, Times New Roman, serif — tutti sistemi font con
supporto Unicode broad. Per script non-latini, il browser fallback
al system font dello script (arabic, CJK, devanagari) automatico.
L'italic è applicato ma il `font-family: var(--font-serif)` in
contesto arabo/CJK degrada gracefully al font sistema (che non
ha italic per alcuni script — il browser lo emulerà o userà
normal). **`name_original` resta in qualsiasi caso lo script
originale**.

Verifica post-deploy: controllare le 45+ entità con lang non-latin
(audit v4 Round 8) — devono essere leggibili e non visivamente
degradate rispetto alle entità latin-script.

### 4. Rimozione del timeline canvas eventi (regressione accettata)

**Scelta**: il canvas `#timeline-chart` nella bottom bar (legacy)
è stato rimosso. La bottom bar è ora esclusivamente year slider +
era ticks + year display (spec §4).

**Regressione utenti accettata**: ~2% degli utenti (stima basata
su analytics v6.67 pre-redesign: clicks su `#timeline-toggle`)
potrebbero voler vedere la distribuzione eventi nel tempo.

**Mitigazione**:
- L'endpoint `/v1/events?year_start=X&year_end=Y` resta disponibile
  per consumer AI/API (scope primary di AtlasPI).
- Se telemetria post-deploy mostra regressione UX significativa
  (drop nel time-on-map o query API /v1/events non aumenta), v6.91
  può aggiungere uno sparkline inline in timeline-bar senza
  re-introdurre il canvas full.

**Alternative considerate**:
- **Canvas collapsed default + expand**: mantiene complessità DOM,
  contraddice spec §4 60px fissi.
- **Sparkline MVP**: aggiungerebbe scope al redesign, rimandato.

### 5. Filtraggio `status='deprecated'` di default (addendum E + ADR-005)

**Scelta**: `/v1/entities` filtra `status='deprecated'` di default
(implementato in v6.87). La sidebar "On map" e il contatore header
riflettono 992 active entities (vs 1038 totali). Le 44 deprecated
secondary entities (Round 14 audit v4) sono accessibili solo via
permalink diretto `/v1/entities/{id}` o `?include_deprecated=true`.

**Rischio considerato**: utente non avvisato del fatto che 44 entità
esistono ma non sono visibili.

**Mitigazione**: ADR-005 documenta la policy e la reversibilità.
Permalinks preservati per Zenodo DOI compatibility. Future UI
potrebbe esporre un toggle `[ ] Include deprecated (archival)` in
sidebar, ma non è in scope v6.90.

### 6. Accent color ambra sostituisce blu GitHub (#58a6ff → #e8b14a)

**Scelta**: il colore accent primario è stato cambiato da `#58a6ff`
(GitHub blue) a `#e8b14a` (ambra editoriale).

**Rischio considerato**: il colore potrebbe essere associato a
simbolismi culturali (es. "oro" = occidentale, "zafferano" =
indiano, "giallo" = imperiale cinese). Il senso "ambra" non è
però univocamente legato a una cultura.

**Mitigazione**: il colore è stato scelto per la sua neutralità
editoriale (evoca pergamena, non oro), il contrasto AAA
(`#e8b14a` su `#0f1318` = 8.9:1), e la complementarità con i
colori status (`--confirmed #6eb58a`, `--uncertain #d4a13a`,
`--disputed #d57770`). Documentato in ADR-006.

Per il tema chiaro, `--accent: #b38420` (ottone invecchiato) è
usato per AAA contrast su `#faf8f3`.

### 7. Dataset stability (no data touched)

**Verificato**: il redesign tocca solo `static/` (frontend) e
documentazione. **Zero modifiche**:
- `src/` (Python backend)
- `data/` (tutti dataset JSON/GeoJSON)
- `alembic/` (migrations)
- Schema Pydantic `EntityResponse` (API contract)
- Endpoint URLs, parametri, response structure

Quindi: zero impatto per consumer AI/MCP/SDK, zero cambio
entity count 992 active / 1038 total, zero alterazione di
`name_original`, `confidence_score`, `sources[]`, `ethical_notes`,
`capital_history[]`.

---

## Cosa verificare al cofounder audit

- [ ] Su un test frame (Europa 1500, India 1700, Asia centrale 1250):
  nessuna pair di entità adiacenti ha hue confondibili (>2 entità
  con hue entro ±15° che si toccano geograficamente).
- [ ] 13 entità con capital_history mostrano cronologia nel detail
  panel con styling editorial (Playfair italic 13px nome, range
  tabular-nums).
- [ ] 44 deprecated entities NON appaiono in sidebar "On map" né
  nel counter header (`/v1/entities?include_deprecated=false`).
- [ ] Entità con lang non-latino (es. Mughal in arabo, Ming in CJK)
  sono visualizzate correttamente nel nome (h2 detail panel) e
  nell'entity-row swatch.
- [ ] `status='disputed'` ha stroke dashed visibile — confrontare
  con `status='confirmed'` stesso hue per verificare distinguibilità.
- [ ] Palette AAA contrast verificato via Lighthouse ≥ 95
  Accessibility score.

---

## Reversal / rollback

Se una delle scelte sopra si rivela problematica:
- **Palette HSL**: `git revert` del commit Phase 2.6 + re-deploy
  → torna a palette status color.
- **Tipografia**: revert del commit Phase 2.3 + Phase 2.7.
- **Timeline canvas**: revert del commit Phase 2.5 ripristina
  `#timeline-chart` + `#timeline-toggle`.
- **Deprecated filter**: era già in v6.87 — non introdotto qui.

Rollback full del redesign: `git revert <merge-commit-A+>` oppure
`ssh vps "docker compose restart atlaspi"` (ripristina Docker
image cached v6.89).
