# ETHICS-001 — Nomi geografici: originali, imposti e contestati

**Data**: 2026-04-11
**Stato**: Accettato
**Autore**: Clirim
**Impatto**: Alto — definisce come tutti i nomi vengono archiviati

## Il problema

I nomi geografici sono carichi di storia politica. Ogni scelta
su quale nome usare come "principale" è una presa di posizione.

Esempi:
- Costantinopoli / Istanbul: stesso luogo, epoche diverse
- Bombay / Mumbai: nome coloniale vs nome locale originale
- Palestina / Israele: confini attivamente contestati
- Nordamerica precolombiana: nomi indigeni spesso ignorati

## Decisione

Struttura dati adottata:

class EntityName:
    name_original: str          # nome locale — CAMPO PRIMARIO
    name_original_lang: str     # codice ISO 639-1
    name_variants: list[NameVariant]

class NameVariant:
    name: str
    lang: str
    period_start: int | None    # anno, negativo = a.C.
    period_end: int | None
    context: str                # es. "nome coloniale britannico"
    source: str

Esempio — Istanbul:
{
  "name_original": "İstanbul",
  "name_original_lang": "tr",
  "name_variants": [
    {
      "name": "Costantinopoli",
      "lang": "it",
      "period_start": 330,
      "period_end": 1453,
      "context": "nome romano-bizantino",
      "source": "Enciclopedia Treccani"
    },
    {
      "name": "Byzantium",
      "lang": "la",
      "period_start": -657,
      "period_end": 330,
      "context": "nome greco originale della colonia",
      "source": "Tucidide, I.94"
    }
  ]
}

## Motivazioni

Il nome nella lingua locale ha priorità etica rispetto ai nomi
imposti da potenze esterne. I nomi storici imposti non vengono
cancellati — sono presenti come varianti con contesto esplicito.

## Casi limite aperti

- Nomi di territori indigeni senza fonti scritte → nota esplicita
- Territori con dispute attive oggi → tutte le denominazioni
  ufficiali con note sulle dispute (vedi ETHICS-003)

## Impatto sul codice

Qualsiasi funzione che restituisce un nome geografico deve:
1. Restituire name_original come campo principale
2. Includere name_variants nell'output completo
3. Avere commento # ETHICS: vedi ETHICS-001
