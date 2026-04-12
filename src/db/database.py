"""Setup del database SQLAlchemy.

Supporto duale: SQLite (dev) / PostgreSQL+PostGIS (prod).
Vedi ADR-001 per la motivazione della scelta PostgreSQL.

SQLite: usato in sviluppo locale, con WAL mode e FK enforcement.
PostgreSQL: usato in produzione, con connection pooling ottimizzato.
"""

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DATABASE_URL

logger = logging.getLogger(__name__)

is_sqlite = DATABASE_URL.startswith("sqlite")
is_postgres = DATABASE_URL.startswith("postgresql")


def _build_engine():
    """Crea l'engine SQLAlchemy in base al DATABASE_URL configurato."""
    if is_sqlite:
        eng = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(eng, "connect")
        def _set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

        logger.info("Database: SQLite (%s)", DATABASE_URL)
        return eng

    if is_postgres:
        eng = create_engine(
            DATABASE_URL,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        logger.info("Database: PostgreSQL")
        return eng

    # Fallback generico per altri database URL
    eng = create_engine(DATABASE_URL)
    logger.warning("Database: tipo non riconosciuto (%s), usando configurazione default", DATABASE_URL)
    return eng


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency FastAPI per ottenere una sessione DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
