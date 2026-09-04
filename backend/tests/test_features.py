"""Unit tests for feature engineering and edge-case resilience."""

import pytest
import numpy as np
from datetime import datetime, timezone
from app.core.config import BusinessCategory
from app.core.models import Merchant, Transaction, Settlement, Refund
from app.data.store import DataStore
from app.ml.feature_extractor import MerchantFeatureExtractor


def test_feature_extractor_fields_and_types():
    """Verify all required features are extracted without NaN or infinity."""
    ds = DataStore(auto_seed=True)
    extractor = MerchantFeatureExtractor(ds)

    expected_features = extractor.feature_names
    assert len(expected_features) == 32

    df, m_ids = extractor.extract_feature_matrix()
    assert len(df) == 240
    assert list(df.columns) == expected_features

    # Check for NaN or Inf across entire feature matrix
    assert not df.isna().any().any(), "Feature matrix contains NaN values"
    assert not np.isinf(df.to_numpy()).any(), "Feature matrix contains Inf values"


def test_features_deterministic():
    """Verify feature values are 100% deterministic across multiple extractions."""
    ds = DataStore(auto_seed=True)
    extractor1 = MerchantFeatureExtractor(ds)
    extractor2 = MerchantFeatureExtractor(ds)

    f1 = extractor1.extract_features_for_merchant("M-1001")
    f2 = extractor2.extract_features_for_merchant("M-1001")

    for k in f1:
        assert f1[k] == f2[k], f"Feature {k} is not deterministic"


def test_edge_case_zero_transactions():
    """Verify merchant with zero transactions produces clean 0.0 metrics with no division by zero."""
    ds = DataStore(auto_seed=False)
    # Add empty merchant
    m = Merchant(
        id="M-EMPTY",
        business_name="Empty Store",
        legal_name="Empty Store Ltd",
        category=BusinessCategory.ECOMMERCE_FASHION,
        business_type="PROPRIETORSHIP",
        declared_avg_ticket=1850.0,
        onboarding_date=datetime(2026, 8, 1, 12, 0, 0),
        kyc_status="VERIFIED",
        device_id="DEV-9999",
        phone_id="PH-9999",
        bank_account_id="BA-9999",
        upi_handle_id="UPI-9999",
        address_id="ADDR-9999",
        is_active=True,
        created_at=datetime(2026, 8, 1, 12, 0, 0),
    )
    ds.merchants[m.id] = m

    extractor = MerchantFeatureExtractor(ds)
    features = extractor.extract_features_for_merchant("M-EMPTY")

    assert features["transaction_count"] == 0.0
    assert features["total_transaction_volume"] == 0.0
    assert features["average_transaction_amount"] == 0.0
    assert features["unique_buyer_ratio"] == 0.0
    assert features["buyer_hhi"] == 0.0
    assert features["refund_ratio"] == 0.0
    assert not any(np.isnan(v) for v in features.values())
    assert not any(np.isinf(v) for v in features.values())


def test_edge_case_single_transaction_and_buyer():
    """Verify single transaction merchant handles std, HHI, and velocity properly."""
    ds = DataStore(auto_seed=False)
    m = Merchant(
        id="M-SINGLE",
        business_name="Single Txn Store",
        legal_name="Single Txn Store Ltd",
        category=BusinessCategory.ELECTRONICS,
        business_type="PROPRIETORSHIP",
        declared_avg_ticket=14500.0,
        onboarding_date=datetime(2026, 8, 1, 12, 0, 0),
        kyc_status="VERIFIED",
        device_id="DEV-9998",
        phone_id="PH-9998",
        bank_account_id="BA-9998",
        upi_handle_id="UPI-9998",
        address_id="ADDR-9998",
        is_active=True,
        created_at=datetime(2026, 8, 1, 12, 0, 0),
    )
    ds.merchants[m.id] = m
    txn = Transaction(
        id="TXN-SINGLE-1",
        merchant_id="M-SINGLE",
        buyer_id="B-SINGLE-1",
        amount=15000.0,
        currency="INR",
        status="SUCCESS",
        payment_method="UPI",
        timestamp=datetime(2026, 8, 15, 12, 0, 0),
        is_round_amount=True,
        ip_address="192.168.1.1",
        device_id="DEV-9998",
    )
    ds.transactions[txn.id] = txn
    ds.merchant_transactions[m.id].append(txn)

    extractor = MerchantFeatureExtractor(ds)
    features = extractor.extract_features_for_merchant("M-SINGLE")

    assert features["transaction_count"] == 1.0
    assert features["transaction_amount_std"] == 0.0
    assert features["buyer_hhi"] == 1.0
    assert features["top_buyer_concentration"] == 1.0
    assert features["unique_buyer_ratio"] == 1.0
    assert features["refund_ratio"] == 0.0
    assert not any(np.isnan(v) for v in features.values())
    assert not any(np.isinf(v) for v in features.values())
