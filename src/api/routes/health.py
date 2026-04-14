"""Endpoint di health check approfondito.

Ritorna 'ok' / 'degraded' / 'down' in base alle sotto-verifiche.
Monitoring esterno (UptimeRobot, Sentry Cron) legge questo endpoint.
"""

import logging
import time

from fastapi import APIRouter, Depends, Response
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from src.api.schemas import HealthResponse
from src.config import APP_VERSION, DATABASE_URL, ENVIRONMENT
from src.db.database import get_db
from src.db.models import GeoEntity
from src.monitoring import sentry_is_active, uptime_seconds

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sistema"])

# Soglia minima sotto cui consideriamo il dataset "vuoto" → degraded
MIN_EXPECTED_ENTITIES = 100


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Stato di salute del servizio",
    description=(
        "Health check multi-livello: connettivita' DB, conta entita', "
        "stato Sentry, uptime. Ritorna 'ok' se tutto funziona, 'degraded' "
        "se qualcosa non e' al 100%, 'down' se il DB e' irraggiungibile. "
        "Il codice HTTP e' sempre 200 per non confondere monitoring tools, "
        "tranne 503 in caso di 'down'."
    ),
)
def health_check(response: Response, db: Session = Depends(get_db)):
    start = time.perf_counter()
    checks: dict[str, str] = {}

    # ── 1. Database connectivity ─────────────────────────────────
    db_type = "sqlite" if DATABASE_URL.startswith("sqlite") else "postgresql"
    try:
        db.execute(text("SELECT 1"))
        db_status = f"{db_type}:connected"
        checks["database"] = "ok"
    except Exception as e:
        logger.error("Health check: database non raggiungibile: %s", e)
        db_status = f"{db_type}:disconnected"
        checks["database"] = "error"

    # ── 2. Entity count (dataset seeded) ─────────────────────────
    count = 0
    if checks["database"] == "ok":
        try:
            count = db.query(func.count(GeoEntity.id)).scalar() or 0
            if count >= MIN_EXPECTED_ENTITIES:
                checks["seed"] = "ok"
            elif count > 0:
                checks["seed"] = f"partial:{count}"
            else:
                checks["seed"] = "empty"
        except Exception as e:
            logger.error("Health check: count fallito: %s", e)
            checks["seed"] = "error"

    # ── 3. Sentry status ─────────────────────────────────────────
    sentry_on = sentry_is_active()
    checks["sentry"] = "active" if sentry_on else "disabled"

    # ── 4. Determina status aggregato ────────────────────────────
    if checks["database"] == "error":
        status = "down"
        response.status_code = 503
    elif checks.get("seed") in ("empty", "error", None):
        status = "degraded"
    elif checks.get("seed", "").startswith("partial"):
        status = "degraded"
    else:
        status = "ok"

    duration = (time.perf_counter() - start) * 1000

    return HealthResponse(
        status=status,
        version=APP_VERSION,
        environment=ENVIRONMENT,
        database=db_status,
        entity_count=count,
        uptime_seconds=uptime_seconds(),
        check_duration_ms=round(duration, 2),
        sentry_active=sentry_on,
        checks=checks,
    )
