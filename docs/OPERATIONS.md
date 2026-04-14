# AtlasPI — Operations Runbook

Questo documento e' il riferimento operativo per la gestione di AtlasPI in produzione.

Se stai leggendo questo durante un incidente: vai direttamente alla sezione
[Quick actions](#quick-actions) e poi torna qui per approfondire.

---

## Deployment target

- **Dominio**: https://atlaspi.cra-srl.com
- **Host**: Aruba Cloud
- **Container**: Docker (multi-stage build, non-root user `atlaspi`)
- **Processo**: `gunicorn` con 2 uvicorn workers, porta 10100
- **Reverse proxy**: nginx (per HTTPS + multi-app routing)
- **Database**: SQLite (default) / PostgreSQL+PostGIS (opzionale, via `DATABASE_URL`)

---

## Quick actions

### Il sito e' giu'

```bash
# 1. Check dal nostro stesso host
curl -i https://atlaspi.cra-srl.com/health

# 2. Verifica container
ssh aruba 'docker ps | grep atlaspi'

# 3. Guarda gli ultimi log
ssh aruba 'docker logs --tail 200 atlaspi'

# 4. Se il container e' crashato, restart
ssh aruba 'docker restart atlaspi'

# 5. Verifica dopo restart
curl -i https://atlaspi.cra-srl.com/health
```

### Il sito e' lento (>1s)

```bash
# Dal tuo laptop
./scripts/smoke_test.sh https://atlaspi.cra-srl.com

# Sul server: top dei processi
ssh aruba 'docker exec atlaspi top -b -n 1 | head -20'

# Sul server: log ultima ora filtrati per warning/error
ssh aruba 'docker logs --since 1h atlaspi 2>&1 | grep -iE "warn|error|slow"'
```

### Il DB si e' corrotto / voglio ripristinare un backup

```bash
# 1. Stop container
ssh aruba 'docker stop atlaspi'

# 2. Sul server, scegli il backup
ssh aruba 'ls -lt /opt/atlaspi/backup/ | head -5'

# 3. Restore (script chiede conferma)
ssh aruba 'cd /opt/atlaspi && ./scripts/restore.sh backup/atlaspi-YYYY-MM-DD-HHMM.db.gz'

# 4. Restart
ssh aruba 'docker start atlaspi'

# 5. Verifica
curl https://atlaspi.cra-srl.com/health
```

---

## Deploy di nuova versione

### Flusso standard

```bash
# Sul laptop: build e push (se CI non lo fa)
git push origin main

# Sul server: pull + rebuild + restart
ssh aruba 'cd /opt/atlaspi && git pull && docker compose up -d --build'

# Verifica con smoke test
./scripts/smoke_test.sh https://atlaspi.cra-srl.com
```

### Rollback rapido

```bash
# Identifica la versione precedente
ssh aruba 'cd /opt/atlaspi && git log --oneline -5'

# Checkout + rebuild
ssh aruba 'cd /opt/atlaspi && git checkout <commit> && docker compose up -d --build'
```

---

## Backup

I backup sono **obbligatori** e automatici via cron.

### Configurazione cron (fatta una volta sul server)

```bash
# Edit crontab sul server
ssh aruba 'crontab -e'

# Aggiungi questa linea (backup giornaliero alle 03:00)
0 3 * * * /opt/atlaspi/scripts/backup.sh >> /var/log/atlaspi-backup.log 2>&1
```

### Parametri

Impostabili via env var o in `.env`:

| Variabile | Default | Note |
|---|---|---|
| `BACKUP_DIR` | `./backup` | Dove salvare i file |
| `BACKUP_RETAIN` | `14` | Giorni di retention |
| `DATABASE_URL` | da `.env` | Auto-detect SQLite vs Postgres |

### Verifica backup funzionanti

```bash
# Sul server, una volta a settimana:
ssh aruba 'ls -lh /opt/atlaspi/backup/ | tail -5'

# Test restore su DB temporaneo (distruttivo, fai in ambiente dedicato):
cp backup/atlaspi-latest.db.gz /tmp/
gunzip /tmp/atlaspi-latest.db.gz
sqlite3 /tmp/atlaspi-latest.db 'SELECT COUNT(*) FROM geo_entities;'
```

### Backup offsite (TODO)

- Sync dei backup verso S3/R2 o un altro provider → protezione contro perdita totale del server.
- Script consigliato: `rclone sync /opt/atlaspi/backup/ remote:atlaspi-backups/`
- Schedulato in cron dopo lo script di backup locale.

---

## Monitoring

### Health endpoint

`GET /health` ritorna JSON con:
- `status`: `ok` | `degraded` | `down`
- `database`: `sqlite:connected` | `postgresql:connected` | `*:disconnected`
- `entity_count`: numero di entita' nel DB (soglia minima 100)
- `uptime_seconds`: secondi dall'avvio
- `sentry_active`: true/false
- `checks`: dettaglio sotto-verifiche

HTTP code: 200 per `ok` e `degraded`, 503 per `down` → così UptimeRobot capisce.

### UptimeRobot (setup)

1. Crea account su https://uptimerobot.com (free: 50 monitor, check ogni 5 min)
2. Add new monitor:
   - Type: **HTTPS**
   - URL: `https://atlaspi.cra-srl.com/health`
   - Interval: 5 min
   - Keyword alert: `"status":"ok"` (ti avvisa anche se torna 200 ma status e' `degraded`)
3. Alert contact: la tua email + eventuale Telegram bot

### Sentry (setup)

1. Crea account su https://sentry.io (free tier: 5K errori/mese)
2. Crea project "atlaspi" (tipo Python/FastAPI)
3. Copia il DSN
4. Sul server, aggiungi a `.env`:
   ```
   SENTRY_DSN=https://xxx@oOOOO.ingest.sentry.io/PPPP
   SENTRY_ENVIRONMENT=production
   SENTRY_TRACES_SAMPLE_RATE=0.1
   SENTRY_RELEASE=atlaspi@6.1.0
   ```
5. Restart container: `docker restart atlaspi`
6. Verifica: `curl https://atlaspi.cra-srl.com/health | jq .sentry_active` → deve essere `true`

---

## Logging

- Formato: JSON in produzione (`LOG_FORMAT=json`)
- Output: stdout/stderr → docker logs
- Rotazione: gestita da docker (`--log-opt max-size=10m --log-opt max-file=3` nel compose)

### Aggregazione log (opzionale)

Per produzione seria:
- Option A: forward a Grafana Loki self-hosted
- Option B: shipper verso Better Stack / Axiom (hanno free tier)
- Option C: solo docker logs, review manuale

---

## Rate limiting

- Middleware: `slowapi` (in-memory per worker)
- Default: `60/minute` (env var `RATE_LIMIT`)
- IP reale via header `X-Forwarded-For` (nginx lo inoltra)
- **Limitazione nota**: in-memory → ogni worker ha il suo contatore. Per rate limit globale serve Redis.

### Abilitare Redis-backed rate limit (v6.3)

Documentato come roadmap item. Non ancora implementato.

---

## Sicurezza

### HTTPS

Gestito da nginx con Let's Encrypt. Rinnovo automatico via `certbot renew` in cron.

### Secrets

- `SECRET_KEY` → deve essere diverso da `"dev-secret-change-in-production"` in prod
- `SENTRY_DSN` → sensibile ma non critico (read-only per terzi)
- `DATABASE_URL` → contiene password Postgres se abilitato
- Nessuno di questi dev'essere committato. Usare `.env` sul server (gitignored).

### Header di sicurezza

Il middleware `SecurityHeadersMiddleware` applica:
- HSTS (1 anno, includeSubDomains)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer-Policy: strict-origin-when-cross-origin
- Content-Security-Policy (vedi implementazione)

### CORS

Default: `*`. In produzione **restringere** tramite env var:

```
CORS_ORIGINS=https://atlaspi.cra-srl.com,https://docs.cra-srl.com
```

---

## Performance

### Baseline attesa (v6.1)

| Endpoint | p50 | p95 | Note |
|---|---|---|---|
| `/health` | <20ms | <50ms | Solo `SELECT 1` + count |
| `/v1/stats` | <50ms | <150ms | Aggregazioni cached (no) |
| `/v1/snapshot/{year}` | <200ms | <500ms | Dipende da year_range |
| `/v1/nearby` | <150ms | <400ms | Pre-PostGIS, O(n) |
| `/v1/entities/{id}` | <30ms | <100ms | PK lookup |

Se superiamo il p95 target stabilmente → priorita' v6.1 (migrazione PostgreSQL + PostGIS + GiST index).

---

## Troubleshooting comuni

### "database disk image is malformed" (SQLite)

```bash
# Copia e riprova
cp data/atlaspi.db data/atlaspi.db.bad
sqlite3 data/atlaspi.db.bad ".recover" | sqlite3 data/atlaspi.db.recovered
mv data/atlaspi.db.recovered data/atlaspi.db
```

Se fallisce → restore da backup piu' recente.

### "too many open files"

Limite per worker gunicorn. Aumenta `ulimit -n` nel Dockerfile o nel compose:

```yaml
services:
  app:
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### Container OOM-killed

Dockerfile gira con 2 workers. Su Aruba Cloud minimo (es. 1 GB RAM) potrebbe essere troppo per 2 workers + seed di 747 entita'. Prove:

```yaml
# docker-compose.yml
services:
  app:
    mem_limit: 512m  # ridurre se serve
```

E ridurre i workers modificando `Dockerfile` CMD: `--workers 1`.

---

## Riconciliazione dei confini (v6.1.1+)

Il pipeline di arricchimento v6.1.1 aggiorna i boundary nei file batch
`data/entities/batch_*.json`. In produzione il `seed_database()` gira solo
su un DB vuoto, quindi un database di lunga durata conserva i confini
pre-arricchimento anche dopo che le nuove versioni sono state committate.

Il modulo `src/ingestion/sync_boundaries_from_json.py` fa la
**riconciliazione monotona** tra JSON e DB. Solo upgrade, mai downgrade.
Idempotente.

### Comando

Dry-run (raccomandato prima di qualsiasi modifica):

```bash
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi python -m src.ingestion.sync_boundaries_from_json --dry-run"
```

Output tipico:

```
Sync stats
  total_db                                  747
  matched_in_batch                          747
  upgraded                                  419
  skipped_no_batch_entry                    0
  skipped_batch_has_no_boundary             44
  skipped_db_already_better                 284
  skipped_equal                             0
  confidence_capped_disputed                5
```

Esecuzione effettiva (committa le modifiche al DB):

```bash
# PRIMA: backup del DB Postgres
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "docker exec cra-atlaspi-db pg_dump -U atlaspi atlaspi > /root/atlaspi-backup-\$(date +%Y%m%d-%H%M%S).sql"

# Sync
ssh -i ~/.ssh/cra_vps root@77.81.229.242 \
  "cd /opt/cra && docker compose exec atlaspi python -m src.ingestion.sync_boundaries_from_json"
```

### Garanzie

1. **Monotona**: un poligono con 1000 vertici nel DB non viene mai sostituito
   con uno a 100 vertici dal batch. Guardrail nel predicato `_should_upgrade`.
2. **ETHICS-003**: entita' `status == "disputed"` vengono sempre cappate a
   `confidence ≤ 0.70`, anche se il batch dichiara 0.85.
3. **Idempotenza**: eseguire due volte restituisce `upgraded: 0` alla seconda.
4. **Dry-run safe**: nessuna scrittura, la transazione viene rolled back
   esplicitamente.

### Quando eseguirlo

- Dopo un commit che aggiorna i batch JSON con nuovi boundary enrichment.
- Dopo una release che bumpa il dataset (es. v6.1.1 → v6.2.0).
- **NON** serve eseguirlo ad ogni deploy: se non ci sono drift tra JSON e DB
  il comando e' un no-op.

### Test di copertura

`tests/test_sync_boundaries.py` (11 test): predicati puri, dry-run,
idempotenza, rispetto ETHICS-003 cap.

---

## Contatti e governance

- Repo: https://github.com/Soil911/AtlasPI
- License: MIT (core open source)
- Ethics records: `docs/ethics/ETHICS-*.md`
- Decisioni architetturali: `docs/adr/`

Per decisioni che alterano dati storici: aprire ETHICS record prima di procedere.
Vedi CLAUDE.md per dettagli sulla governance.
