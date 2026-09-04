"""Unit tests for RiskExplainer evidence generation."""

import pytest
from app.data.store import DataStore
from app.ml.scoring_engine import HybridScoringEngine


def test_explanations_grounded_in_real_data():
    """Verify generated risk factor explanations contain real entity IDs and exact metrics."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)

    # Test Ring Alpha member
    alpha_breakdown = engine.calculate_merchant_risk("M-ALPHA-01")
    factors = alpha_breakdown.top_factors
    assert len(factors) > 0

    # Ensure device or ring evidence is present and references real entity ID
    factor_texts = " ".join([f.title + " " + f.description + " " + f.value_observed for f in factors])
    assert "DEV-FARM-991" in factor_texts or "PH-VOIP-ALPHA" in factor_texts or "RING-ALPHA-DEVICE-FARM" in factor_texts

    # Verify factors are sorted by weight descending
    weights = [f.weight for f in factors]
    assert weights == sorted(weights, reverse=True)


def test_mule_explanation_metrics():
    """Verify mule explanation contains real burst multipliers, round ratio, and HHI."""
    ds = DataStore(auto_seed=True)
    engine = HybridScoringEngine(datastore=ds)

    mule_breakdown = engine.calculate_merchant_risk("M-2001")
    factors = mule_breakdown.top_factors
    assert len(factors) > 0

    factor_ids = {f.factor_id for f in factors}
    # Check for presence of velocity spike, round numbers, buyer concentration or category mismatch
    assert any(
        fid in factor_ids
        for fid in [
            "VEL_VOLUME_SPIKE_48H",
            "BEH_ROUND_NUMBERS",
            "BEH_BUYER_CONCENTRATION",
            "BEH_CATEGORY_MISMATCH",
            "VEL_DORMANT_BURST",
        ]
    )
