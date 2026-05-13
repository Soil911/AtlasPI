"""Models: DynastyChain + ChainLink (catene successorie).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS-002 / ETHICS-003: ogni link ha transition_type esplicito —
CONQUEST/SUCCESSION/DECOLONIZATION etc. Non si riducono violenze a
"successione" generica. Le catene IDEOLOGICAL portano avvertimento
esplicito che self-proclaimed continuità ≠ legittimità.
"""

from __future__ import annotations

from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base
from src.db.enums import EntityStatus  # noqa: F401
from src.db.models.entities import GeoEntity  # noqa: F401 — relationship target


class DynastyChain(Base):
    """Catena successoria che lega più entità geopolitiche.

    Esempi:
      * "Roman Power Center" (SUCCESSION): Roma Repubblica → Impero
        Romano → Impero Romano d'Occidente → ...
      * "Chinese Imperial Dynasties" (DYNASTY): Han → Tang → ... → Qing
        → Repubblica
      * "Inca → Peruvian Republic" (COLONIAL): Tawantinsuyu → Vicereame
        del Perù → Repubblica del Perù

    ETHICS-002 / ETHICS-003: ogni link ha un transition_type esplicito
    (CONQUEST, SUCCESSION, DECOLONIZATION, ecc.).
    """

    __tablename__ = "dynasty_chains"
    __table_args__ = (
        Index("ix_dynasty_chains_name", "name"),
        Index("ix_dynasty_chains_chain_type", "chain_type"),
        Index("ix_dynasty_chains_region", "region"),
        Index("ix_dynasty_chains_status", "status"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_chains_confidence_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    name_lang: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    # ChainType enum (DYNASTY / SUCCESSION / RESTORATION / COLONIAL /
    # IDEOLOGICAL / OTHER).
    chain_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Macro-area geografica della catena (descrittiva, non normativa).
    region: Mapped[str | None] = mapped_column(String(200), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS: avvertimenti su self-proclaimed continuità, cancellazioni
    # culturali, nature contestate.
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    sources: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    links: Mapped[list[ChainLink]] = relationship(
        "ChainLink", back_populates="chain", cascade="all, delete-orphan",
        order_by="ChainLink.sequence_order",
    )


class ChainLink(Base):
    """Link tra una DynastyChain e una GeoEntity, con tipo di transizione.

    sequence_order = 0 è l'entità più antica della catena. Ogni link ha
    transition_type che descrive COME questa entità è subentrata alla
    precedente. La PRIMA entità (sequence_order=0) ha transition_type=NULL.
    """

    __tablename__ = "chain_links"
    __table_args__ = (
        Index("ix_chain_links_chain_id", "chain_id"),
        Index("ix_chain_links_entity_id", "entity_id"),
        Index("ix_chain_links_sequence", "chain_id", "sequence_order"),
        Index("ix_chain_links_transition_type", "transition_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chain_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dynasty_chains.id"), nullable=False
    )
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("geo_entities.id"), nullable=False
    )

    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Anno della transizione DAL predecessore A questa entità. NULL per il
    # primo link della catena.
    transition_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # TransitionType enum. NULL solo per il primo link.
    transition_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # ETHICS-002: era violenta? Default CONQUEST=True; altri tipi possono
    # essere overridden esplicitamente (es. PARTITION con violenze).
    is_violent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    chain: Mapped[DynastyChain] = relationship("DynastyChain", back_populates="links")
    entity: Mapped[GeoEntity] = relationship("GeoEntity")
