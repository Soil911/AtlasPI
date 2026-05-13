"""Models: ArchaeologicalSite (UNESCO + ruins + monuments).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS-005-analogy: confidence_score riflette qualità evidenza, non
giudizio politico.
ETHICS-009-analogy: siti spesso hanno DUE nomi — quello originale e
quello coloniale. name_original = indigeno (Uluru, non "Ayers Rock").
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import EntityStatus  # noqa: F401
from src.db.models.entities import GeoEntity  # noqa: F401 — relationship target


class ArchaeologicalSite(Base):
    """Sito archeologico / culturale discreto con coordinate puntuali.

    Distinto da `HistoricalCity` (centro urbano con vita politica) e da
    `GeoEntity` (stato/regno con boundary). Un sito e' un luogo materiale:
    Pompeii, Stonehenge, Chichen Itza, Angkor Wat, Petra, Uluru, ecc.

    Design choices:
      * Coordinate puntuali, non polygon.
      * date_start/date_end = periodi di costruzione/uso attestato.
      * entity_id nullable — molti siti pre-datano qualsiasi entità
        politica (Gobekli Tepe, Stonehenge).
      * unesco_id = "Ref ID" del sito UNESCO.
    """

    __tablename__ = "archaeological_sites"
    __table_args__ = (
        Index("ix_arch_sites_name", "name_original"),
        Index("ix_arch_sites_entity_id", "entity_id"),
        Index("ix_arch_sites_years", "date_start", "date_end"),
        Index("ix_arch_sites_site_type", "site_type"),
        Index("ix_arch_sites_unesco", "unesco_id"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_arch_sites_confidence_range",
        ),
        CheckConstraint(
            "latitude >= -90.0 AND latitude <= 90.0",
            name="ck_arch_sites_lat_range",
        ),
        CheckConstraint(
            "longitude >= -180.0 AND longitude <= 180.0",
            name="ck_arch_sites_lon_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ETHICS-001: nome originale/locale come chiave primaria.
    name_original: Mapped[str] = mapped_column(String(500), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    # Coordinate puntuali WGS84 del centro del sito.
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    date_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    site_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="ruins"
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # UNESCO World Heritage Site ID (es. "757" per Pompei area).
    unesco_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unesco_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Entità politica di appartenenza principale (nullable per siti
    # pre-statali — Gobekli Tepe, Stonehenge).
    entity_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=True
    )

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS-009-analogy: colonial renaming, ritorni/rivendicazioni indigene.
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON-serialized — vedi audit R8 per migrazione relazionale.
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity: Mapped[GeoEntity | None] = relationship("GeoEntity")
