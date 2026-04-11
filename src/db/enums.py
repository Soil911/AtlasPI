"""Enumerazioni per AtlasPI — valori controllati a livello DB.

ETHICS-002: i tipi di cambio territoriale sono definiti qui.
Qualsiasi valore fuori da questa lista viene rifiutato.
"""

import enum


class EntityStatus(enum.StrEnum):
    """Status di un'entità geopolitica."""
    CONFIRMED = "confirmed"
    UNCERTAIN = "uncertain"
    DISPUTED = "disputed"


class ChangeType(enum.StrEnum):
    """Tipi di cambio territoriale — vedi ETHICS-002.

    NON usare linguaggio eufemistico.
    """
    CONQUEST_MILITARY = "CONQUEST_MILITARY"
    TREATY = "TREATY"
    PURCHASE = "PURCHASE"
    INHERITANCE = "INHERITANCE"
    REVOLUTION = "REVOLUTION"
    COLONIZATION = "COLONIZATION"
    ETHNIC_CLEANSING = "ETHNIC_CLEANSING"
    GENOCIDE = "GENOCIDE"
    CESSION_FORCED = "CESSION_FORCED"
    LIBERATION = "LIBERATION"
    UNKNOWN = "UNKNOWN"


class SourceType(enum.StrEnum):
    """Tipo di fonte bibliografica."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACADEMIC = "academic"
