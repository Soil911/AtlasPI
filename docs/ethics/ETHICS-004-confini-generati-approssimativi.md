# ETHICS-004: Confini generati approssimativi

## Data: 2026-04-12

## Contesto

Su 752 entità nel database, 525 non hanno alcun confine poligonale
(`boundary_geojson == null`) e 53 hanno solo un punto (`"type": "Point"`).
Solo 174 entità hanno poligoni reali derivati da dati cartografici storici.

Per migliorare la visualizzazione sulla mappa e rendere il database più
utilizzabile dagli agenti AI, si è deciso di generare confini approssimativi
per le entità mancanti.

## Rischio di distorsione

I confini generati computazionalmente NON sono dati storici reali.
Presentarli come tali sarebbe una falsificazione della documentazione storica.

Rischi specifici:
- Un utente potrebbe confondere un confine approssimativo con un dato storico verificato
- Le dimensioni stimate per tipo di entità sono medie statistiche, non misurazioni reali
- Imperi e regni avevano confini irregolari dettati da geografia, guerre e trattati,
  non da cerchi attorno alla capitale
- I confini di entità nomadiche (khanati, confederazioni steppiche) non erano
  linee fisse ma zone di influenza fluide

## Alternative considerate

1. **Non generare nulla** — mantenere solo i dati reali.
   Pro: massima accuratezza. Contro: 70% delle entità invisibili sulla mappa.

2. **Generare confini e marcarli chiaramente** (scelta adottata).
   Pro: tutte le entità visibili, con trasparenza sull'origine del dato.
   Contro: rischio che il marcatore venga ignorato dagli utilizzatori.

3. **Usare solo cerchi fissi per tipo**.
   Pro: più semplice. Contro: ancora meno realistico.

## Scelta adottata

Opzione 2 con le seguenti salvaguardie:

### Campo `boundary_source`
Ogni entità ha un campo `boundary_source` con uno dei seguenti valori:
- `"historical_map"` — confine derivato da dati cartografici storici reali
- `"approximate_generated"` — confine generato computazionalmente
- `"natural_earth"` — confine derivato dal dataset Natural Earth

### Riduzione del confidence_score
Le entità con confini approssimativi subiscono una riduzione di 0.1
nel `confidence_score` per riflettere l'incertezza aggiuntiva.

### Poligoni irregolari
I confini generati non sono cerchi perfetti ma poligoni irregolari
con variazione del raggio del ±20-30% a ogni vertice, per evitare
l'impressione di una precisione che non esiste.

### Dimensioni calibrate per tipo
Le dimensioni sono basate su stime storiografiche comparative per tipo
di entità e periodo storico. Non pretendono di essere accurate per
la singola entità.

## Modulo responsabile

`src/ingestion/boundary_generator.py` — generazione dei confini
`src/ingestion/enrich_boundaries.py` — arricchimento batch

## Principi CLAUDE.md applicati

- **Principio 1** (Verità prima del comfort): i confini approssimativi
  non vengono presentati come dati reali
- **Principio 3** (Trasparenza dell'incertezza): il campo `boundary_source`
  e la riduzione del `confidence_score` documentano l'incertezza
- **Principio 4** (Nessun bias): le dimensioni sono calibrate per tipo,
  non per area geografica
