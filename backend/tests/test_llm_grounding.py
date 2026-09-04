"""Unit tests verifying strict grounding of AI case briefings."""

import pytest
from datetime import datetime, timezone
from app.core.config import RiskLevel, ActionType, BusinessCategory
from app.core.models import (
    RiskScoreBreakdown,
    EvidenceItem,
    EvidenceType,
    BusinessImpact,
)
from app.services.llm_service import AICaseBriefingService


def test_grounded_briefing_structure():
    """Verify deterministic AI briefing contains all 5 required structural sections."""
    service = AICaseBriefingService()

    merchant_profile = {
        "merchant_id": "M-ALPHA-01",
        "business_name": "Alpha Tech Deals",
        "category": "ELECTRONICS",
    }
    risk_summary = RiskScoreBreakdown(
        merchant_id="M-ALPHA-01",
        behavioral_risk=82.0,
        network_risk=95.0,
        overall_risk=88.5,
        risk_level=RiskLevel.CRITICAL,
        confidence=0.96,
        top_factors=[],
        recommended_action=ActionType.URGENT_SETTLEMENT_FREEZE,
        action_rationale="High probability of active mule or coordinated ring syndicate.",
        ring_id="RING-ALPHA-DEVICE-FARM",
        connected_high_risk_count=9,
        calculated_at=datetime.now(timezone.utc),
    )
    behavioral_evidence = [
        EvidenceItem(
            evidence_id="EVD-VEL-M-ALPHA-01",
            evidence_type=EvidenceType.TEMPORAL,
            title="48-Hour Velocity Surge",
            observed_value="6.4× volume multiplier",
            baseline_value="1.0× baseline",
            severity="CRITICAL",
            confidence=0.95,
            source="Velocity Engine",
            explanation="Processed 6.4x baseline volume in 48h.",
        )
    ]
    network_evidence = [
        EvidenceItem(
            evidence_id="EVD-DEV-M-ALPHA-01",
            evidence_type=EvidenceType.IDENTITY,
            title="Shared Device Fingerprint",
            observed_value="4 shared merchants on DEV-FARM-991",
            baseline_value="0 shared",
            severity="CRITICAL",
            confidence=0.98,
            source="Device Indexer",
            explanation="Hardware fingerprint DEV-FARM-991 is shared with 4 other accounts.",
        )
    ]

    briefing = service.generate_case_briefing(
        merchant_profile=merchant_profile,
        risk_summary=risk_summary,
        behavioral_evidence=behavioral_evidence,
        network_evidence=network_evidence,
    )

    assert briefing.summary is not None
    assert len(briefing.key_evidence) >= 2
    assert "RING-ALPHA-DEVICE-FARM" in briefing.network_context
    assert briefing.risk_interpretation is not None
    assert briefing.recommended_next_step is not None
    assert briefing.evidence_count == 2
    assert set(briefing.evidence_ids_used) == {"EVD-VEL-M-ALPHA-01", "EVD-DEV-M-ALPHA-01"}
    assert briefing.grounding_mode in ["DETERMINISTIC_FALLBACK", "LLM"]


def test_ai_cannot_invent_unsupplied_evidence():
    """Verify briefing only references supplied evidence IDs and is strictly constrained to structured inputs."""
    service = AICaseBriefingService()

    merchant_profile = {"merchant_id": "M-1001", "business_name": "Apex Fashion #1", "category": "ECOMMERCE_FASHION"}
    risk_summary = RiskScoreBreakdown(
        merchant_id="M-1001",
        behavioral_risk=12.0,
        network_risk=8.0,
        overall_risk=10.0,
        risk_level=RiskLevel.LOW,
        confidence=0.90,
        top_factors=[],
        recommended_action=ActionType.CONTINUE_MONITORING,
        action_rationale="Operations within standard baseline boundaries.",
        ring_id=None,
        connected_high_risk_count=0,
        calculated_at=datetime.now(timezone.utc),
    )

    # Supply empty evidence list
    briefing = service.generate_case_briefing(
        merchant_profile=merchant_profile,
        risk_summary=risk_summary,
        behavioral_evidence=[],
        network_evidence=[],
    )

    assert briefing.evidence_count == 0
    assert len(briefing.evidence_ids_used) == 0
    assert "LOW" in briefing.summary or "standard low-risk" in briefing.summary
