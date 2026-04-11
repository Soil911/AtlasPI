"""Endpoint di health check approfondito."""

import logging
import time

from fastapi import APIRouter, Depends
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from src.api.schemas import HealthResponse
from src.config import APP_VERSION, DATABASE_URL
from src.db.database import get_db
from src.db.models import GeoEntity

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sistema"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Stato di salute del servizio",
    description="Verifica connettività database, conta entità, riporta versione.",
)
def health_check(db: Session = Depends(get_db)):
    start = time.perf_counter()

    # Verifica connettività DB
    try:
        db.execute(text("SELECT 1"))
        db_type = "sqlite" if DATABASE_URL.startswith("sqlite") else "postgresql"
        db_status = f"{db_type}:connected"
    except Exception as e:
        logger.error("Health check: database non raggiungibile: %s", e)
        db_status = "disconnected"

    count = db.query(func.count(GeoEntity.id)).scalar() or 0
    duration = (time.perf_counter() - start) * 1000
    logger.debug("Health check completato in %.1fms", duration)

    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        database=db_status,
        entity_count=count,
    )
