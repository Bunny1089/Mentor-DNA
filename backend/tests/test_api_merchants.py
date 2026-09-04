"""Unit tests for merchant query and risk endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_merchants_paginated():
    """Verify GET /api/merchants returns paginated list with total count."""
    response = client.get("/api/merchants?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 240
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["merchants"]) == 10
    assert "merchant_id" in data["merchants"][0]
    assert "overall_risk" in data["merchants"][0]


def test_get_merchants_filtered_by_risk_and_category():
    """Verify GET /api/merchants filter parameters work correctly."""
    # Filter by CRITICAL
    res_crit = client.get("/api/merchants?risk_level=CRITICAL")
    assert res_crit.status_code == 200
    data_crit = res_crit.json()
    for m in data_crit["merchants"]:
        assert m["risk_level"] == "CRITICAL"

    # Filter by Category
    res_cat = client.get("/api/merchants?category=ELECTRONICS")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    for m in data_cat["merchants"]:
        assert m["category"] == "ELECTRONICS"


def test_get_merchant_detail_and_404():
    """Verify GET /api/merchants/{id} returns merchant profile and handles 404."""
    response = client.get("/api/merchants/M-ALPHA-01")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == "M-ALPHA-01"
    assert data["risk_summary"]["overall_risk"] >= 80.0

    # Non-existent merchant
    res_404 = client.get("/api/merchants/M-NON-EXISTENT-999")
    assert res_404.status_code == 404
    assert "error" in res_404.json()["detail"]


def test_get_merchant_risk_breakdown():
    """Verify GET /api/merchants/{id}/risk returns complete RiskScoreBreakdown."""
    response = client.get("/api/merchants/M-2001/risk")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_id"] == "M-2001"
    assert 0.0 <= data["behavioral_risk"] <= 100.0
    assert 0.0 <= data["network_risk"] <= 100.0
    assert 0.0 <= data["overall_risk"] <= 100.0
    assert len(data["top_factors"]) > 0
