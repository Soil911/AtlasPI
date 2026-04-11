"""AtlasPI — Database geografico storico strutturato per agenti AI."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import entities, health
from src.config import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from src.db.database import Base, engine
from src.db.seed import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea tabelle e popola dati demo all'avvio."""
    logger.info("Inizializzazione database...")
    Base.metadata.create_all(bind=engine)
    seed_database()
    logger.info("AtlasPI pronto su http://127.0.0.1:8000")
    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(entities.router)


@app.get("/", include_in_schema=False)
async def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
