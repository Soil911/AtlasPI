"""Setup del database SQLAlchemy.

Supporto duale: SQLite (dev) / PostgreSQL+PostGIS (prod).
Vedi ADR-001 per la motivazione della scelta PostgreSQL.
"""

import logging

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DATABASE_URL

logger = logging.getLogger(__name__)

is_sqlite = DATABASE_URL.startswith("sqlite")

# Configurazione engine in base al tipo di database
if is_sqlite:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    logger.info("Database: SQLite (%s)", DATABASE_URL)
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    logger.info("Database: PostgreSQL")


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
