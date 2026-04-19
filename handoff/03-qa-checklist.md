# AtlasPI A+ — QA Checklist (per te, utente)

Checklist da seguire **tu** dopo che Claude Code ha finito. Servono 15-20 minuti.

## Pre-merge (branch redesign/aplus-map, locale)

### Visual
- [ ] Header: logo "PI" in ambra (non blu), subtitle "HISTORICAL GEOGRAPHY" in uppercase letter-spaced
- [ ] Anno in header: serif italic grande (~32px), font Playfair Display
- [ ] Era a fianco dell'anno: serif italic ambra uppercase (es. "AGE OF DISCOVERY")
- [ ] Nav header: 4 link testuali (Search, Timeline, Compare, More) — no bottoni bordati
- [ ] "Embed", "API Docs", "OpenAPI", "Language" → dentro "More ⌄"
- [ ] CTA "Ask Claude" ambra (non rosso)
- [ ] Contatore "N on map" con pallino verde

### Sidebar
- [ ] Sezioni: Era aperta, Status aperta, Region chiusa, Overlay chiusa
- [ ] Click su ▾/▸ → collassa/espande correttamente
- [ ] Era chip attivo: testo ambra serif italic con linea sotto (non pillola piena)
- [ ] Era chip non attivo: solo testo grigio
- [ ] Lista "On map" in fondo, scrollabile, conteggio live

### Timeline bar
- [ ] Altezza 60px (più alta di prima)
- [ ] Sopra lo slider: tick delle ere (Bronze, Classical, Medieval, ...)
- [ ] Era attiva nel tick: serif italic ambra
- [ ] Slider thumb ambra con doppia ombra
- [ ] A destra: anno in serif italic ambra (es. "1500" grande + "CE" piccolo grigio)
- [ ] Play button cerchio ambra

### Mappa
- [ ] Confini con fill più tenue (28%)
- [ ] Stroke più sottile (0.9px)
- [ ] Colori diversi per entità diverse (HSL per-ID)
- [ ] Click su impero → fill più intenso, stroke più spesso, altri imperi attenuati al 55%
- [ ] Hover → tooltip in alto a sinistra con nome, periodo, capitale
- [ ] Capital dot: grigio → ambra quando selezionato
- [ ] Imperi con `status=disputed` visivamente distinti (stroke dashed o pattern) ⚠️ importante

### Detail panel (destra, quando cliccato)
- [ ] Nome entità in serif italic grande
- [ ] Nome latino in serif italic piccolo grigio
- [ ] Life timeline (barra con segmento colorato + pallino anno corrente)
- [ ] K/V rows (PERIOD, CAPITAL, CONFIDENCE, SOURCE) con labels uppercase piccole
- [ ] Bottoni in fondo: GeoJSON, Sources, API

### Tema
- [ ] Dark (default): palette warm #0f1318
- [ ] Light: toggle funziona, colori coerenti, Playfair ancora applicato
- [ ] Preferenza salvata in localStorage

### Responsive
- [ ] 1440px: tutto visibile, nessun overflow
- [ ] 1280px: tutto visibile
- [ ] 1024px: sidebar può collassare, detail panel a modal (o scompare elegantemente)
- [ ] 768px: mobile layout (non scope di questo handoff, ma verifica che non sia rotto)

---

## Data safety (conferma ZERO cambi funzionali)

Apri DevTools → Network tab, trascina la timeline da 500 a 1500 e verifica:

- [ ] URL delle call API identiche a prima: `/v1/entities?year_start=...`, `/v1/boundaries/...`
- [ ] Payload response struttura identica (stessi campi)
- [ ] Numero di imperi mostrati a un dato anno = uguale a produzione
- [ ] Cliccando su un impero, `name_original`, `confidence_score`, `status`, sono invariati
- [ ] Confini geografici sulla mappa = identici a produzione (stesso shape)

Se qualcosa è cambiato oltre la presentazione → STOP, non deployare.

---

## Ethics compliance

- [ ] Nessun colore "speciale" per potenze coloniali vs indigene
- [ ] Imperi conquistati e conquistatori usano la stessa scala visiva
- [ ] `name_original` resta il nome primario (non spostato in secondary)
- [ ] ETHICS-XXX record presente in `docs/ethics/` con motivazioni del redesign
- [ ] ADR presente in `docs/adr/` con scelte tecniche (palette, tipografia)

---

## Performance

Lighthouse su Chrome (locale):
- [ ] Performance >= 85 (era ~80 in prod? Non deve peggiorare)
- [ ] Accessibility >= 95
- [ ] Best Practices >= 95
- [ ] Playfair Display caricato con `display=swap` (no FOIT)
- [ ] First Contentful Paint < 1.5s
- [ ] Cumulative Layout Shift < 0.1

---

## Test

- [ ] `pytest tests/ -v` tutto verde
- [ ] `ruff check src/ tests/` nessun warning nuovo
- [ ] Console browser: zero errori JS, zero warning 404

---

## Git hygiene

- [ ] Branch `redesign/aplus-map`
- [ ] Commit separati per sezione (7-8 commit max)
- [ ] Nessun file fuori whitelist modificato
- [ ] ROADMAP.md aggiornato
- [ ] CHANGELOG.md aggiornato
- [ ] PR con descrizione completa + screenshot before/after

---

## Deploy

- [ ] Merge in main
- [ ] `bash ~/bin/cra-deploy.sh atlaspi`
- [ ] Attesa ~2 min per docker build + restart
- [ ] Apri https://atlaspi.cra-srl.com/app in incognito (no cache)
- [ ] Ripeti sezione "Visual" (top di questa checklist) in prod
- [ ] Ripeti sezione "Data safety" in prod
- [ ] Test con agente (chiama /v1/entities via curl) — risposta identica

Se qualcosa è rotto in prod:
```bash
ssh -i ~/.ssh/cra_vps root@77.81.229.242 "cd /opt/cra && docker compose restart atlaspi"
```

Se resta rotto:
```bash
git revert <commit-hash>
git push origin main
bash ~/bin/cra-deploy.sh atlaspi
```

---

## Smoke test MCP

Dato che gli agenti AI sono target primary, verifica che MCP sia intatto:

- [ ] `curl https://atlaspi.cra-srl.com/v1/entities?limit=5` → JSON valido
- [ ] `curl https://atlaspi.cra-srl.com/v1/boundaries/1` → GeoJSON valido
- [ ] Testa tool MCP da Claude Desktop se configurato: `search_entities("roman")`

Se tutto qui è ok, il redesign è invisibile agli agenti (obiettivo raggiunto).

---

## Post-deploy analytics

Dopo 48h, verifica su `/admin/analytics`:

- [ ] Time on map aumentato (umani restano più a lungo)
- [ ] Bounce rate dal /app non peggiorato
- [ ] API call rate invariato (agenti non toccati)
- [ ] Nessun 5xx spike
