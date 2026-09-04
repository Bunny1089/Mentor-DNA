"""Unit tests for model evaluation API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_evaluation_metrics_endpoint():
    """Verify GET /api/evaluation/metrics returns actual generated evaluation report."""
    response = client.get("/api/evaluation/metrics?threshold=60.0")
    assert response.status_code == 200
    data = response.json()
    
    # Primary benchmark is the out-of-sample harder holdout (321 merchants)
    assert data["total_merchants_evaluated"] == 321
    assert data["standard_benchmark"]["total_merchants_evaluated"] == 240
    assert data["harder_benchmark"]["total_merchants_evaluated"] == 321

    assert "metrics" in data
    assert "confusion_matrix" in data
    assert "detection_rates" in data
    assert "financial_impact_inr" in data
    assert "threshold_selection_methodology" in data
    assert "false_positive_cost_analysis" in data
    assert "known_limitations" in data

    metrics = data["metrics"]
    assert metrics["precision"] >= 0.90  # 97.2%
    assert metrics["recall"] >= 0.80     # 86.4%
    assert metrics["roc_auc"] >= 0.90    # 93.8%

    detection = data["detection_rates"]
    assert detection["planted_ring_detection_rate"] >= 0.90  # 95.1%
    assert detection["mule_shell_detection_rate"] >= 0.55   # 60.0%
