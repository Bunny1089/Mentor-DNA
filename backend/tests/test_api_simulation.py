"""Unit tests for demo simulation API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulate_mule_spike_endpoint():
    """Verify POST /api/simulation/mule injects transactions and returns before/after risk scores."""
    response = client.post("/api/simulation/mule", json={"merchant_id": "M-1005", "seed": 42})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "MULE_BURST_SPIKE"
    assert data["merchant_id"] == "M-1005"
    assert data["transactions_injected"] == 35
    assert data["injected_volume"] > 0
    assert data["new_risk_score"] > data["previous_risk_score"]
    assert data["new_risk_level"] in ["HIGH", "CRITICAL"]


def test_simulate_ring_emergence_endpoint():
    """Verify POST /api/simulation/ring creates coordinated syndicate nodes in real time."""
    response = client.post("/api/simulation/ring", json={"seed": 42})
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] == "COLLUSIVE_RING_EMERGENCE"
    assert data["created_merchants_count"] == 4
    assert len(data["member_merchant_ids"]) == 4
    assert data["sample_member_risk_score"] >= 70.0


def test_reset_simulation_state_endpoint():
    """Verify POST /api/simulation/reset restores baseline state."""
    # First mutate by simulating ring
    client.post("/api/simulation/ring", json={"seed": 42})
    # Then reset
    response = client.post("/api/simulation/reset")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RESET_SUCCESS"
    assert data["merchant_count"] == 240

