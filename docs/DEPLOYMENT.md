# AtlasPI — Guida al deploy

## Sviluppo locale

### Requisiti
- Python >= 3.11

### Setup
```bash
git clone https://github.com/UTENTE/atlaspi.git
cd atlaspi
pip install -r requirements.txt
cp .env.example .env    # personalizza se necessario
python run.py
```

Apri http://127.0.0.1:10100

### Test
```bash
pytest tests/ -v
ruff check src/ tests/
```

## Docker

### Build e avvio
```bash
docker compose up --build
```

Il servizio sara' disponibile su http://localhost:10100

### Solo build
```bash
docker build -t atlaspi .
docker run -p 10100:10100 atlaspi
```

## Configurazione

Tutte le variabili sono in `.env` (vedi `.env.example`):

| Variabile | Default | Descrizione |
|-----------|---------|-------------|
| DATABASE_URL | sqlite:///data/atlaspi.db | URL del database |
| HOST | 127.0.0.1 | Indirizzo del server |
| PORT | 10100 | Porta del server |
| CORS_ORIGINS | * | Origini CORS permesse |
| LOG_LEVEL | INFO | Livello di log |
| LOG_FORMAT | json | Formato log: json o text |
| RATE_LIMIT | 60/minute | Rate limiting |
| AUTO_SEED | true | Seed automatico all'avvio |

## PostgreSQL (produzione)

Per usare PostgreSQL + PostGIS:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/atlaspi
```

Richiede `psycopg2-binary`:
```bash
pip install psycopg2-binary
```

## Struttura del progetto

```
atlaspi/
├── src/                 # Codice sorgente
│   ├── api/             # Endpoint FastAPI
│   ├── db/              # Modelli e database
│   ├── ingestion/       # Pipeline importazione dati
│   ├── middleware/       # Middleware (logging, security)
│   └── validation/      # Validazione confidence score
├── static/              # Interfaccia web
├── data/                # Database e dati grezzi
├── tests/               # Test (56 test)
├── docs/                # Documentazione
├── Dockerfile           # Build container
└── docker-compose.yml   # Orchestrazione locale
```
