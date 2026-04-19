# AtlasPI A+ — Handoff Package

Pacchetto pronto per essere usato con **Claude Code desktop** sul repo AtlasPI.

## Come usarlo (workflow completo)

### 1. Setup branch
```bash
cd path/to/AtlasPI
git checkout main
git pull
git checkout -b redesign/aplus-map
```

### 2. Copia questa cartella nel repo
```bash
# Dalla root del tuo progetto design (questo)
cp -r handoff /path/to/AtlasPI/
cd /path/to/AtlasPI
git add handoff/
git commit -m "docs: add A+ redesign handoff package (spec + prototype + QA)"
```

### 3. Apri il prototipo nel browser
```bash
open handoff/prototype/A-plus-prototype.html
```
Questo è la **ground truth visiva**. Tienilo aperto in una finestra a parte mentre Claude Code lavora.

### 4. Apri Claude Code desktop sulla cartella AtlasPI

### 5. Incolla il prompt
Copia il contenuto di `handoff/02-claude-code-prompt.md` (solo il blocco ` ``` ... ``` `) e incollalo come primo messaggio in Claude Code.

### 6. Aspetta la FASE 1 (verifica preliminare)
Claude Code risponderà con un report strutturato A-B-C-D-E. **Non saltare questa fase.** Leggi tutto, discuti le mitigazioni proposte (specialmente in B "Boundary Realism" — confini disputed devono essere visivamente distinti), approva o modifica.

### 7. Dai "OK procedi" e supervisiona la FASE 2
Claude Code farà un commit per sezione. Dopo ogni commit vedrai il diff. Approvi e passa avanti.

### 8. FASE 3 — QA locale
Usa `handoff/03-qa-checklist.md` come checklist. Prima di merge verifica:
- Visual (header, sidebar, timeline, mappa, detail)
- Data safety (Network tab DevTools: API identiche)
- Ethics compliance (ETHICS-XXX scritto, no bias cromatico)

### 9. FASE 4 — Deploy
- PR verso main + review
- Merge
- `bash ~/bin/cra-deploy.sh atlaspi`
- Verifica prod in incognito: https://atlaspi.cra-srl.com/app
- Ripeti checklist visual + data safety in prod
- Smoke test MCP: `curl https://atlaspi.cra-srl.com/v1/entities?limit=5`

### 10. Post-deploy
Dopo 48h guarda `/admin/analytics`: time on map, bounce rate, API call rate.

---

## Contenuto del pacchetto

```
handoff/
├── README.md                       ← questo file
├── 01-visual-spec.md               ← design tokens, sezioni 1-13
├── 02-claude-code-prompt.md        ← prompt da incollare in Claude Code
├── 03-qa-checklist.md              ← checklist per te post-implementazione
└── prototype/
    ├── A-plus-prototype.html       ← prototipo React funzionante (ground truth)
    └── comparison.html             ← before/after side-by-side
```

---

## Rischi e mitigazioni previste

| Rischio | Livello | Mitigazione |
|---|---|---|
| Cambio involontario dati/API | **Critico** | Whitelist file in spec §12, Fase 1-A del prompt verifica esplicita |
| Confini disputed invisibili | Medio | Fase 1-B richiede stroke dashed o pattern distinto |
| Collisioni HSL in aree dense | Medio | Fase 1-B richiede verifica e salt se necessario |
| Rottura test E2E | Basso | Fase 1-D richiede audit preventivo |
| Rottura SEO/meta tags | Basso | Spec non tocca `<head>` meta, solo font-import |
| MCP/API behavioral drift | Critico | Zero touch su src/, verificato in Fase 0 e checklist QA |
| Rollback difficile | Basso | Branch isolato + `docker compose restart` + revert commit |

---

## Ethics note

Il redesign è sotto CLAUDE.md §"Governance etica": qualunque scelta visiva che potrebbe distorcere la rappresentazione storica DEVE essere documentata in `docs/ethics/ETHICS-XXX-redesign-aplus.md`. In particolare:

- La palette HSL per-entity è **arbitraria** (hash dell'ID). Non comunica gerarchie né giudizi storici.
- Nessuna entità ha trattamento preferenziale (stessa scala visiva per imperi coloniali e stati indigeni).
- `name_original` resta primario in tutti i contesti visivi.
- `status=disputed` deve avere un marker visivo distinto (non solo semantico) per onorare la trasparenza dell'incertezza.

---

## Supporto

Se durante il lavoro di Claude Code qualcosa va storto:

1. **Rollback branch locale**: `git checkout main`
2. **Se già deployato**: rollback VPS con `docker compose restart atlaspi`, poi revert commit + redeploy
3. **Dubbio etico**: consulta CLAUDE.md § Governance etica — se dubbi, aggiungi un record in `docs/ethics/` e aspetta review

Buon redesign. 🟠
