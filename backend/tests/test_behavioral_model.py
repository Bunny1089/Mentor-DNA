"""Unit tests for BehavioralModelScorer ML model."""

import pytest
from app.data.store import DataStore
from app.ml.feature_extractor import MerchantFeatureExtractor
from app.ml.behavioral_model import BehavioralModelScorer


def test_behavioral_model_training():
    """Verify HistGradientBoostingClassifier trains and achieves solid performance."""
    ds = DataStore(auto_seed=True)
    scorer = BehavioralModelScorer(seed=42)

    fit_stats = scorer.fit_from_datastore(ds)
    assert scorer.is_trained
    assert fit_stats["train_accuracy"] > 0.85
    assert fit_stats["val_accuracy"] > 0.80
    assert len(scorer.feature_importances_) == len(scorer.feature_names)


def test_behavioral_model_predictions_bounds():
    """Verify behavioral risk predictions are strictly bounded 0.0 to 100.0."""
    ds = DataStore(auto_seed=True)
    scorer = BehavioralModelScorer(seed=42)
    scorer.fit_from_datastore(ds)

    extractor = MerchantFeatureExtractor(ds)

    for m in ds.get_all_merchants():
        features = extractor.extract_features_for_merchant(m.id)
        prob, score = scorer.predict_risk(features)

        assert 0.0 <= prob <= 1.0
        assert 0.0 <= score <= 100.0


def test_behavioral_risk_separation():
    """Verify that mule merchants score significantly higher than legitimate merchants on behavioral signals."""
    ds = DataStore(auto_seed=True)
    scorer = BehavioralModelScorer(seed=42)
    scorer.fit_from_datastore(ds)
    extractor = MerchantFeatureExtractor(ds)

    # Legitimate baseline merchant
    legit_features = extractor.extract_features_for_merchant("M-1001")
    _, legit_score = scorer.predict_risk(legit_features)

    # Mule merchant with dormant burst and 92% round numbers
    mule_features = extractor.extract_features_for_merchant("M-2001")
    _, mule_score = scorer.predict_risk(mule_features)

    assert mule_score > legit_score
    assert mule_score >= 60.0
