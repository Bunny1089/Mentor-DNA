"""Unit tests for investigation dossier and AI briefing endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_open_investigation_and_get_dossier():
    """Verify POST /api/investigations/{id} and GET /api/investigations/{id}."""
    # Open Investigation
    res_open = client.post("/api/investigations/M-ALPHA-01")
    assert res_open.status_code == 200
    dossier = res_open.json()
    assert dossier["merchant_id"] == "M-ALPHA-01"
    assert dossier["investigation_id"] == "INV-M-ALPHA-01"
    assert dossier["current_state"] in ["NEW", "UNDER_REVIEW", "ACTION_RECOMMENDED"]
    assert len(dossier["all_evidence"]) > 0
    assert len(dossier["timeline"]) > 0

    # Get Investigation by ID
    res_get = client.get("/api/investigations/INV-M-ALPHA-01")
    assert res_get.status_code == 200
    assert res_get.json()["merchant_id"] == "M-ALPHA-01"


def test_generate_ai_briefing_endpoint():
    """Verify POST /api/investigations/{id}/briefing returns grounded case note."""
    response = client.post("/api/investigations/INV-M-ALPHA-01/briefing")
    assert response.status_code == 200
    briefing = response.json()
    assert "summary" in briefing
    assert "key_evidence" in briefing
    assert "network_context" in briefing
    assert "risk_interpretation" in briefing
    assert "recommended_next_step" in briefing
    assert briefing["evidence_count"] > 0
    assert len(briefing["evidence_ids_used"]) > 0
    assert briefing["grounding_mode"] in ["DETERMINISTIC_FALLBACK", "LLM"]


def test_investigation_404_handling():
    """Verify invalid merchant/investigation ID returns 404."""
    res = client.get("/api/investigations/INV-NONEXISTENT")
    assert res.status_code == 404


def test_merchant_appeal_flow():
    """Verify POST /api/investigations/{id}/appeal transitions to PENDING_APPEAL_REVIEW and logs event."""
    client.post("/api/investigations/M-1005")
    res = client.post(
        "/api/investigations/INV-M-1005/appeal",
        json={"reason": "Legitimate seasonal discount sale; bank verification provided."},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "APPEAL_SUBMITTED"
    assert data["new_state"] == "PENDING_APPEAL_REVIEW"

    # Verify audit trail recorded appeal
    audit_res = client.get("/api/investigations/INV-M-1005/audit-log")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert any("PENDING_APPEAL_REVIEW" in e["description"] for e in events)
