"""Golden Demo Configuration for Merchant DNA.

Deterministic reference IDs and metadata for live Buildathon presentations.
"""

from typing import Dict, Any

# Golden Demo Identifiers
GOLDEN_MERCHANT_ID: str = "M-ALPHA-01"
GOLDEN_MERCHANT_NAME: str = "Alpha Fashion Outlet"
GOLDEN_RING_ID: str = "RING-ALPHA-DEVICE-FARM"
GOLDEN_RING_NAME: str = "Device Farm Syndicate"

# Selection Rationale & Case Documentation
GOLDEN_CASE_METADATA: Dict[str, Any] = {
    "merchant_id": GOLDEN_MERCHANT_ID,
    "business_name": GOLDEN_MERCHANT_NAME,
    "category": "ECOMMERCE_FASHION",
    "ring_id": GOLDEN_RING_ID,
    "ring_type": "DEVICE_FARM_SYNDICATE",
    "shared_device_id": "DEV-FARM-991",
    "shared_phone_id": "PH-VOIP-ALPHA",
    "rationale": (
        "Selected for demo because it presents the ideal dual-vector risk profile: "
        "1. Strong Behavioral Anomaly: Severe catalog ticket mismatch (₹43,943 avg ticket vs ₹1,850 baseline), "
        "92% round denominations (₹25k/₹50k), abnormal buyer concentration (HHI: 0.39), and rapid settlement drawdown (< 2h). "
        "2. Definitive Network Evidence: Directly shares hardware emulator fingerprint DEV-FARM-991 with 4 merchants "
        "and VOIP gateway PH-VOIP-ALPHA across all 10 syndicate storefronts. "
        "3. Visual Clarity: Cytoscape network graph renders an immediately intuitive hub-and-spoke cluster "
        "without visual clutter or required zooming."
    ),
    "expected_risk_tier": "CRITICAL",
    "expected_overall_score": 100.0,
    "recommended_action": "URGENT_SETTLEMENT_FREEZE",
}
