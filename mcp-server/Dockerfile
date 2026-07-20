# Dockerfile del server MCP di AtlasPI (transport stdio).
#
# Perché esiste: i registry MCP (Glama e simili) compilano ed ESEGUONO il
# server in sandbox per introspezionarne i tool (tools/list). Senza questo
# file dedurrebbero il Dockerfile della root, che compila l'app web FastAPI
# (richiede Postgres e non parla MCP) → introspezione fallita. Vedi
# docs/DISCOVERY.md.
#
# Build (il contesto è QUESTA directory, non la root del repo):
#     docker build -t atlaspi-mcp mcp-server/
# Uso (stdio: il client MCP parla sullo stdin/stdout del container):
#     docker run -i --rm atlaspi-mcp
#
# Env opzionale: ATLASPI_API_URL per puntare a un'istanza AtlasPI diversa
# (default https://atlaspi.it). Nessuna porta esposta: il transport è stdio.

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Metadati del package + sorgenti (readme = README.md in pyproject).
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Utente non-root: il server fa solo chiamate HTTP in uscita.
RUN useradd --create-home --uid 10001 mcp
USER mcp

ENTRYPOINT ["atlaspi-mcp"]
