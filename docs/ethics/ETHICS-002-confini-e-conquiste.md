# ETHICS-002 — Confini disputati e metodi di acquisizione

**Data**: 2026-04-11
**Stato**: Accettato
**Autore**: Clirim
**Impatto**: Alto — definisce come rappresentare conquiste e conflitti

## Il problema

I confini storici non sono mai linee neutre. Rappresentano guerre,
trattati imposti, deportazioni, cancellazioni di popoli interi.
Un database che mostra solo il poligono geografico senza contesto
è tecnicamente accurato ma storicamente disonesto.

Pericolo concreto: un agente AI che genera una mappa dell'Impero
Romano potrebbe farlo con tono neutro o celebrativo, senza che
l'utente capisca che quei confini sono stati raggiunti attraverso
la conquista militare di decine di popoli.

## Decisione

Ogni entità ha territory_changes[] con questi tipi obbligatori:

CONQUEST_MILITARY   = conquista militare
TREATY              = trattato (anche se imposto)
PURCHASE            = acquisto
INHERITANCE         = successione
REVOLUTION          = rivoluzione interna
COLONIZATION        = colonizzazione di territori abitati
ETHNIC_CLEANSING    = pulizia etnica documentata
GENOCIDE            = genocidio riconosciuto
CESSION_FORCED      = cessione forzata
LIBERATION          = liberazione da occupazione
UNKNOWN             = sconosciuto (da minimizzare)

Esempio — conquista romana della Gallia:
{
  "year": -51,
  "region": "Gallia",
  "change_type": "conquest_military",
  "description": "Conquista di Giulio Cesare (58-50 a.C.).
    Le fonti antiche stimano 1-3 milioni di morti. La
    storiografia moderna ritiene le cifre probabilmente
    esagerate ma indicative di violenza su larga scala.",
  "population_affected": 1000000,
  "sources": ["Cesare, De Bello Gallico",
              "Goldsworthy, Caesar (2006)"],
  "confidence_score": 0.75
}

## Regole di applicazione

NON usare linguaggio eufemistico:
- "pacificazione" → usa "conquista militare" o "repressione"
- "civilizzazione" → usa "colonizzazione" con contesto
- "scoperta" per terre già abitate → mai usare questo termine

Includere dati demografici quando esistono.
Includere prospettiva dei conquistati quando possibile.
Per eventi riconosciuti come genocidi usare il termine corretto.

## Impatto sul codice

# ETHICS: ogni cambio territoriale deve avere change_type esplicito.
# Non usare linguaggio che minimizza conquiste violente.
# Vedi ETHICS-002.

if change.change_type == "UNKNOWN":
    logger.warning(
        f"Territory change for {entity_id} has unknown type. "
        "Review historical sources before publishing."
    )
