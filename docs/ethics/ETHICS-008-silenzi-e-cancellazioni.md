# ETHICS-008 — Silenzi delle fonti e cancellazione storica

**Data**: 2026-04-15
**Stato**: Accettato
**Autore**: Pianificazione v6.3 (Claude Code, con Clirim Ramadani)
**Impatto**: Trasversale — riguarda come rappresentiamo la mancanza di dati

## Contesto

Un database storico che elenca solo ciò che è documentato eredita i
bias delle fonti. La storia scritta è sistematicamente parziale:

- **Conquistatori cancellano i vinti**: dopo la conquista assira
  di Samaria (722 a.C.), le Dieci Tribù di Israele scompaiono
  dalla documentazione scritta. Cronache assire elencano la
  deportazione; cronache israelite di quel regno non esistono.
- **Archivi coloniali bruciano**: il governo britannico ha distrutto
  sistematicamente documenti coloniali al momento dell'indipendenza
  (Operation Legacy, 1948-1966). Molti eventi della decolonizzazione
  sono documentati solo nelle fonti locali (orali).
- **Oralità viene svalorizzata**: storie orali di tradizioni
  africane, indigene americane, aborigene australiane sono state a
  lungo escluse dal "canone" storico accademico occidentale.
- **Negazionismo di stato**: il genocidio hererno-nama (1904-08) è
  stato ufficialmente riconosciuto dalla Germania solo nel 2021.
  Per 113 anni l'archivio "ufficiale" tedesco lo negava.
- **Cancellazione letterale**: Akhenaten e il periodo di Amarna
  furono cancellati dagli annali egizi subito dopo la sua morte.

Un database che indicizza solo "eventi documentati" riproduce
questo silenzio. AtlasPI deve invece **nominare il silenzio**
come un fatto storico di primo livello.

## Rischi di ignorare il problema

Senza ETHICS-008, AtlasPI rischia:

1. **Bias di fonte**: eventi coperti da archivi occidentali
   dominano il DB; eventi coperti solo da oralità o fonti
   non-latine spariscono.
2. **Confidence engineering al contrario**: eventi ben documentati
   dai conquistatori ricevono `confidence_score = 0.9`, mentre
   eventi meno documentati ma storicamente significativi
   ricevono score bassi e finiscono in fondo agli ordinamenti.
   Un agente AI che interroga "eventi importanti del 1904" riceve
   la risposta filtrata dai bias dell'archivio tedesco.
3. **Riproducibilità dell'ingiustizia**: se il DB è consumato per
   training di modelli storici, riproduce i bias a valle.

## Decisione

### 1. Campo `known_silence` sul modello HistoricalEvent

```python
class HistoricalEvent(Base):
    ...
    known_silence: bool = False
    silence_reason: str | None = None  # testo libero, documentazione
```

Un evento è marcato `known_silence = True` quando:

- Esistono fonti NON-contemporanee che documentano l'evento,
  ma le fonti contemporanee del potere dominante sono assenti o
  lo negano.
- Esiste tradizione orale forte, ma non documentazione scritta
  contemporanea.
- L'evento è stato attivamente cancellato dagli archivi (Amarna,
  Operation Legacy, Holodomor pre-Gorbachev).

In questi casi `confidence_score` NON viene abbassato per il
silenzio stesso. Il silenzio è documentato separatamente; la
confidence riflette la solidità delle fonti alternative
(orali, archeologiche, riferimenti indiretti).

### 2. Field `oral_tradition_sources` complementare

```python
sources: [
    {"citation": "...", "source_type": "academic"},
    {"citation": "Oral tradition recorded by X (ethnographer) in year Y",
     "source_type": "oral_tradition"}
]
```

Estensione del `SourceType` enum:

```
PRIMARY
SECONDARY
ACADEMIC
ORAL_TRADITION     # NUOVO
ARCHAEOLOGICAL     # NUOVO
INDIRECT_REFERENCE # NUOVO
```

`ORAL_TRADITION` non è inferiore a `ACADEMIC` — entrambi sono
evidence valide con caratteristiche diverse.

### 3. Eventi di cancellazione esplicita

Alcuni silenzi sono essi stessi eventi storici. Es.:

- "Cancellazione degli annali di Amarna" (~1320 a.C.): evento
  di tipo `INTELLECTUAL_EVENT` con descrizione dell'atto di
  cancellazione.
- "Operation Legacy" (1948-1966): evento di tipo
  `INTELLECTUAL_EVENT` / `COLONIAL_VIOLENCE` sulla distruzione
  sistematica di archivi coloniali britannici.
- "Damnatio memoriae" di Geta (212 d.C.): rimozione dal registro
  imperiale romano.

Questi eventi vanno nel DB come eventi di pieno diritto, con
descrizione esplicita dell'atto di cancellazione.

### 4. Prospective queries

L'API deve permettere di filtrare:

```
GET /v1/events?known_silence=true
GET /v1/events?source_type=oral_tradition
```

Un ricercatore deve poter estrarre TUTTI gli eventi che dipendono
da fonti non-occidentali, o TUTTI gli eventi documentati come
attivamente cancellati. Queste query sono prime class nella API.

### 5. Esempio di seed — evento di silenzio

```json
{
  "name_original": "Operation Legacy",
  "name_original_lang": "en",
  "event_type": "INTELLECTUAL_EVENT",
  "year": 1948,
  "year_end": 1966,
  "location_name": "UK colonies (global)",
  "main_actor": "UK Colonial Office",
  "description": "The UK Colonial Office systematically destroyed or repatriated sensitive documents from colonies approaching independence. Documents recording torture, detention, and killings during independence movements (Kenya, Malaya, Cyprus, etc.) were burned, dumped at sea, or hidden in the Hanslope Park archive until partially released by court order in 2011-2013.",
  "casualties_low": null,
  "casualties_high": null,
  "casualties_source": null,
  "confidence_score": 0.95,
  "status": "confirmed",
  "known_silence": false,
  "ethical_notes": "Though this event itself is well-documented post-2011, it CAUSED the silencing of many other colonial-era events. Entities and events downstream of 1948-1966 British colonial administration carry partial-archive risk: their 'confidence_score' may be depressed because primary documentation was destroyed, not because the event didn't happen.",
  "sources": [
    {"citation": "Elkins, C. (2005). Imperial Reckoning: The Untold Story of Britain's Gulag in Kenya.", "source_type": "academic"},
    {"citation": "Anderson, D. (2011). Histories of the Hanged.", "source_type": "academic"},
    {"citation": "FCO Migrated Archives, partially released by UK High Court order 2011.", "source_type": "primary"}
  ]
}
```

### 6. Esempio di seed — evento con silenzio

```json
{
  "name_original": "Herero and Nama genocide",
  "name_original_lang": "en",
  "event_type": "GENOCIDE",
  "year": 1904,
  "year_end": 1908,
  "location_name": "German South-West Africa (modern Namibia)",
  "main_actor": "Imperial German Army (Lothar von Trotha, Vernichtungsbefehl)",
  "description": "German colonial forces under General von Trotha issued an extermination order (Vernichtungsbefehl) against the Herero and Nama peoples. Survivors of direct killings were driven into the Omaheke desert where most died of thirst, or placed in concentration camps (Konzentrationslager — the earliest documented German use of the term) on Shark Island and elsewhere. The genocide killed an estimated 65-80% of the Herero population and 50% of the Nama.",
  "casualties_low": 34000,
  "casualties_high": 110000,
  "casualties_source": "Zimmerer, J. (2004) & Olusoga, D. (2010)",
  "confidence_score": 0.9,
  "status": "confirmed",
  "known_silence": true,
  "silence_reason": "German government officially denied genocide classification for 113 years (1908-2021). Contemporary German archival record downplayed or omitted the scale of killings. The event is primarily documented today via survivor testimony, ethnographic record, and later German academic work — not via the contemporary German colonial archive.",
  "ethical_notes": "Germany formally recognized the genocide in May 2021 and agreed to reparations. Recognition does NOT retroactively fix the century of silence from official sources."
}
```

## Implementazione

- Campo `known_silence` e `silence_reason` sul modello
  `HistoricalEvent`
- Estensione `SourceType` enum con `ORAL_TRADITION`,
  `ARCHAEOLOGICAL`, `INDIRECT_REFERENCE`
- Filtri API: `?known_silence=true`, `?source_type=oral_tradition`
- Almeno 10 eventi di seed marcati come silence (armeno, hererno-nama,
  Holodomor pre-1991, Operation Legacy, Amarna, Geta damnatio,
  incendio biblioteca di Alessandria come "cancellazione intellettuale",
  massacri di Nanking-nell'archivio-giapponese, Katyn pre-1990,
  popolazione Tasmania aboriginal)

## Lezione generale

**La mancanza di fonti non prova l'assenza di eventi.** Rappresentare
onestamente l'archivio storico richiede di:

1. Nominare i silenzi come fatti.
2. Trattare oralità e archeologia come evidence di pari dignità.
3. Rendere i silenzi interrogabili via API, non nasconderli dietro
   `confidence_score` bassi.

## Vedi anche

- ETHICS-001: nomi contestati
- ETHICS-007: rappresentazione di eventi storici
- ETHICS-005: boundary natural earth e anacronismo
- `src/db/models.py::HistoricalEvent` (campo `known_silence`)
- `src/db/enums.py::SourceType` (valori `ORAL_TRADITION`, etc.)
