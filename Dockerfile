# ─── Stage 1: Builder ───────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── Stage 2: Production runtime ────────────────────────────────
FROM python:3.13-slim

# System utilities: per backup/restore scripts + smoke_test.sh
# sqlite3 per .backup, pg client per pg_dump/psql, jq per asserzioni smoke test
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
         sqlite3 postgresql-client curl jq \
    && rm -rf /var/lib/apt/lists/*

# Security: non-root user
RUN groupadd --gid 1000 atlaspi \
    && useradd --uid 1000 --gid atlaspi --shell /bin/bash --create-home atlaspi

WORKDIR /app

# Install dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=atlaspi:atlaspi src/ src/
COPY --chown=atlaspi:atlaspi static/ static/
COPY --chown=atlaspi:atlaspi data/ data/
COPY --chown=atlaspi:atlaspi scripts/ scripts/
COPY --chown=atlaspi:atlaspi run.py .
COPY --chown=atlaspi:atlaspi requirements.txt .
COPY --chown=atlaspi:atlaspi alembic/ alembic/
COPY --chown=atlaspi:atlaspi alembic.ini .

# Make operational scripts executable
RUN chmod +x scripts/*.sh

# Environment defaults for production
ENV HOST=0.0.0.0
ENV PORT=10100
ENV RELOAD=false
ENV LOG_FORMAT=json
ENV LOG_LEVEL=INFO
ENV AUTO_SEED=true
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER atlaspi

EXPOSE ${PORT}

# Health check — polls /health every 30s, fails after 5s, 3 retries
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Production server: gunicorn with uvicorn workers
CMD gunicorn src.main:app \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile -
