"""Models: HistoricalLanguage (lingue storiche geocoded).

Sub-module di src.db.models (split v6.96.0 / audit R7).

ETHICS: languages endangered/extinct flaggate. Colonial impositions
(Nahuatl soppresso da spagnolo, aborigeni AU da inglese) esplicitate
in ethical_notes.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base
from src.db.enums import EntityStatus  # noqa: F401


class HistoricalLanguage(Base):
    """Lingua storica geocoded — area geografica d'uso + periodo.

    Distinta da GeoEntity (stato politico) e HistoricalCity (urban center).
    Una lingua puo' coprire multiple entita' politiche (latino sotto Roma
    e sotto Bizantino) e sopravvivere oltre la fine di uno stato.

    Design choices:
      * Geocoding: center point + region_name. Polygon optional.
      * period_start/end: prima attestazione scritta → ultimo parlante
        native (o 'living' status). Per lingue ricostruite (PIE),
        confidence_score < 0.5 + status='uncertain'.
    """

    __tablename__ = "historical_languages"
    __table_args__ = (
        Index("ix_lang_name", "name_original"),
        Index("ix_lang_period", "period_start", "period_end"),
        Index("ix_lang_region", "region_name"),
        Index("ix_lang_family", "family"),
        Index("ix_lang_iso", "iso_code"),
        CheckConstraint(
            "confidence_score >= 0.0 AND confidence_score <= 1.0",
            name="ck_lang_confidence_range",
        ),
        CheckConstraint(
            "center_lat IS NULL OR (center_lat >= -90.0 AND center_lat <= 90.0)",
            name="ck_lang_lat_range",
        ),
        CheckConstraint(
            "center_lon IS NULL OR (center_lon >= -180.0 AND center_lon <= 180.0)",
            name="ck_lang_lon_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_original: Mapped[str] = mapped_column(String(200), nullable=False)
    name_original_lang: Mapped[str] = mapped_column(String(10), nullable=False)

    # ISO 639-3 (3-letter) dove disponibile.
    iso_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Language family (Indo-European, Afro-Asiatic, ecc.)
    family: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Script(s) storicamente usati (latin, greek, cuneiform, ...)
    script: Mapped[str | None] = mapped_column(String(100), nullable=True)

    center_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    center_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    region_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # Period: prima attestazione → ultimo parlante native.
    period_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    period_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # vitality: living / endangered / extinct / reconstructed / classical.
    vitality_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="extinct"
    )

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EntityStatus.CONFIRMED.value
    )

    # ETHICS: soppressioni coloniali, repressioni linguistiche, revival
    # (Welsh, Maori, Cornish, Hebrew).
    ethical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    sources: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    name_variants: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
