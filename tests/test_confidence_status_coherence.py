"""Wave 2.4 / ETHICS-013: confidence < 0.5 non può essere status='confirmed'.

Principio 3 (trasparenza dell'incertezza): un dato a bassa confidenza marcato
'confirmed' è "certezza inventata" — peggiore dell'incertezza onesta. Un event
listener su GeoEntity (before_insert/before_update) forza 'confirmed'→'uncertain'
quando confidence < 0.5, lasciando 'disputed' (ETHICS-003) intatto.

Audit Wave 2, finding #4/#9 (HIGH): la funzione derive_status era codice morto,
mai chiamata da seed/ingest.
"""
from src.db.enums import EntityStatus
from src.db.models import GeoEntity


def test_no_confirmed_entity_below_confidence_floor(db):
    """Invariante sull'intero corpus seedato: nessun confirmed con conf<0.5."""
    bad = (
        db.query(GeoEntity)
        .filter(GeoEntity.confidence_score < 0.5, GeoEntity.status == "confirmed")
        .all()
    )
    assert not bad, (
        f"{len(bad)} entità con confidence<0.5 e status='confirmed': "
        f"{[(e.id, e.name_original, e.confidence_score) for e in bad[:10]]}"
    )


def test_listener_coerces_confirmed_to_uncertain_on_insert(db):
    e = GeoEntity(
        name_original="__test_lowconf_coerce__",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        confidence_score=0.3,
        status="confirmed",
    )
    db.add(e)
    db.flush()
    try:
        assert e.status == EntityStatus.UNCERTAIN.value
    finally:
        db.rollback()


def test_listener_leaves_disputed_untouched(db):
    # 'disputed' è riservato ai territori contestati (ETHICS-003): non va
    # sovrascritto anche se confidence è bassa.
    e = GeoEntity(
        name_original="__test_lowconf_disputed__",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        confidence_score=0.3,
        status="disputed",
    )
    db.add(e)
    db.flush()
    try:
        assert e.status == "disputed"
    finally:
        db.rollback()


def test_listener_leaves_high_confidence_confirmed(db):
    e = GeoEntity(
        name_original="__test_highconf_confirmed__",
        name_original_lang="en",
        entity_type="kingdom",
        year_start=1000,
        confidence_score=0.9,
        status="confirmed",
    )
    db.add(e)
    db.flush()
    try:
        assert e.status == "confirmed"
    finally:
        db.rollback()
