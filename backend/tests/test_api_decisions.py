"""Unit tests for action recommendations, decisions, rollback, audit, and feedback endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_action_recommendation():
    """Verify GET /api/investigations/{id}/action returns bounded action."""
    response = client.get("/api/investigations/INV-M-ALPHA-01/action")
    assert response.status_code == 200
    data = response.json()
    assert data["action"] in ["URGENT_SETTLEMENT_FREEZE", "SETTLEMENT_REVIEW"]
    assert data["requires_analyst_approval"] is True
    assert data["reversible"] is True


def test_approve_reject_and_rollback_action():
    """Verify approve, reject, and rollback API flows."""
    m_id = "M-ALPHA-03"

    # 1. Approve
    res_app = client.post(
        f"/api/investigations/INV-{m_id}/action/approve",
        json={"notes": "Approved settlement freeze after reviewing shared device fingerprint."},
    )
    assert res_app.status_code == 200
    dec_data = res_app.json()
    assert dec_data["decision"] == "CONFIRMED_FRAUD"
    assert dec_data["new_state"] == "ACTIONED"

    # 2. Rollback
    res_rb = client.post(
        f"/api/investigations/INV-{m_id}/action/rollback",
        json={"rollback_reason": "Merchant supplied official corporate physical lease agreement."},
    )
    assert res_rb.status_code == 200
    rb_data = res_rb.json()
    assert rb_data["new_state"] == "CLEARED"

    # 3. Reject flow on another merchant
    res_rej = client.post(
        "/api/investigations/INV-M-ALPHA-04/action/reject",
        json={"justification": "False positive; seasonal promotional surge verified."},
    )
    assert res_rej.status_code == 200
    assert res_rej.json()["decision"] == "FALSE_POSITIVE"


def test_decision_validation_and_reasons():
    """Verify decision recording validates non-empty justification."""
    res_err = client.post(
        "/api/investigations/INV-M-1001/decision",
        json={"decision": "CLEARED", "justification": ""},
    )
    # Validation error from Pydantic (min_length=3)
    assert res_err.status_code == 422


def test_audit_log_and_feedback_endpoints():
    """Verify GET audit-log and POST/GET feedback endpoints."""
    # Audit log
    res_aud = client.get("/api/investigations/INV-M-ALPHA-03/audit-log")
    assert res_aud.status_code == 200
    logs = res_aud.json()
    assert len(logs) >= 2  # Approval + Rollback entries

    # Submit feedback
    res_fb = client.post(
        "/api/investigations/INV-M-ALPHA-03/feedback",
        json={"feedback_type": "CONFIRMED_FRAUD", "notes": "Emulator farm pattern verified"},
    )
    assert res_fb.status_code == 200
    assert res_fb.json()["feedback_type"] == "CONFIRMED_FRAUD"

    # Get all feedback
    res_all_fb = client.get("/api/feedback")
    assert res_all_fb.status_code == 200
    fb_summary = res_all_fb.json()
    assert fb_summary["total_feedback_count"] >= 1
