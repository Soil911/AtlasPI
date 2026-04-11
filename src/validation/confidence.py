"""Calcolo e validazione del confidence_score.

ETHICS: un dato incerto comunicato come tale è più onesto
di un dato certo inventato. Vedi CLAUDE.md, principio 3.
"""

import logging

logger = logging.getLogger(__name__)


def validate_confidence(score: float) -> float:
    """Normalizza e valida un confidence_score nel range 0.0-1.0."""
    clamped = max(0.0, min(1.0, score))
    if clamped != score:
        logger.warning(
            "confidence_score %.3f fuori range, normalizzato a %.3f", score, clamped
        )
    return clamped


def derive_status(confidence: float, has_active_dispute: bool = False) -> str:
    """Deriva lo status da confidence_score e flag di disputa.

    ETHICS: i territori contestati devono sempre avere status 'disputed',
    indipendentemente dal confidence_score. Vedi ETHICS-003.
    """
    if has_active_dispute:
        return "disputed"
    if confidence < 0.5:
        return "uncertain"
    return "confirmed"


def score_completeness(
    has_sources: bool,
    has_boundary: bool,
    has_name_variants: bool,
    has_territory_changes: bool,
) -> float:
    """Stima un confidence_score base dalla completezza dei dati."""
    score = 0.3  # base
    if has_sources:
        score += 0.25
    if has_boundary:
        score += 0.20
    if has_name_variants:
        score += 0.15
    if has_territory_changes:
        score += 0.10
    return min(1.0, score)
