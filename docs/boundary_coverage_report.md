# Boundary Coverage Report — AtlasPI

**Data**: 2026-04-14
**Versione AtlasPI**: post v6.0-prep, pre v6.1
**Autore**: pipeline boundary-enrichment (Claude Code)

---

## 1. Stato attuale (pre-processing)

### Aggregati

| Metrica | Valore | % |
|---|---:|---:|
| Entita' totali | 752 | 100% |
| Boundary REALI (historical_map / academic_source / natural_earth) | **174** | **23.1%** |
| Boundary GENERATI (approximate_generated) | 575 | 76.5% |
| Senza boundary o solo Point | 3 | 0.4% |
| MultiPolygon presenti | 0 | 0.0% |

> Tutti i 174 reali sono di tipo `historical_map` (estratti da
> `aourednik/historical-basemaps`), tranne pochi casi taggati a posteriori.
> Nessun MultiPolygon presente — tutti i poligoni sono semplici.

### Breakdown per entity_type

| Tipo | Total | Real | Generated | None |
|---|---:|---:|---:|---:|
| kingdom | 287 | 72 | 215 | 0 |
| empire | 115 | 35 | 80 | 0 |
| confederation | 96 | 18 | 75 | 3 |
| republic | 53 | 5 | 48 | 0 |
| sultanate | 41 | 18 | 23 | 0 |
| colony | 32 | 3 | 29 | 0 |
| dynasty | 30 | 4 | 26 | 0 |
| city-state | 24 | 6 | 18 | 0 |
| khanate | 24 | 0 | 24 | 0 |
| principality | 20 | 2 | 18 | 0 |
| duchy | 13 | 3 | 10 | 0 |
| disputed_territory | 7 | 7 | 0 | 0 |
| federation | 5 | 1 | 4 | 0 |
| caliphate | 3 | 0 | 3 | 0 |
| city | 2 | 0 | 2 | 0 |

> Osservazioni:
> - Tutti i `disputed_territory` (7) hanno gia' boundary reale — buon
>   segno per la trasparenza.
> - I `khanate` (24) e i `caliphate` (3) sono al 100% generati: queste
>   entita' avevano confini fluidi/zone di influenza, difficile mappare.
> - I `republic` (53) hanno solo 5 reali su 53: c'e' molto upside.

### Breakdown per periodo (bucket 500 anni)

| Periodo | Total | Real | Gen | None |
|---|---:|---:|---:|---:|
| < -8000 a.C. | 9 | 1 | 8 | 0 |
| -8000..-2001 | 16 | 1 | 15 | 0 |
| -2000..-1001 | 29 | 2 | 27 | 0 |
| -1000..-1 | 91 | 17 | 74 | 0 |
| 0..499 | 35 | 6 | 29 | 0 |
| 500..999 | 119 | 21 | 96 | 2 |
| 1000..1499 | 222 | 64 | 157 | 1 |
| 1500..1999 | 230 | 60 | 170 | 0 |
| 2000+ | 2 | 2 | 0 | 0 |

> Il "centro di massa" del dataset e' tra il 500 e il 2000 d.C.
> (571 entita' su 752 = 76%). Qui c'e' il maggior potenziale di
> miglioramento via Natural Earth (per le entita' moderne) e via
> historical-basemaps esistente (per le medievali).

---

## 2. Strategia di miglioramento

### Pipeline a 3 livelli

```
                        +-------------------------------+
   batch_*.json  ->     |  enrich_all_boundaries.py     |  -> batch_*.json (aggiornato)
                        +-------------------------------+
                                    |
        +---------------------------+----------------------------+
        |                           |                            |
        v                           v                            v
  L1: Skip se gia' reale     L2: Match Natural Earth      L3: Genera approx
  (historical_map,           (boundary_match.py)          (boundary_generator.
   academic_source,          - solo year_end>1800          name_seeded_boundary)
   natural_earth)              o year_start>1700           - 12 vertici
                              - 4 strategie               - perturbazione det.
                              - vincoli ETHICS-005        - confidence 0.4
```

### Vincolo etico fondamentale (ETHICS-005)

Solo entita' MODERNE possono essere matchate con Natural Earth:
- `year_end > 1800`, OPPURE
- `year_end == None` E `year_start > 1700`

Per tutte le altre, il rischio di anacronismo (es. impero romano con
boundary italiani moderni) e' troppo alto: si usa solo
`name_seeded_boundary`.

### Eligibilita' del dataset

| Categoria | Conteggio |
|---|---:|
| Entita' totali | 752 |
| Modern eligible (year_end>1800 o live>=1700) | **290** |
| - di cui gia' con boundary reale | 76 |
| - di cui con boundary generato (upgrade target) | 214 |
| - di cui senza boundary | 0 |
| Pre-modern (no NE match consentito) | 462 |

---

## 3. Coverage proiettata

### Scenario A — Run baseline (Natural Earth 110m, no fuzzy)

Con il dataset Natural Earth 1:110M attualmente nel repo
(`data/raw/natural-earth/ne_110m_admin_0_countries.geojson`, 177 paesi)
e SENZA `rapidfuzz` (fuzzy disabilitato), una simulazione su 750 entita'
ha dato:

- **43 match esatti** trovati via `exact_name` (incluso match cross-language
  via `NAME_*` di Natural Earth)
- 461 entita' rifiutate per anacronismo (`not_modern_eligible`)
- 246 entita' moderne senza match (mancano fuzzy + capital-in-polygon)
- 2 territori contestati gia' matchati: ESH (W. Sahara), PSE (Palestina)

Coverage proiettata Scenario A:
```
real:      174 + 43 = 217 (28.9%)
generated: 532          (70.7%)
none:        3          (0.4%)
```

### Scenario B — Run completo (Natural Earth 10m + fuzzy + capital-in-polygon)

Con lo shapefile 10m installato e tutte le dipendenze (`rapidfuzz`,
`shapely`):

- 10m ha ~250 paesi/territori vs 177 del 110m
- Fuzzy match a 85% recupera molti nomi storici (es. "Imperio Espanol"
  → Spain, "Republic of Cuba" → Cuba)
- Capital-in-polygon recupera entita' con nomi non-occidentali (es.
  "Konungariket Sverige" → Sverige di NE — anche se gia' matchabile via
  cross-language)

Stima conservativa: 100-150 match aggiuntivi sui 290 eligibili.

Coverage proiettata Scenario B:
```
real:      174 + 130 ≈ 304 (40.4%)   (low estimate)
real:      174 + 200 ≈ 374 (49.7%)   (high estimate)
generated:           ≈ 445   (59%)
none:                  3   (0.4%)
```

### Scenario C — Run completo + ulteriori dataset storici

Per superare il 60% si dovra' integrare dataset storici aggiuntivi:
- `aourednik/historical-basemaps` ha 8 mappe-mondo per epoca (gia'
  presenti in `data/raw/historical-basemaps/`); estendere
  `extract_boundaries.ENTITY_MAPPINGS` da 28 a ~200 entita' storiche
  significative.
- Eventuale integrazione con Wikidata / Wikipedia historical maps
  (richiede cleanup, fuori scope di questa pipeline).

Coverage proiettata Scenario C:
```
real:      304 + 200 ≈ 504 (67%)   (target raggiunto)
generated:           ≈ 245   (32.6%)
none:                  3   (0.4%)
```

### Riepilogo

| Scenario | Real boundary | % | Note |
|---|---:|---:|---|
| Baseline (oggi) | 174 | 23.1% | solo historical-basemaps esistenti |
| A — NE 110m + name-only | ~217 | 28.9% | quick win, no install |
| B — NE 10m + fuzzy + capital | ~304-374 | 40-50% | richiede shp 10m e rapidfuzz |
| C — B + estensione mapping storici | ~500+ | 60%+ | **target v6.1** |

---

## 4. Top-10 entita' problematiche (modern eligible, nessun match Natural Earth con name-only)

Queste entita' sono moderne (eligibili) ma il match esatto sul nome non
ha avuto successo. Saranno candidate per fuzzy match (Scenario B) o per
mapping storico esplicito (Scenario C).

| # | Entity (key = name\|year_start) | Motivo probabile |
|---|---|---|
| 1 | `Osmanli Imparatorlugu\|1299` | Nome non corrisponde a stato moderno (Turkey) |
| 2 | `Kongo dia Ntotila\|1390` | Stato pre-coloniale, no match diretto in NE |
| 3 | `مغلیہ سلطنت (Mughal)\|1526` | Stato storico, no entita' "Mughal" in NE |
| 4 | `徳川幕府 (Tokugawa)\|1603` | Stato storico vs Japan moderno |
| 5 | `大清帝國 (Qing)\|1636` | Stato storico vs China moderna |
| 6 | `Российская Империя\|1721` | Russian Empire vs Russia moderna (fuzzy lo prenderebbe) |
| 7 | `臺灣 / Taiwan\|1949` | NE NAME = "Taiwan" senza prefisso, fuzzy lo prende |
| 8 | `የኢትዮጵያ ንጉሠ ነገሥት መንግሥት (Ethiopia)\|1270` | Lingua amarica, fuzzy lo prende |
| 9 | `Крим / Крым\|2014` | Crimea (territorio contestato — vedi ETHICS-005) |
| 10 | `Imperio Español\|1492` | Spanish Empire vs Spain moderna (fuzzy lo prende) |

> Tutti questi sono recuperabili in Scenario B (10m + fuzzy + capital).
> Per i 246 totali rifiutati, l'analisi caso-per-caso e' nel JSON
> `docs/_match_dryrun.json` (non committato — file di working).

---

## 5. Esecuzione

### Prerequisiti

```bash
pip install -r requirements.txt   # include geopandas, shapely, rapidfuzz
```

Per Scenario B / C, scaricare manualmente il dataset Natural Earth 10m:

```
https://www.naturalearthdata.com/downloads/10m-cultural-vectors/
# oppure
https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip
```

Estrarre tutti i file dello shapefile (.shp/.shx/.dbf/.prj/.cpg) in:
```
data/raw/natural_earth/
```

### Step 1 — Importare Natural Earth

Dry-run (non scrive nulla):
```bash
python -m src.ingestion.natural_earth_import --dry-run
```

Run reale (scrive `data/processed/natural_earth_boundaries.json`):
```bash
python -m src.ingestion.natural_earth_import
```

### Step 2 — Pipeline di arricchimento

Dry-run (consigliato sempre prima):
```bash
python -m src.ingestion.enrich_all_boundaries --dry-run
```

Run reale (modifica i file batch, crea backup .bak):
```bash
python -m src.ingestion.enrich_all_boundaries
```

Solo generated (skip Natural Earth, utile in test):
```bash
python -m src.ingestion.enrich_all_boundaries --skip-natural-earth
```

### Step 3 — (Opzionale) Re-seed del DB

Dopo aver aggiornato i batch JSON, ricaricare il DB:
```bash
python -m src.db.seed   # o lo script equivalente del progetto
```

---

## 6. Garanzie di sicurezza

### Idempotenza

- Boundary `historical_map` / `academic_source` / `natural_earth`:
  **mai sovrascritti**.
- Boundary `approximate_generated`: possono essere upgradati a
  `natural_earth` se viene trovato un match valido (miglioramento
  monotono).
- Boundary mancanti o di tipo Point: sempre rigenerati.

### Backup

Per ogni file batch modificato, viene creato un `.bak` accanto al file
originale. Il backup viene sovrascritto al run successivo (e' un
"backup ultima esecuzione", non versioning storico — quello e' git).

---

## 7. Decisioni etiche

Durante questa pipeline e' stata creata una nuova decisione etica:

**ETHICS-005 — Boundary da Natural Earth e territori contestati**
(`docs/ethics/ETHICS-005-boundary-natural-earth.md`).

Punti chiave:
- Solo entita' moderne (year_end > 1800 o year_start > 1700) eligibili.
- Territori contestati (Taiwan, Western Sahara, Palestina, Kosovo,
  Cipro Nord, Kashmir, Somaliland) ricevono ethical_notes esplicite.
- Confidence_score modulato per strategia di match.
- Rispetta i 4 principi CLAUDE.md (verita' prima del comfort, no
  versione unica, trasparenza, no bias geografico).

ETHICS-004 (boundary generati approssimativi) resta valido e
applicabile a tutte le entita' che ricadono nel ramo "L3: Genera approx".

---

## 8. Prossimi passi (proposta v6.1+)

- [ ] Installare lo shapefile NE 10m e rieseguire la pipeline (Scenario B).
- [ ] Estendere `extract_boundaries.ENTITY_MAPPINGS` da 28 a ~200 entita'
  storiche significative usando i 8 file world_*.geojson gia' presenti
  (Scenario C).
- [ ] Aggiungere test di regressione: per ogni 10 entita' campione,
  verificare che il boundary sia coerente per area (km^2) e geografia
  (centroide vicino alla capitale).
- [ ] Migrare a PostGIS (vedi ADR-001) per query spaziali avanzate.
- [ ] Pubblicare `docs/boundary_coverage_report.md` come parte della
  documentazione open core (questo file).
