# AtlasPI — Scripts operativi

Script bash per operazioni di produzione. Tutti sono compatibili Linux (server) e richiedono bash + coreutils + curl + jq (per smoke_test).

## Script disponibili

### `backup.sh`
Backup del database (auto-detect SQLite vs PostgreSQL).

```bash
./scripts/backup.sh                # usa ./backup come output dir
./scripts/backup.sh /mnt/data/bkp  # output dir esplicita
```

Parametri via env:
- `DATABASE_URL` — URL connessione DB (default da .env)
- `BACKUP_DIR` — dir output (default `./backup`)
- `BACKUP_RETAIN` — quanti backup conservare (default 14)

Schedula in cron per backup automatici:
```
0 3 * * * /opt/atlaspi/scripts/backup.sh >> /var/log/atlaspi-backup.log 2>&1
```

### `restore.sh`
Ripristino del database da un backup. Richiede conferma esplicita (`yes`).

```bash
./scripts/restore.sh backup/atlaspi-2026-04-14-0300.db.gz
./scripts/restore.sh backup/atlaspi-2026-04-14-0300.sql.gz
```

Salva automaticamente il DB corrente come `.pre-restore.<timestamp>` prima di sovrascriverlo.

### `smoke_test.sh`
Test end-to-end degli endpoint critici. Exit code 0 se tutto ok, 1 altrimenti.

```bash
./scripts/smoke_test.sh                          # localhost:10100
./scripts/smoke_test.sh https://atlaspi.cra-srl.com
BASE_URL=http://staging ./scripts/smoke_test.sh
```

Include 14 check: health, stats, entities, snapshot, aggregation, random, nearby, docs, openapi, robots, sitemap.

## Permessi di esecuzione

Prima del primo uso, dare il bit di esecuzione (Linux):
```bash
chmod +x scripts/*.sh
```

Su Windows (dev locale): il bit di esecuzione non e' rilevante, ma gli script vanno lanciati con `bash scripts/backup.sh` esplicito.

## Dipendenze richieste

Sul server:
- `bash` >= 4.0
- `sqlite3` (solo se usi SQLite)
- `pg_dump`, `psql` (solo se usi PostgreSQL)
- `gzip`
- `curl` (per smoke_test)
- `jq` (per smoke_test assertions)

Su Ubuntu/Debian:
```bash
apt install -y sqlite3 postgresql-client curl jq
```
