"""Tests for Score Stability and Dual-Population Feature Perturbation (Workstream 1.3)."""

import pytest
from app.data.generator import SyntheticDataGenerator
from app.data.store import DataStore
from app.ml.behavioral_model import BehavioralModelScorer
from app.ml.network_detector import NetworkRiskDetector
from app.ml.scoring_engine import HybridScoringEngine
from app.ml.evaluator import ModelEvaluator
from sklearn.model_selection import train_test_split
from app.core.models import TrueLabel


@pytest.fixture(scope="module")
def harder_test_setup():
    """Initializes a trained hybrid engine and test holdout partition for stability testing."""
    gen = SyntheticDataGenerator(seed=142)
    data = gen.generate_harder_batch(seed=142)

    ds = DataStore()
    ds.merchants = {m.id: m for m in data["merchants"]}
    ds.devices = {d.id: d for d in data["devices"]}
    ds.phones = {p.id: p for p in data["phones"]}
    ds.bank_accounts = {b.id: b for b in data["bank_accounts"]}
    ds.upi_handles = {u.id: u for u in data["upi_handles"]}
    ds.addresses = {a.id: a for a in data["addresses"]}
    ds.buyers = {b.id: b for b in data["buyers"]}
    ds.ground_truths = dict(data["ground_truths"])

    for t in data["transactions"]:
        ds.transactions[t.id] = t
        ds.merchant_transactions[t.merchant_id].append(t)
    for s in data["settlements"]:
        ds.settlements[s.id] = s
        ds.merchant_settlements[s.merchant_id].append(s)
    for r in data["refunds"]:
        ds.refunds[r.id] = r
        ds.merchant_refunds[r.merchant_id].append(r)

    all_merchants = data["merchants"]
    y_all = [1 if data["ground_truths"][m.id].true_label != TrueLabel.LEGITIMATE else 0 for m in all_merchants]

    train_m, test_m = train_test_split(
        all_merchants,
        test_size=0.30,
        random_state=142,
        stratify=y_all,
    )
    train_ids = [m.id for m in train_m]

    scorer = BehavioralModelScorer(seed=142)
    scorer.fit_from_datastore(ds, merchant_ids=train_ids)
    net_detector = NetworkRiskDetector(datastore=ds)
    engine = HybridScoringEngine(datastore=ds, scorer=scorer, net_detector=net_detector)

    return engine, test_m


def test_score_stability_dual_population(harder_test_setup):
    """Verifies score stability for non-borderline vs borderline merchants under ±5% noise."""
    engine, test_merchants = harder_test_setup
    evaluator = ModelEvaluator(datastore=engine.ds, engine=engine)

    stability = evaluator.evaluate_score_stability(
        harder_engine=engine,
        test_merchants=test_merchants,
        n_samples=20,
        perturbation_pct=0.05,
    )

    assert "non_borderline_cohort" in stability
    assert "borderline_cohort" in stability

    nb = stability["non_borderline_cohort"]
    b = stability["borderline_cohort"]

    # (a) Non-borderline merchants: expected near-0% tier flips
    assert nb["sample_size"] > 0
    assert nb["flip_rate"] <= 0.05, f"Expected near-0% flips for non-borderline, got {nb['flip_rate']}"

    # (b) Borderline merchants: measured and reported honestly without failing on non-zero
    assert b["sample_size"] > 0
    assert isinstance(b["flip_rate"], float)
    assert "Score stability near the decision threshold" in b["summary"]
    assert "Boundary sensitivity is an expected property" in b["explanation"]
