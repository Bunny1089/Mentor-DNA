"""Tests for Backend Error & Failure Hardening (clean JSON errors, no tracebacks, input validation)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invalid_merchant_id_returns_clean_404_across_endpoints():
    """Requesting non-existent merchant IDs should return clean 404 JSON, not unhandled errors."""
    endpoints = [
        "/api/merchants/M-INVALID-9999",
        "/api/merchants/M-INVALID-9999/risk",
        "/api/graph/merchant/M-INVALID-9999",
        "/api/investigations/M-INVALID-9999",
        "/api/investigations/M-INVALID-9999/action",
        "/api/trust/M-INVALID-9999",
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 404, f"Endpoint {ep} did not return 404 (returned {res.status_code})"
        body = res.json()
        assert "error" in body or "detail" in body
        assert "Traceback" not in str(body)


def test_malformed_request_body_returns_clean_422():
    """Submitting malformed or type-mismatched JSON bodies should return clean 422 validation error."""
    res = client.post(
        "/api/investigations/M-ALPHA-01/decision",
        json={"decision": "NOT_A_VALID_ENUM", "justification": 12345},
    )
    assert res.status_code == 422
    body = res.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert "Traceback" not in str(body)


def test_empty_string_validation_returns_clean_error():
    """Blank or whitespace-only justifications should be rejected with 400 or 422."""
    res = client.post(
        "/api/investigations/M-ALPHA-01/action/reject",
        json={"justification": "   "},
    )
    assert res.status_code in (400, 422)
    body = res.json()
    assert "Traceback" not in str(body)


def test_nonexistent_ring_returns_clean_404():
    """Querying non-existent ring should return clean 404 JSON."""
    res = client.get("/api/graph/rings/RING-NONEXISTENT")
    assert res.status_code == 404
    body = res.json()
    assert "Traceback" not in str(body)
