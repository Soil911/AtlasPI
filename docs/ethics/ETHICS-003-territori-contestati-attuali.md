# ETHICS-003 — Territori contestati nel presente e denominazioni concorrenti

**Data**: 2026-04-11
**Stato**: Accettato
**Autore**: Clirim
**Impatto**: Alto — definisce come rappresentare dispute territoriali ancora attive

## Il problema

Esistono territori il cui status è oggi contestato da stati,
popolazioni locali, organismi internazionali o storiografie concorrenti.
Ridurre questi casi a una singola rappresentazione significa trasformare
il database in uno strumento di arbitraggio politico.

Esempi:
- Palestina / Israele
- Crimea
- Kosovo
- Taiwan
- Sahara Occidentale

## Decisione

Quando una disputa è attiva nel presente:
- non esiste una sola denominazione privilegiata in modo assoluto
- il record deve includere tutte le denominazioni ufficiali rilevanti
- ogni denominazione deve avere contesto politico, temporale e fonte
- i confini devono poter avere più geometrie concorrenti
- lo status del record deve riflettere esplicitamente la disputa

Campi minimi richiesti:
- status = "disputed"
- contested_names[]
- contested_boundaries[]
- claims[]
- sources[]
- confidence_score

## Motivazioni

Un database storico-geografico onesto non semplifica artificialmente
le dispute ancora vive. Rende esplicite le rivendicazioni concorrenti,
le fonti e i limiti di ciascuna rappresentazione.

## Casi limite ancora aperti

- Dispute senza riconoscimento internazionale uniforme
- Nomi usati da comunità locali ma assenti in documentazione statale
- Rappresentazione di entità de facto vs de jure

## Impatto sul codice

Qualsiasi endpoint che restituisce territori contestati deve:
1. Segnalare esplicitamente status = "disputed"
2. Restituire tutte le denominazioni rilevanti
3. Evitare normalizzazioni che nascondano conflitti attivi
4. Avere commento # ETHICS: vedi ETHICS-003
