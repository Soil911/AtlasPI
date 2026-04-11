# ADR-001 — Scelta del database: PostgreSQL + PostGIS

**Data**: 2026-04-11
**Stato**: Accettato
**Autore**: Clirim
**Impatto**: Alto — decisione fondazionale, difficile da invertire

## Contesto

Il progetto richiede di archiviare e interrogare dati geografici
storici: poligoni di confini, punti (città, battaglie), linee
(rotte commerciali). Le query tipiche sono spaziali: "dammi tutto
ciò che era dentro i confini dell'Impero Ottomano nel 1550".

Opzioni valutate:
1. PostgreSQL + PostGIS
2. MongoDB
3. SQLite + Spatialite

## Decisione

Scegliamo PostgreSQL + PostGIS.

## Motivazioni

A favore di PostgreSQL + PostGIS:
- Query spaziali native (ST_Within, ST_Intersects, ST_Distance)
- Indici R-tree per performance su grandi volumi di poligoni
- Output GeoJSON diretto con ST_AsGeoJSON()
- Standard de facto per dati geografici in ambito accademico
- Supporto nativo per range di date, utile per storia

Contro MongoDB:
- Query spaziali meno mature di PostGIS
- Nessun vantaggio reale per questo caso d'uso

Contro SQLite:
- Non scala oltre un singolo server
- Concorrenza limitata per API multi-utente

## Conseguenze

- Ogni developer deve avere PostgreSQL + PostGIS localmente
- Il deploy richiede un'istanza PostgreSQL
- Costo leggermente maggiore rispetto a SQLite, giustificato

## Riapertura

Valutare TimescaleDB se il volume supera i 500 GB.
