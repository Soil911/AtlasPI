"""Test per il modulo di validazione confidence_score."""

from src.validation.confidence import derive_status, score_completeness, validate_confidence


def test_validate_confidence_clamps_high():
    assert validate_confidence(1.5) == 1.0


def test_validate_confidence_clamps_low():
    assert validate_confidence(-0.3) == 0.0


def test_validate_confidence_passes_valid():
    assert validate_confidence(0.75) == 0.75


def test_derive_status_disputed_overrides():
    """ETHICS-003: le dispute attive hanno sempre status disputed."""
    assert derive_status(0.95, has_active_dispute=True) == "disputed"


def test_derive_status_low_confidence():
    assert derive_status(0.3) == "uncertain"


def test_derive_status_high_confidence():
    assert derive_status(0.8) == "confirmed"


def test_score_completeness_base():
    score = score_completeness(False, False, False, False)
    assert score == 0.3


def test_score_completeness_full():
    score = score_completeness(True, True, True, True)
    assert score == 1.0
