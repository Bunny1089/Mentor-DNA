"""Unit tests for synthetic dataset generator and planted fraud patterns."""

import pytest
from app.core.config import BusinessCategory, CATEGORY_BASELINES
from app.core.models import TrueLabel, FraudScenarioType
from app.data.generator import SyntheticDataGenerator


def test_generator_counts_and_types():
    """Verify generated entity and merchant counts meet specifications."""
    gen = SyntheticDataGenerator(seed=42)
    data = gen.generate_all()

    merchants = data["merchants"]
    transactions = data["transactions"]
    settlements = data["settlements"]
    refunds = data["refunds"]
    ground_truths = data["ground_truths"]

    assert len(merchants) == 240
    assert len(transactions) > 10000
    assert len(settlements) > 200
    assert len(refunds) > 100
    assert len(ground_truths) == 240


def test_ground_truth_distribution():
    """Verify legitimate, mule, and ring ground truth distribution."""
    gen = SyntheticDataGenerator(seed=42)
    data = gen.generate_all()
    gts = data["ground_truths"]

    legit_count = sum(1 for gt in gts.values() if gt.true_label == TrueLabel.LEGITIMATE)
    mule_count = sum(1 for gt in gts.values() if gt.true_label == TrueLabel.MULE_SHELL)
    ring_count = sum(1 for gt in gts.values() if gt.true_label == TrueLabel.RING_MEMBER)

    assert legit_count == 186
    assert mule_count == 24
    assert ring_count == 30


def test_planted_rings_entity_sharing():
    """Verify that planted fraud rings share target entities properly."""
    gen = SyntheticDataGenerator(seed=42)
    data = gen.generate_all()
    merchants = {m.id: m for m in data["merchants"]}

    # Ring Alpha (Device Farm Syndicate)
    alpha_merchants = [merchants[f"M-ALPHA-{i:02d}"] for i in range(1, 11)]
    assert len(alpha_merchants) == 10
    alpha_devices = {m.device_id for m in alpha_merchants}
    assert alpha_devices.issubset({"DEV-FARM-991", "DEV-FARM-992"})
    alpha_phones = {m.phone_id for m in alpha_merchants}
    assert alpha_phones == {"PH-VOIP-ALPHA"}

    # Ring Beta (Payout Laundering Cluster)
    beta_merchants = [merchants[f"M-BETA-{i:02d}"] for i in range(1, 11)]
    assert len(beta_merchants) == 10
    beta_banks = {m.bank_account_id for m in beta_merchants}
    assert beta_banks.issubset({"BA-BETA-HUB1", "BA-BETA-HUB2"})
    beta_upis = {m.upi_handle_id for m in beta_merchants}
    assert beta_upis == {"UPI-BETA-HUB"}

    # Ring Gamma (Burst-and-Bust Address Hub)
    gamma_merchants = [merchants[f"M-GAMMA-{i:02d}"] for i in range(1, 11)]
    assert len(gamma_merchants) == 10
    gamma_addresses = {m.address_id for m in gamma_merchants}
    assert gamma_addresses == {"ADDR-GAMMA-HUB"}


def test_reproducibility():
    """Verify that seeded generation produces 100% reproducible results."""
    gen1 = SyntheticDataGenerator(seed=42)
    data1 = gen1.generate_all()

    gen2 = SyntheticDataGenerator(seed=42)
    data2 = gen2.generate_all()

    assert len(data1["merchants"]) == len(data2["merchants"])
    assert len(data1["transactions"]) == len(data2["transactions"])
    assert data1["merchants"][0].id == data2["merchants"][0].id
    assert data1["transactions"][0].amount == data2["transactions"][0].amount
    assert data1["transactions"][100].timestamp == data2["transactions"][100].timestamp
