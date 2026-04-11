# ADR-002 — Design dell'API: REST con output GeoJSON

**Data**: 2026-04-11
**Stato**: Accettato
**Autore**: Clirim
**Impatto**: Alto — definisce il contratto con i consumatori

## Contesto

L'API deve essere consumata principalmente da agenti AI,
non da umani. Questo cambia le priorità: semplicità e
prevedibilità del formato contano più della flessibilità.

Opzioni valutate:
1. REST con GeoJSON
2. GraphQL
3. gRPC

## Decisione

REST con output GeoJSON standard + metadati etici.

## Motivazioni

- GeoJSON è il formato geografico più diffuso e compreso
  dagli agenti AI per generare mappe
- REST è più semplice da consumare senza SDK dedicato
- GraphQL aggiunge complessità non giustificata a questo stadio
- gRPC è eccessivo per un MVP

## Struttura endpoint principale

GET /entity?name={nome}&year={anno}

Risposta:
{
  "entity": "string",
  "year": int,
  "name_original": "string",
  "name_original_lang": "string",
  "name_variants": [...],
  "capital": {"name": "string", "lat": float, "lon": float},
  "boundary_geojson": {...},
  "confidence_score": float,
  "status": "confirmed|uncertain|disputed",
  "territory_changes": [...],
  "sources": [...],
  "ethical_notes": "string"
}

## Conseguenze

Il formato è stabile — cambiarlo in futuro richiede versioning.
Introdurre /v2/ se necessario, non modificare /v1/.
