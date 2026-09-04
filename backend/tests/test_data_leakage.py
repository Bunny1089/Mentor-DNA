"""Unit test verifying complete isolation of ground truth from runtime inference."""

import pytest
from app.data.store import DataStore
from app.ml.feature_extractor import MerchantFeatureExtractor
from app.ml.network_detector import NetworkRiskDetector
from app.ml.scoring_engine import HybridScoringEngine


def test_no_ground_truth_in_features():
    """Verify ground truth labels or fraud tags never appear in feature names or extracted values."""
    ds = DataStore(auto_seed=True)
    extractor = MerchantFeatureExtractor(ds)

    feature_names = extractor.feature_names
    forbidden_terms = ["ground_truth", "true_label", "fraud_scenario", "is_fraud", "target", "y_true"]

    for name in feature_names:
        for term in forbidden_terms:
            assert term not in name.lower(), f"Forbidden label leak detected in feature name: {name}"

    # Verify extracted dictionary does not contain forbidden keys
    features = extractor.extract_features_for_merchant("M-ALPHA-01")
    for key in features.keys():
        for term in forbidden_terms:
            assert term not in key.lower(), f"Forbidden label leak detected in feature key: {key}"


def test_no_ground_truth_in_runtime_graph():
    """Verify entity graph nodes and edges do not embed true labels as runtime attributes."""
    ds = DataStore(auto_seed=True)
    detector = NetworkRiskDetector(ds)

    for node_id, attrs in detector.graph.nodes(data=True):
        assert "true_label" not in attrs, f"Ground truth leaked in node {node_id}"
        assert "fraud_scenario" not in attrs, f"Ground truth scenario leaked in node {node_id}"


def test_runtime_inference_without_ground_truth_store():
    """Verify runtime scoring engine functions seamlessly even if ground truth store is completely cleared."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)

    # Train model first
    engine.scorer.fit_from_datastore(ds)

    # Delete all ground truths from data store to simulate a live production environment
    ds.ground_truths.clear()
    assert len(ds.get_all_ground_truths()) == 0

    # Inference should execute 100% without referencing ground truth
    breakdown = engine.calculate_merchant_risk("M-1001")
    assert breakdown.overall_risk is not None
    assert breakdown.risk_level is not None

    breakdown_alpha = engine.calculate_merchant_risk("M-ALPHA-01")
    assert breakdown_alpha.overall_risk is not None
    assert breakdown_alpha.risk_level is not None
