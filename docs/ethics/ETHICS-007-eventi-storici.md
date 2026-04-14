# ETHICS-007 — Rappresentazione di eventi storici discreti

**Data**: 2026-04-15
**Stato**: Accettato
**Autore**: Pianificazione v6.3 (Claude Code, con Clirim Ramadani)
**Impatto**: Strutturale — introduce una nuova entità di primo livello

## Contesto

AtlasPI v6.2 copre entità geopolitiche e i loro cambiamenti
territoriali. Ma molti eventi storici hanno una realtà puntuale
(battaglie, trattati, crisi, eruzioni, epidemie, scoperte, morti di
sovrani) che non si mappa bene sulla tabella `territory_changes`:

- Una battaglia può coinvolgere più entità come contendenti.
- Un trattato crea o scioglie entità (le `territory_changes` si
  riferiscono sempre a una singola entità).
- Un'epidemia (peste nera, vaiolo in Mesoamerica, influenza del 1918)
  non ha un'entità proprietaria.
- Un terremoto, una carestia o l'esplosione di un vulcano (Thera,
  Tambora, Krakatoa) hanno impatto su più popolazioni.

La v6.3 introduce una tabella `historical_events` di primo livello,
distinta da `territory_changes`, con una junction many-to-many verso
`geo_entities` (`event_entity_links`).

## Rischi etici

Una volta che esiste uno schema per "evento storico", ogni scelta
lessicale diventa politica.

### 1. Il framing dell'evento

Esempio: come definire il 1453?

- "Fall of Constantinople" (narrativa occidentale)
- "Fetih" / conquista (narrativa ottomana)
- "Άλωση της Κωνσταντινουπόλεως" (narrativa greca)

Ognuna di queste descrizioni non è neutrale. La tabella deve
permettere **tutte e tre** con lingua + prospettiva documentata.

### 2. Tipo dell'evento

La lista enum `EventType` deve includere termini scomodi senza
eufemismi:

- `GENOCIDE` — non "massacre", non "conflict".
- `ETHNIC_CLEANSING` — non "population exchange".
- `FAMINE` — non "food crisis".
- `COLONIAL_VIOLENCE` — non "pacification".

Se una fonte accademica usa il termine "genocide" (anche se
contestato politicamente da uno stato), il tipo nel DB è `GENOCIDE`.
Lo stato politico di un termine non prevale sul consenso storico.

### 3. Attore e vittima

I campi `main_actor` e `affected_entities` rendono ESPLICITO chi
ha fatto cosa a chi. Il linguaggio passivo ("X was conquered", "Y
was liberated") è vietato nelle descrizioni — usa la voce attiva.

Esempio errato:
> "Armenia was emptied of its population in 1915."

Esempio corretto:
> "The Ottoman government ordered the deportation and killing
> of Armenian civilians in 1915-1923, an event academically
> documented as the Armenian Genocide."

### 4. Numeri di vittime

I campi numerici (`casualties_low`, `casualties_high`,
`casualties_source`) documentano un **range** con la fonte, non
un valore puntuale. I numeri sono spesso pretesto politico:

- Nanking: stime da 40k (negazionismo giapponese) a 300k (RPC).
- Holodomor: stime da 3M (URSS) a 10M (storiografia ucraina).
- Massacro delle Fosse Ardeatine: 335 documentato al certo.

Il DB deve riflettere il range + fonti, non imporre una cifra.

### 5. Eventi non documentati per i vincitori

La Storia è scritta dai vincitori, e i silenzi sono rilevanti.
Eventi ben noti oralmente ma cancellati dalle fonti scritte
vengono trattati in ETHICS-008. In ETHICS-007 il punto è:
**non escludere** un evento solo perché è sotto-documentato.

## Decisioni

### 1. Schema del modello

```python
class HistoricalEvent(Base):
    __tablename__ = "historical_events"

    id: int
    name_original: str              # nome nella lingua originale/locale
    name_original_lang: str         # ISO 639
    event_type: str                 # enum EventType (vedi sotto)
    year: int                       # anno principale
    year_end: int | None            # per eventi multi-anno
    location_name: str | None       # toponimo evento
    location_lat: float | None
    location_lon: float | None
    main_actor: str | None          # CHI ha fatto l'evento
    description: str                # voce attiva, niente eufemismi
    casualties_low: int | None
    casualties_high: int | None
    casualties_source: str | None   # citazione della stima
    confidence_score: float         # 0.0-1.0
    status: str                     # confirmed / uncertain / disputed
    ethical_notes: str | None
```

### 2. EventType enum

```
BATTLE
SIEGE
TREATY
REBELLION
REVOLUTION
CORONATION
DEATH_OF_RULER
MARRIAGE_DYNASTIC
FOUNDING_CITY
FOUNDING_STATE
DISSOLUTION_STATE
CONQUEST
COLONIAL_VIOLENCE     # invece di "pacification"
GENOCIDE              # NON massacre né conflict
ETHNIC_CLEANSING      # NON population exchange
MASSACRE              # per eventi < scala genocide
DEPORTATION
FAMINE                # NON food crisis
EPIDEMIC
EARTHQUAKE
VOLCANIC_ERUPTION
TSUNAMI
FLOOD
DROUGHT
FIRE
EXPLORATION           # scoperta geografica (con attento framing)
TRADE_AGREEMENT
RELIGIOUS_EVENT       # conversione di massa, scisma, etc.
INTELLECTUAL_EVENT    # pubblicazione di opera fondamentale
TECHNOLOGICAL_EVENT   # invenzione, adozione di tecnologia
OTHER
```

### 3. EventEntityLink — ruolo esplicito

```python
class EventEntityLink(Base):
    __tablename__ = "event_entity_links"

    event_id: int
    entity_id: int
    role: str                # enum EventRole
    # MAIN_ACTOR | VICTIM | PARTICIPANT | AFFECTED | WITNESS | FOUNDED | DISSOLVED
```

Un trattato ha di solito due `PARTICIPANT`.
Una battaglia ha un `MAIN_ACTOR` e uno o più `AFFECTED` o `VICTIM`.
Un'epidemia ha solo `AFFECTED`.
Una fondazione di stato ha un `FOUNDED` sulla nuova entità.

### 4. Name variants per eventi

Come per `GeoEntity`, ogni evento può avere nomi alternativi:
- "Fall of Constantinople" (EN, contesto occidentale)
- "Fetih" (TR, contesto ottomano)
- "Άλωση" (GR, contesto greco)
- "1453 conquest" (neutro)

v6.3 accetta più nomi nel campo `name_variants` (JSON list, non
una tabella separata — volumi più bassi rispetto a GeoEntity).

### 5. Confidence & status

- `confidence_score` segue la stessa scala di GeoEntity (0.0-1.0).
- `status = "disputed"` se c'è disaccordo accademico sostanziale
  sul fatto che l'evento sia avvenuto o sul suo caratterizzazione
  (es. numeri delle vittime di Nanking, definizione di genocidio
  per un dato evento, etc.).
- Eventi `disputed` hanno cap confidence = 0.70 (ETHICS-003 analogia).

## Esempi di seed

**Esempio 1 — Battaglia di Manzikert (1071)**
```json
{
  "name_original": "Malazgirt Muharebesi",
  "name_original_lang": "tr",
  "event_type": "BATTLE",
  "year": 1071,
  "location_name": "Malazgirt, modern Muş province",
  "location_lat": 39.14, "location_lon": 42.54,
  "main_actor": "Seljuk Empire",
  "description": "Seljuk forces under Alp Arslan defeated a Byzantine army led by Emperor Romanos IV Diogenes. The battle destabilized Byzantine control of Anatolia and opened the region to Turkic settlement.",
  "casualties_low": 2000, "casualties_high": 8000,
  "casualties_source": "Cahen, C. (1968). Pre-Ottoman Turkey.",
  "confidence_score": 0.9,
  "status": "confirmed"
}
```

**Esempio 2 — Caduta di Tenōchtitlan (1521)**
```json
{
  "name_original": "Huey Tlacohcholōliztli",
  "name_original_lang": "nah",
  "event_type": "CONQUEST",
  "year": 1521,
  "year_end": 1521,
  "location_name": "Tenōchtitlan (Mexico City)",
  "location_lat": 19.43, "location_lon": -99.13,
  "main_actor": "Spanish conquistadores (Hernán Cortés) and Tlaxcaltec allies",
  "description": "Spanish forces and Tlaxcaltec allies besieged and destroyed Tenōchtitlan, capital of the Aztec Triple Alliance. Smallpox, brought by Spanish forces, had already killed a substantial fraction of the Mexica population. The Spanish then systematically demolished the city and built Mexico City on its ruins.",
  "casualties_low": 100000, "casualties_high": 240000,
  "casualties_source": "Restall, M. (2003). Seven Myths of the Spanish Conquest.",
  "confidence_score": 0.85,
  "status": "confirmed",
  "ethical_notes": "Date documented from both Spanish and Nahua sources (Sahagún, Aubin Codex). Casualty estimates include direct combat deaths plus smallpox deaths."
}
```

**Esempio 3 — Genocidio armeno (1915-1923)**
```json
{
  "name_original": "Հայոց ցեղասպանություն",
  "name_original_lang": "hye",
  "event_type": "GENOCIDE",
  "year": 1915,
  "year_end": 1923,
  "location_name": "Ottoman Empire (primarily Anatolia)",
  "main_actor": "Ottoman government (Committee of Union and Progress)",
  "description": "The Ottoman government, under the Committee of Union and Progress, ordered and organized the mass deportation and killing of Armenian civilians across the empire. The events constitute the Armenian Genocide, academically documented and recognized by most Western and Armenian historians.",
  "casualties_low": 600000, "casualties_high": 1500000,
  "casualties_source": "Akçam, T. (2012). The Young Turks' Crime against Humanity.",
  "confidence_score": 0.95,
  "status": "disputed",
  "ethical_notes": "Academic consensus classifies this as genocide (IAGS 1997, most university scholars). Turkey officially denies the genocide classification. The 'disputed' status here reflects the political controversy, NOT the historical-academic consensus."
}
```

Nota l'uso esplicito del termine `GENOCIDE`, con `status = "disputed"`
a livello politico ma `confidence_score = 0.95` a livello storico.

## Implementazione

- Migration `alembic/versions/003_historical_events.py`
- Modello `src/db/models.py::HistoricalEvent` + `EventEntityLink`
- Enum `src/db/enums.py::EventType` + `EventRole`
- API `src/api/routes/events.py`:
  - `GET /v1/events` — list + filter
  - `GET /v1/events/{id}` — detail
  - `GET /v1/entities/{id}/events` — events per entity
  - estensione `GET /v1/snapshot/{year}` per includere eventi puntuali
- Seed `src/db/seed.py` → importa `data/events/batch_*.json`
- 100+ eventi iniziali: battaglie, trattati, genocidi, epidemie,
  eruzioni, carestie, rivolte — copertura per periodo e regione.

## Lezione generale

Una rappresentazione "neutrale" non esiste. Lo schema DEVE permettere
la differenza di framing (name_variants), il range di vittime
(casualties_low/high), la voce attiva obbligatoria nelle descrizioni
e l'uso di terminologia accademica anche quando politicamente
contestata.

## Vedi anche

- ETHICS-002: cambi territoriali (tipologia dei conflitti)
- ETHICS-008: eventi cancellati e silenzi delle fonti
- `src/db/models.py::HistoricalEvent`
- `src/api/routes/events.py`
