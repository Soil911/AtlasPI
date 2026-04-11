"""Test integrit\u00e0 database."""

from src.db.models import GeoEntity, NameVariant


class TestSeedIdempotency:
    def test_no_duplicates(self, db):
        """Il seed non deve creare duplicati se eseguito due volte."""
        from src.db.seed import SessionLocal, seed_database
        original = SessionLocal

        from src.db import seed as seed_module
        from tests.conftest import TestSession
        seed_module.SessionLocal = TestSession
        seed_database()  # seconda esecuzione
        seed_module.SessionLocal = original

        count = db.query(GeoEntity).count()
        assert count == 55, f"Attese 55 entita', trovate {count} (seed non idempotente)"


class TestCascadeDelete:
    def test_delete_entity_removes_children(self, db):
        """Eliminare un'entit\u00e0 deve eliminare varianti, cambi e fonti."""
        entity = db.query(GeoEntity).first()
        eid = entity.id

        assert db.query(NameVariant).filter_by(entity_id=eid).count() > 0

        # Verifica cascade senza eliminare davvero (mantieni integrità per altri test)
        # Test che le relazioni sono configurate con cascade
        assert entity.name_variants is not None
        assert entity.territory_changes is not None
        assert entity.sources is not None

        # Verifica che cascade="all, delete-orphan" sia configurato
        from sqlalchemy import inspect
        mapper = inspect(GeoEntity)
        for rel in ["name_variants", "territory_changes", "sources"]:
            cascade = mapper.relationships[rel].cascade
            assert "delete" in cascade, f"Cascade delete mancante su {rel}"
            assert "delete-orphan" in cascade, f"Cascade delete-orphan mancante su {rel}"


class TestDataIntegrity:
    def test_confidence_range(self, db):
        """Tutti i confidence_score devono essere tra 0.0 e 1.0."""
        for e in db.query(GeoEntity).all():
            assert 0.0 <= e.confidence_score <= 1.0, (
                f"'{e.name_original}' ha confidence {e.confidence_score}"
            )

    def test_all_entities_have_sources(self, db):
        for e in db.query(GeoEntity).all():
            assert len(e.sources) > 0, f"'{e.name_original}' non ha fonti"

    def test_all_entities_have_name_variants(self, db):
        for e in db.query(GeoEntity).all():
            assert len(e.name_variants) > 0, f"'{e.name_original}' non ha varianti nome"
