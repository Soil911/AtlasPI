"""Modelli ORM per AtlasPI.

ETHICS: Ogni modello riflette le decisioni etiche documentate in docs/ethics/.
I nomi usano name_original come campo primario (ETHICS-001).
I cambi territoriali richiedono change_type esplicito (ETHICS-002).
I territori contestati hanno status 'disputed' (ETHICS-003).
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.db.database import Base


class GeoEntity(Base):
    """Entità geopolitica storica."""

    __tablename__ = "geo_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # ETHICS: il nome primario è quello originale/locale (ETHICS-001)
    name_original = Column(String, nullable=False, index=True)
    name_original_lang = Column(String(10), nullable=False)

    entity_type = Column(String(50), nullable=False)  # empire, kingdom, city-state, colony, disputed_territory
    year_start = Column(Integer, nullable=False)       # negativo = a.C.
    year_end = Column(Integer, nullable=True)           # None = ancora esistente

    capital_name = Column(String, nullable=True)
    capital_lat = Column(Float, nullable=True)
    capital_lon = Column(Float, nullable=True)

    # GeoJSON come testo — in produzione usare PostGIS geometry (ADR-001)
    boundary_geojson = Column(Text, nullable=True)

    confidence_score = Column(Float, nullable=False, default=0.5)
    # ETHICS: i territori contestati devono avere status='disputed' (ETHICS-003)
    status = Column(String(20), nullable=False, default="confirmed")

    ethical_notes = Column(Text, nullable=True)

    name_variants = relationship("NameVariant", back_populates="entity", cascade="all, delete-orphan")
    territory_changes = relationship("TerritoryChange", back_populates="entity", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="entity", cascade="all, delete-orphan")


class NameVariant(Base):
    """Variante di nome per un'entità — vedi ETHICS-001."""

    __tablename__ = "name_variants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    name = Column(String, nullable=False)
    lang = Column(String(10), nullable=False)
    period_start = Column(Integer, nullable=True)
    period_end = Column(Integer, nullable=True)
    context = Column(String, nullable=True)
    source = Column(String, nullable=True)

    entity = relationship("GeoEntity", back_populates="name_variants")


class TerritoryChange(Base):
    """Cambio territoriale con tipo esplicito — vedi ETHICS-002.

    ETHICS: ogni cambio territoriale deve avere change_type esplicito.
    Non usare linguaggio che minimizza conquiste violente.
    """

    __tablename__ = "territory_changes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    year = Column(Integer, nullable=False)
    region = Column(String, nullable=False)
    # ETHICS: tipi definiti in ETHICS-002
    change_type = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    population_affected = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.5)

    entity = relationship("GeoEntity", back_populates="territory_changes")


class Source(Base):
    """Fonte bibliografica per un'entità."""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_id = Column(Integer, ForeignKey("geo_entities.id"), nullable=False)

    citation = Column(String, nullable=False)
    url = Column(String, nullable=True)
    source_type = Column(String(20), nullable=False, default="secondary")  # primary, secondary, academic

    entity = relationship("GeoEntity", back_populates="sources")
