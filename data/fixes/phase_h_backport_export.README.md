# phase_h_backport_export.json — provenance

**Cos'è**: export **read-only** dello stato confine "solo-prod" usato da
`scripts/backport_phase_h_to_json.py` per riallineare il JSON sorgente alla
realtà-prod già revisionata (Wave 2 audit #7, vedi `docs/ethics/ETHICS-012`).

**Esportato il**: 2026-05-31, dal DB di produzione `cra-atlaspi-db`.

**Query** (`tmp_backport/export_divergent.sql`):

```sql
SELECT id, name_original, entity_type, year_start, boundary_source,
       boundary_geojson, boundary_aourednik_name, boundary_aourednik_year,
       boundary_aourednik_precision, boundary_ne_iso_a3, confidence_score, status
FROM geo_entities
WHERE boundary_source IN ('approximate_circle', 'historical_approximation');
```

**Contenuto**: 599 entità —
- **372** `approximate_circle` (cerchi capitale Phase H, `docs/boundary-review-v6.99.79/*.sql`)
- **227** `historical_approximation` (polygon storici disegnati a mano dalla
  iter-series, `scripts/sql_iter*_boundaries.sql` + `sql_manual_boundaries.sql`)

Entrambe le campagne erano state applicate via SQL **solo in prod**, mai nel
JSON → un seed fresco rigenerava ~22 super-group collision e perdeva gli
arricchimenti. Questo file è l'input deterministico del backport (idempotente).

`boundary_geojson` qui è già un oggetto GeoJSON annidato (lo `string` di psql è
stato risolto in fase di export per leggibilità). Nessuna modifica ai dati prod.
