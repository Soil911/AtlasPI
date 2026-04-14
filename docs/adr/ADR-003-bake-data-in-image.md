# ADR-003 — `data/` viene bakata nell'immagine, non montata come volume

**Data**: 2026-04-14
**Stato**: Accettato
**Autore**: Clirim (sessione di hardening post-v6.1.1)
**Impatto**: Medio — semplifica il deploy e rimuove una classe di bug

## Contesto

Fino a v6.1.1, il compose di produzione (`/opt/cra/docker-compose.yml`)
montava un volume Docker named sul servizio `atlaspi`:

```yaml
volumes:
  - atlaspi-appdata:/app/data
```

Analogamente, il compose standalone nel repo (`docker-compose.yml`)
montava `app-data:/app/data` sul servizio `app`.

Il `Dockerfile` fa `COPY --chown=atlaspi:atlaspi data/ data/`: tutti i
`batch_*.json`, i dataset `raw/natural-earth/` e `raw/historical-basemaps/`
vengono copiati nell'immagine al build.

## Problema osservato

Durante il sync di produzione post-v6.1.1 con i dati aggiornati dei
batch JSON (addizione provenienza aourednik + fix ETHICS-006), `cra-deploy`
ha:

1. fatto `git pull` sul VPS (correttamente aggiornato `/opt/cra/atlaspi/data/entities/*.json`),
2. ricostruito l'immagine (correttamente includendo i JSON nuovi in `/app/data/`),
3. ricreato il container (il named volume `atlaspi-appdata` ha mascherato
   `/app/data/` del layer immagine con i dati **stali** del primo `up`
   risalente a giorni prima).

Risultato: `docker exec cra-atlaspi cat /app/data/entities/batch_XX.json`
restituiva il file vecchio, non quello appena deployato. Il sync non
vedeva le modifiche al JSON finché non si `docker cp`-pava manualmente il
file nel volume.

Questa è la stessa classe di bug che affligge tutti i mount `named-volume:
/path-in-image` dove `/path-in-image` è popolato dal `Dockerfile COPY`:
al primo `up`, Docker inizializza il volume col contenuto della directory
in-image; ma da lì in poi il volume diventa autoritativo e le ricostruzioni
dell'immagine non aggiornano più i dati visti dal container.

## Decisione

**Rimuovere completamente il mount `/app/data`** su `atlaspi` (prod) e `app`
(dev standalone). I dati (`entities/`, `raw/`, `processed/`) vivono
esclusivamente nel layer immagine.

File modificati:
- `/opt/cra/docker-compose.yml` (prod): rimosso `atlaspi-appdata:/app/data`
  e la relativa dichiarazione top-level `volumes:`.
- `docker-compose.yml` (repo): rimosso `app-data:/app/data`, `app-data:/data:ro`
  dal backup sidecar, e `app-data:` top-level.

Il volume `cra_atlaspi-appdata` è stato rimosso dal daemon prod con
`docker volume rm`, dopo tarball di backup salvato in
`/root/atlaspi-volume-backups/`.

## Alternative considerate

### Alternativa A — Entrypoint che sincronizza `/app/data/` dall'immagine al volume

```bash
# in run.py o entrypoint.sh
rsync -a --delete /app/data-image/ /app/data/
```

con `COPY data/ /app/data-image/` nel Dockerfile.

**Scartata** perché:
- raddoppia la RAM/disco del dato (due copie nell'immagine + volume),
- aggiunge complessità operazionale,
- il beneficio teorico (poter fare `docker exec` per modificare un batch
  senza rebuild) non corrisponde al workflow reale (i batch JSON sono
  source-controlled, non si editano mai live).

### Alternativa B — Bind-mount del repo sul VPS (`./data:/app/data`)

**Scartata** perché:
- crea dipendenza dal filesystem host (rompe la portabilità),
- complica i deploy (le modifiche di permessi devono coincidere host/container),
- il mount viene invalidato se si rinomina il path sul VPS.

### Alternativa C — Status quo + riscrittura del volume al deploy

Modificare `cra-deploy` per fare `docker cp` dei file del repo nel volume
dopo il rebuild.

**Scartata** perché:
- il bug del mount rimane — il volume è ancora masked,
- è uno workaround che cementa il problema,
- nessun beneficio rispetto alla baking dell'immagine.

## Conseguenze

### Positive

- **Un'immagine == uno stato dei dati**: il tag immagine identifica
  univocamente anche il dataset incluso. Rollback di codice e dataset è
  atomico.
- **Deploy idempotenti**: ogni `docker compose up -d atlaspi` dopo un
  rebuild garantisce che i file in `/app/data/` corrispondano al repo al
  commit deployato.
- **Nessuno stato persistente superfluo**: i dati veri (DB Postgres) sono
  già in un volume dedicato `atlaspi-pgdata`, che resta intatto.
- **Debug più semplice**: `docker exec cra-atlaspi ls /app/data/entities/`
  riflette sempre cosa ha visto `AUTO_SEED` all'avvio.

### Negative

- **Immagine più grande**: +62 MB circa (entities 52 MB + raw 10 MB). Per il
  nostro caso d'uso è trascurabile.
- **Rebuild necessario per cambi ai dati**: non si può più `docker cp` un
  JSON nel container per testare al volo. Tradeoff accettato — il workflow
  corretto passa per git + rebuild.

## Verifica

Post-deploy, `/app/data/` è popolata dall'immagine:

```
$ docker inspect cra-atlaspi --format '{{json .Mounts}}'
[]

$ docker exec cra-atlaspi ls /app/data/entities/*.json | wc -l
25
```

`/health` risponde 200 con `entity_count: 747`, `boundary_source`
distribution intatta (290 aourednik + 168 historical_map + 78 natural_earth
+ 209 approximate_generated).

## Note operative

**Non ricreare il volume `app-data` / `atlaspi-appdata`.** Se un futuro
`docker-compose.yml` lo reintroduce (es. per sbaglio durante un refactor),
si riaprirà la stessa classe di bug. Il linter del compose non lo segnala
perché non è sintatticamente scorretto — è solo operazionalmente sbagliato.

Il commento nel `docker-compose.yml` del repo richiama esplicitamente
questo ADR.

## Vedi anche

- ETHICS-006 — il bug del matcher fuzzy che ha motivato il sync dei dati
  ad alto volume, rivelando il problema del volume stale.
- `Dockerfile` — layer `COPY --chown=atlaspi:atlaspi data/ data/`.
- `src/db/seed.py` — legge `data/entities/*.json` all'avvio quando
  `AUTO_SEED=true`.
- `scripts/backup.sh` — non dipende più da `/app/data/`; lavora solo
  contro `DATABASE_URL`.
