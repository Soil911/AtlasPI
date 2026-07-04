"""Modelli ORM AtlasPI — package split per dominio (v6.96.0 / audit R7).

Il file `src/db/models.py` (1131 righe, 20 classi) e' stato splittato in
sub-moduli per dominio per migliorare la navigazione e ridurre la
superficie di merge conflict. Questo `__init__.py` ri-esporta TUTTE le
classi al namespace `src.db.models`, mantenendo backward-compat per ogni
`from src.db.models import X` esistente nel codebase.

Mapping:
- `entities`: GeoEntity, CapitalHistory, NameVariant, TerritoryChange, Source
- `events`: HistoricalEvent, EventEntityLink, EventSource
- `places`: HistoricalCity, TradeRoute, RouteCityLink
- `chains`: DynastyChain, ChainLink
- `periods`: HistoricalPeriod
- `archaeology`: ArchaeologicalSite
- `rulers`: HistoricalRuler
- `languages`: HistoricalLanguage
- `observability`: ApiRequestLog, AiSuggestion

IMPORTANTE per SQLAlchemy: tutte le classi devono essere importate qui
affinche' siano registrate in `Base.metadata` per migration + create_all.
Non rimuovere import "unused" — sono semantici, non sintattici.

ETHICS: invariato. Ogni modello riflette le decisioni etiche documentate
in docs/ethics/. Vedi singolo sub-module per ETHICS-XXX rilevanti.
"""

# noqa: F401 — gli import sono ri-esportazioni intenzionali per backward-compat
from src.db.models.archaeology import ArchaeologicalSite  # noqa: F401
from src.db.models.chains import ChainLink, DynastyChain  # noqa: F401
from src.db.models.entities import (  # noqa: F401
    CapitalHistory,
    GeoEntity,
    NameVariant,
    Source,
    TerritoryChange,
)
from src.db.models.events import (  # noqa: F401
    EventEntityLink,
    EventSource,
    HistoricalEvent,
)
from src.db.models.feedback import FeedbackSubmission  # noqa: F401
from src.db.models.languages import HistoricalLanguage  # noqa: F401
from src.db.models.observability import (  # noqa: F401
    AiSuggestion,
    ApiRequestLog,
)
from src.db.models.periods import HistoricalPeriod  # noqa: F401
from src.db.models.places import HistoricalCity, RouteCityLink, TradeRoute  # noqa: F401
from src.db.models.rulers import HistoricalRuler  # noqa: F401

__all__ = [
    # entities
    "GeoEntity",
    "CapitalHistory",
    "NameVariant",
    "TerritoryChange",
    "Source",
    # events
    "HistoricalEvent",
    "EventEntityLink",
    "EventSource",
    # places (cities + trade routes)
    "HistoricalCity",
    "TradeRoute",
    "RouteCityLink",
    # chains
    "DynastyChain",
    "ChainLink",
    # periods
    "HistoricalPeriod",
    # archaeology
    "ArchaeologicalSite",
    # rulers
    "HistoricalRuler",
    # languages
    "HistoricalLanguage",
    # observability
    "ApiRequestLog",
    "AiSuggestion",
    # feedback (Phase G1)
    "FeedbackSubmission",
]
