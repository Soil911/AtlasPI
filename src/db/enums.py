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
    # Transizioni di stato / demografiche
    MIGRATION = "MIGRATION"
    COLLAPSE = "COLLAPSE"
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


# ─── v6.5: Dynasty / Succession Chains ─────────────────────────────────────


class ChainType(enum.StrEnum):
    """Tipo di catena successoria che lega più entità geopolitiche.

    Distingue tra:
      * DYNASTY: stessa entità politica con dinastie consecutive (es. Cina:
        Han→Tang→Song→Yuan→Ming→Qing).
      * SUCCESSION: una entità succede a un'altra su tema territoriale
        (es. Western Roman → Byzantine → Ottoman su core mediterraneo).
      * RESTORATION: entità formalmente restaurata dopo interruzione
        (es. Ancien Régime → Restoration France 1814).
      * COLONIAL: catena coloniale (Inca → Viceroyalty of Peru → Republic
        of Peru — l'oppressione coloniale è dato di prima classe ETHICS-002).
      * IDEOLOGICAL: linea di continuità ideologica anche con cesura statale
        (Holy Roman Empire → German Empire → Third Reich, NB: la self-
        proclaimed continuità non implica legittimità storica).
    """
    DYNASTY = "DYNASTY"
    SUCCESSION = "SUCCESSION"
    RESTORATION = "RESTORATION"
    COLONIAL = "COLONIAL"
    IDEOLOGICAL = "IDEOLOGICAL"
    OTHER = "OTHER"


# ─── v6.14: Date Precision ────────────────────────────────────────────────


class DatePrecision(enum.StrEnum):
    """Precisione della data associata a un evento o territory_change.

    Permette granularità sub-annuale: da giornaliera (DAY) a secolo (CENTURY).
    Valori più precisi non garantiscono accuratezza — il confidence_score
    dell'evento resta il giudizio di affidabilità complessivo.

    ETHICS: per date BCE, il campo calendar_note deve specificare che si
    usa il calendario prolettico gregoriano e che il calendario originale
    era diverso (es. lunare, egiziano, giuliano pre-riforma).
    """
    DAY = "DAY"           # Es. 14 luglio 1789
    MONTH = "MONTH"       # Es. ottobre 331 a.C.
    SEASON = "SEASON"     # Es. estate 410 (sacco di Roma)
    YEAR = "YEAR"         # Solo anno (default attuale)
    DECADE = "DECADE"     # Es. "anni 1340" (Peste Nera)
    CENTURY = "CENTURY"   # Es. "III secolo" (crisi del III secolo)


class SiteType(enum.StrEnum):
    """Tipo di sito archeologico / culturale (v6.37).

    ETHICS: un sito puo' essere contemporaneamente di piu' tipi (es.
    Teotihuacan e' city + religious_center). In tal caso scegliere il
    tipo dominante storiograficamente e usare `ethical_notes` per
    documentare gli altri. UNESCO e' ortogonale (flag `unesco_id` sul
    modello, non un tipo).
    """
    RUINS = "ruins"
    MONUMENT = "monument"
    ARCHAEOLOGICAL_ZONE = "archaeological_zone"
    SACRED_SITE = "sacred_site"
    BURIAL_SITE = "burial_site"
    CAVE_SITE = "cave_site"
    ROCK_ART = "rock_art"
    FORTIFICATION = "fortification"
    SETTLEMENT = "settlement"  # distinct from HistoricalCity (unincorporated/pre-urban)
    TEMPLE = "temple"
    PYRAMID = "pyramid"
    PALACE = "palace"
    ARENA = "arena"
    AQUEDUCT = "aqueduct"
    MEGALITHIC = "megalithic"
    OTHER = "other"


class TransitionType(enum.StrEnum):
    """Modalità di transizione da un'entità all'altra in una catena.

    ETHICS: il transition_type DEVE essere esplicito. CONQUEST e
    REVOLUTION non sono sostituibili da "succession" o "transition".
    Una conquista violenta non è una "successione" pacifica.
    """
    CONQUEST = "CONQUEST"           # militare, violenta
    REVOLUTION = "REVOLUTION"       # interna, regime change
    REFORM = "REFORM"               # legale/amministrativa (es. Diocletian 285)
    SUCCESSION = "SUCCESSION"       # dinastica/legittima
    RESTORATION = "RESTORATION"     # dopo interruzione
    DECOLONIZATION = "DECOLONIZATION"  # indipendenza da potenza coloniale
    PARTITION = "PARTITION"         # divisione (es. India 1947)
    UNIFICATION = "UNIFICATION"     # fusione (es. Italia 1861)
    DISSOLUTION = "DISSOLUTION"     # collasso (es. URSS 1991)
    ANNEXATION = "ANNEXATION"       # incorporazione formale
    OTHER = "OTHER"
