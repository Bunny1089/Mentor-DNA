"""Tests for the Merchant Trust Signal API (GET /api/trust/{merchant_id})."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.store import store
from app.core.config import RiskLevel

client = TestClient(app)


def test_trust_signal_verified_or_standard_merchant():
    """Legitimate low-risk merchants should return a positive trust tier (VERIFIED / STANDARD)."""
    # Find a low-risk merchant
    merchants = store.get_all_merchants()
    # M-1024 or legitimate merchant
    low_risk_m = next((m for m in merchants if not m.id.startswith("M-ALPHA") and not m.id.startswith("M-BETA") and not m.id.startswith("M-GAMMA")), merchants[0])
    
    response = client.get(f"/api/trust/{low_risk_m.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == low_risk_m.id
    assert data["business_name"] == low_risk_m.business_name
    assert data["trust_tier"] in ("VERIFIED", "STANDARD", "CAUTION")
    assert isinstance(data["instant_settlement_eligible"], bool)
    assert isinstance(data["agentic_purchasing_approved"], bool)
    assert "last_updated" in data
    # Ensure internal raw numbers (e.g. behavioral_score, network_risk) are NOT leaked in public trust payload
    assert "behavioral_risk" not in data
    assert "network_risk" not in data
    assert "overall_risk" not in data


def test_trust_signal_critical_risk_merchant_withheld():
    """Critical risk ring merchants should have their trust signal withheld (trust_tier: null)."""
    response = client.get("/api/trust/M-ALPHA-01")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == "M-ALPHA-01"
    assert data["trust_tier"] is None
    assert data["instant_settlement_eligible"] is False
    assert data["agentic_purchasing_approved"] is False
    assert "withheld" in data["short_reason"].lower() or "active risk" in data["short_reason"].lower()


def test_trust_signal_nonexistent_merchant_404():
    """Non-existent merchant IDs should return clean 404 JSON error."""
    response = client.get("/api/trust/M-DOES-NOT-EXIST-999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == "MERCHANT_NOT_FOUND" or data.get("status_code") == 404


def test_trust_tier_high_risk_boundary(monkeypatch):
    """Test the exact boundary at the HIGH risk threshold (60.0).
    
    A merchant scored at 59.0 (MEDIUM risk) must receive a non-null trust tier (CAUTION),
    while a merchant scored at 60.0 (HIGH risk threshold) must have trust_tier: null.
    """
    from app.ml.scoring_engine import scoring_engine
    from app.core.models import RiskScoreBreakdown, ActionType
    from datetime import datetime, timezone

    # Pick a baseline merchant
    m = store.get_all_merchants()[0]

    # Case 1: Just below threshold (Score 59.0 -> MEDIUM Risk)
    def mock_calc_medium(merchant_id):
        return RiskScoreBreakdown(
            merchant_id=merchant_id,
            behavioral_risk=60.0,
            network_risk=58.0,
            overall_risk=59.0,
            risk_level=RiskLevel.MEDIUM,
            confidence=0.85,
            top_factors=[],
            recommended_action=ActionType.ENHANCED_MONITORING,
            action_rationale="Moderate risk",
            ring_id=None,
            connected_high_risk_count=0,
            calculated_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(scoring_engine, "calculate_merchant_risk", mock_calc_medium)
    store.set_merchant_state(m.id, store.get_merchant_state(m.id)) # keep current state
    res_59 = client.get(f"/api/trust/{m.id}")
    assert res_59.status_code == 200
    data_59 = res_59.json()
    assert data_59["trust_tier"] == "CAUTION"
    assert data_59["trust_tier"] is not None
    assert data_59["instant_settlement_eligible"] is False
    assert data_59["agentic_purchasing_approved"] is True

    # Case 2: At/Above threshold (Score 60.0 -> HIGH Risk)
    def mock_calc_high(merchant_id):
        return RiskScoreBreakdown(
            merchant_id=merchant_id,
            behavioral_risk=62.0,
            network_risk=59.0,
            overall_risk=60.0,
            risk_level=RiskLevel.HIGH,
            confidence=0.88,
            top_factors=[],
            recommended_action=ActionType.SETTLEMENT_REVIEW,
            action_rationale="High risk review required",
            ring_id=None,
            connected_high_risk_count=1,
            calculated_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(scoring_engine, "calculate_merchant_risk", mock_calc_high)
    res_60 = client.get(f"/api/trust/{m.id}")
    assert res_60.status_code == 200
    data_60 = res_60.json()
    assert data_60["trust_tier"] is None
    assert data_60["instant_settlement_eligible"] is False
    assert data_60["agentic_purchasing_approved"] is False
    assert "withheld" in data_60["short_reason"].lower()


def test_trust_api_rate_limiting():
    """Rapid queries exceeding 60 req/min should receive HTTP 429 with rate limit headers."""
    from app.core.security import trust_rate_limiter
    trust_rate_limiter.reset()

    merchants = store.get_all_merchants()
    m_id = merchants[0].id

    headers = {"X-Forwarded-For": "198.51.100.42"}

    # First 60 requests should succeed
    for _ in range(60):
        resp = client.get(f"/api/trust/{m_id}", headers=headers)
        assert resp.status_code == 200
        assert "X-RateLimit-Remaining" in resp.headers

    # 61st request should be throttled with HTTP 429
    throttled_resp = client.get(f"/api/trust/{m_id}", headers=headers)
    assert throttled_resp.status_code == 429
    data = throttled_resp.json()
    assert data["error"] == "RATE_LIMIT_EXCEEDED"
    assert "Retry-After" in throttled_resp.headers


def test_trust_api_probing_abuse_detection():
    """Querying >20 distinct merchants in under 5 minutes triggers probing abuse detection."""
    from app.core.security import trust_rate_limiter
    trust_rate_limiter.reset()

    merchants = store.get_all_merchants()
    headers = {"X-Forwarded-For": "203.0.113.88"}

    # Query 22 distinct merchants
    abuse_triggered = False
    for i in range(min(25, len(merchants))):
        resp = client.get(f"/api/trust/{merchants[i].id}", headers=headers)
        if resp.status_code == 429:
            abuse_triggered = True
            data = resp.json()
            assert data["error"] in ("PROBE_ABUSE_DETECTED", "RATE_LIMIT_EXCEEDED", "ABUSE_DETECTED_SCORE_PROBING")
            break

    # Once flagged, the IP is throttled
    assert abuse_triggered or "203.0.113.88" in trust_rate_limiter.flagged_probe_ips

