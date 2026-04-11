# AtlasPI — Documentazione API

Base URL: `http://localhost:10100`
Documentazione interattiva: `http://localhost:10100/docs`

## Autenticazione

Nessuna. L'API e' pubblica in lettura.

## Rate limiting

60 richieste/minuto per IP. Header `X-RateLimit-Remaining` indica le richieste residue.

## Endpoint

### GET /health

Stato di salute del servizio.

```bash
curl http://localhost:10100/health
```

Risposta:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "database": "sqlite:connected",
  "entity_count": 10
}
```

### GET /v1/entity

Endpoint principale (ADR-002). Cerca entita' per nome, anno, status.

Parametri:
- `name` (string, max 200) — Ricerca parziale in name_original e name_variants
- `year` (int, -4000..2100) — Anno di riferimento (negativo = a.C.)
- `status` (string) — confirmed, uncertain, disputed
- `limit` (int, 1..100, default 20) — Risultati per pagina
- `offset` (int, >= 0) — Offset paginazione

```bash
# Cerca per nome
curl "http://localhost:10100/v1/entity?name=Ottoman"

# Filtra per anno
curl "http://localhost:10100/v1/entity?year=1500"

# Solo territori contestati
curl "http://localhost:10100/v1/entity?status=disputed"

# Combinato con paginazione
curl "http://localhost:10100/v1/entity?year=100&limit=5&offset=0"
```

### GET /v1/entities

Elenco paginato di tutte le entita'.

```bash
curl "http://localhost:10100/v1/entities?limit=5"
```

### GET /v1/entities/{id}

Dettaglio completo di una singola entita'.

```bash
curl http://localhost:10100/v1/entities/2
```

## Formato risposta entita'

```json
{
  "id": 1,
  "entity_type": "empire",
  "year_start": -27,
  "year_end": 476,
  "name_original": "Imperium Romanum",
  "name_original_lang": "la",
  "name_variants": [...],
  "capital": {"name": "Roma", "lat": 41.9028, "lon": 12.4964},
  "boundary_geojson": {"type": "MultiPolygon", "coordinates": [...]},
  "confidence_score": 0.90,
  "status": "confirmed",
  "territory_changes": [...],
  "sources": [...],
  "ethical_notes": "..."
}
```

## Codici errore

| Codice | Significato |
|--------|------------|
| 200 | Successo |
| 404 | Entita' non trovata |
| 422 | Parametri non validi |
| 429 | Rate limit superato |
| 500 | Errore interno |

Formato errore:
```json
{
  "error": true,
  "detail": "Descrizione dell'errore",
  "request_id": "abc123def456"
}
```

## Header notevoli

- `X-Request-ID` — ID univoco della richiesta (per debugging)
- `Cache-Control: public, max-age=3600` — Dati storici cacheable
- `X-Content-Type-Options: nosniff` — Security header
- `X-Frame-Options: DENY` — Security header
