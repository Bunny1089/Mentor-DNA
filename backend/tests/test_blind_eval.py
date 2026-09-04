"""Tests for Approximated Blind Hard-Negative Evaluation (Workstream 2.3)."""

import pytest
from app.data.generator import SyntheticDataGenerator
from app.data.store import store
from app.ml.evaluator import evaluator
from app.ml.scoring_engine import scoring_engine
from app.core.models import TrueLabel


def test_blind_hard_negatives_generation():
    """Confirms 10 realistic edge cases are generated with distinct scenario labels."""
    gen = SyntheticDataGenerator(seed=777)
    data = gen.generate_blind_hard_negatives(seed=777)

    merchants = data["merchants"]
    gts = data["ground_truths"]
    txns = data["transactions"]

    assert len(merchants) == 10
    assert len(gts) == 10
    assert len(txns) > 0

    # Ensure ground truth labels contain legitimate edge cases (hard negatives)
    labels = [gts[m.id].true_label for m in merchants]
    assert all(l == TrueLabel.LEGITIMATE for l in labels)
    # Ensure distinct scenario types are represented in planted anomalies
    scenarios = [gts[m.id].planted_anomalies[0] for m in merchants if gts[m.id].planted_anomalies]
    assert len(set(scenarios)) >= 5


def test_blind_hard_negatives_evaluation():
    """Runs the approximated blind check and verifies structure and accuracy reporting."""
    blind_res = evaluator._evaluate_blind_hard_negatives(
        harder_engine=scoring_engine,
        threshold_score=60.0,
    )

    assert blind_res["total_blind_cases"] == 10
    assert "accuracy" in blind_res
    assert isinstance(blind_res["accuracy"], float)
    assert len(blind_res["cases"]) == 10

    # Ensure methodology note honestly frames as approximated blind check
    assert "approximated blind check" in blind_res["methodology_note"].lower()

    # Check each case has full evaluation detail
    for c in blind_res["cases"]:
        assert "merchant_id" in c
        assert "business_name" in c
        assert "overall_risk_score" in c
        assert "is_correctly_classified" in c
        assert "top_factor" in c
