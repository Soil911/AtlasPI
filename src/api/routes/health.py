"""Endpoint di health check."""

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.schemas import HealthResponse
from src.config import APP_VERSION
from src.db.database import get_db
from src.db.models import GeoEntity

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    count = db.query(func.count(GeoEntity.id)).scalar() or 0
    return HealthResponse(status="ok", version=APP_VERSION, entity_count=count)
