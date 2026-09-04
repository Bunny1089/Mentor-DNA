"""Grounded AI Case Briefing service synthesizing structured risk evidence."""

import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from app.core.models import (
    AICaseBriefing,
    EvidenceItem,
    RiskScoreBreakdown,
    BusinessImpact,
)


class AICaseBriefingService:
    """Synthesizes structured risk evidence into concise, factual analyst briefings."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def generate_case_briefing(
        self,
        merchant_profile: Dict[str, Any],
        risk_summary: RiskScoreBreakdown,
        behavioral_evidence: List[EvidenceItem],
        network_evidence: List[EvidenceItem],
        business_impact: Optional[BusinessImpact] = None,
    ) -> AICaseBriefing:
        """Generates grounded synthesis constrained to structured evidence inputs."""
        all_evidence = behavioral_evidence + network_evidence
        evidence_ids_used = [e.evidence_id for e in all_evidence]

        # Use deterministic template fallback
        return self._generate_deterministic_briefing(
            merchant_profile=merchant_profile,
            risk_summary=risk_summary,
            behavioral_evidence=behavioral_evidence,
            network_evidence=network_evidence,
            business_impact=business_impact,
            evidence_ids=evidence_ids_used,
        )

    def _generate_deterministic_briefing(
        self,
        merchant_profile: Dict[str, Any],
        risk_summary: RiskScoreBreakdown,
        behavioral_evidence: List[EvidenceItem],
        network_evidence: List[EvidenceItem],
        business_impact: Optional[BusinessImpact],
        evidence_ids: List[str],
    ) -> AICaseBriefing:
        """Deterministic, grounded briefing generated from structured evidence."""
        all_evidence = behavioral_evidence + network_evidence
        m_id = merchant_profile.get("merchant_id", "UNKNOWN")
        biz_name = merchant_profile.get("business_name", "Merchant")
        category = merchant_profile.get("category", "General")
        risk_level = risk_summary.risk_level.value
        score = risk_summary.overall_risk
        beh_score = risk_summary.behavioral_risk
        net_score = risk_summary.network_risk

        # 1. Summary
        if risk_summary.overall_risk >= 80.0:
            summary = (
                f"Merchant {m_id} ({biz_name}, {category}) has been escalated to {risk_level} risk "
                f"with an overall risk score of {score}/100 (Behavioral: {beh_score}, Network: {net_score}). "
                f"The merchant exhibits high-velocity burst anomalies synchronized with multi-entity cross-merchant linkage."
            )
        elif risk_summary.overall_risk >= 60.0:
            summary = (
                f"Merchant {m_id} ({biz_name}, {category}) is flagged as {risk_level} risk "
                f"(Overall Score: {score}/100). Elevated behavioral deviations and shared infrastructure "
                f"require manual operational review."
            )
        elif risk_summary.overall_risk >= 30.0:
            summary = (
                f"Merchant {m_id} ({biz_name}) displays moderate risk indicators (Overall Score: {score}/100). "
                f"Behavioral telemetry suggests emerging deviation from standard {category} baselines."
            )
        else:
            summary = (
                f"Merchant {m_id} ({biz_name}) is currently operating within standard low-risk parameters "
                f"(Overall Score: {score}/100) with healthy buyer entropy and isolated infrastructure."
            )

        # 2. Key Evidence Highlights
        key_evidence = []
        for e in behavioral_evidence[:4]:
            key_evidence.append(f"{e.title}: {e.observed_value} (vs. benchmark {e.baseline_value})")

        for e in network_evidence[:3]:
            key_evidence.append(f"{e.title}: {e.observed_value} ({e.explanation})")

        if not key_evidence:
            key_evidence.append("No critical anomaly thresholds exceeded.")

        # 3. Network Context
        if risk_summary.ring_id:
            network_context = (
                f"Identified as an active node within collusive ring '{risk_summary.ring_id}'. "
                f"Connected to {risk_summary.connected_high_risk_count} co-linked merchant account(s) via shared hardware/payout infrastructure."
            )
        elif risk_summary.connected_high_risk_count > 0:
            network_context = (
                f"Shared entity graph connects this merchant to {risk_summary.connected_high_risk_count} other registered merchant(s). "
                f"Network score is {net_score}/100."
            )
        else:
            network_context = "No suspicious entity sharing or multi-merchant cluster links detected (isolated infrastructure)."

        # 4. Risk Interpretation
        if risk_summary.overall_risk >= 80.0:
            risk_interpretation = (
                "The co-occurrence of high transaction velocity and infrastructure sharing strongly suggests coordinated mule or shell account syndicate operations. "
                "Immediate intervention is warranted to mitigate chargeback and payout default exposure."
            )
        elif risk_summary.overall_risk >= 60.0:
            risk_interpretation = (
                "The behavioral volume surge combined with shared identifier telemetry deviates significantly from organic retail patterns. "
                "Settlement review is recommended prior to fund disbursement."
            )
        else:
            risk_interpretation = "Risk indicators remain within acceptable tolerance thresholds. Standard monitoring is sufficient."

        # 5. Recommended Next Step
        if risk_summary.overall_risk >= 80.0:
            exposure_text = f" (Potential exposure: ₹{business_impact.estimated_exposure:,.2f})" if business_impact else ""
            recommended_next_step = (
                f"Initiate temporary settlement hold (Action: {risk_summary.recommended_action.value}){exposure_text}. "
                "Request business proof of inventory, terminal ownership validation, and customer fulfillment logs."
            )
        elif risk_summary.overall_risk >= 60.0:
            recommended_next_step = (
                f"Apply 24h settlement review hold (Action: {risk_summary.recommended_action.value}). "
                "Verify beneficiary bank account documentation and validate high-ticket transactions."
            )
        elif risk_summary.overall_risk >= 30.0:
            recommended_next_step = (
                f"Enable enhanced monitoring (Action: {risk_summary.recommended_action.value}) with dynamic daily payout ceilings."
            )
        else:
            recommended_next_step = "Maintain continuous automated background surveillance. No manual analyst intervention needed."

        return AICaseBriefing(
            summary=summary,
            key_evidence=key_evidence,
            network_context=network_context,
            risk_interpretation=risk_interpretation,
            recommended_next_step=recommended_next_step,
            evidence_count=len(all_evidence),
            evidence_ids_used=evidence_ids,
            generated_at=datetime.now(timezone.utc),
            grounding_mode="DETERMINISTIC_FALLBACK",
        )


# Global AI briefing service instance
llm_service = AICaseBriefingService()
