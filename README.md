# AtlasPI

Database geografico storico strutturato per agenti AI.

## Filosofia

Questo progetto nasce da una convinzione: Internet è costruita
per gli umani, non per le macchine. Gli agenti AI che cercano
dati geografici storici oggi devono raccogliere informazioni
sparse, in formati incompatibili, spesso incomplete o prive
di contesto. AtlasPI colma questo gap.

I dati geografici storici non sono neutri. Ogni confine, ogni
nome, ogni territorio racconta una storia che include conquiste,
popoli cancellati, nomi imposti. Questo progetto sceglie di non
nascondere quella complessità — la struttura, la documenta,
la rende leggibile anche dalle macchine.

## Principi

- Verità prima del comfort
- Nessuna versione unica della storia
- Trasparenza dell'incertezza
- Nessun bias geografico o culturale dominante

## Sviluppo

Leggi CLAUDE.md prima di qualsiasi sessione di sviluppo.
Le decisioni architetturali sono in docs/adr/.
Le decisioni etiche sono in docs/ethics/.
La roadmap è in ROADMAP.md.
Le modifiche di release sono tracciate in CHANGELOG.md.

## Roadmap

Lo sviluppo segue una roadmap incrementale con versionamento esplicito:
v0.0.1, v0.0.2, v0.1.0, ...

Ogni release introduce un insieme limitato di cambiamenti coerenti
con i principi architetturali ed etici del progetto.

## Open core

Il progetto segue un modello open core:
- core open source
- documentazione pubblica
- possibilità di componenti premium separati
- verifica obbligatoria delle licenze dei dataset prima della pubblicazione

## Stack

Python · FastAPI · PostgreSQL · PostGIS · Redis

## Stato

In sviluppo. MVP previsto Q3 2026.
