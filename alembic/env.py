"""Alembic environment configuration per AtlasPI.

Supporto duale: SQLite (dev) / PostgreSQL+PostGIS (prod).
Il DATABASE_URL viene letto da src.config per garantire coerenza
con il resto dell'applicazione.
"""

import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from src.config import DATABASE_URL
from src.db.database import Base

# Importa tutti i modelli per registrarli nel metadata di Base
from src.db.models import GeoEntity, NameVariant, Source, TerritoryChange  # noqa: F401

logger = logging.getLogger("alembic.env")

# Alembic Config object
config = context.config

# Setup logging da alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sovrascrivi sqlalchemy.url con il valore da src.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# MetaData target per autogenerate
target_metadata = Base.metadata

# Rileva se stiamo usando SQLite
is_sqlite = DATABASE_URL.startswith("sqlite")


def include_name(name, type_, parent_names):
    """Filtra oggetti durante autogenerate — include tutto per default."""
    return True


def run_migrations_offline() -> None:
    """Esegui migrazioni in modalita' 'offline'.

    Genera SQL senza connessione al database.
    Utile per generare script SQL da applicare manualmente.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
        render_as_batch=is_sqlite,  # Batch mode necessario per ALTER TABLE su SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Esegui migrazioni in modalita' 'online'.

    Crea una connessione al database ed esegue le migrazioni.
    """
    # Configurazione engine specifica per tipo di database
    engine_config = config.get_section(config.config_ini_section, {})

    if is_sqlite:
        # SQLite: nessun pooling necessario
        connectable = engine_from_config(
            engine_config,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    else:
        # PostgreSQL: usa pool standard
        connectable = engine_from_config(
            engine_config,
            prefix="sqlalchemy.",
            poolclass=pool.QueuePool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name,
            render_as_batch=is_sqlite,  # Batch mode per SQLite (ALTER TABLE limitato)
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
