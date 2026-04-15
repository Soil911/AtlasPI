# Template per nuovi ADR ed ETHICS record

## Template ADR

# ADR-XXX — Titolo breve

**Data**: YYYY-MM-DD
**Stato**: Bozza | In revisione | Accettato | Sostituito da ADR-YYY
**Autore**:
**Impatto**: Basso | Medio | Alto

## Contesto
Perché questa decisione è necessaria ora?

## Opzioni valutate
### Opzione A
Pro e contro.
### Opzione B
Pro e contro.

## Decisione
Abbiamo scelto X perché...

## Conseguenze
Cosa cambia? Cosa diventa più difficile? Più facile?

## Come riaprire questa decisione
In quali circostanze riconsiderare?

---

## Template ETHICS record

# ETHICS-XXX — Titolo del problema etico

**Data**: YYYY-MM-DD
**Stato**: Bozza | In revisione | Accettato
**Autore**:
**Impatto**: Basso | Medio | Alto

## Il problema
Qual è il dilemma etico concreto?
Quali rappresentazioni diverse sono possibili?
Quale sarebbe il danno di una scelta sbagliata?
Includi esempi storici specifici.

## Decisione
Come si riflette nella struttura dei dati o nel codice?

## Motivazioni
Perché questa scelta è più onesta delle alternative?

## Casi limite ancora aperti
Quali situazioni non sono risolte? Aprire nuovi ETHICS?

## Impatto sul codice
Esempio con commento # ETHICS: vedi ETHICS-XXX.

---

## Timeline unificato entità

Endpoint: `GET /v1/entities/{entity_id}/timeline`

Restituisce un unico stream cronologico che fonde tre sorgenti
distinte — `territory_changes`, `historical_events` (via
`event_entity_links`) e `chain_transitions` (derivate dalle
`DynastyChain` che includono l'entità). Ogni elemento dell'array
`timeline` ha un campo `kind` che disambigua la sorgente:
`territory_change` | `event` | `chain_transition`.

### Parametri

| Parametro | Tipo | Default | Descrizione |
|---|---|---|---|
| `include_entity_links` | bool (query) | `true` | Se `true`, include eventi con qualunque ruolo (MAIN_ACTOR, VICTIM, PARTICIPANT, AFFECTED, WITNESS, FOUNDED, DISSOLVED). Se `false`, restringe ai soli eventi dove l'entità è MAIN_ACTOR, FOUNDED o DISSOLVED — utile per "cosa ha fatto attivamente questa entità" senza rumore. |

### Oggetto `counts`

Aggregatore riassuntivo calcolato sui record effettivamente
inclusi nella risposta (dopo il filtro `include_entity_links`).
Permette all'agente AI di dimensionare la risposta senza
iterare l'array:
```json
{
  "events": 14,
  "territory_changes": 7,
  "chain_transitions": 2,
  "total": 23
}
```

### Payload di esempio

Entità: Impero Romano d'Occidente (id=42). Ordinamento:
cronologico per `year`, a parità di anno priorità
`event > territory_change > chain_transition` (solo per
stabilità di rendering, non ha valore semantico).

```json
{
  "entity_id": 42,
  "entity_name": "Imperium Romanum Occidentale",
  "entity_type": "empire",
  "year_start": 395,
  "year_end": 476,
  "counts": {
    "events": 2,
    "territory_changes": 1,
    "chain_transitions": 2,
    "total": 5
  },
  "timeline": [
    {
      "kind": "chain_transition",
      "year": 395,
      "chain_id": 3,
      "chain_name": "Roman Power Center",
      "chain_type": "SUCCESSION",
      "transition_type": "PARTITION",
      "is_violent": false,
      "direction": "inbound",
      "from_entity_id": 1,
      "from_entity_name": "Imperium Romanum",
      "to_entity_id": 42,
      "to_entity_name": "Imperium Romanum Occidentale",
      "description": "Divisione definitiva alla morte di Teodosio I",
      "ethical_notes": null
    },
    {
      "kind": "event",
      "year": 410,
      "year_end": null,
      "event_id": 118,
      "name_original": "Sacco di Roma",
      "name_original_lang": "it",
      "event_type": "BATTLE",
      "role": "VICTIM",
      "link_notes": null,
      "main_actor": "Visigoti sotto Alarico I",
      "known_silence": false,
      "confidence_score": 0.9,
      "status": "confirmed"
    },
    {
      "kind": "territory_change",
      "year": 439,
      "change_type": "LOSS",
      "region": "Africa Proconsolare",
      "description": "Conquista di Cartagine da parte dei Vandali",
      "population_affected": null,
      "confidence_score": 0.85
    },
    {
      "kind": "event",
      "year": 455,
      "year_end": null,
      "event_id": 131,
      "name_original": "Sacco di Roma (Vandali)",
      "name_original_lang": "it",
      "event_type": "COLONIAL_VIOLENCE",
      "role": "VICTIM",
      "link_notes": null,
      "main_actor": "Vandali sotto Genserico",
      "known_silence": false,
      "confidence_score": 0.88,
      "status": "confirmed"
    },
    {
      "kind": "chain_transition",
      "year": 476,
      "chain_id": 3,
      "chain_name": "Roman Power Center",
      "chain_type": "SUCCESSION",
      "transition_type": "CONQUEST",
      "is_violent": true,
      "direction": "outbound",
      "from_entity_id": 42,
      "from_entity_name": "Imperium Romanum Occidentale",
      "to_entity_id": 57,
      "to_entity_name": "Regnum Italiae (Odoacre)",
      "description": "Deposizione di Romolo Augustolo",
      "ethical_notes": null
    }
  ]
}
```

### Note etiche

- ETHICS-007: `event_type` e `role` sono preservati letteralmente.
  `GENOCIDE`, `COLONIAL_VIOLENCE`, `VICTIM` non vengono edulcorati
  in termini neutri.
- ETHICS-002: `transition_type` (CONQUEST, DECOLONIZATION,
  PARTITION, ecc.) e `is_violent` sono espliciti su ogni
  `chain_transition`.

---

## Ricerca fuzzy cross-script

Endpoint: `GET /v1/search/fuzzy?q=...&limit=...&min_score=...`

Ricerca fuzzy character-level su `name_original` e tutte le
`name_variants`. Funziona cross-script (greco, persiano, cinese,
cirillico, arabo) perché la metrica di similarità opera a livello
di carattere — utile per agenti AI che ricevono nomi approssimati
o traslitterazioni errate.

### Parametri

| Parametro | Tipo | Default | Descrizione |
|---|---|---|---|
| `q` | str (query, richiesto) | — | Testo da cercare, 1–200 caratteri. |
| `limit` | int (query) | 10 | Risultati massimi (1–50). |
| `min_score` | float (query) | 0.4 | Soglia minima di similarità. `0.0` = tutto, `1.0` = solo match esatti. Score è `SequenceMatcher.ratio()` + bonus (può superare 1.0, cappato in display). |

### Algoritmo di scoring

Per ogni candidato (`name_original` + ogni `name_variants.name`):

1. Base: `difflib.SequenceMatcher(None, q_norm, cand_norm).ratio()`
   — similarità character-level su stringhe lowercase/stripped.
2. `+0.10` se il candidato è `name_original` — ETHICS-001: il
   nome nella lingua locale ha priorità sulle varianti (che
   possono essere trascrizioni coloniali).
3. `+0.15` se uno è prefisso dell'altro (case-insensitive).
4. `+0.08` altrimenti se uno è sottostringa dell'altro —
   fallback per acronimi (es. "URSS" matcha nel nome esteso).

Il miglior score per entità è conservato, poi filtrato per
`min_score` e ordinato desc. Nel payload il campo `score` è
cappato a 1.0 per leggibilità — il ranking interno usa il
valore non-cappato per tie-breaking.

### Esempio

Query `q=safavid` restituisce (tra altri) l'entità persiana
`دولت صفویه` anche se la query è in ASCII — il ratio character-
level su "safavid" vs "safaviyeh" (variante latinizzata) è
elevato, e il +0.10 per match su `name_original` rispetto a
varianti europee spinge l'entità persiana in cima.

Request:
```
GET /v1/search/fuzzy?q=safavid&limit=5&min_score=0.4
```

Response:
```json
{
  "query": "safavid",
  "count": 3,
  "results": [
    {
      "id": 211,
      "name_original": "دولت صفویه",
      "name_original_lang": "fa",
      "matched_name": "Safaviyeh",
      "matched_is_original": false,
      "score": 1.0,
      "entity_type": "empire",
      "year_start": 1501,
      "year_end": 1736,
      "status": "confirmed",
      "confidence_score": 0.92
    },
    {
      "id": 305,
      "name_original": "Safavid Dynasty",
      "name_original_lang": "en",
      "matched_name": "Safavid Dynasty",
      "matched_is_original": true,
      "score": 0.82,
      "entity_type": "dynasty",
      "year_start": 1501,
      "year_end": 1736,
      "status": "confirmed",
      "confidence_score": 0.9
    },
    {
      "id": 412,
      "name_original": "Sarvabhauma",
      "name_original_lang": "sa",
      "matched_name": "Sarvabhauma",
      "matched_is_original": true,
      "score": 0.57,
      "entity_type": "kingdom",
      "year_start": 550,
      "year_end": 750,
      "status": "uncertain",
      "confidence_score": 0.6
    }
  ]
}
```

### Note etiche

- ETHICS-001: il bonus di `+0.10` su `name_original` privilegia
  sistematicamente il nome nella lingua locale. Una query in
  trascrizione coloniale matcha comunque, ma l'entità ranka col
  suo vero nome di identità (persiano, arabo, cinese, ecc.).
- `matched_is_original=false` è un segnale per l'agente AI che
  ha match su una variant (potenzialmente esonima o coloniale);
  `matched_name` riporta la stringa effettivamente matchata, così
  l'agente può risolvere ambiguità di trascrizione.
