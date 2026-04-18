# AtlasPI — Handoff Sessione Audit v4 (Fase A + B)

**Creato**: 2026-04-18 (post-v6.68.0)
**Autore**: Sessione precedente Claude Code
**Destinatario**: Sessione Claude Code successiva
**Scope**: eseguire Fase A (Wikidata Q-ID bootstrap) + Fase B (automated drift detection) autonomamente

---

## TL;DR

Il DB AtlasPI ha 1034 entità storiche. Finora abbiamo auditato 20 entità manualmente contro fonti accademiche (audit v2 Agent 04) e trovato 45% error rate su MED+HIGH. Estrapolando: potenzialmente ~400 entità con problemi nel long-tail. Il manual audit non scala.

**Soluzione**: cross-reference sistematico con Wikidata.
- **Fase A (v6.69)**: a ogni entità AtlasPI associa un Wikidata Q-ID via fuzzy match (name + year + type). Target ≥80% auto-match high-confidence.
- **Fase B (v6.70)**: per ogni entità con Q-ID, fetcha Wikidata properties (P571 inception, P576 dissolved, P36 capital) e genera diff report + auto-patches per discrepanze banali.

Output: AtlasPI passa da "audit periodico manuale costoso" a "drift detection automatico nightly zero-cost".

---

## Stato attuale (baseline)

### Dataset al 2026-04-18 (v6.68.0 live)

```
entities:  1034
events:    643
rulers:    105
languages: 29
sites:     1249
routes:    41
chains:    94
cities:    110
periods:   55
```

### Deploy produzione

- **URL live**: https://atlaspi.cra-srl.com
- **VPS**: Aruba `77.81.229.242` (Ubuntu + Docker)
- **Stack**: FastAPI + PostgreSQL + PostGIS + Redis
- **SSH**: `~/.ssh/cra_vps` autorizzata come root
- **Repo**: `Soil911/AtlasPI` branch `main`
- **Deploy comando**: `bash ~/bin/cra-deploy.sh atlaspi`
- **Healthcheck**: `curl https://atlaspi.cra-srl.com/health`

### Convenzioni progetto (da CLAUDE.md)

- **Lingua codice**: inglese
- **Lingua documentazione**: italiano
- **ETHICS comments**: `# ETHICS:` sulle funzioni che toccano dati sensibili
- **Versioni**: progressive v6.X.Y, bump con CHANGELOG entry
- **Migrations**: Alembic autogenerate, girano allo startup container
- **Testi**: pytest, test files in `tests/`
- **Native script names**: CLAUDE.md ETHICS-001 prescrive `name_original` in lingua locale

### Tool esistenti da riusare (NON riscrivere)

- **`scripts/apply_data_patch.py`** — unified patch applier con whitelist, null guard, idempotent, transactional, dry-run. Usalo per applicare patches. Whitelist in `PATCHABLE_FIELDS` — se serve aggiungere `wikidata_qid` alla whitelist, fallo.
- **`src/api/routes/entities.py::_get_continent()`** — classificazione continent runtime, già corretta in v6.67 (Iran bug).
- **`src/ingestion/fix_antimeridian_and_wrong_polygons.py`** — fix geometric bug.

### Stato audit precedenti (NON ri-auditare)

- `research_output/audit_v2/agent_04_external_accuracy.json` — 20 entità già auditate. Skip queste nel campione Fase A sanity check.
- Entità già toccate da patch v6.66: ruler 14/17/18/84/85/86/97, entity 27/46/52/55/76/99/108/130/147/170/177/193/230/602.
- ETHICS-009 Aotearoa già creato.

---

## Fase A — Wikidata Q-ID bootstrap

### Goal

Per ogni entità AtlasPI in `geo_entities`, trovare il Wikidata Q-ID corrispondente (quando esiste) e salvarlo nel nuovo campo `wikidata_qid`.

### Target

- ≥800/1034 (77%) matchate auto-high-confidence (score ≥ 0.85)
- ~100-200 flagged per review manuale (0.5 ≤ score < 0.85)
- ~30-80 no-match (score < 0.5 o Wikidata non ha il concetto)

### Task 1 — Alembic migration

Crea migration `alembic/versions/XXX_add_wikidata_qid.py`:

```python
def upgrade():
    op.add_column(
        'geo_entities',
        sa.Column('wikidata_qid', sa.String(20), nullable=True),
    )
    op.create_index(
        'ix_geo_entities_wikidata_qid',
        'geo_entities',
        ['wikidata_qid'],
    )

def downgrade():
    op.drop_index('ix_geo_entities_wikidata_qid')
    op.drop_column('geo_entities', 'wikidata_qid')
```

Aggiungi colonna anche al model `src/db/models.py::GeoEntity`.

### Task 2 — Script bootstrap

**File**: `scripts/wikidata_bootstrap.py`

Strategia matching per ogni entità AtlasPI:

1. **Query SPARQL con label search**:
   - Prova `name_original` in `name_original_lang`
   - Prova `name_english` (da name_variants dove `lang='en'`)
   - Prova tutti i `name_variants`

2. **Filtra per tipo** (P31 instance_of):
   - empire → Q34770 (historical country) OR Q48349 (empire)
   - kingdom → Q417175 OR Q34770
   - city-state → Q133442 OR Q34770
   - sultanate → Q34770
   - confederation → Q34770
   - tribe → Q41710
   - caliphate → Q34770
   - khanate → Q34770
   - republic → Q7270 (republic) OR Q34770

3. **Verify year overlap** (P571 inception + P576 dissolved):
   - Fetch P571 year da Wikidata result
   - Overlap score = |AtlasPI.year_start - Wikidata.P571| ≤ 10y → +0.3
   - Stessa logica per year_end/P576

4. **Confidence scoring**:
   ```
   score = 0
   if exact_label_match: score += 0.5
   if fuzzy_label_match (>0.85): score += 0.3
   if type_consistent: score += 0.2
   if year_start_diff <= 10: score += 0.2
   if year_end_diff <= 10: score += 0.1
   
   # Penalizzazioni
   if multiple_candidates_same_score: score -= 0.15  # ambiguo
   ```

5. **Output per ogni entità**:
   ```json
   {
     "entity_id": 1,
     "name_original": "Imperium Romanum",
     "wikidata_qid": "Q2277",
     "wikidata_label": "Roman Empire",
     "score": 0.95,
     "match_reasons": ["exact_label", "type_consistent", "year_start=27"],
     "review_needed": false
   }
   ```

### Task 3 — Rate limit + caching

- Wikidata SPARQL: max 1 query/sec (ufficiale), usa `User-Agent: AtlasPI/6.69 (https://atlaspi.cra-srl.com)` per salire a 5/sec
- Cache risposte in `scripts/wikidata_cache/{entity_id}.json` (evita ri-interrogare Wikidata su re-run)
- Total: 1034 entità * 1 query/sec = ~17 min per run completo + eventuali retry

### Task 4 — Query SPARQL esempio

```python
import requests

SPARQL = "https://query.wikidata.org/sparql"
UA = "AtlasPI/6.69 (https://atlaspi.cra-srl.com; contact@cra-srl.com)"

def search_by_label(label: str, lang: str = "en", limit: int = 10):
    """Cerca entità Wikidata per label + historical country instance."""
    query = f"""
    SELECT ?item ?itemLabel ?inception ?dissolved ?typeLabel WHERE {{
      ?item rdfs:label "{label}"@{lang} .
      ?item wdt:P31 ?type .
      VALUES ?type {{ wd:Q34770 wd:Q48349 wd:Q417175 wd:Q133442 wd:Q41710 wd:Q7270 }}
      OPTIONAL {{ ?item wdt:P571 ?inception }}
      OPTIONAL {{ ?item wdt:P576 ?dissolved }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
    }}
    LIMIT {limit}
    """
    r = requests.get(
        SPARQL,
        params={"query": query, "format": "json"},
        headers={"User-Agent": UA, "Accept": "application/sparql-results+json"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["results"]["bindings"]
```

### Task 5 — Applica i match high-confidence

Via `scripts/apply_data_patch.py`:

- Aggiungi `wikidata_qid` alla whitelist `PATCHABLE_FIELDS["entity"]`
- Genera patch file `data/wikidata/v669_qid_high_confidence.json` con entity_id + wikidata_qid per score ≥ 0.85
- Applica in prod via ssh + docker exec
- Redis flush post-apply

### Task 6 — Report

Scrivi `research_output/audit_v4/fase_a_report.md`:

- Stats: N high-conf auto-applied / N flagged review / N no-match
- Distribuzione score histogram
- Top 20 ambigui per review manuale (con candidati alternativi)
- Entità "famose" che hanno fallito il match (eye-test)

### Task 7 — Deploy v6.69

- Version bump 6.68.0 → 6.69.0
- CHANGELOG entry
- Commit + tag + push + `bash ~/bin/cra-deploy.sh atlaspi`
- Verifica: `curl https://atlaspi.cra-srl.com/v1/entities/1` → ha `wikidata_qid: "Q2277"` nel response? (Se sì, esponi il campo nel schema Pydantic `EntityResponse` in `src/api/schemas.py`)

---

## Fase B — Automated drift detection

### Goal

Per ogni entità AtlasPI con `wikidata_qid` non-null, confronta i campi chiave contro Wikidata e genera:
1. Report `wikidata_diff_report.md` delle discrepanze
2. Patch JSON con fix autofixable (bug banali)

### Task 1 — Script drift check

**File**: `scripts/wikidata_drift_check.py`

Per ogni entità con QID:

```python
def check_entity(entity_id: int, qid: str) -> dict:
    wd = fetch_wikidata_entity(qid)  # uses wbgetentities API
    diffs = []
    
    # Year check (P571 inception)
    wd_inception = extract_year(wd.get("P571"))
    if wd_inception is not None and abs(atlas.year_start - wd_inception) > 10:
        diffs.append({
            "field": "year_start",
            "atlas_value": atlas.year_start,
            "wikidata_value": wd_inception,
            "delta": atlas.year_start - wd_inception,
            "severity": "HIGH" if abs(delta) > 50 else "MED",
        })
    
    # Year check (P576 dissolved)
    # ... similar
    
    # Capital check (P36)
    wd_capital_qid = wd.get("P36")
    if wd_capital_qid and atlas.capital_name:
        wd_capital = fetch_wikidata_entity(wd_capital_qid)
        if not labels_match(atlas.capital_name, wd_capital["labels"]):
            diffs.append({
                "field": "capital_name",
                "atlas_value": atlas.capital_name,
                "wikidata_value": wd_capital["labels"],
                "severity": "MED",
            })
        # Geographic check via P625 coordinate
        wd_coord = wd_capital.get("P625")
        if wd_coord:
            km_diff = haversine(atlas.capital_lat, atlas.capital_lon, wd_coord.lat, wd_coord.lon)
            if km_diff > 50:
                diffs.append({
                    "field": "capital_coord",
                    "atlas_value": f"{atlas.capital_lat},{atlas.capital_lon}",
                    "wikidata_value": f"{wd_coord.lat},{wd_coord.lon}",
                    "km_difference": km_diff,
                    "severity": "HIGH" if km_diff > 200 else "MED",
                })
    
    return {"entity_id": entity_id, "qid": qid, "diffs": diffs}
```

### Task 2 — Classificazione & autofix

Regole per autofix (applica senza review):
- `year_start` diff ≤ 5y → lascia AtlasPI (errore piccolo, potrebbe essere convention AtlasPI preferita)
- `year_start` diff 5-20y → **FLAG for review** (non auto)
- `year_start` diff > 20y → **FLAG HIGH** (come Cahokia 600→1050)
- `capital_coord` diff < 10km → lascia AtlasPI (precisione diversa ok)
- `capital_coord` diff 10-50km → **FLAG for review**
- `capital_coord` diff > 50km → **FLAG HIGH**

**NIENTE autofix automatico sulle date**. Wikidata e AtlasPI possono avere convention diverse (es. Roman Empire year_start: 27 BCE AtlasPI vs 753 BCE Wikidata "Kingdom of Rome inclusivo"). Tutto va flagged per review umana.

L'unico autofix accettabile in Fase B: **correzione typo coordinate** (es. lat swap lon, segno sbagliato). Soglia: km_diff > 1000 E wd_coord valido E flip_dispatch produce < 10km diff → flip.

### Task 3 — Report output

`research_output/audit_v4/fase_b_drift_report.md`:

- Stats: N entità con Q-ID / N con ≥1 diff / N HIGH / N MED / N autofixable
- Top 50 HIGH diff per review urgente
- Categorie di drift (year_start systemic bias? capital shift?)
- Pattern: entità con boundary_geojson mancante + Wikidata ha P625 → potenziale backfill

JSON `research_output/audit_v4/fase_b_autofixable.json` con patch nel formato `apply_data_patch.py`.

### Task 4 — Apply autofixable

- Dry-run via `python -m scripts.apply_data_patch research_output/audit_v4/fase_b_autofixable.json --dry-run`
- Apply in prod
- Redis flush

### Task 5 — Deploy v6.70

- Version bump 6.69.0 → 6.70.0
- CHANGELOG entry
- Commit + tag + push + deploy
- Verifica live

### Task 6 — Handoff per Fase C

Scrivi `docs/audit/FASE_C_HANDOFF.md` con:
- Report sommario Fase A+B (cosa è stato fatto, stats finali)
- Lista entità che hanno drift NON autofixable — da processare in Fase C (structural cleanup)
- Lista Q-ID non trovati che potrebbero essere nuove entità da creare
- Stato dei pattern sistemici noti (sites NULL, cities NULL, ecc.)

---

## Working principles

### Background mode

Questa sessione deve funzionare senza input umano. Quindi:
- **NON** chiedere conferma all'utente per fix ovvi (typo, year bump small, capital coord swap)
- **NON** aspettare conferma prima di commit/push/deploy
- **SÌ** fai dry-run prima di apply in prod (usando flag `--dry-run`)
- **SÌ** committa spesso (piccoli commit atomici, facili da revertare)
- **SÌ** scrivi log dettagliati nei report

### Quando stopparti

Stoppati solo se:
- Test falla dopo un fix → investiga ma non andare in loop
- Deploy fallisce con migration error → fix + re-deploy, ma se 2 tentativi falliscono, stop
- Rate limit Wikidata persistente (>10 min 429) → stop + log issue
- Più di 200 entità con match confidence < 0.3 → qualcosa è rotto nell'algoritmo, stop + debug

### Quando finisci

Scrivi un handoff finale in `docs/audit/FASE_C_HANDOFF.md` + una risposta finale che contenga:
- v6.69 + v6.70 deployate
- Stats finali Fase A + B
- Cosa resta per Fase C (come puntatore al handoff)
- Eventuali decisioni architetturali rimandate all'utente

### Cosa NON fare

- **NON** riauditare entità già viste in audit_v2 (lista in `research_output/audit_v2/agent_04_external_accuracy.json`)
- **NON** splittare entità bundled (Babilonia, Chola) — fase C
- **NON** toccare ruler/event/site FK — fase C
- **NON** creare nuove entità — fase C
- **NON** fixare i 45 script/lang mismatch — fase C
- **NON** toccare static/* frontend — fase audit dati, non UI
- **NON** modificare `_get_continent()` — già corretto in v6.67

---

## Risorse utili

### API Wikidata

- SPARQL endpoint: `https://query.wikidata.org/sparql`
- Entity data: `https://www.wikidata.org/wiki/Special:EntityData/{qid}.json`
- Search: `https://www.wikidata.org/w/api.php?action=wbsearchentities&search={label}&language={lang}&format=json`

### Proprietà Wikidata rilevanti

| Property | Meaning | AtlasPI field |
|----------|---------|---------------|
| P31 | instance of | entity_type (indirect mapping) |
| P571 | inception | year_start |
| P576 | dissolved | year_end |
| P36 | capital | capital_name + capital_lat/lon (via P625 of capital) |
| P17 | country (geographic placement) | (indirect) |
| P1365 | replaces | chain predecessor |
| P1366 | replaced by | chain successor |
| P361 | part of | (possibile successor/parent entity) |
| P527 | has part | (possibile sub-entities) |
| P625 | coordinate location | capital_lat + capital_lon |
| P421 | time zone | (nothing in AtlasPI) |
| P37 | official language | (possibile validate languages table) |

### Type Q-IDs (P31 targets) comuni

- Q34770: historical country
- Q48349: empire
- Q417175: kingdom
- Q133442: city-state
- Q41710: ethnic group / tribe
- Q7270: republic
- Q179164: polis
- Q756316: khanate
- Q5474748: sultanate
- Q429885: caliphate
- Q28171280: ancient kingdom
- Q1763527: tribal kingdom

### Dipendenze Python da aggiungere

```toml
# pyproject.toml → [project].dependencies
"SPARQLWrapper>=2.0.0",  # opzionale, altrimenti requests + manual SPARQL
"rapidfuzz>=3.5.0",      # fuzzy string matching (già possibile avere in deps)
```

Se SPARQLWrapper è troppo, usa `requests` diretto (esempio in Task 4).

---

## Metriche di successo

### Fase A success

- ≥ 800 entità con `wikidata_qid` non-null
- Score distribution: > 60% ≥ 0.85, < 20% < 0.5
- Pytest pass (incluso nuovo test per migration)
- v6.69 deployata
- API `/v1/entities/{id}` espone `wikidata_qid` nel response

### Fase B success

- ≥ 100 discrepanze identificate (attese data error rate 45% su metriche quantitative)
- Report ben strutturato in markdown leggibile
- Autofixable applicati in prod (anche solo 0-5 sono OK — il valore è nel report per review)
- v6.70 deployata
- FASE_C_HANDOFF.md scritto con lista actionable per sessione successiva

### Fase A+B success OVERALL

**Il vero valore di questa sessione non sono i fix ma l'infrastruttura**: dopo v6.70, AtlasPI può lanciare un nightly cron che fa drift detection contro Wikidata in 20 minuti. Questo è il jump qualitativo — da "rigore verificato a campione" a "rigore verificabile sistematicamente".

---

## Contatti

Domande/dubbi da parte di Claude: lascia nelle `NOTE:` del commit message. L'utente riprenderà dopo nella sessione #2 (Fase C) e le vedrà.

Bug critici in prod post-deploy: se rompi qualcosa che blocca la UI, fa rollback immediato con `ssh -i ~/.ssh/cra_vps root@77.81.229.242 "cd /opt/cra && docker compose restart atlaspi"` e logga nel handoff.

Buon lavoro.
