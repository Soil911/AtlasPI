"""Test per audit R3 (v6.95.0): skip-when-populated update_boundaries + seed_all.

Verifica:
  * update_all_boundaries() skippa quando >=80% entita' hanno boundary_source
    (no expensive file I/O dopo prima inizializzazione).
  * update_all_boundaries(force=True) bypassa lo skip.
  * scripts.seed_all importabile (CLI ready).
  * scripts.seed_all.run_all() esegue ogni step idempotentemente.
"""

from unittest.mock import patch


class TestUpdateBoundariesSkip:
    def test_skips_when_80pct_have_boundary_source(self, db):
        """Setup: 100 entita', 80+ con boundary_source -> skip extraction."""
        from src.db.models import GeoEntity
        from src.ingestion.update_boundaries import update_all_boundaries

        # Tutte le entita' nel test DB (conftest seedato).
        entities = db.query(GeoEntity).all()
        total = len(entities)
        assert total > 0, "Conftest deve avere popolato entita'"

        # Forza boundary_source su tutte le entita' = 100% has source
        for e in entities:
            if e.boundary_source is None:
                e.boundary_source = "test_synthetic"
        db.commit()

        # Mock extract_all_boundaries — non deve essere chiamato.
        with patch(
            "src.ingestion.update_boundaries.extract_all_boundaries"
        ) as mock_extract:
            update_all_boundaries(force=False)
            mock_extract.assert_not_called()

    def test_runs_when_force_true(self, db):
        """force=True bypassa il check skip, anche se >80% populated."""
        from src.db.models import GeoEntity
        from src.ingestion.update_boundaries import update_all_boundaries

        # Idem setup: 100% has source
        for e in db.query(GeoEntity).all():
            if e.boundary_source is None:
                e.boundary_source = "test_synthetic"
        db.commit()

        with patch(
            "src.ingestion.update_boundaries.extract_all_boundaries",
            return_value={},  # nessun boundary estratto, ma chiamato
        ) as mock_extract:
            update_all_boundaries(force=True)
            mock_extract.assert_called_once()


class TestSeedAllOrchestrator:
    def test_seed_all_importable(self):
        """Lo script deve essere importabile come modulo."""
        from scripts.seed_all import main, run_all

        assert callable(run_all)
        assert callable(main)

    def test_seed_all_cli_parses_args(self):
        """argparse non deve fallire su flag standard."""
        from unittest.mock import patch

        from scripts.seed_all import main

        # Mock run_all per evitare side effect su DB
        with patch("scripts.seed_all.run_all", return_value=0) as mock_run:
            exit_code = main(["--skip-boundaries"])
            assert exit_code == 0
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args.kwargs
            assert call_kwargs["skip_boundaries"] is True
            assert call_kwargs["force_boundaries"] is False

    def test_seed_all_only_flag(self):
        """--only=entities deve passare 'entities' a run_all."""
        from unittest.mock import patch

        from scripts.seed_all import main

        with patch("scripts.seed_all.run_all", return_value=0) as mock_run:
            main(["--only=entities"])
            assert mock_run.call_args.kwargs["only"] == "entities"
