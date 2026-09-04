"""Unit tests for ModelEvaluator, financial cost calculations, and threshold methodology."""

import pytest
from app.data.store import DataStore
from app.ml.scoring_engine import HybridScoringEngine
from app.ml.evaluator import ModelEvaluator
from app.core.config import settings


def test_evaluator_metrics_calculation():
    """Verify evaluation generates honest, non-fabricated metrics from actual predictions."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)
    evaluator = ModelEvaluator(datastore=ds, engine=engine)

    report = evaluator.evaluate_model_performance(threshold_score=60.0)

    # Primary benchmark is the 30% out-of-sample holdout (321 merchants)
    assert report["total_merchants_evaluated"] == 321
    assert report["primary_benchmark"].startswith("Harder Benchmark")

    # Check metrics on unseen holdout
    metrics = report["metrics"]
    assert 0.90 <= metrics["precision"] <= 1.0  # 97.2%
    assert 0.80 <= metrics["recall"] <= 1.0     # 86.4%
    assert 0.85 <= metrics["f1_score"] <= 1.0   # 0.915
    assert 0.90 <= metrics["roc_auc"] <= 1.0    # 0.938

    # Check archetype detection rates
    detection = report["detection_rates"]
    assert detection["planted_ring_detection_rate"] >= 0.90  # 95.1%
    assert 0.50 <= detection["mule_shell_detection_rate"] <= 0.75  # 60.0%

    # Check confusion matrix reconciliation
    cm = report["confusion_matrix"]
    tp, tn, fp, fn = cm["true_positives"], cm["true_negatives"], cm["false_positives"], cm["false_negatives"]
    assert tp + tn + fp + fn == 321
    calculated_precision = round(tp / (tp + fp), 4)
    calculated_recall = round(tp / (tp + fn), 4)
    assert calculated_precision == metrics["precision"]
    assert calculated_recall == metrics["recall"]


def test_false_positive_financial_cost_consistency():
    """Verify exact mathematical consistency between delayed volume, friction rate, and friction cost."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)
    evaluator = ModelEvaluator(datastore=ds, engine=engine)

    report = evaluator.evaluate_model_performance(threshold_score=60.0)
    fp_cost = report["false_positive_cost_analysis"]
    financials = report["financial_impact_inr"]

    # 1. Friction cost must exactly equal delayed volume * friction rate (2.0%)
    delayed_vol = fp_cost["fp_delayed_volume_inr"]
    friction_rate = fp_cost["fp_delay_friction_rate"]
    calculated_friction_cost = round(delayed_vol * friction_rate, 2)
    assert fp_cost["fp_estimated_friction_cost_inr"] == calculated_friction_cost
    assert financials["false_positive_friction_cost"] == calculated_friction_cost

    # 2. Cumulative historical volume must be strictly greater than or equal to 3-day delayed volume
    if fp_cost["fp_merchants_count"] > 0:
        assert fp_cost["fp_cumulative_historical_volume_inr"] >= delayed_vol

    # 3. Expected net loss must equal false negative cost + false positive friction cost
    expected_loss = round(financials["false_negative_exposure_cost"] + financials["false_positive_friction_cost"], 2)
    assert financials["expected_net_loss"] == expected_loss


def test_threshold_selection_methodology_structure():
    """Verify threshold sweep runs on training partition and provides defensible operating rationale."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)
    evaluator = ModelEvaluator(datastore=ds, engine=engine)

    report = evaluator.evaluate_model_performance(threshold_score=60.0)
    methodology = report["threshold_selection_methodology"]

    assert methodology["train_sample_size"] == 749
    assert len(methodology["sweep_grid"]) >= 5
    assert methodology["selected_threshold"] in [50.0, 55.0, 60.0]
    assert len(methodology["selection_rationale"]) > 20
    assert "Holdout test data was completely isolated" in methodology["selection_rationale"]
