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
    """Tipo di fonte bibliografica.

    ETHICS-008: oral_tradition e archaeological NON sono inferiori
    ad academic — sono evidence diverse ma di pari dignità.
    """
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACADEMIC = "academic"
    # ETHICS-008: fonti non scritte, fondamentali per storie coperte
    # solo da tradizioni orali o evidenze materiali.
    ORAL_TRADITION = "oral_tradition"
    ARCHAEOLOGICAL = "archaeological"
    INDIRECT_REFERENCE = "indirect_reference"


class EventType(enum.StrEnum):
    """Tipi di evento storico — vedi ETHICS-007.

    NON usare linguaggio eufemistico: GENOCIDE, non "conflict";
    COLONIAL_VIOLENCE, non "pacification"; FAMINE, non "food crisis".
    """
    # Eventi militari / politici
    BATTLE = "BATTLE"
    SIEGE = "SIEGE"
    TREATY = "TREATY"
    REBELLION = "REBELLION"
    REVOLUTION = "REVOLUTION"
    CORONATION = "CORONATION"
    DEATH_OF_RULER = "DEATH_OF_RULER"
    MARRIAGE_DYNASTIC = "MARRIAGE_DYNASTIC"
    FOUNDING_CITY = "FOUNDING_CITY"
    FOUNDING_STATE = "FOUNDING_STATE"
    DISSOLUTION_STATE = "DISSOLUTION_STATE"
    CONQUEST = "CONQUEST"
    # ETHICS-007: termini scomodi, voluti espliciti
    COLONIAL_VIOLENCE = "COLONIAL_VIOLENCE"
    GENOCIDE = "GENOCIDE"
    ETHNIC_CLEANSING = "ETHNIC_CLEANSING"
    MASSACRE = "MASSACRE"
    DEPORTATION = "DEPORTATION"
    # Disastri / crisi
    FAMINE = "FAMINE"
    EPIDEMIC = "EPIDEMIC"
    EARTHQUAKE = "EARTHQUAKE"
    VOLCANIC_ERUPTION = "VOLCANIC_ERUPTION"
    TSUNAMI = "TSUNAMI"
    FLOOD = "FLOOD"
    DROUGHT = "DROUGHT"
    FIRE = "FIRE"
    # Altri
    EXPLORATION = "EXPLORATION"
    TRADE_AGREEMENT = "TRADE_AGREEMENT"
    RELIGIOUS_EVENT = "RELIGIOUS_EVENT"
    INTELLECTUAL_EVENT = "INTELLECTUAL_EVENT"
    TECHNOLOGICAL_EVENT = "TECHNOLOGICAL_EVENT"
    OTHER = "OTHER"


class EventRole(enum.StrEnum):
    """Ruolo di un'entità geopolitica in un evento storico — ETHICS-007.

    Esplicita CHI ha fatto cosa a chi: la voce attiva è obbligatoria.
    """
    MAIN_ACTOR = "MAIN_ACTOR"
    VICTIM = "VICTIM"
    PARTICIPANT = "PARTICIPANT"
    AFFECTED = "AFFECTED"
    WITNESS = "WITNESS"
    FOUNDED = "FOUNDED"          # l'evento ha fondato questa entità
    DISSOLVED = "DISSOLVED"      # l'evento ha dissolto questa entità


# ─── v6.4: Cities + Trade Routes ────────────────────────────────────────────


class CityType(enum.StrEnum):
    """Tipo funzionale di una città storica.

    ETHICS: una città può avere più funzioni in epoche diverse (Venezia
    come trade_hub + capital + religious_center). Se una funzione è
    dominante nel periodo rappresentato, usa quella. Altrimenti
    MULTI_PURPOSE con note esplicite.
    """
    CAPITAL = "CAPITAL"
    TRADE_HUB = "TRADE_HUB"
    RELIGIOUS_CENTER = "RELIGIOUS_CENTER"
    FORTRESS = "FORTRESS"
    PORT = "PORT"
    ACADEMIC_CENTER = "ACADEMIC_CENTER"
    INDUSTRIAL_CENTER = "INDUSTRIAL_CENTER"
    MULTI_PURPOSE = "MULTI_PURPOSE"
    OTHER = "OTHER"


class RouteType(enum.StrEnum):
    """Tipo geografico di una rotta commerciale.

    CARAVAN è distinto da LAND perché implica carovane (cammelli, yak)
    e infrastrutture specifiche (caravanserragli), non semplice strada.
    """
    LAND = "LAND"
    SEA = "SEA"
    RIVER = "RIVER"
    CARAVAN = "CARAVAN"
    MIXED = "MIXED"
