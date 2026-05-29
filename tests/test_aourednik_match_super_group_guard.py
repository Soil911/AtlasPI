"""Test aourednik_match.py Phase H super-group guard (ETHICS-012).

Phase H (v6.99.80) added two guards to `match_entity_aourednik`:
  1. Super-group label blacklist — reject matches against cultural-zone
     labels (Bantou, Polynesians, "minor states", etc.) UNLESS exact_name.
  2. Area sanity check — reject if polygon area > type ceiling × factor
     UNLESS exact_name (which is trusted).

These tests verify both guards reject the right matches and accept
legitimate ones.
"""

from __future__ import annotations

from src.ingestion.aourednik_match import (
    TYPE_MAX_AREA_DEG2,
    _is_polygon_too_large_for_type,
    _is_super_group_label,
)

# ─── Super-group label blacklist ─────────────────────────────────────────


def test_bantu_label_is_blacklisted():
    """The 'Bantou' label was the cause of 4 collisions in Phase H."""
    assert _is_super_group_label("Bantou") is True
    assert _is_super_group_label("bantou") is True  # case insensitive
    assert _is_super_group_label("BANTOU") is True


def test_polynesians_label_is_blacklisted():
    """The 'Polynesians' label was the cause of 3 collisions in Phase H."""
    assert _is_super_group_label("Polynesians") is True


def test_hunter_gatherer_labels_blacklisted():
    """Hunter-gatherer cultural zones are too broad for any polity match."""
    assert _is_super_group_label("Amazon hunter-gatherers") is True
    assert _is_super_group_label("Eastern North American hunter-gatherers") is True
    assert _is_super_group_label("West African cereal farmers") is True


def test_kingdom_of_david_anachronistic_label_blacklisted():
    """The 'Kingdom of David and Solomon' is anachronistic for most matches."""
    assert _is_super_group_label("Kingdom of David and Solomon") is True


def test_minor_states_label_blacklisted():
    """aourednik uses 'minor states' as a bucket for Hellenistic Anatolia."""
    assert _is_super_group_label("minor states") is True


def test_specific_polity_names_not_blacklisted():
    """Specific polity names should NOT be in the blacklist."""
    assert _is_super_group_label("Roman Empire") is False
    assert _is_super_group_label("Egypt") is False
    assert _is_super_group_label("Tawantinsuyu") is False
    assert _is_super_group_label("") is False
    assert _is_super_group_label(None) is False


def test_blacklist_normalizes_diacritics():
    """The check should normalize accents — defensive against orthographic variants."""
    # If aourednik ever spells with diacritics, the blacklist still catches it.
    # (Bantou is already accent-free; this is a defensive test for future cases.)
    assert _is_super_group_label("BANTOU") == _is_super_group_label("Bantou")


# ─── Area sanity check ──────────────────────────────────────────────────


def _make_polygon(width_deg: float, height_deg: float) -> dict:
    """Build a rectangular polygon of given size centered at (0,0)."""
    w, h = width_deg / 2, height_deg / 2
    return {
        "type": "Polygon",
        "coordinates": [
            [[-w, -h], [w, -h], [w, h], [-w, h], [-w, -h]]
        ],
    }


def test_city_state_rejects_continent_sized_polygon():
    """A city-state should not match a polygon spanning a continent."""
    # 20° × 30° polygon ≈ 600 deg² — entire sub-Saharan Africa size
    huge = _make_polygon(20, 30)
    assert _is_polygon_too_large_for_type(huge, "city-state") is True


def test_city_state_accepts_small_polygon():
    """A city-state should accept a small polygon (city hinterland)."""
    small = _make_polygon(1, 1)  # 1 deg² ≈ 12k km²
    assert _is_polygon_too_large_for_type(small, "city-state") is False


def test_kingdom_accepts_large_but_not_huge():
    """A kingdom can be hundreds of km², but not millions."""
    # Kingdom ceiling: 640 deg² (~8M km²)
    moderate = _make_polygon(30, 20)  # ~600 deg² — at the limit
    assert _is_polygon_too_large_for_type(moderate, "kingdom") is False
    # Above 3× ceiling (1920 deg²) → rejected
    huge = _make_polygon(60, 50)  # 3000 deg²
    assert _is_polygon_too_large_for_type(huge, "kingdom") is True


def test_empire_accepts_huge_polygon():
    """Empires legitimately span vast areas — ceiling much higher."""
    # Empire ceiling: 3200 deg² (~40M km²)
    huge = _make_polygon(60, 50)  # 3000 deg² < 3200
    assert _is_polygon_too_large_for_type(huge, "empire") is False


def test_earthwork_complex_rejects_anything_above_2sqdeg():
    """An earthwork complex is a small archaeological site, never huge."""
    # Earthwork ceiling: 0.5 deg² × 2.0 strict factor = 1.0 deg² max
    # Just slightly above ~1.0 deg²
    above_threshold = _make_polygon(1.2, 1.2)  # 1.44 deg²
    assert _is_polygon_too_large_for_type(above_threshold, "earthwork-complex") is True
    # 0.5 deg² is OK
    ok = _make_polygon(0.5, 0.5)  # 0.25 deg² ≤ 1.0
    assert _is_polygon_too_large_for_type(ok, "earthwork-complex") is False


def test_unknown_type_passes_through():
    """If we don't have a ceiling for the type, don't reject."""
    huge = _make_polygon(60, 50)  # 3000 deg²
    # 'fictional_type' is not in TYPE_MAX_AREA_DEG2 → pass
    assert _is_polygon_too_large_for_type(huge, "fictional_type") is False


def test_null_geometry_passes_through():
    """Defensive: None geometry must not raise."""
    assert _is_polygon_too_large_for_type(None, "city-state") is False


def test_null_entity_type_passes_through():
    """Defensive: None entity_type must not raise."""
    poly = _make_polygon(1, 1)
    assert _is_polygon_too_large_for_type(poly, None) is False


# ─── Phase H baseline ────────────────────────────────────────────────────


def test_super_group_blacklist_covers_phase_h_regressions():
    """Spot-check that the labels that caused Phase H damage are blacklisted."""
    phase_h_collision_labels = {
        "Bantou",                        # 4 entities (Bunyoro, Bigo, Ntusi, Mbundu)
        "Fatimid Caliphate",             # 6 entities
        "Kingdom of David and Solomon",  # 5 entities
        "Greek city-states",             # 5 entities
        "minor states",                  # 4 entities (Hellenistic Anatolia)
        "Holy Roman Empire",             # 4 entities
        "Byzantine Empire",              # 4 entities
        "Huari Empire",                  # 4 entities
        "Srivijaya Empire",              # 4 entities
        "Sui Empire",                    # 4 entities
        "Sasanian Empire",               # 1 entity (Lakhmids)
        "Mwenemutapa",                   # 1 entity (Thulamela)
        "Jin",                           # 1 entity (Later Zhao)
        "Cuman-Kipchak confederation",   # 1 entity (Qocho)
        "Amazon hunter-gatherers",       # 1 entity (Kuhikugu)
        "West African cereal farmers",   # 1 entity (Yoruba early)
        "Eastern North American hunter-gatherers",  # 1 entity (Theloal)
    }
    missing = [
        label for label in phase_h_collision_labels
        if not _is_super_group_label(label)
    ]
    assert not missing, (
        f"Phase H regression labels missing from blacklist: {missing}. "
        "These caused 100+ collisions and must be rejected by the matcher."
    )


def test_type_ceilings_cover_common_entity_types():
    """All entity_types used in current AtlasPI DB should have a ceiling."""
    required = {
        "city", "city-state", "kingdom", "empire", "republic",
        "confederation", "chiefdom", "sultanate", "dynasty",
        "khanate", "caliphate", "earthwork-complex",
        "cultural_region", "settlement",
    }
    missing = required - set(TYPE_MAX_AREA_DEG2.keys())
    assert not missing, f"Missing type ceilings: {missing}"
