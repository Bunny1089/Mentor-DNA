"""Merchant behavioral feature extraction engine (32 features)."""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from app.core.config import CATEGORY_BASELINES, BusinessCategory
from app.core.models import Merchant, Transaction, Settlement, Refund
from app.data.store import DataStore, store


def _as_naive(dt: datetime) -> datetime:
    """Converts any datetime to naive datetime for clean arithmetic."""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


class MerchantFeatureExtractor:
    """Computes merchant behavioral feature vectors from historical transactional activity."""

    def __init__(self, datastore: DataStore = store, anchor_time: Optional[datetime] = None):
        self.ds = datastore
        # Default anchor to end of synthetic observation window
        self.anchor_time = _as_naive(anchor_time or datetime(2026, 7, 1, 0, 0, 0))
        self._cache: Dict[str, Dict[str, float]] = {}

        # Full 32 feature names list
        self.feature_names = [
            # 1. Transaction Behavior (7)
            "transaction_count",
            "total_transaction_volume",
            "average_transaction_amount",
            "median_transaction_amount",
            "transaction_amount_std",
            "max_transaction_amount",
            "round_transaction_ratio",
            # 2. Buyer Behavior (6)
            "unique_buyer_count",
            "unique_buyer_ratio",
            "repeat_buyer_ratio",
            "new_buyer_ratio_last_7d",
            "buyer_hhi",
            "top_buyer_concentration",
            # 3. Velocity & Time-Series Dynamics (7)
            "transactions_last_24h",
            "volume_last_24h",
            "transactions_last_48h",
            "volume_last_48h",
            "volume_growth_48h",
            "dormancy_days_before_burst",
            "night_transaction_ratio",
            # 4. Catalog & Category Consistency (3)
            "ticket_size_mismatch_ratio",
            "ticket_size_zscore",
            "declared_vs_actual_ticket_ratio",
            # 5. Settlement & Liquidity Velocity (4)
            "settlement_count",
            "avg_settlement_lag_hours",
            "rapid_settlement_ratio",
            "settlement_to_volume_ratio",
            # 6. Refund & Dispute Signals (3)
            "refund_count",
            "refund_ratio",
            "refund_to_chargeback_risk_ratio",
            # 7. Operational & Lifecycle (2)
            "merchant_age_days",
            "time_to_first_transaction_hours",
        ]

    def extract_features_for_merchant(self, merchant_id: str) -> Dict[str, float]:
        """Extracts a feature dictionary for a single merchant, guaranteeing no NaN/inf."""
        if hasattr(self.ds, "_feature_cache") and merchant_id in self.ds._feature_cache:
            return dict(self.ds._feature_cache[merchant_id])
        if merchant_id in self._cache:
            return dict(self._cache[merchant_id])

        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            return {f: 0.0 for f in self.feature_names}

        txns = self.ds.get_merchant_transactions(merchant_id)
        settlements = self.ds.get_merchant_settlements(merchant_id)
        refunds = self.ds.get_merchant_refunds(merchant_id)
        cat_info = CATEGORY_BASELINES.get(
            merchant.category,
            {
                "avg_ticket": merchant.declared_avg_ticket or 1000.0,
                "ticket_std": 500.0,
                "min_ticket": 100.0,
                "max_normal_ticket": 10000.0,
                "expected_refund_rate": 0.02,
                "round_number_ratio_baseline": 0.10,
            },
        )

        txn_count = len(txns)
        amounts = [t.amount for t in txns] if txn_count > 0 else []
        timestamps = [_as_naive(t.timestamp) for t in txns] if txn_count > 0 else []

        # ==========================================
        # 1. Transaction Behavior
        # ==========================================
        if txn_count > 0:
            total_vol = float(np.sum(amounts))
            avg_amount = float(np.mean(amounts))
            med_amount = float(np.median(amounts))
            std_amount = float(np.std(amounts)) if txn_count > 1 else 0.0
            max_amount = float(np.max(amounts))
            round_count = sum(
                1 for a in amounts if (a >= 100 and a % 100 == 0) or (a >= 1000 and a % 1000 == 0)
            )
            round_ratio = float(round_count / txn_count)
        else:
            total_vol = 0.0
            avg_amount = 0.0
            med_amount = 0.0
            std_amount = 0.0
            max_amount = 0.0
            round_ratio = 0.0

        # ==========================================
        # 2. Buyer Behavior
        # ==========================================
        if txn_count > 0:
            buyer_counts: Dict[str, int] = {}
            buyer_volume: Dict[str, float] = {}
            for t in txns:
                buyer_counts[t.buyer_id] = buyer_counts.get(t.buyer_id, 0) + 1
                buyer_volume[t.buyer_id] = buyer_volume.get(t.buyer_id, 0.0) + t.amount

            uniq_buyers = len(buyer_counts)
            uniq_buyer_ratio = float(uniq_buyers / txn_count)
            repeat_buyers = sum(1 for c in buyer_counts.values() if c > 1)
            repeat_buyer_ratio = float(repeat_buyers / max(1, uniq_buyers))

            # New buyers in last 7 days
            seven_days_ago = self.anchor_time - timedelta(days=7)
            recent_buyer_ids = {t.buyer_id for t in txns if _as_naive(t.timestamp) >= seven_days_ago}
            earlier_buyer_ids = {t.buyer_id for t in txns if _as_naive(t.timestamp) < seven_days_ago}
            new_recent_buyers = len(recent_buyer_ids - earlier_buyer_ids)
            new_buyer_ratio_7d = float(new_recent_buyers / max(1, len(recent_buyer_ids)))

            # Buyer Concentration & HHI
            vol_shares = [v / total_vol for v in buyer_volume.values()] if total_vol > 0 else []
            buyer_hhi = float(sum(s**2 for s in vol_shares))
            top_buyer_conc = float(max(vol_shares)) if vol_shares else 0.0
        else:
            uniq_buyers = 0
            uniq_buyer_ratio = 0.0
            repeat_buyer_ratio = 0.0
            new_buyer_ratio_7d = 0.0
            buyer_hhi = 0.0
            top_buyer_conc = 0.0

        # ==========================================
        # 3. Velocity & Time-Series Dynamics
        # ==========================================
        if txn_count > 0:
            last_24h_cut = self.anchor_time - timedelta(hours=24)
            last_48h_cut = self.anchor_time - timedelta(hours=48)
            txns_24h = [t for t in txns if _as_naive(t.timestamp) >= last_24h_cut]
            txns_48h = [t for t in txns if _as_naive(t.timestamp) >= last_48h_cut]

            count_24h = len(txns_24h)
            vol_24h = float(sum(t.amount for t in txns_24h))
            count_48h = len(txns_48h)
            vol_48h = float(sum(t.amount for t in txns_48h))

            # Growth rate over 48h vs baseline daily
            merchant_onb = _as_naive(merchant.onboarding_date)
            active_days = max(1.0, (self.anchor_time - merchant_onb).total_seconds() / 86400.0)
            baseline_daily_vol = max(1.0, total_vol / active_days)
            vol_growth_48h = float((vol_48h / 2.0) / baseline_daily_vol)

            # Dormancy days before first burst
            sorted_times = sorted(timestamps)
            first_txn_time = sorted_times[0]
            dormancy_days = max(0.0, (first_txn_time - merchant_onb).total_seconds() / 86400.0)

            # Night transactions ratio (23:00 - 05:00)
            night_txns = sum(1 for t in timestamps if t.hour >= 23 or t.hour < 5)
            night_ratio = float(night_txns / txn_count)
        else:
            count_24h = 0
            vol_24h = 0.0
            count_48h = 0
            vol_48h = 0.0
            vol_growth_48h = 0.0
            merchant_onb = _as_naive(merchant.onboarding_date)
            dormancy_days = max(0.0, (self.anchor_time - merchant_onb).total_seconds() / 86400.0)
            night_ratio = 0.0

        # ==========================================
        # 4. Catalog & Category Consistency
        # ==========================================
        expected_avg = cat_info["avg_ticket"]
        expected_std = cat_info.get("ticket_std", 500.0)
        declared_avg = merchant.declared_avg_ticket or expected_avg

        if txn_count > 0:
            ticket_size_mismatch_ratio = float(abs(avg_amount - expected_avg) / max(1.0, expected_avg))
            ticket_size_zscore = float(abs(avg_amount - expected_avg) / max(1.0, expected_std))
            declared_vs_actual_ticket_ratio = float(avg_amount / max(1.0, declared_avg))
        else:
            ticket_size_mismatch_ratio = 0.0
            ticket_size_zscore = 0.0
            declared_vs_actual_ticket_ratio = 1.0

        # ==========================================
        # 5. Settlement & Liquidity Velocity
        # ==========================================
        settle_count = len(settlements)
        if settle_count > 0:
            settle_lags = [s.velocity_in_out_hours for s in settlements]
            avg_settle_lag = float(np.mean(settle_lags))
            rapid_settles = sum(1 for lag in settle_lags if lag < 2.0)
            rapid_settle_ratio = float(rapid_settles / settle_count)
            total_settled_vol = sum(s.amount for s in settlements)
            settle_to_vol_ratio = float(total_settled_vol / max(1.0, total_vol)) if total_vol > 0 else 0.0
        else:
            avg_settle_lag = 24.0
            rapid_settle_ratio = 0.0
            settle_to_vol_ratio = 0.0

        # ==========================================
        # 6. Refund & Dispute Signals
        # ==========================================
        refund_count = len(refunds)
        if txn_count > 0:
            refund_vol = sum(r.amount for r in refunds)
            refund_ratio = float(refund_count / txn_count)
            expected_ref_rate = cat_info.get("expected_refund_rate", 0.02)
            # High refund rate or 0 refunds when expected both carry distinct signal
            refund_risk_ratio = float(refund_ratio / max(0.001, expected_ref_rate))
        else:
            refund_ratio = 0.0
            refund_risk_ratio = 0.0

        # ==========================================
        # 7. Operational & Lifecycle
        # ==========================================
        merchant_age_days = float(max(1.0, (self.anchor_time - _as_naive(merchant.onboarding_date)).total_seconds() / 86400.0))
        if txn_count > 0:
            time_to_first_txn_hours = float((timestamps[0] - _as_naive(merchant.onboarding_date)).total_seconds() / 3600.0)
        else:
            time_to_first_txn_hours = float(merchant_age_days * 24.0)

        # Assemble and clean all features
        features = {
            "transaction_count": float(txn_count),
            "total_transaction_volume": float(total_vol),
            "average_transaction_amount": float(avg_amount),
            "median_transaction_amount": float(med_amount),
            "transaction_amount_std": float(std_amount),
            "max_transaction_amount": float(max_amount),
            "round_transaction_ratio": float(round_ratio),
            "unique_buyer_count": float(uniq_buyers),
            "unique_buyer_ratio": float(uniq_buyer_ratio),
            "repeat_buyer_ratio": float(repeat_buyer_ratio),
            "new_buyer_ratio_last_7d": float(new_buyer_ratio_7d),
            "buyer_hhi": float(buyer_hhi),
            "top_buyer_concentration": float(top_buyer_conc),
            "transactions_last_24h": float(count_24h),
            "volume_last_24h": float(vol_24h),
            "transactions_last_48h": float(count_48h),
            "volume_last_48h": float(vol_48h),
            "volume_growth_48h": float(vol_growth_48h),
            "dormancy_days_before_burst": float(dormancy_days),
            "night_transaction_ratio": float(night_ratio),
            "ticket_size_mismatch_ratio": float(ticket_size_mismatch_ratio),
            "ticket_size_zscore": float(ticket_size_zscore),
            "declared_vs_actual_ticket_ratio": float(declared_vs_actual_ticket_ratio),
            "settlement_count": float(settle_count),
            "avg_settlement_lag_hours": float(avg_settle_lag),
            "rapid_settlement_ratio": float(rapid_settle_ratio),
            "settlement_to_volume_ratio": float(settle_to_vol_ratio),
            "refund_count": float(refund_count),
            "refund_ratio": float(refund_ratio),
            "refund_to_chargeback_risk_ratio": float(refund_risk_ratio),
            "merchant_age_days": float(merchant_age_days),
            "time_to_first_transaction_hours": float(time_to_first_txn_hours),
        }

        # Impute any accidental NaN or inf
        clean_features = {}
        for k, v in features.items():
            if np.isnan(v) or np.isinf(v):
                clean_features[k] = 0.0
            else:
                clean_features[k] = float(v)

        self._cache[merchant_id] = clean_features
        if not hasattr(self.ds, "_feature_cache"):
            self.ds._feature_cache = {}
        self.ds._feature_cache[merchant_id] = clean_features
        return clean_features

    # Method alias for convenience
    extract_merchant_features = extract_features_for_merchant

    def extract_features_all_merchants(self) -> Dict[str, Dict[str, float]]:
        """Extracts features for all merchants currently in the datastore."""
        results = {}
        for m in self.ds.get_all_merchants():
            results[m.id] = self.extract_features_for_merchant(m.id)
        return results

    def extract_feature_matrix(self) -> Tuple[pd.DataFrame, List[str]]:
        """Extracts feature DataFrame and merchant ID list for all merchants in datastore."""
        data = []
        merchant_ids = []
        for m in self.ds.get_all_merchants():
            feats = self.extract_features_for_merchant(m.id)
            data.append(feats)
            merchant_ids.append(m.id)
        df = pd.DataFrame(data, index=merchant_ids)
        return df, merchant_ids


# Global Feature Extractor Singleton
feature_extractor = MerchantFeatureExtractor()
