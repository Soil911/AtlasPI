"""Unit + integration tests per Phase G1 feedback layer.

Copre:
- Validation (categoria invalida, submitter_type invalido, cross-field)
- Submit success
- Listing + filtering
- Stats aggregate
- PATCH admin-only
- Privacy (email masking nel response)
"""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from src.db.database import Base, engine
from src.db.models import FeedbackSubmission
from src.main import app


@pytest.fixture(scope="module")
def client():
    # Crea tabella feedback in dev SQLite
    Base.metadata.create_all(bind=engine, tables=[FeedbackSubmission.__table__])
    with TestClient(app) as c:
        yield c


def test_stats_initial_empty(client):
    r = client.get("/v1/feedback/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert "by_status" in data
    assert "by_category" in data
    assert "last_24h" in data


def test_invalid_category_rejected(client):
    r = client.post(
        "/v1/feedback",
        json={"category": "DEFINITELY_NOT_VALID", "submitter_type": "human"},
    )
    assert r.status_code == 422


def test_invalid_submitter_type_rejected(client):
    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "alien"},
    )
    assert r.status_code == 422


def test_incorrect_data_requires_target(client):
    # Status 422 is enough — the global error handler normalizes the
    # error detail to a generic message, but the underlying validation
    # rejected the payload (verified manually in feedback.py).
    r = client.post(
        "/v1/feedback",
        json={"category": "incorrect_data", "submitter_type": "human"},
    )
    assert r.status_code == 422


def test_missing_entity_does_not_require_target(client):
    r = client.post(
        "/v1/feedback",
        json={
            "category": "missing_entity",
            "submitter_type": "anonymous",
            "suggested_value": "An ancient kingdom not in the DB",
            "reasoning": "From Cambridge UP source",
        },
    )
    assert r.status_code == 201
    assert r.json()["id"] > 0


def test_nonexistent_entity_rejected(client):
    r = client.post(
        "/v1/feedback",
        json={
            "category": "incorrect_data",
            "submitter_type": "ai_agent",
            "submitter_id": "test-agent",
            "entity_id": 9999999,
            "suggested_value": "X",
        },
    )
    assert r.status_code == 404


def test_full_submission_roundtrip(client):
    r = client.post(
        "/v1/feedback",
        json={
            "category": "missing_source",
            "submitter_type": "ai_agent",
            "submitter_id": "claude-sonnet-4.7",
            "entity_id": 1,  # GeoEntity ID 1 should exist (Roma)
            "field_name": "sources",
            "suggested_value": "Goldsworthy 2006",
            "citation": "Goldsworthy, A. Caesar: Life of a Colossus. Yale UP, 2006. ISBN 978-0-300-12048-1.",
            "reasoning": "Strong recent academic source on Julius Caesar era",
            "confidence": 0.9,
        },
    )
    assert r.status_code == 201, f"Body: {r.text}"
    fb_id = r.json()["id"]

    # Fetch detail
    r = client.get(f"/v1/feedback/{fb_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["category"] == "missing_source"
    assert data["submitter_id"] == "claude-sonnet-4.7"  # not an email, kept as-is
    assert data["status"] == "pending"
    assert data["confidence"] == 0.9


def test_email_masking(client):
    """Email submitter_id deve essere mascherata nel response (privacy)."""
    r = client.post(
        "/v1/feedback",
        json={
            "category": "other",
            "submitter_type": "human",
            "submitter_id": "researcher@yale.edu",
            "reasoning": "Test PII masking",
        },
    )
    assert r.status_code == 201
    masked = r.json()["submitter_id"]
    assert "***@yale.edu" == masked, f"Expected masked, got: {masked!r}"


def test_list_filter_by_status(client):
    r = client.get("/v1/feedback?status=pending&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert all(item["status"] == "pending" for item in data["items"])


def test_list_filter_by_category(client):
    r = client.get("/v1/feedback?category=missing_entity&limit=5")
    assert r.status_code == 200
    data = r.json()
    assert all(item["category"] == "missing_entity" for item in data["items"])


def test_patch_without_admin_token_forbidden(client):
    # Create one to patch
    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "anonymous"},
    )
    assert r.status_code == 201
    fb_id = r.json()["id"]

    # No token configured + no header → 403
    r = client.patch(f"/v1/feedback/{fb_id}", json={"status": "accepted"})
    assert r.status_code == 403


def test_patch_with_valid_admin_token(client, monkeypatch):
    monkeypatch.setenv("ATLASPI_ADMIN_TOKEN", "test-secret-token")

    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "anonymous"},
    )
    fb_id = r.json()["id"]

    r = client.patch(
        f"/v1/feedback/{fb_id}",
        json={"status": "accepted", "review_notes": "Looks good", "applied_in_version": "6.99.76"},
        headers={"X-Admin-Token": "test-secret-token"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "accepted"
    assert data["review_notes"] == "Looks good"
    assert data["applied_in_version"] == "6.99.76"
    assert data["applied_at"] is not None


def test_patch_invalid_status_rejected(client, monkeypatch):
    monkeypatch.setenv("ATLASPI_ADMIN_TOKEN", "test-secret-token")

    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "anonymous"},
    )
    fb_id = r.json()["id"]

    r = client.patch(
        f"/v1/feedback/{fb_id}",
        json={"status": "INVALID_STATUS"},
        headers={"X-Admin-Token": "test-secret-token"},
    )
    assert r.status_code == 422


def test_stats_reflects_submissions(client):
    """Dopo molti POST, /stats deve riflettere i conteggi."""
    r = client.get("/v1/feedback/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] > 0
    assert "pending" in data["by_status"] or "accepted" in data["by_status"]


def test_text_field_max_length_enforced(client):
    """GPT-5.5 review #3: bounded text fields."""
    huge = "a" * 5000
    r = client.post(
        "/v1/feedback",
        json={
            "category": "other",
            "submitter_type": "anonymous",
            "citation": huge,  # exceeds MAX_CITATION_LEN (2000)
        },
    )
    assert r.status_code == 422


def test_nonexistent_event_id_rejected(client):
    """GPT-5.5 review #4: validate event_id existence."""
    r = client.post(
        "/v1/feedback",
        json={
            "category": "incorrect_data",
            "submitter_type": "ai_agent",
            "submitter_id": "test",
            "event_id": 999999999,
            "suggested_value": "X",
        },
    )
    assert r.status_code == 404


def test_list_default_hides_rejected(client, monkeypatch):
    """GPT-5.5 review #5: GET default should hide rejected/duplicate."""
    monkeypatch.setenv("ATLASPI_ADMIN_TOKEN", "test-token")

    # Create then reject one
    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "anonymous", "reasoning": "spam test"},
    )
    fb_id = r.json()["id"]
    client.patch(
        f"/v1/feedback/{fb_id}",
        json={"status": "rejected"},
        headers={"X-Admin-Token": "test-token"},
    )

    # Default list should NOT include the rejected one
    r = client.get("/v1/feedback?limit=200")
    ids_visible = {item["id"] for item in r.json()["items"]}
    assert fb_id not in ids_visible, "Rejected feedback leaked into default view"

    # But explicit status=rejected filter DOES show it
    r = client.get("/v1/feedback?status=rejected&limit=200")
    ids_visible = {item["id"] for item in r.json()["items"]}
    assert fb_id in ids_visible


def test_reputation_academic_email_gets_higher_score(client):
    """G2: email accademica → reputation 0.4."""
    r = client.post(
        "/v1/feedback",
        json={
            "category": "other",
            "submitter_type": "human",
            "submitter_id": "researcher@harvard.edu",
            "reasoning": "Academic test",
        },
    )
    assert r.status_code == 201
    assert r.json()["submitter_reputation"] == 0.4


def test_reputation_standard_email_lower_score(client):
    """G2: email non accademica → reputation 0.1."""
    r = client.post(
        "/v1/feedback",
        json={
            "category": "other",
            "submitter_type": "human",
            "submitter_id": "foo@gmail.com",
            "reasoning": "Standard test",
        },
    )
    assert r.status_code == 201
    assert r.json()["submitter_reputation"] == 0.1


def test_reputation_anonymous_zero(client):
    """G2: anonymous → reputation 0.0."""
    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "anonymous"},
    )
    assert r.status_code == 201
    assert r.json()["submitter_reputation"] == 0.0


def test_contributors_endpoint(client):
    """G2: leaderboard funzionante."""
    r = client.get("/v1/feedback/contributors")
    assert r.status_code == 200
    items = r.json()
    # ≥1 submitter ID con email (creato nei test sopra)
    assert isinstance(items, list)
    # Check structure of any row
    if items:
        row = items[0]
        assert "submitter_id" in row
        assert "accepted" in row
        assert "reputation" in row


def test_admin_token_constant_time(client, monkeypatch):
    """GPT-5.5 review #2: hmac.compare_digest, no timing leakage.

    Smoke test: wrong token (length match) is rejected with 403.
    Real timing test requires statistical comparison — qui solo correctness.
    """
    monkeypatch.setenv("ATLASPI_ADMIN_TOKEN", "abcdef1234567890")

    # Create a feedback first
    r = client.post(
        "/v1/feedback",
        json={"category": "other", "submitter_type": "anonymous"},
    )
    fb_id = r.json()["id"]

    # Wrong token, same length
    r = client.patch(
        f"/v1/feedback/{fb_id}",
        json={"status": "accepted"},
        headers={"X-Admin-Token": "zzzzzz1234567890"},
    )
    assert r.status_code == 403

    # Empty token rejected
    r = client.patch(
        f"/v1/feedback/{fb_id}",
        json={"status": "accepted"},
        headers={"X-Admin-Token": ""},
    )
    assert r.status_code == 403
