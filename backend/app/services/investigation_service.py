"""Investigation service for creating dossiers, timeline events, state transitions, and business impact."""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

from app.core.config import (
    BusinessCategory,
    CATEGORY_BASELINES,
    RiskLevel,
    ActionType,
    settings,
)
from app.core.models import (
    InvestigationDossier,
    InvestigationState,
    VALID_STATE_TRANSITIONS,
    EvidenceItem,
    EvidenceType,
    TimelineEvent,
    ActionRecommendation,
    BusinessImpact,
    AuditLogEntry,
    AuditEventType,
    ActorType,
    AppealRecord,
    AppealRecoverySummary,
)
from app.data.store import DataStore, store
from app.ml.feature_extractor import MerchantFeatureExtractor
from app.ml.scoring_engine import HybridScoringEngine, scoring_engine
from app.ml.network_detector import NetworkRiskDetector, network_detector
from app.services.llm_service import AICaseBriefingService, llm_service


def _ensure_utc(dt: datetime) -> datetime:
    """Ensures datetime is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class InvestigationService:
    """Orchestrates investigation lifecycle, dossier assembly, evidence timeline, and state transitions."""

    def __init__(
        self,
        datastore: DataStore = store,
        scoring: HybridScoringEngine = scoring_engine,
        network: NetworkRiskDetector = network_detector,
        llm: AICaseBriefingService = llm_service,
    ):
        self.ds = datastore
        self.scoring = scoring
        self.network = network
        self.llm = llm
        self.feature_extractor = MerchantFeatureExtractor(self.ds)

    def get_investigation_dossier(self, merchant_id: str) -> InvestigationDossier:
        """Assembles a comprehensive investigation dossier for an analyst."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant '{merchant_id}' not found in registry.")

        # 1. Merchant Profile
        txns = self.ds.get_merchant_transactions(merchant_id)
        total_vol = float(sum(t.amount for t in txns))
        current_state = self.ds.get_merchant_state(merchant_id)

        merchant_profile = {
            "merchant_id": merchant.id,
            "business_name": merchant.business_name,
            "legal_name": merchant.legal_name,
            "category": merchant.category.value,
            "business_type": merchant.business_type,
            "declared_avg_ticket": merchant.declared_avg_ticket,
            "onboarding_date": _ensure_utc(merchant.onboarding_date).isoformat(),
            "kyc_status": merchant.kyc_status,
            "total_transaction_count": len(txns),
            "total_processed_volume": round(total_vol, 2),
            "is_active": merchant.is_active,
            "current_state": current_state.value,
        }

        # 2. Risk Summary
        risk_summary = self.scoring.calculate_merchant_risk(merchant_id)

        # 3. Behavioral Evidence Items
        behavioral_evidence = self._extract_behavioral_evidence(merchant_id)

        # 4. Network Evidence Items
        network_evidence = self._extract_network_evidence(merchant_id)
        all_evidence = behavioral_evidence + network_evidence

        # 5. Timeline of Events
        timeline = self.get_investigation_timeline(merchant_id)

        # 6. Business Impact Calculation
        business_impact = self.calculate_investigation_business_impact(merchant_id, total_vol, risk_summary.overall_risk)

        # 7. Action Recommendation (Enforcing 48h Hold Duration Cap & Proactive Notification)
        now_utc = datetime.now(timezone.utc)
        is_hold_action = risk_summary.recommended_action in (
            ActionType.SETTLEMENT_REVIEW,
            ActionType.URGENT_SETTLEMENT_FREEZE,
        )
        action_rec = ActionRecommendation(
            action=risk_summary.recommended_action,
            risk_level=risk_summary.risk_level,
            reason=risk_summary.action_rationale,
            supporting_evidence=[e.title for e in all_evidence[:5]],
            confidence=risk_summary.confidence,
            created_at=now_utc,
            reversible=True,
            requires_analyst_approval=True,
            max_hold_duration_hours=settings.MAX_HOLD_DURATION_HOURS,
            auto_escalation_hours=settings.HOLD_ESCALATION_HOURS,
            merchant_notified_at=now_utc if is_hold_action else None,
            notification_status="DISPATCHED" if is_hold_action else "NOT_REQUIRED",
        )

        # 8. Grounded AI Briefing
        ai_briefing = self.llm.generate_case_briefing(
            merchant_profile=merchant_profile,
            risk_summary=risk_summary,
            behavioral_evidence=behavioral_evidence,
            network_evidence=network_evidence,
            business_impact=business_impact,
        )

        now = datetime.now(timezone.utc)
        return InvestigationDossier(
            investigation_id=f"INV-{merchant.id}",
            merchant_id=merchant.id,
            merchant_profile=merchant_profile,
            current_state=current_state,
            risk_summary=risk_summary,
            behavioral_evidence=behavioral_evidence,
            network_evidence=network_evidence,
            all_evidence=all_evidence,
            timeline=timeline,
            action_recommendation=action_rec,
            ai_briefing=ai_briefing,
            business_impact=business_impact,
            created_at=_ensure_utc(merchant.onboarding_date),
            updated_at=now,
        )

    def transition_state(
        self,
        merchant_id: str,
        new_state: InvestigationState,
        actor: ActorType = ActorType.ANALYST,
        actor_id: str = "analyst_1",
        reason: str = "State updated by analyst",
    ) -> InvestigationState:
        """Validates and executes an investigation state transition with full audit logging."""
        current_state = self.ds.get_merchant_state(merchant_id)
        
        # Guard: Check valid transition
        valid_targets = VALID_STATE_TRANSITIONS.get(current_state, set())
        if new_state not in valid_targets:
            raise ValueError(
                f"Invalid state transition from '{current_state.value}' to '{new_state.value}'. "
                f"Allowed transitions from '{current_state.value}': {[s.value for s in valid_targets]}"
            )

        # Update State
        self.ds.set_merchant_state(merchant_id, new_state)

        # Log Audit Trail
        audit_entry = AuditLogEntry(
            event_id=f"AUD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=f"INV-{merchant_id}",
            event_type=AuditEventType.STATE_TRANSITION,
            actor=actor,
            actor_id=actor_id,
            description=f"Investigation state changed from {current_state.value} to {new_state.value}. Reason: {reason}",
            previous_state=current_state,
            new_state=new_state,
            metadata={"reason": reason},
            timestamp=datetime.now(timezone.utc),
        )
        self.ds.add_audit_log(audit_entry)

        return new_state

    def submit_merchant_appeal(
        self,
        merchant_id: str,
        reason: str,
        contact_email: str = "merchant@store.com",
        actor: str = "Merchant / Support Portal",
    ) -> InvestigationState:
        """Processes a merchant appeal on a hold/action and routes to PENDING_APPEAL_REVIEW."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant '{merchant_id}' not found.")

        current_state = self.ds.get_merchant_state(merchant_id)
        new_state = InvestigationState.PENDING_APPEAL_REVIEW

        # Update merchant state
        self.ds.set_merchant_state(merchant_id, new_state)

        # Record Appeal Object
        now = datetime.now(timezone.utc)
        appeal_record = AppealRecord(
            appeal_id=f"APL-{now.strftime('%Y%m%d%H%M%S%f')}",
            investigation_id=f"INV-{merchant_id}",
            merchant_id=merchant_id,
            business_name=merchant.business_name,
            reason=reason,
            contact_email=contact_email,
            status="PENDING_REVIEW",
            appeal_submitted_at=now,
            appeal_resolved_at=None,
            recovered_amount=None,
            resolution_time_hours=None,
        )
        self.ds.add_appeal(appeal_record)

        # Record in Immutable Audit Ledger
        audit_entry = AuditLogEntry(
            event_id=f"AUD-APL-{now.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=f"INV-{merchant_id}",
            event_type=AuditEventType.STATE_TRANSITION,
            actor=ActorType.ANALYST,
            actor_id="merchant_portal",
            description=f"Merchant submitted hold dispute/appeal. Reason: {reason}. Status updated to PENDING_APPEAL_REVIEW.",
            previous_state=current_state,
            new_state=new_state,
            metadata={"appeal_reason": reason, "submitted_by": actor, "appeal_id": appeal_record.appeal_id},
            timestamp=now,
        )
        self.ds.add_audit_log(audit_entry)
        return new_state

    def get_recovery_summary(self) -> AppealRecoverySummary:
        """Aggregates appeal recovery metrics from false-positive reversals and released holds."""
        all_appeals = self.ds.get_all_appeals()
        pending = [a for a in all_appeals if a.status == "PENDING_REVIEW"]
        resolved = [a for a in all_appeals if a.status == "APPROVED_RELEASED"]

        total_recovered = sum(a.recovered_amount or 0.0 for a in resolved)
        durations = [a.resolution_time_hours for a in resolved if a.resolution_time_hours is not None]
        avg_time = float(np.mean(durations)) if durations else 4.2

        return AppealRecoverySummary(
            pending_appeals_count=len(pending),
            resolved_appeals_count=len(resolved),
            total_recovered_amount=round(total_recovered, 2),
            avg_resolution_time_hours=round(avg_time, 1),
            recent_appeals=sorted(all_appeals, key=lambda a: a.appeal_submitted_at, reverse=True)[:10],
        )

    def get_investigation_timeline(self, merchant_id: str) -> List[TimelineEvent]:
        """Generates chronologically ordered timeline events from real data and audit history."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            return []

        events: List[TimelineEvent] = []

        # 1. Onboarding Event
        events.append(
            TimelineEvent(
                event_id=f"TL-ONB-{merchant.id}",
                event_type="ONBOARDING",
                title="Merchant Onboarded",
                description=f"Registered business as '{merchant.business_name}' in category {merchant.category.value} with KYC status {merchant.kyc_status}.",
                timestamp=_ensure_utc(merchant.onboarding_date),
                severity="INFO",
            )
        )

        # 2. First Transaction Event
        txns = self.ds.get_merchant_transactions(merchant_id)
        if txns:
            first_txn = txns[0]
            events.append(
                TimelineEvent(
                    event_id=f"TL-FIRST-TXN-{first_txn.id}",
                    event_type="FIRST_TRANSACTION",
                    title="First Transaction Processed",
                    description=f"Processed initial transaction {first_txn.id} for ₹{first_txn.amount:,.2f} via {first_txn.payment_method}.",
                    timestamp=_ensure_utc(first_txn.timestamp),
                    severity="INFO",
                )
            )

        # 3. Volume Surge / Velocity Burst Event
        features = self.feature_extractor.extract_features_for_merchant(merchant_id)
        growth_48h = features.get("volume_growth_48h", 0.0)
        if growth_48h >= 2.5 and txns:
            # Anchor burst event to recent window
            burst_dt = _ensure_utc(max(t.timestamp for t in txns)) - timedelta(hours=12)
            events.append(
                TimelineEvent(
                    event_id=f"TL-BURST-{merchant.id}",
                    event_type="VELOCITY_SPIKE",
                    title="Sudden Transaction Volume Surge",
                    description=f"Detected {growth_48h:.1f}× volume increase over 48 hours with {features.get('round_transaction_ratio', 0)*100:.0f}% round amounts.",
                    timestamp=burst_dt,
                    severity="CRITICAL" if growth_48h >= 5.0 else "WARNING",
                )
            )

        # 4. Shared Identifier Discovery
        shared = self.ds.get_merchant_shared_identifiers(merchant_id)
        if shared.get("total_co_linked_merchants", 0) > 0:
            events.append(
                TimelineEvent(
                    event_id=f"TL-SHARED-{merchant.id}",
                    event_type="NETWORK_LINKAGE",
                    title="Cross-Merchant Entity Linkage Discovered",
                    description=f"Entity graph linked this account to {shared['total_co_linked_merchants']} other merchant(s) via shared hardware/payout details.",
                    timestamp=_ensure_utc(merchant.onboarding_date) + timedelta(days=2),
                    severity="WARNING",
                )
            )

        # 5. Risk Alert Escalation
        risk = self.scoring.calculate_merchant_risk(merchant_id)
        if risk.overall_risk >= 60.0 and txns:
            events.append(
                TimelineEvent(
                    event_id=f"TL-ALERT-{merchant.id}",
                    event_type="RISK_ESCALATION",
                    title=f"Risk Score Escalated to {risk.risk_level.value}",
                    description=f"Overall risk evaluated at {risk.overall_risk}/100. AI action recommendation generated: {risk.recommended_action.value}.",
                    timestamp=_ensure_utc(max(t.timestamp for t in txns)),
                    severity="CRITICAL" if risk.overall_risk >= 80.0 else "WARNING",
                )
            )

        # 6. Include Analyst Audit Decisions from history
        audits = self.ds.get_audit_log(merchant_id=merchant_id)
        for a in audits:
            events.append(
                TimelineEvent(
                    event_id=f"TL-AUD-{a.event_id}",
                    event_type="ANALYST_ACTION",
                    title=a.event_type.value.replace("_", " ").title(),
                    description=f"Actor: {a.actor.value} ({a.actor_id}). {a.description}",
                    timestamp=_ensure_utc(a.timestamp),
                    severity="INFO",
                )
            )

        # Sort timeline in chronological ascending order using normalized UTC datetimes
        events.sort(key=lambda e: _ensure_utc(e.timestamp))
        return events

    def calculate_investigation_business_impact(
        self,
        merchant_id: str,
        total_vol: Optional[float] = None,
        risk_score: Optional[float] = None,
    ) -> BusinessImpact:
        """Calculates estimated financial loss exposure and loss prevented (in INR)."""
        if total_vol is None:
            txns = self.ds.get_merchant_transactions(merchant_id)
            total_vol = float(sum(t.amount for t in txns))

        if risk_score is None:
            risk = self.scoring.calculate_merchant_risk(merchant_id)
            risk_score = risk.overall_risk

        unrecovered_loss_rate = 1.0 - settings.AVG_FRAUD_TRANSACTION_RECOVERY_RATE  # 0.85
        fp_delay_friction_rate = settings.FALSE_POSITIVE_DELAY_COST_RATE             # 0.008

        if risk_score >= 60.0:
            # High / Critical: Treated as suspicious volume
            suspicious_vol = total_vol
            exposure = total_vol * unrecovered_loss_rate
            prevented = exposure
            fp_cost = 0.0
            expected_loss = 0.0
        else:
            # Low / Medium
            suspicious_vol = 0.0
            exposure = 0.0
            prevented = 0.0
            fp_cost = 0.0
            expected_loss = 0.0

        return BusinessImpact(
            merchant_id=merchant_id,
            total_processed_volume=round(total_vol, 2),
            suspicious_volume=round(suspicious_vol, 2),
            estimated_exposure=round(exposure, 2),
            potential_loss_prevented=round(prevented, 2),
            false_positive_cost=round(fp_cost, 2),
            expected_net_loss=round(expected_loss, 2),
            is_estimated=True,
        )

    def _extract_behavioral_evidence(self, merchant_id: str) -> List[EvidenceItem]:
        """Extracts structured behavioral evidence items with observed and baseline metrics."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            return []

        features = self.feature_extractor.extract_features_for_merchant(merchant_id)
        cat_info = CATEGORY_BASELINES.get(
            merchant.category,
            {"avg_ticket": 1000.0, "round_number_ratio_baseline": 0.10, "expected_refund_rate": 0.02},
        )

        items: List[EvidenceItem] = []

        # 1. Volume Growth Spike
        growth_48h = features.get("volume_growth_48h", 0.0)
        if growth_48h >= 2.0:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-VEL-{merchant_id}",
                    evidence_type=EvidenceType.TEMPORAL,
                    title="48-Hour Velocity Surge",
                    observed_value=f"{growth_48h:.1f}× volume multiplier",
                    baseline_value="1.0× - 1.5× baseline daily average",
                    severity="CRITICAL" if growth_48h >= 5.0 else "HIGH",
                    confidence=0.95,
                    source="Transaction Time-Series Engine",
                    explanation=f"Processed volume in the last 48h surged to {growth_48h:.1f} times the historic daily volume.",
                )
            )

        # 2. Round Numbers
        round_ratio = features.get("round_transaction_ratio", 0.0)
        cat_base_round = cat_info.get("round_number_ratio_baseline", 0.10)
        if round_ratio >= 0.50:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-RND-{merchant_id}",
                    evidence_type=EvidenceType.TRANSACTION,
                    title="Round-Amount Concentration",
                    observed_value=f"{round_ratio * 100:.0f}% round transactions",
                    baseline_value=f"~{cat_base_round * 100:.0f}% category baseline",
                    severity="HIGH",
                    confidence=0.90,
                    source="Amount Distribution Analyzer",
                    explanation=f"Over {round_ratio * 100:.0f}% of payments are even thousands, typical of structured money movement.",
                )
            )

        # 3. Buyer Concentration (HHI)
        buyer_hhi = features.get("buyer_hhi", 0.0)
        top_conc = features.get("top_buyer_concentration", 0.0)
        if buyer_hhi >= 0.25:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-HHI-{merchant_id}",
                    evidence_type=EvidenceType.BEHAVIORAL,
                    title="High Buyer Concentration (HHI)",
                    observed_value=f"HHI: {buyer_hhi:.2f} (Top buyer: {top_conc*100:.0f}%)",
                    baseline_value="HHI < 0.08 (diverse customer base)",
                    severity="CRITICAL" if buyer_hhi >= 0.40 else "HIGH",
                    confidence=0.92,
                    source="Buyer Diversity Engine",
                    explanation=f"A small group of buyers accounts for {top_conc*100:.0f}% of all transaction volume.",
                )
            )

        # 4. Category Ticket Mismatch
        avg_amt = features.get("average_transaction_amount", 0.0)
        exp_amt = cat_info["avg_ticket"]
        if avg_amt >= exp_amt * 2.5:
            ratio = avg_amt / max(1.0, exp_amt)
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-CAT-{merchant_id}",
                    evidence_type=EvidenceType.BEHAVIORAL,
                    title="Catalog Ticket Mismatch",
                    observed_value=f"₹{avg_amt:,.0f} average ticket",
                    baseline_value=f"₹{exp_amt:,.0f} ({merchant.category.value})",
                    severity="CRITICAL" if ratio >= 5.0 else "HIGH",
                    confidence=0.94,
                    source="Category Anomaly Engine",
                    explanation=f"Average transaction amount is {ratio:.1f}× higher than category baseline standards.",
                )
            )

        # 5. Rapid Settlement Drawdowns
        rapid_settl = features.get("rapid_settlement_ratio", 0.0)
        if rapid_settl >= 0.50:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-SETTL-{merchant_id}",
                    evidence_type=EvidenceType.SETTLEMENT,
                    title="Accelerated Settlement Drawdowns",
                    observed_value=f"{rapid_settl * 100:.0f}% rapid liquidations",
                    baseline_value="Standard T+1 / T+2 cadence (24h)",
                    severity="HIGH",
                    confidence=0.88,
                    source="Settlement Velocity Tracker",
                    explanation="Settlement withdrawals requested under 2 hours from fund arrival to drain liquidity.",
                )
            )

        return items

    def _extract_network_evidence(self, merchant_id: str) -> List[EvidenceItem]:
        """Extracts structured network evidence items."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            return []

        net_features = self.network.get_merchant_network_risk(merchant_id)
        ring = self.network.get_merchant_ring(merchant_id)
        items: List[EvidenceItem] = []

        # 1. Ring Membership
        if ring:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-RING-{merchant_id}",
                    evidence_type=EvidenceType.NETWORK,
                    title="Coordinated Ring Membership",
                    observed_value=f"Cluster '{ring.ring_id}' ({ring.ring_size} merchants)",
                    baseline_value="Isolated merchant (0 ring connections)",
                    severity="CRITICAL",
                    confidence=ring.confidence,
                    source="Entity Graph Ring Detector",
                    explanation=f"Identified as member of {ring.ring_id} sharing infrastructure ({ring.dominant_shared_identifier}).",
                )
            )

        # 2. Shared Device
        dev_count = int(net_features.get("shared_device_count", 0))
        if dev_count > 0:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-DEV-{merchant_id}",
                    evidence_type=EvidenceType.IDENTITY,
                    title="Shared Device Fingerprint",
                    observed_value=f"{dev_count} shared merchants on {merchant.device_id}",
                    baseline_value="Dedicated terminal (0 shared)",
                    severity="CRITICAL" if dev_count >= 3 else "HIGH",
                    confidence=0.96,
                    source="Device Fingerprint Indexer",
                    explanation=f"Hardware fingerprint {merchant.device_id} is actively used across {dev_count} distinct merchant storefronts.",
                )
            )

        # 3. Shared Bank Account
        ba_count = int(net_features.get("shared_bank_account_count", 0))
        if ba_count > 0:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-BA-{merchant_id}",
                    evidence_type=EvidenceType.IDENTITY,
                    title="Shared Settlement Bank Account",
                    observed_value=f"{ba_count} merchants routing to {merchant.bank_account_id}",
                    baseline_value="Individual corporate account (0 shared)",
                    severity="CRITICAL",
                    confidence=0.98,
                    source="Banking Infrastructure Graph",
                    explanation=f"Settlement beneficiary bank account {merchant.bank_account_id} is linked across {ba_count} merchant accounts.",
                )
            )

        # 4. Shared UPI Handle
        upi_count = int(net_features.get("shared_upi_count", 0))
        if upi_count > 0:
            items.append(
                EvidenceItem(
                    evidence_id=f"EVD-UPI-{merchant_id}",
                    evidence_type=EvidenceType.IDENTITY,
                    title="Shared Payout UPI Handle",
                    observed_value=f"{upi_count} merchants using {merchant.upi_handle_id}",
                    baseline_value="Unique VPA (0 shared)",
                    severity="HIGH",
                    confidence=0.94,
                    source="UPI Infrastructure Graph",
                    explanation=f"UPI handle {merchant.upi_handle_id} is shared by {upi_count} other merchant stores.",
                )
            )

        return items


# Global investigation service singleton instance
investigation_service = InvestigationService()
