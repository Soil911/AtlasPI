# AtlasPI — Istruzioni per Claude Code

Questo file viene letto automaticamente da Claude Code
all'inizio di ogni sessione. Contiene i valori fondamentali,
le convenzioni di sviluppo e i riferimenti etici del progetto.

---

## Cos'è questo progetto

AtlasPI è un database geografico storico strutturato,
progettato per essere consumato da agenti AI. Fornisce coordinate,
confini GeoJSON e metadati storici di entità geopolitiche in
qualsiasi epoca — ottimizzato per essere leggibile dalle macchine.

Obiettivo: colmare il gap tra i dati geografici grezzi esistenti
(Natural Earth, OpenStreetMap, Wikidata) e il formato strutturato,
affidabile e contestualizzato di cui gli agenti AI hanno bisogno.

---

## Valori fondamentali — leggili prima di scrivere qualsiasi codice

### 1. Verità prima del comfort
I dati storici spesso riguardano conquiste, genocidi, deportazioni,
cancellazioni culturali. Questi fatti vanno rappresentati con
precisione, non edulcorati.
- Se un territorio è stato occupato con la forza → il campo
  acquisition_method lo dice esplicitamente
- Se una popolazione è stata decimata → i dati demografici
  lo mostrano con le fonti
- Se un nome geografico è stato imposto cancellando quello
  originale → entrambi i nomi sono presenti
NON omettere la verità scomoda. Renderla accessibile è lo scopo.

### 2. Nessuna versione unica della storia
- I confini contestati mostrano tutte le versioni note,
  con date e fonti
- I nomi mostrano la forma nella lingua originale +
  forme in altre lingue rilevanti
- Le dispute accademiche vengono esplicitate, non risolte
  arbitrariamente
Il database non arbitra la storia. La documenta.

### 3. Trasparenza dell'incertezza
- Ogni record ha un campo confidence_score (0.0 → 1.0)
- Ogni dato ha sources[] con citazione della fonte primaria
- I record con score < 0.5 sono marcati come status: "disputed"
Un dato incerto comunicato come tale è più onesto di un dato
certo inventato.

### 4. Nessun bias geografico o culturale dominante
- I nomi dei luoghi usano la forma nella lingua locale
  come nome primario
- Le fonti devono includere storiografia non-occidentale
  dove disponibile
- Le conquiste coloniali sono descritte anche dal punto di
  vista dei conquistati

---

## Architettura del progetto

.
├── CLAUDE.md              ← questo file
├── README.md
├── LICENSE                ← Apache License 2.0 (testo ufficiale)
├── NOTICE                 ← attribuzioni terze parti (Natural Earth, aourednik, ...)
├── ROADMAP.md
├── CHANGELOG.md
├── .gitignore
├── docs/
│   ├── TEMPLATES.md
│   ├── adr/               ← Architecture Decision Records
│   └── ethics/            ← decisioni etiche documentate
├── src/
│   ├── api/               ← FastAPI endpoints
│   ├── db/                ← modelli PostgreSQL + PostGIS
│   ├── ingestion/         ← pipeline importazione dati
│   └── validation/        ← confidence scoring
├── data/
│   ├── raw/               ← dati originali non modificati
│   └── processed/         ← dati normalizzati
└── tests/

---

## Convenzioni temporali

- Gli anni usano sempre interi
- Gli anni negativi rappresentano date a.C.
- Gli intervalli temporali devono usare questa convenzione
  in modo coerente in tutto il progetto
- Se una data è incerta, l'incertezza deve essere esplicitata
  nei metadati e nel confidence_score

---

## Stack tecnologico

| Componente | Tecnologia |
|---|---|
| API | FastAPI (Python) |
| Database | PostgreSQL + PostGIS |
| Cache | Redis |
| Storage GeoJSON | Cloudflare R2 |
| Deploy | Railway (MVP) |

---

## Convenzioni di codice

- Lingua del codice: inglese
- Lingua della documentazione: italiano
- Ogni funzione che tocca dati storici sensibili deve avere
  un commento # ETHICS: che spiega la scelta
- I test devono coprire i casi limite etici, non solo tecnici

Esempio corretto:
def get_territory_name(entity_id, lang="original"):
    # ETHICS: il nome primario è sempre quello originale/locale.
    # Il nome imposto da potenze coloniali è in name_colonial,
    # non come campo principale. Vedi ETHICS-001.
    ...

---

## Roadmap e versionamento obbligatori

Lo sviluppo deve sempre seguire una roadmap chiara,
incrementale e documentata.

Regole:
- usare versioni progressive: v0.0.1, v0.0.2, v0.1.0, v0.2.0, v1.0.0
- ogni versione deve avere uno scopo chiaro e limitato
- prima di implementare nuove funzionalità, aggiornare ROADMAP.md
- ogni cambiamento rilevante deve essere riflesso in CHANGELOG.md
- evitare sviluppo disordinato o aggiunte non tracciate
- ogni milestone deve essere documentata nel repository

Se una feature non appartiene chiaramente alla versione corrente,
deve essere rinviata a una versione successiva esplicitamente pianificata.

---

## Governance etica durante lo sviluppo

Se durante lo sviluppo emerge una scelta che può alterare,
semplificare o distorcere la rappresentazione storica, Claude
non deve procedere in silenzio.

In questi casi deve:
1. aprire o aggiornare un record in docs/ethics/
2. descrivere il rischio di distorsione
3. documentare le alternative considerate
4. spiegare la scelta adottata
5. solo dopo procedere con l'implementazione

Regola pratica:
se una decisione tecnica ha impatto sulla verità storica,
sulla rappresentazione di popoli, confini, nomi o conquiste,
va trattata come decisione etica documentata.

---

## Modello di distribuzione

AtlasPI segue un modello open core.

Principi:
- il repository è pubblico
- il core del progetto è open source
- la documentazione architetturale ed etica è pubblica
- gli asset premium possono includere dataset curati, servizi hosted,
  funzionalità avanzate, accesso API ad alto volume e componenti enterprise
- codice open e componenti premium devono restare chiaramente separati

Prima di pubblicare qualunque componente:
- definire la licenza del core
- verificare la compatibilità delle licenze dei dataset
- distinguere chiaramente ciò che è open da ciò che è premium

---

## Gestione operativa del repository

AtlasPI è progettato per essere sviluppato come repository pubblico su GitHub.

Claude deve:
- mantenere il repository ordinato e documentato
- creare e aggiornare roadmap, changelog e documentazione architetturale
- strutturare il lavoro in milestone e versioni progressive
- preparare il progetto per pubblicazione open core
- evitare codice non documentato o non coerente con i principi del progetto

---

## Controllo qualità a 360° — per agenti AI

Gli agenti AI (AI Co-Founder + Claude Code) devono fare quality check
su più livelli, non solo metadata:

### Metadata checks (esistenti, 7 analizzatori)
- `geographic_gaps` / `temporal_gaps` — copertura dataset
- `low_confidence` — confidence < 0.4
- `missing_boundaries` — boundary null
- `orphan_entities` — non in chain
- `failed_searches` — 404/zero-result patterns
- `date_coverage_gaps` — on-this-day coverage

### Geometric checks (v6.31, NUOVO)
Il campo `boundary_geojson` può essere **presente** (passa metadata check)
ma **geometricamente sbagliato**. Un polygon può:
- Attraversare l'antimeridian (bbox > 180° → label rende in posto errato)
- Essere troppo grande per il `entity_type` (city-state con polygon USA)
- Essere condiviso byte-per-byte con altre entità (fuzzy-match error)

**Analizzatore**: `analyze_geometric_bugs` in `scripts/ai_cofounder_analyze.py`.
**Auto-fix**: `src/ingestion/fix_antimeridian_and_wrong_polygons.py`.
**Startup guard**: incluso in `main.py` lifespan, idempotent.

**Se scrivi codice che crea/aggiorna boundary**, verifica SEMPRE dopo:
```python
from shapely.geometry import shape
g = shape(json.loads(entity.boundary_geojson))
assert g.bounds[2] - g.bounds[0] < 180, "polygon crosses antimeridian!"
```

### Visual checks (raccomandati per nuove feature)
Quando aggiungi una feature che altera rendering o dati visibili:
1. Aprire https://atlaspi.cra-srl.com/app e navigare ad un anno campione
2. Verificare che labels, boundary, markers siano in posizioni sensate
3. Screenshotare o descrivere risultato nel commit message

**Lezione imparata dal bug v6.31**: metadata-only checks possono mancare
classi intere di bug visibili solo su mappa. Integra controlli geometrici
e visuali nel pipeline.

---

## Regola d'oro

Prima di scrivere codice chiedi: "questo dato, in questo formato,
potrebbe essere usato per distorcere la comprensione storica?"
Se la risposta è sì, apri un ETHICS record prima di procedere.

---

## Deploy in produzione

### ⚠️ HAI ACCESSO SSH AL VPS
La chiave privata `~/.ssh/cra_vps` è autorizzata come root sul VPS. Puoi eseguire **qualsiasi** comando sul server di produzione via:
```bash
ssh -i ~/.ssh/cra_vps root@77.81.229.242 "<comando>"
```
Usalo per: ispezionare container, leggere log, fare backup del DB Postgres, eseguire Alembic manualmente, ecc. Esempi pratici:
```bash
# Backup DB Postgres prima di una migration
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "docker exec cra-atlaspi-db pg_dump -U atlaspi atlaspi > /root/atlaspi-backup-\$(date +%Y%m%d-%H%M%S).sql"
# Esegui query ad-hoc
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "docker exec cra-atlaspi-db psql -U atlaspi -d atlaspi -c 'SELECT count(*) FROM some_table'"
# Alembic downgrade manuale
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi alembic downgrade -1"
```
Operazioni irreversibili (DROP TABLE, docker compose down -v, alembic downgrade oltre -1) vanno confermate con Clirim prima.

### Topologia
- **Produzione**: Aruba VPS `77.81.229.242` (Ubuntu 24.04 + Docker)
- **Dominio pubblico**: https://atlaspi.cra-srl.com (Nginx + Let's Encrypt)
- **Porta interna container**: 10100
- **Stack**: 3 container — `cra-atlaspi` (app), `cra-atlaspi-db` (Postgres), `cra-atlaspi-redis`
- **Path sul server**: `/opt/cra/atlaspi` (git repo)
- **Repo GitHub**: `Soil911/AtlasPI` branch `main`
- **Env**: `/opt/cra/.env.atlaspi` (DATABASE_URL postgres, REDIS_URL, CORS_ORIGINS)
- **DB**: PostgreSQL dedicato su `cra-atlaspi-db` (volume persistente), migrazioni Alembic automatiche al startup

### Quando Clirim dice "aggiorna sul server" / "deploy" / "pusha in produzione"
Esegui **in sequenza**:

```bash
# 1. Tutto committato e pushato
git status              # clean
git push origin main

# 2. Deploy sul VPS (pull + rebuild + healthcheck)
cra-deploy atlaspi
```

Lo script `cra-deploy` (in `~/bin/`) esegue sul VPS: `git pull` → `docker compose build atlaspi` → `docker compose up -d atlaspi` → healthcheck su `http://127.0.0.1:10100/health` (timeout 60s).

### ⚠️ Migrazioni Alembic
Le migrazioni girano automaticamente allo startup del container tramite `run.py`. Quando aggiungi una nuova migration:
1. Genera in locale: `alembic revision --autogenerate -m "..."`
2. **Testa in locale** contro un DB di test prima di pushare
3. Commit del file in `alembic/versions/`
4. Push + deploy — parte al prossimo startup del container
5. Verifica post-deploy: `cra-logs atlaspi 100` — cerca righe Alembic "Running upgrade..."

Il Dockerfile fa `COPY alembic/ alembic/` e `COPY alembic.ini .` — se sposti la cartella Alembic, aggiorna il Dockerfile.

### Verifica post-deploy
```bash
cra-health
curl -sS https://atlaspi.cra-srl.com/health | python -m json.tool
```

### Se il deploy fallisce
```bash
cra-logs atlaspi 100
cra-logs atlaspi-db 50        # errori Postgres (es. migration fallita)
```

Errori tipici:
- Migration fallisce → il container si riavvia in loop. Fixa la migration in locale, push, re-deploy
- DB non connette → verifica `cra-atlaspi-db` sia `healthy`: `ssh ... docker ps`
- `CORS_ORIGINS` manca → aggiorna `/opt/cra/.env.atlaspi` e `docker compose restart atlaspi`

**Mai toccare il codice sul VPS**: `git reset --hard origin/main` cancella tutto.

### Rollback (⚠️ attento con le migrazioni)
Rollback del codice:
```bash
git revert HEAD
git push
cra-deploy atlaspi
```

Se il commit revertato includeva una migration Alembic **già applicata in produzione**, devi anche downgradare il DB manualmente:
```bash
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi alembic downgrade -1"
```
Prima di farlo: **fai un backup del DB** (`pg_dump`) perché i downgrade possono perdere dati.

### NON deployare se:
- Test falliscono
- Ci sono modifiche non committate
- Migration non testata in locale
- Clirim ha detto "solo locale" / "non deployare"

Per workflow completo dello sviluppo in parallelo delle 3 app (CRAgent, CRApp, AtlasPI) vedi la memoria Claude in `~/.claude/projects/C--Users-cliri-Documents-CRA-AGENT/memory/deploy_workflow.md`.
