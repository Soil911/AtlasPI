"""Test per audit R8 (v6.98.0): external_source_records polymorphic mirror.

Coverage:
  * sync_source_records script importabile + CLI parses args.
  * `_parse_sources_json` parsing robusto (malformed JSON, missing
    citation, non-list, ecc.).
  * sync_parent_type idempotente (re-run produce 0 nuovi inserts).

I test contro DB reale (SQLite test) richiedono fixture per popolare
JSON sources. Si limitano a smoke + parse logic.
"""

from __future__ import annotations


class TestParseSourcesJson:
    def test_parse_empty(self):
        from scripts.sync_source_records import _parse_sources_json
        assert _parse_sources_json(None) == []
        assert _parse_sources_json("") == []

    def test_parse_malformed(self):
        from scripts.sync_source_records import _parse_sources_json
        assert _parse_sources_json("not json") == []
        assert _parse_sources_json("{not a list}") == []
        assert _parse_sources_json("[1, 2, 3]") == []  # non-dict entries

    def test_parse_valid(self):
        from scripts.sync_source_records import _parse_sources_json
        raw = '[{"citation": "Cambridge History", "url": "http://x.com", "source_type": "academic"}]'
        result = _parse_sources_json(raw)
        assert len(result) == 1
        assert result[0]["citation"] == "Cambridge History"
        assert result[0]["url"] == "http://x.com"
        assert result[0]["source_type"] == "academic"

    def test_parse_skips_missing_citation(self):
        from scripts.sync_source_records import _parse_sources_json
        raw = '[{"url": "no citation"}, {"citation": "ok"}]'
        result = _parse_sources_json(raw)
        assert len(result) == 1
        assert result[0]["citation"] == "ok"

    def test_parse_default_source_type(self):
        from scripts.sync_source_records import _parse_sources_json
        raw = '[{"citation": "no source_type"}]'
        result = _parse_sources_json(raw)
        assert result[0]["source_type"] == "secondary"

    def test_parse_caps_long_fields(self):
        from scripts.sync_source_records import _parse_sources_json
        long_cite = "x" * 5000
        long_url = "http://" + "x" * 5000
        raw = '[{"citation": "' + long_cite + '", "url": "' + long_url + '"}]'
        result = _parse_sources_json(raw)
        assert len(result[0]["citation"]) == 1000
        assert len(result[0]["url"]) == 2000


class TestSyncCLI:
    def test_cli_importable(self):
        from scripts.sync_source_records import PARENT_TYPE_MAP, main

        assert callable(main)
        assert len(PARENT_TYPE_MAP) == 6
        assert "city" in PARENT_TYPE_MAP
        assert "language" in PARENT_TYPE_MAP

    def test_cli_invalid_only(self):
        # argparse choices reject unknown value

        from scripts.sync_source_records import main

        try:
            main(["--only=nope"])
            raise AssertionError("Should have exited with SystemExit")
        except SystemExit as exc:
            # argparse exit code 2 per invalid choice
            assert exc.code == 2
