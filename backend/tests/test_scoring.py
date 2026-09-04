"""Unit tests for HybridScoringEngine and bounded action mapping."""

import pytest
from app.core.config import RiskLevel, ActionType
from app.data.store import DataStore
from app.ml.scoring_engine import HybridScoringEngine


def test_hybrid_scoring_bounds_and_tiers():
    """Verify hybrid risk scores stay in [0, 100] and risk tiers map accurately."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)

    all_scores = engine.calculate_all_merchants_risk()
    assert len(all_scores) == 240

    for m_id, breakdown in all_scores.items():
        assert 0.0 <= breakdown.behavioral_risk <= 100.0
        assert 0.0 <= breakdown.network_risk <= 100.0
        assert 0.0 <= breakdown.overall_risk <= 100.0
        assert 0.0 <= breakdown.confidence <= 1.0

        # Verify risk level mapping
        if breakdown.overall_risk >= 80.0:
            assert breakdown.risk_level == RiskLevel.CRITICAL
            assert breakdown.recommended_action == ActionType.URGENT_SETTLEMENT_FREEZE
        elif breakdown.overall_risk >= 60.0:
            assert breakdown.risk_level == RiskLevel.HIGH
            assert breakdown.recommended_action == ActionType.SETTLEMENT_REVIEW
        elif breakdown.overall_risk >= 30.0:
            assert breakdown.risk_level == RiskLevel.MEDIUM
            assert breakdown.recommended_action == ActionType.ENHANCED_MONITORING
        else:
            assert breakdown.risk_level == RiskLevel.LOW
            assert breakdown.recommended_action == ActionType.CONTINUE_MONITORING


def test_legitimate_vs_fraud_tier_separation():
    """Verify legitimate merchants stay LOW/MEDIUM while mule & ring members reach HIGH/CRITICAL."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)

    # Legitimate merchant
    legit_risk = engine.calculate_merchant_risk("M-1001")
    assert legit_risk.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
    assert legit_risk.overall_risk < 40.0

    # Mule merchant
    mule_risk = engine.calculate_merchant_risk("M-2001")
    assert mule_risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert mule_risk.overall_risk >= 60.0

    # Ring Alpha member
    ring_risk = engine.calculate_merchant_risk("M-ALPHA-01")
    assert ring_risk.risk_level == RiskLevel.CRITICAL
    assert ring_risk.ring_id == "RING-ALPHA-DEVICE-FARM"
    assert ring_risk.overall_risk >= 80.0
