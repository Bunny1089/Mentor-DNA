"""Unit tests verifying ground truth isolation and scenario labeling."""

import pytest
from app.core.models import TrueLabel, FraudScenarioType, RiskLevel
from app.data.store import DataStore


def test_ground_truth_isolation():
    """Verify ground truth is stored separately and accurately matches all merchant archetypes."""
    ds = DataStore(auto_seed=True)
    gts = ds.get_all_ground_truths()

    assert len(gts) == 240

    # Test Legitimate Merchant Ground Truth
    gt_legit = ds.get_ground_truth("M-1001")
    assert gt_legit is not None
    assert gt_legit.true_label == TrueLabel.LEGITIMATE
    assert gt_legit.fraud_scenario == FraudScenarioType.NONE
    assert gt_legit.expected_risk_tier == RiskLevel.LOW

    # Test Mule Merchant Ground Truth
    gt_mule = ds.get_ground_truth("M-2001")
    assert gt_mule is not None
    assert gt_mule.true_label == TrueLabel.MULE_SHELL
    assert len(gt_mule.planted_anomalies) > 0
    assert gt_mule.expected_risk_tier in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    # Test Ring Member Ground Truth
    gt_ring_alpha = ds.get_ground_truth("M-ALPHA-01")
    assert gt_ring_alpha is not None
    assert gt_ring_alpha.true_label == TrueLabel.RING_MEMBER
    assert gt_ring_alpha.planted_ring_id == "RING-ALPHA-DEVICE-FARM"
    assert gt_ring_alpha.fraud_scenario == FraudScenarioType.DEVICE_FARM_SYNDICATE
    assert gt_ring_alpha.expected_risk_tier == RiskLevel.CRITICAL
