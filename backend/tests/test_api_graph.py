"""Unit tests for graph exploration and ring endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_merchant_graph():
    """Verify GET /api/graph/merchant/{id} returns Cytoscape-compatible subgraph."""
    response = client.get("/api/graph/merchant/M-ALPHA-01")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == "M-ALPHA-01"
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0
    assert data["ring_id"] == "RING-ALPHA-DEVICE-FARM"

    node_ids = {n["id"] for n in data["nodes"]}
    assert "M-ALPHA-01" in node_ids


def test_get_rings_and_cluster_subgraph():
    """Verify GET /api/graph/rings and GET /api/graph/rings/{id}."""
    res_rings = client.get("/api/graph/rings")
    assert res_rings.status_code == 200
    rings = res_rings.json()
    assert len(rings) >= 3

    alpha_ring = next(r for r in rings if r["ring_id"] == "RING-ALPHA-DEVICE-FARM")
    assert alpha_ring["ring_size"] == 10
    assert alpha_ring["dominant_shared_identifier"] in ["DEVICE", "PHONE"]

    # Retrieve full ring cluster subgraph
    res_sub = client.get("/api/graph/rings/RING-ALPHA-DEVICE-FARM")
    assert res_sub.status_code == 200
    sub_data = res_sub.json()
    assert sub_data["ring_id"] == "RING-ALPHA-DEVICE-FARM"
    assert len(sub_data["nodes"]) >= 10


def test_graph_404_handling():
    """Verify invalid merchant or ring IDs return 404."""
    res_m = client.get("/api/graph/merchant/M-INVALID")
    assert res_m.status_code == 404

    res_r = client.get("/api/graph/rings/RING-INVALID")
    assert res_r.status_code == 404
