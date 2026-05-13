# ADR-009 — `boundary_geom` PostGIS Geometry column

**Status**: Accettato v6.94.0 (2026-05-13)
**Autori**: audit architetturale 2026-05-13 (R1)
**Deciders**: Clirim Ramadani
**Riferimenti**: ADR-001 (PostgreSQL+PostGIS), ETHICS-005 (boundary provenance)

---

## Contesto

ADR-001 (2026-04-11) ha scelto PostgreSQL+PostGIS per supportare query
spaziali native (ST_Within, ST_Intersects, ST_DWithin). Tuttavia, la
colonna `geo_entities.boundary_geojson` è stata implementata come `Text`
(JSON serializzato) per compatibilità con SQLite in dev. Conseguenze:

- Le query "trova tutte le entità che contengono il punto (lat, lon)
  nel polygon" richiedono runtime `ST_GeomFromGeoJSON(boundary_geojson)`
  → parsing JSON per ogni riga → no indice spaziale sfruttabile.
- Il piano di esecuzione PostgreSQL fa **seq scan** anche con `ST_Within`,
  perché il geom è derivato da una colonna Text non indicizzata.
- `/v1/nearby` (ST_DWithin su capital point) gira a ~20ms p95 perché usa
  un indice GiST su `lat,lon` punto. Ma `/v1/entities?contains=lat,lon`
  non esiste ancora — e quando esisterà, sarà O(n) senza questa
  migrazione.

La roadmap v6.24 ("POSTGIS SPATIAL OPTIMIZATION") elenca proprio questo
come target p95 < 50ms. Senza colonna Geometry indicizzata, è
irraggiungibile sopra ~500 entità con polygon (oggi ~700 entità con
boundary_geojson reale).

## Decisione

Aggiungere una colonna PostGIS `boundary_geom GEOMETRY(MULTIPOLYGON, 4326)`
**affiancata** a `boundary_geojson Text`, con indice GiST. La colonna
viene popolata da `boundary_geojson` via `ST_GeomFromGeoJSON()` al
backfill e mantenuta sincrona da un guard al boot.

### Schema target (PostgreSQL)

```sql
ALTER TABLE geo_entities
    ADD COLUMN boundary_geom geometry(MultiPolygon, 4326);

CREATE INDEX idx_geo_entities_boundary_geom
    ON geo_entities USING GIST(boundary_geom);

-- Backfill iniziale
UPDATE geo_entities
SET boundary_geom = ST_Multi(ST_GeomFromGeoJSON(boundary_geojson))
WHERE boundary_geojson IS NOT NULL AND boundary_geojson != '';
```

`ST_Multi()` wrappa un singolo Polygon in MultiPolygon — necessario
perché molte boundary_geojson sono `Polygon` semplice, ma la colonna
è dichiarata `MultiPolygon` per uniformità.

### Compatibilità SQLite

SQLite dev environment **non** crea la colonna. SQLAlchemy ORM non
mappa `boundary_geom` (vedi "ORM strategy" sotto). Tutte le query
spaziali che usano `boundary_geom` sono via `text("...")` con
controllo `if is_postgres` upstream.

Trade-off: doppio code path per query spatial in `is_postgres` vs
`is_sqlite`. Costo accettato — SQLite era già un environment "best
effort" per le query spaziali (haversine math manuale dove serviva).

### ORM strategy: NON mappare `boundary_geom` in SQLAlchemy

Opzioni considerate:

#### Opzione A — Mappare via `geoalchemy2.Geometry`

```python
from geoalchemy2 import Geometry

class GeoEntity(Base):
    ...
    boundary_geom: Mapped[Any | None] = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326),
        nullable=True,
    )
```

**Pro**: query Pythoniche `db.query(GeoEntity).filter(GeoEntity.boundary_geom.ST_Within(...))`.
**Contro**: aggiunge dep `geoalchemy2` + comportamento incerto su SQLite
(geoalchemy2 fa fallback ma non testato sul nostro setup CI dual-DB).
Rischio: import error o type mismatch in dev.

#### Opzione B — Colonna gestita solo da Alembic + query raw

```python
# Nessuna mappatura ORM. La colonna esiste a livello DB ma non in models.py.
# Query spatial usano raw SQL:
db.execute(text("""
    SELECT id, name_original FROM geo_entities
    WHERE ST_Within(ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), boundary_geom)
    LIMIT 50
"""), {"lon": lon, "lat": lat})
```

**Pro**: zero impatto su SQLite. Nessuna dipendenza aggiunta. Massima
chiarezza su quale code path è PostGIS-only.
**Contro**: query spaziali non type-safe. Un endpoint che usa
`boundary_geom` deve `if is_postgres` check.

**Adopted: Opzione B.** L'opzione A è seducente ma il costo di
debugging quando geoalchemy2 si comporta diverso su SQLite vs Postgres
non vale i benefici. AtlasPI ha pochissimi endpoint che richiedono
spatial query reali (`/v1/nearby`, futura `/v1/entities?contains=`).
Quei 2-3 endpoint possono raw-SQL senza pena.

### Sincronia boundary_geojson ↔ boundary_geom

**Decisione**: backfill periodico al boot (idempotente), non trigger SQL.

#### Opzione X — Trigger SQL ON UPDATE/INSERT

```sql
CREATE TRIGGER sync_boundary_geom
    BEFORE INSERT OR UPDATE OF boundary_geojson ON geo_entities
    FOR EACH ROW
    EXECUTE FUNCTION update_boundary_geom();
```

**Pro**: sincronia garantita a transazione.
**Contro**: trigger DB-specific. SQLite non ha PL/pgSQL. Rollback
complesso. Errore in trigger fa fallire l'INSERT/UPDATE (es. polygon
geometricamente invalido → tutto il batch fail).

#### Opzione Y — ORM event listener Python

```python
@event.listens_for(GeoEntity, "before_update")
def _sync_geom(mapper, conn, target):
    if is_postgres and target.boundary_geojson:
        conn.execute(
            text("UPDATE geo_entities SET boundary_geom = ST_Multi(ST_GeomFromGeoJSON(:gj)) WHERE id = :id"),
            {"gj": target.boundary_geojson, "id": target.id},
        )
```

**Pro**: agnostico DB (skip su SQLite).
**Contro**: race condition possibili se la transazione è già in
commit. Test fragile.

#### Opzione Z — Backfill batch periodico (adopted)

`src/ingestion/boundary_guards.py::sync_boundary_geom_from_geojson()`
chiamato al boot del container, idempotente:

```sql
UPDATE geo_entities
SET boundary_geom = ST_Multi(ST_GeomFromGeoJSON(boundary_geojson))
WHERE boundary_geojson IS NOT NULL
  AND (boundary_geom IS NULL  -- mai sincronizzato
       OR ST_AsGeoJSON(boundary_geom) != boundary_geojson  -- drift)
;
```

**Pro**: zero overhead durante INSERT/UPDATE normale. Drift recovery
automatico. SQLite-safe (skip su `is_sqlite`).
**Contro**: window di inconsistenza fino al prossimo restart del
container. Per AtlasPI questo è ~daily (deploy frequency). Per query
spaziali aggiornate a runtime, non un problema reale (le boundary
cambiano raramente, e quando cambiano è via ingestion pipeline che
fa il sync esplicito).

**Adopted: Opzione Z.**

### Backfill iniziale (one-shot, in Alembic migration)

La migration `019_boundary_geom_postgis.py` esegue:
1. `ADD COLUMN boundary_geom geometry(MultiPolygon, 4326)`
2. `CREATE INDEX ... USING GIST(boundary_geom)`
3. `UPDATE geo_entities SET boundary_geom = ST_Multi(ST_GeomFromGeoJSON(boundary_geojson))`

Su ~700 righe con polygon, è ~2-5s. Accettabile per il startup del
container post-migrazione.

### Edge cases

- **Polygon geometricamente invalido** (self-intersect, hole esterno):
  `ST_GeomFromGeoJSON()` lo accetta. `ST_Within()` lo gestisce.
  Se invece la conversione fallisse, il backfill UPDATE setterebbe NULL
  per quella riga (CATCH via `WHERE ST_IsValid(ST_GeomFromGeoJSON(...))`
  o `EXCEPTION` handler). Per ora: lasciar fallire visibilmente.
- **GeoJSON non-Polygon** (Point, LineString): non dovrebbero esistere
  in `geo_entities.boundary_geojson` (campo per polygon territoriali).
  Se ce ne sono, fix nel dataset prima del backfill.
- **Antimeridian-crossing**: `fix_antimeridian_and_wrong_polygons.py`
  già normalizza prima del boot. La colonna `boundary_geom` riceverà
  versione già clippata.

## Alternative considerate

### Alt 1 — Sostituire `boundary_geojson` direttamente con `boundary_geom`

**Rejected.** Avrebbe richiesto rewrite di tutti gli endpoint che
serializzano boundary in response JSON (`ST_AsGeoJSON()` ovunque),
oltre a rompere SQLite dev. Mantenere entrambe le colonne è additive
ed elimina retrocompat issue.

### Alt 2 — Calcolare geometry on-the-fly senza colonna materializzata

```sql
SELECT * FROM geo_entities
WHERE ST_Within(point, ST_GeomFromGeoJSON(boundary_geojson));
```

**Rejected.** Funziona ma è esattamente il problema iniziale: nessun
indice possibile. ST_GeomFromGeoJSON ricalcola per ogni riga. p95 non
scala oltre ~500 entità.

### Alt 3 — Storage GeoJSON externalizzato (es. Cloudflare R2)

Storage e' geojson grossi su R2, indici locali su PostGIS solo per id+geom.

**Rejected per ora.** Aggiunge dipendenza esterna + latency I/O per
fetch. AtlasPI ha ~700 boundary di max ~50KB ciascuno → ~35MB totali
in DB, gestibile. R2 ha senso se boundary salgono a milioni.

### Alt 4 — Hybrid: PostGIS Geometry materializzata + sync via backfill (adopted)

**Adopted.** Best trade-off: indice spatiale efficace + zero overhead
runtime su INSERT/UPDATE + SQLite-safe + drift recovery automatico.

## Conseguenze

### Positive

- **Query `?contains=lat,lon` ora indicizzata**. `EXPLAIN ANALYZE` su
  `WHERE ST_Within(point, boundary_geom)` userà l'indice GiST.
  Target p95 < 50ms su 1000+ entità diventa raggiungibile.
- **Backward compat totale**. `/v1/entities` continua a serializzare
  `boundary_geojson` invariato. Nessun consumer è impattato.
- **Foundation per R11** (tabella `geographic_regions` con polygon
  PostGIS): stesso pattern.
- **Foundation per future query spaziali avanzate**: `/v1/entities?intersects=`,
  `/v1/entities/contemporaries-overlapping-territory`, ecc.

### Negative

- **Storage +50% per boundary in Postgres**. Boundary GeoJSON Text ~50KB
  → Geometry compressa ~20-30KB. Doppia rappresentazione = ~70-80KB per
  riga × 700 righe = ~50MB in più. Trascurabile (DB attuale ~200MB).
- **CI postgres-migrations job ora più lento** (~2-5s di backfill nel
  migration). Sotto il timeout di 5min.
- **Doppio code path PostGIS vs SQLite** per query spatial. Manutenzione
  ridotta perché solo 2-3 endpoint hanno spatial query.

### Trade-off di dev experience

Dev locale con SQLite **non** ha le query spatial nuove. Per testarle
serve Postgres+PostGIS locale (via `docker compose up -d db` quando si
lavora su endpoint spatial). Accettato — gli endpoint spatial sono
edge case, non workflow quotidiano.

## Stato implementation

| Componente | Status |
|-----------|--------|
| ADR-009 (questo documento) | ✅ v6.94.0 |
| Alembic migration 019 (ADD COLUMN + GIST + backfill) | ✅ v6.94.0 |
| `boundary_guards.sync_boundary_geom_from_geojson()` al boot | ✅ v6.94.0 |
| Test in CI postgres-migrations (alembic upgrade head verifica) | ✅ v6.94.0 |
| Endpoint `/v1/entities?contains=lat,lon` usa indice GiST | ⏳ TODO v6.94.1 |
| Trigger PostgreSQL ON UPDATE (se serve real-time sync) | ⏳ valutare post-launch |
| Migrazione storage R2 (Alt 3) | ⏳ post-MVP, solo se boundary >10MB ciascuno |

## Riapertura

Riapertura prevista se:
- Postgres backfill al boot diventa >30s (boundary count >5000, oggi
  ~700). Considerare migration incrementale.
- Si decide di sostituire `boundary_geojson` Text con `boundary_geom`
  come source-of-truth (richiede ADR per breaking change interno,
  rewrite seed/export).
- SpatiaLite diventa supportabile in CI per allineare SQLite dev a
  query spatial reali.
