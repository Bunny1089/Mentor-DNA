"""Unit tests for core FastAPI application, health check, and system status."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify /health returns status ok and version."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "merchant-dna"
    assert "version" in data


def test_system_status_endpoint():
    """Verify /api/system/status returns backend telemetry."""
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["backend_status"] == "ONLINE"
    assert data["data_loaded"] is True
    assert data["merchant_count"] == 240
    assert data["graph_nodes_count"] > 500
    assert data["detected_rings_count"] >= 3
