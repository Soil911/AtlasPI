# Roadmap AtlasPI

## Principi di roadmap

- sviluppo incrementale
- versionamento esplicito
- scope limitato per ogni release
- prima la base etica e architetturale, poi il codice applicativo
- nessuna feature fuori roadmap senza aggiornamento esplicito di questo file

## Versioni previste

### v0.0.1
Fondazione del progetto:
- CLAUDE.md
- README.md
- LICENSE.md
- ROADMAP.md
- CHANGELOG.md
- docs/adr/
- docs/ethics/
- docs/TEMPLATES.md
- struttura repository iniziale

### v0.0.2
Bootstrap tecnico minimo:
- pyproject o requirements
- configurazione base FastAPI
- struttura iniziale src/
- struttura iniziale tests/
- .gitignore
- convenzioni base di progetto

### v0.1.0
Primo scheletro applicativo:
- endpoint healthcheck
- configurazione database
- modello iniziale entità geografica
- schema risposta API iniziale
- prime validazioni di struttura

### v0.2.0
Primo flusso dati:
- pipeline importazione dataset demo
- normalizzazione minima
- primo record interrogabile via API
- primi test tecnici ed etici

### v0.3.0
Primo nucleo storico:
- supporto year nelle query
- supporto name_original e name_variants
- supporto confidence_score
- supporto sources

### v0.4.0
Primo nucleo geopolitico:
- boundary_geojson
- capital
- territory_changes
- status confirmed|uncertain|disputed

### v0.5.0
Primo dataset demo coerente:
- piccola collezione di entità storiche
- validazione documentata
- note etiche nei casi sensibili

### v0.6.0
Preparazione alpha pubblica:
- documentazione migliorata
- quality pass
- review etica
- review architetturale
- definizione licenza core

### v1.0.0
Prima release pubblica stabile del core.
