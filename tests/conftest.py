"""Fixture condivise per i test AtlasPI."""

import os

# Forza SQLite per i test
os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["LOG_FORMAT"] = "text"
os.environ["AUTO_SEED"] = "false"
# Rate limit alto per i test (i 60/min di prod farebbero scattare 429
# quando i test fanno molte richieste in pochi secondi)
os.environ.setdefault("RATE_LIMIT", "100000/minute")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.db.database import Base, get_db
from src.db.seed import seed_database, seed_events_database
from src.main import app

TEST_DATABASE_URL = "sqlite:///./data/test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(test_engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Crea le tabelle e popola i dati demo per tutta la sessione di test."""
    Base.metadata.create_all(bind=test_engine)

    from src.db.models import GeoEntity, HistoricalEvent
    db = TestSession()
    if db.query(GeoEntity).count() == 0:
        from src.db import seed as seed_module
        original = seed_module.SessionLocal
        seed_module.SessionLocal = TestSession
        seed_database()
        # v6.3: seed eventi storici (ETHICS-007 + ETHICS-008)
        if db.query(HistoricalEvent).count() == 0:
            seed_events_database()
        seed_module.SessionLocal = original
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """TestClient FastAPI con database di test."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    """Sessione DB diretta per i test."""
    session = TestSession()
    yield session
    session.close()
