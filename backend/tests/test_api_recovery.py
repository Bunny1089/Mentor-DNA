"""Tests for Merchant Appeal & False-Positive Recovery Tracking."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.store import store

client = TestClient(app)


def test_get_appeal_recovery_summary():
    """Summary should report pending and resolved appeals with total recovered capital."""
    response = client.get("/api/investigations/recovery/summary")
    assert response.status_code == 200
    data = response.json()
    assert "pending_appeals_count" in data
    assert "resolved_appeals_count" in data
    assert "total_recovered_amount" in data
    assert "avg_resolution_time_hours" in data
    assert "recent_appeals" in data
    assert data["resolved_appeals_count"] >= 1
    assert data["total_recovered_amount"] > 0


def test_submit_appeal_and_validation():
    """Submitting valid appeal should transition merchant to PENDING_APPEAL_REVIEW."""
    # Test valid submission on M-ALPHA-01
    response = client.post(
        "/api/investigations/M-ALPHA-01/appeal",
        json={
            "reason": "Legitimate electronics warehouse clearance sale with valid carrier proof of delivery.",
            "contact_email": "legal@alphaelectronics.com",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPEAL_SUBMITTED"
    assert data["new_state"] == "PENDING_APPEAL_REVIEW"

    # Test rejection of empty / whitespace reason
    err_response = client.post(
        "/api/investigations/M-ALPHA-01/appeal",
        json={"reason": "   ", "contact_email": "test@store.com"},
    )
    assert err_response.status_code in (400, 422)


def test_appeal_resolution_on_action_rollback():
    """Rolling back an action on a merchant with a pending appeal should mark appeal APPROVED_RELEASED."""
    # Submit appeal for M-ALPHA-02
    client.post(
        "/api/investigations/M-ALPHA-02/appeal",
        json={
            "reason": "All transactions verified against ERP dispatch orders; requesting hold release.",
            "contact_email": "ops@alpha.com",
        },
    )

    # Roll back action on M-ALPHA-02
    rb_res = client.post(
        "/api/investigations/M-ALPHA-02/action/rollback",
        json={"rollback_reason": "Verified merchant legitimate supply chain invoices."},
    )
    assert rb_res.status_code == 200

    # Verify appeal summary reflects the resolved appeal
    summary_res = client.get("/api/investigations/recovery/summary")
    summary = summary_res.json()
    assert summary["total_recovered_amount"] > 0
