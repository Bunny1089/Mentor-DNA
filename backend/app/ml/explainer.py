"""Explainable risk factor attribution and evidence engine for Merchant DNA."""

from typing import Dict, List, Any, Optional
from app.core.config import BusinessCategory, CATEGORY_BASELINES, RiskLevel
from app.core.models import RiskFactorContribution, Merchant
from app.data.store import DataStore, store
from app.ml.network_detector import DetectedRing


class RiskExplainer:
    """Generates transparent, deterministic evidence breakdowns grounded in actual data."""

    def __init__(self, datastore: DataStore = store):
        self.ds = datastore

    def generate_risk_explanations(
        self,
        merchant_id: str,
        features: Dict[str, float],
        network_features: Dict[str, float],
        ring: Optional[DetectedRing] = None,
        behavioral_score: float = 0.0,
        network_score: float = 0.0,
    ) -> List[RiskFactorContribution]:
        """Generates ranked, evidence-backed factor contributions for a merchant."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            return []

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

        factors: List[RiskFactorContribution] = []

        # ==========================================
        # 1. Network & Ring Factors (Highest Impact)
        # ==========================================
        if ring:
            factors.append(
                RiskFactorContribution(
                    factor_id="NET_RING_MEMBERSHIP",
                    title="Collusive Ring Membership Detected",
                    description=f"Identified as a coordinated node in syndication '{ring.ring_id}' with {ring.ring_size} member merchants sharing infrastructure ({ring.dominant_shared_identifier}).",
                    category="NETWORK",
                    weight=0.35,
                    value_observed=f"{ring.ring_size} merchants linked",
                    benchmark="Isolated operations (1 merchant)",
                    severity="CRITICAL",
                )
            )

        if network_features.get("shared_device_count", 0) > 0:
            count = int(network_features["shared_device_count"])
            factors.append(
                RiskFactorContribution(
                    factor_id="NET_SHARED_DEVICE",
                    title="Shared Hardware Device Fingerprint",
                    description=f"Hardware device fingerprint ({merchant.device_id}) is actively used to operate {count} other merchant accounts.",
                    category="NETWORK",
                    weight=0.28,
                    value_observed=f"{count} shared merchant(s)",
                    benchmark="Dedicated terminal (0 shared)",
                    severity="CRITICAL" if count >= 3 else "HIGH",
                )
            )

        if network_features.get("shared_bank_account_count", 0) > 0:
            count = int(network_features["shared_bank_account_count"])
            factors.append(
                RiskFactorContribution(
                    factor_id="NET_SHARED_BANK",
                    title="Shared Settlement Bank Account",
                    description=f"Settlement beneficiary bank account ({merchant.bank_account_id}) is shared with {count} other distinct legal entities.",
                    category="NETWORK",
                    weight=0.30,
                    value_observed=f"{count} shared merchant(s)",
                    benchmark="Individual corporate account (0 shared)",
                    severity="CRITICAL",
                )
            )

        if network_features.get("shared_upi_count", 0) > 0:
            count = int(network_features["shared_upi_count"])
            factors.append(
                RiskFactorContribution(
                    factor_id="NET_SHARED_UPI",
                    title="Shared Payout UPI Handle",
                    description=f"Payout UPI handle ({merchant.upi_handle_id}) is linked across {count} other storefronts.",
                    category="NETWORK",
                    weight=0.25,
                    value_observed=f"{count} shared merchant(s)",
                    benchmark="Unique VPA (0 shared)",
                    severity="HIGH",
                )
            )

        if network_features.get("shared_phone_count", 0) > 0:
            count = int(network_features["shared_phone_count"])
            factors.append(
                RiskFactorContribution(
                    factor_id="NET_SHARED_PHONE",
                    title="Shared Registration Phone Number",
                    description=f"Primary contact number ({merchant.phone_id}) is shared across {count} merchant accounts.",
                    category="NETWORK",
                    weight=0.20,
                    value_observed=f"{count} shared merchant(s)",
                    benchmark="0 shared numbers",
                    severity="HIGH" if count >= 3 else "MEDIUM",
                )
            )

        if network_features.get("shared_address_count", 0) > 0:
            count = int(network_features["shared_address_count"])
            factors.append(
                RiskFactorContribution(
                    factor_id="NET_SHARED_ADDRESS",
                    title="Shared Physical Business Address",
                    description=f"Registered physical address ({merchant.address_id}) is common to {count} other newly onboarded merchants.",
                    category="NETWORK",
                    weight=0.15,
                    value_observed=f"{count} shared merchant(s)",
                    benchmark="Unique commercial premise",
                    severity="MEDIUM" if count < 5 else "HIGH",
                )
            )

        # ==========================================
        # 2. Velocity & Temporal Factors
        # ==========================================
        growth_48h = features.get("volume_growth_48h", 0.0)
        if growth_48h >= 2.5:
            factors.append(
                RiskFactorContribution(
                    factor_id="VEL_VOLUME_SPIKE_48H",
                    title="Sudden Volume Velocity Spike",
                    description=f"Transaction volume increased {growth_48h:.1f}× over baseline daily averages in the past 48 hours.",
                    category="VELOCITY",
                    weight=0.25,
                    value_observed=f"{growth_48h:.1f}× baseline",
                    benchmark="1.0× - 1.8× baseline",
                    severity="CRITICAL" if growth_48h >= 5.0 else "HIGH",
                )
            )

        dormancy_days = features.get("dormancy_days_before_spike", 0.0)
        if dormancy_days >= 20.0 and growth_48h >= 2.0:
            factors.append(
                RiskFactorContribution(
                    factor_id="VEL_DORMANT_BURST",
                    title="Dormant Account Burst Pattern",
                    description=f"Account remained dormant for {dormancy_days:.0f} days following onboarding before exhibiting sudden high-velocity volume.",
                    category="VELOCITY",
                    weight=0.22,
                    value_observed=f"{dormancy_days:.0f} dormant days",
                    benchmark="Continuous organic transaction ramp",
                    severity="HIGH",
                )
            )

        # ==========================================
        # 3. Behavioral & Catalog Mismatch Factors
        # ==========================================
        round_ratio = features.get("round_transaction_ratio", 0.0)
        cat_round_base = cat_info.get("round_number_ratio_baseline", 0.10)
        if round_ratio >= 0.50:
            factors.append(
                RiskFactorContribution(
                    factor_id="BEH_ROUND_NUMBERS",
                    title="High Round-Amount Clustering",
                    description=f"{round_ratio * 100:.0f}% of transactions are even round denominations (e.g. ₹25k / ₹50k), characteristic of synthetic pass-through laundering.",
                    category="BEHAVIORAL",
                    weight=0.20,
                    value_observed=f"{round_ratio * 100:.0f}% round amounts",
                    benchmark=f"~{cat_round_base * 100:.0f}% organic baseline",
                    severity="HIGH" if round_ratio >= 0.80 else "MEDIUM",
                )
            )

        buyer_hhi = features.get("buyer_hhi", 0.0)
        top_conc = features.get("top_buyer_concentration", 0.0)
        if buyer_hhi >= 0.25 or top_conc >= 0.40:
            factors.append(
                RiskFactorContribution(
                    factor_id="BEH_BUYER_CONCENTRATION",
                    title="Abnormal Buyer Concentration",
                    description=f"Buyer entropy is severely skewed (HHI: {buyer_hhi:.2f}); top buyer generates {top_conc * 100:.0f}% of total processed revenue.",
                    category="BEHAVIORAL",
                    weight=0.22,
                    value_observed=f"HHI: {buyer_hhi:.2f} | Top: {top_conc * 100:.0f}%",
                    benchmark="HHI < 0.08 (diverse customer base)",
                    severity="CRITICAL" if buyer_hhi >= 0.40 else "HIGH",
                )
            )

        avg_ticket = features.get("average_transaction_amount", 0.0)
        exp_ticket = cat_info["avg_ticket"]
        if avg_ticket >= exp_ticket * 2.5:
            ticket_ratio = avg_ticket / max(1.0, exp_ticket)
            factors.append(
                RiskFactorContribution(
                    factor_id="BEH_CATEGORY_MISMATCH",
                    title="Catalog Ticket Mismatch",
                    description=f"Observed average ticket size (₹{avg_ticket:,.0f}) is {ticket_ratio:.1f}× higher than typical {merchant.category.value} baseline (₹{exp_ticket:,.0f}).",
                    category="BEHAVIORAL",
                    weight=0.24,
                    value_observed=f"₹{avg_ticket:,.0f} avg ticket",
                    benchmark=f"₹{exp_ticket:,.0f} expected baseline",
                    severity="CRITICAL" if ticket_ratio >= 5.0 else "HIGH",
                )
            )

        # ==========================================
        # 4. Settlement & Cashout Liquidity Factors
        # ==========================================
        rapid_settl = features.get("rapid_settlement_ratio", 0.0)
        if rapid_settl >= 0.50:
            factors.append(
                RiskFactorContribution(
                    factor_id="SETTL_RAPID_DRAWDOWNS",
                    title="Accelerated Settlement Drawdown",
                    description=f"{rapid_settl * 100:.0f}% of settlements were liquidated within 2 hours of payment receipt, preventing standard dispute recovery.",
                    category="SETTLEMENT",
                    weight=0.18,
                    value_observed=f"{rapid_settl * 100:.0f}% rapid liquidations",
                    benchmark="Standard T+1 / T+2 settlement cadence",
                    severity="HIGH",
                )
            )

        # Sort factors by weight descending
        factors.sort(key=lambda f: f.weight, reverse=True)
        return factors


# Global explainer instance
risk_explainer = RiskExplainer(store)
