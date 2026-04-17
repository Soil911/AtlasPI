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
from src.db.seed import seed_database, seed_events_database, seed_periods_database
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

    from src.db.models import DynastyChain, GeoEntity, HistoricalEvent, HistoricalPeriod
    db = TestSession()
    if db.query(GeoEntity).count() == 0:
        from src.db import seed as seed_module
        original = seed_module.SessionLocal
        seed_module.SessionLocal = TestSession
        seed_database()
        # v6.3: seed eventi storici (ETHICS-007 + ETHICS-008)
        if db.query(HistoricalEvent).count() == 0:
            seed_events_database()
        # v6.27: seed historical periods
        if db.query(HistoricalPeriod).count() == 0:
            seed_periods_database()
        # v6.30: guard against displaced aourednik matches (same as prod startup)
        try:
            from src.ingestion import fix_displaced_aourednik as _fdisp
            original_fd = _fdisp.SessionLocal
            _fdisp.SessionLocal = TestSession
            _fdisp.fix_displaced(dry_run=False)
            _fdisp.SessionLocal = original_fd
        except Exception:
            pass
        seed_module.SessionLocal = original

    # v6.5+: ingest chains (separate from seed — chains reference entities
    # by name_original so must run AFTER entity seed).
    # NOTE: we inline the chain-seeding logic instead of importing
    # ingest_chains, because that module replaces sys.stdout on Windows
    # at import time, which breaks pytest's capture system.
    if db.query(DynastyChain).count() == 0:
        import json as _json
        from pathlib import Path as _Path

        from src.db.models import ChainLink

        _chains_dir = _Path("data") / "chains"
        entity_map = {e.name_original: e.id for e in db.query(GeoEntity).all()}
        for fp in sorted(_chains_dir.glob("*.json")):
            with fp.open(encoding="utf-8") as fh:
                items = _json.load(fh)
            for ch in items:
                chain = DynastyChain(
                    name=ch["name"],
                    name_lang=ch.get("name_lang", "en"),
                    chain_type=ch.get("chain_type", "OTHER"),
                    region=ch.get("region"),
                    description=ch.get("description"),
                    confidence_score=ch.get("confidence_score", 0.7),
                    status=ch.get("status", "confirmed"),
                    ethical_notes=ch.get("ethical_notes"),
                    sources=_json.dumps(ch["sources"], ensure_ascii=False) if ch.get("sources") else None,
                )
                db.add(chain)
                db.flush()
                for i, lk in enumerate(ch.get("links", [])):
                    eid = entity_map.get(lk.get("entity_name"))
                    if eid is None:
                        continue
                    db.add(ChainLink(
                        chain_id=chain.id,
                        entity_id=eid,
                        sequence_order=i,
                        transition_year=lk.get("transition_year"),
                        transition_type=lk.get("transition_type"),
                        is_violent=bool(lk.get("is_violent", False)),
                        description=lk.get("description"),
                        ethical_notes=lk.get("ethical_notes"),
                    ))
        db.commit()

    # v6.37.1: seed archaeological sites + v6.44 languages.
    try:
        from src.ingestion import ingest_sites as _sites_mod, ingest_languages as _lang_mod
        for mod in (_sites_mod, _lang_mod):
            orig = mod.SessionLocal
            mod.SessionLocal = TestSession
            try:
                if mod is _sites_mod:
                    mod.ingest_sites()
                else:
                    mod.ingest_languages()
            except Exception:
                pass
            finally:
                mod.SessionLocal = orig
    except Exception:
        pass

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
