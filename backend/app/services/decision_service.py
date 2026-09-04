"""Bounded Decision Engine, Analyst Action Recording, Rollback, and Audit Trail Management."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from app.core.config import RiskLevel, ActionType, DecisionFeedback, settings
from app.core.models import (
    ActionRecommendation,
    AnalystDecision,
    AnalystFeedback,
    AuditLogEntry,
    AuditEventType,
    ActorType,
    InvestigationState,
)
from app.data.store import DataStore, store
from app.ml.scoring_engine import HybridScoringEngine, scoring_engine
from app.services.investigation_service import InvestigationService, investigation_service


class DecisionService:
    """Manages tiered bounded actions, analyst decision workflows, reversible rollbacks, and audit logging."""

    def __init__(
        self,
        datastore: DataStore = store,
        scoring: Optional[HybridScoringEngine] = None,
        investigation: Optional[InvestigationService] = None,
    ):
        self.ds = datastore
        self.scoring = scoring or (scoring_engine if datastore is store else HybridScoringEngine(datastore=self.ds))
        self.investigation = investigation or (
            investigation_service if datastore is store else InvestigationService(datastore=self.ds, scoring=self.scoring)
        )

    def recommend_action(self, merchant_id: str) -> ActionRecommendation:
        """Generates bounded action recommendation requiring analyst approval."""
        risk = self.scoring.calculate_merchant_risk(merchant_id)
        now_utc = datetime.now(timezone.utc)
        is_hold = risk.recommended_action in (
            ActionType.SETTLEMENT_REVIEW,
            ActionType.URGENT_SETTLEMENT_FREEZE,
        )
        
        supporting = [f.title for f in risk.top_factors[:4]]
        rec = ActionRecommendation(
            action=risk.recommended_action,
            risk_level=risk.risk_level,
            reason=risk.action_rationale,
            supporting_evidence=supporting,
            confidence=risk.confidence,
            created_at=now_utc,
            reversible=True,
            requires_analyst_approval=True,
            max_hold_duration_hours=settings.MAX_HOLD_DURATION_HOURS,
            auto_escalation_hours=settings.HOLD_ESCALATION_HOURS,
            merchant_notified_at=now_utc if is_hold else None,
            notification_status="DISPATCHED" if is_hold else "NOT_REQUIRED",
        )

        # Record recommendation audit event
        audit = AuditLogEntry(
            event_id=f"AUD-REC-{now_utc.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=f"INV-{merchant_id}",
            event_type=AuditEventType.ACTION_RECOMMENDED,
            actor=ActorType.SYSTEM,
            actor_id="risk_scoring_engine",
            description=f"Recommended action '{rec.action.value}' for risk level '{rec.risk_level.value}'. Reason: {rec.reason}",
            previous_state=self.ds.get_merchant_state(merchant_id),
            new_state=self.ds.get_merchant_state(merchant_id),
            metadata={"recommended_action": rec.action.value, "confidence": rec.confidence, "max_hold_hours": rec.max_hold_duration_hours},
            timestamp=now_utc,
        )
        self.ds.add_audit_log(audit)

        # If hold recommended, log proactive notification dispatch
        if is_hold:
            notif_audit = AuditLogEntry(
                event_id=f"AUD-NOTIF-{now_utc.strftime('%Y%m%d%H%M%S%f')}",
                merchant_id=merchant_id,
                investigation_id=f"INV-{merchant_id}",
                event_type=AuditEventType.MERCHANT_NOTIFICATION_DISPATCHED,
                actor=ActorType.SYSTEM,
                actor_id="proactive_notification_service",
                description=f"Proactive hold notification dispatched to merchant {merchant_id}. Notice includes hold duration cap ({settings.MAX_HOLD_DURATION_HOURS}h), reason, and dispute appeal portal link.",
                previous_state=self.ds.get_merchant_state(merchant_id),
                new_state=self.ds.get_merchant_state(merchant_id),
                metadata={
                    "channel": "WEBHOOK_AND_DASHBOARD",
                    "max_hold_hours": settings.MAX_HOLD_DURATION_HOURS,
                    "escalation_hours": settings.HOLD_ESCALATION_HOURS,
                    "appeal_route": f"/api/merchants/{merchant_id}/appeal",
                },
                timestamp=now_utc,
            )
            self.ds.add_audit_log(notif_audit)

        return rec

    def record_decision(
        self,
        investigation_id: str,
        decision: DecisionFeedback,
        analyst_reason: str,
        analyst_id: str = "analyst_1",
        analyst_name: str = "Risk Lead",
    ) -> AnalystDecision:
        """Records an analyst decision, executes bounded state transition, and writes to audit trail."""
        if not analyst_reason or len(analyst_reason.strip()) == 0:
            raise ValueError("Analyst decision requires a valid non-empty reason/justification.")

        merchant_id = investigation_id.replace("INV-", "") if investigation_id.startswith("INV-") else investigation_id
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant '{merchant_id}' not found.")

        current_state = self.ds.get_merchant_state(merchant_id)
        risk = self.scoring.calculate_merchant_risk(merchant_id)

        # Map decision to new state and bounded action
        if decision == DecisionFeedback.CONFIRMED_FRAUD:
            target_state = InvestigationState.ACTIONED
            action_taken = risk.recommended_action
        elif decision == DecisionFeedback.FALSE_POSITIVE:
            target_state = InvestigationState.CLEARED
            action_taken = ActionType.CONTINUE_MONITORING
        elif decision == DecisionFeedback.CLEARED:
            target_state = InvestigationState.CLEARED
            action_taken = ActionType.CONTINUE_MONITORING
        elif decision == DecisionFeedback.NEEDS_INVESTIGATION:
            target_state = InvestigationState.UNDER_REVIEW
            action_taken = ActionType.ENHANCED_MONITORING
        else:
            target_state = InvestigationState.UNDER_REVIEW
            action_taken = ActionType.CONTINUE_MONITORING

        # Auto-promote from NEW to UNDER_REVIEW if taking direct action
        if current_state == InvestigationState.NEW and target_state == InvestigationState.ACTIONED:
            self.investigation.transition_state(
                merchant_id=merchant_id,
                new_state=InvestigationState.UNDER_REVIEW,
                actor=ActorType.ANALYST,
                actor_id=analyst_id,
                reason="Auto-opened review for action application",
            )
            current_state = InvestigationState.UNDER_REVIEW

        # Execute valid state transition
        new_state = self.investigation.transition_state(
            merchant_id=merchant_id,
            new_state=target_state,
            actor=ActorType.ANALYST,
            actor_id=analyst_id,
            reason=analyst_reason,
        )

        # Record Decision Object
        now = datetime.now(timezone.utc)
        decision_obj = AnalystDecision(
            decision_id=f"DEC-{now.strftime('%Y%m%d%H%M%S%f')}",
            investigation_id=investigation_id,
            merchant_id=merchant_id,
            analyst_id=analyst_id,
            analyst_name=analyst_name,
            decision=decision,
            action_taken=action_taken,
            analyst_reason=analyst_reason,
            timestamp=now,
            previous_state=current_state,
            new_state=new_state,
            reversible=True,
        )
        self.ds.record_decision(decision_obj)

        # If cleared/false positive, resolve any pending appeal and calculate recovered capital
        if target_state == InvestigationState.CLEARED:
            for appeal in self.ds.get_merchant_appeals(merchant_id):
                if appeal.status == "PENDING_REVIEW":
                    appeal.status = "APPROVED_RELEASED"
                    appeal.appeal_resolved_at = now
                    delta_hours = (now - appeal.appeal_submitted_at).total_seconds() / 3600.0
                    appeal.resolution_time_hours = max(0.5, round(delta_hours, 1))
                    settlements = self.ds.get_merchant_settlements(merchant_id)
                    held_vol = sum(s.amount for s in settlements if s.status in ("HELD", "PENDING"))
                    if held_vol <= 0:
                        txns = self.ds.get_merchant_transactions(merchant_id)
                        held_vol = sum(t.amount for t in txns[-10:]) if txns else 750000.0
                    appeal.recovered_amount = round(held_vol, 2)

        # Add Analyst Decision Audit Event
        audit = AuditLogEntry(
            event_id=f"AUD-DEC-{now.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=investigation_id,
            event_type=AuditEventType.ANALYST_DECISION,
            actor=ActorType.ANALYST,
            actor_id=analyst_id,
            description=f"Analyst {analyst_name} ({analyst_id}) recorded decision '{decision.value}'. Action: '{action_taken.value}'. Rationale: {analyst_reason}",
            previous_state=current_state,
            new_state=new_state,
            metadata={
                "decision": decision.value,
                "action_taken": action_taken.value,
                "reason": analyst_reason,
            },
            timestamp=now,
        )
        self.ds.add_audit_log(audit)

        # If hold action taken, log proactive notification event
        if action_taken in (ActionType.SETTLEMENT_REVIEW, ActionType.URGENT_SETTLEMENT_FREEZE):
            notif_audit = AuditLogEntry(
                event_id=f"AUD-NOTIF-{now.strftime('%Y%m%d%H%M%S%f')}",
                merchant_id=merchant_id,
                investigation_id=investigation_id,
                event_type=AuditEventType.MERCHANT_NOTIFICATION_DISPATCHED,
                actor=ActorType.SYSTEM,
                actor_id="proactive_notification_service",
                description=f"Proactive hold notification dispatched to merchant {merchant_id}. Notice includes hold duration cap ({settings.MAX_HOLD_DURATION_HOURS}h), reason, and dispute appeal portal link.",
                previous_state=current_state,
                new_state=new_state,
                metadata={
                    "channel": "WEBHOOK_AND_DASHBOARD",
                    "max_hold_hours": settings.MAX_HOLD_DURATION_HOURS,
                    "escalation_hours": settings.HOLD_ESCALATION_HOURS,
                    "appeal_route": f"/api/merchants/{merchant_id}/appeal",
                },
                timestamp=now,
            )
            self.ds.add_audit_log(notif_audit)

        return decision_obj

    def rollback_action(
        self,
        investigation_id: str,
        rollback_reason: str,
        analyst_id: str = "analyst_1",
        analyst_name: str = "Risk Lead",
    ) -> AuditLogEntry:
        """Rolls back an existing action to CLEARED state, preserving all audit history."""
        if not rollback_reason or len(rollback_reason.strip()) == 0:
            raise ValueError("Action rollback requires an explicit justification.")

        merchant_id = investigation_id.replace("INV-", "") if investigation_id.startswith("INV-") else investigation_id
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            raise ValueError(f"Merchant '{merchant_id}' not found.")

        current_state = self.ds.get_merchant_state(merchant_id)

        # Transition to CLEARED
        new_state = self.investigation.transition_state(
            merchant_id=merchant_id,
            new_state=InvestigationState.CLEARED,
            actor=ActorType.ANALYST,
            actor_id=analyst_id,
            reason=f"Action Rolled Back: {rollback_reason}",
        )

        now = datetime.now(timezone.utc)

        # Resolve any pending appeals for this merchant
        for appeal in self.ds.get_merchant_appeals(merchant_id):
            if appeal.status == "PENDING_REVIEW":
                appeal.status = "APPROVED_RELEASED"
                appeal.appeal_resolved_at = now
                delta_hours = (now - appeal.appeal_submitted_at).total_seconds() / 3600.0
                appeal.resolution_time_hours = max(0.5, round(delta_hours, 1))
                settlements = self.ds.get_merchant_settlements(merchant_id)
                held_vol = sum(s.amount for s in settlements if s.status in ("HELD", "PENDING"))
                if held_vol <= 0:
                    txns = self.ds.get_merchant_transactions(merchant_id)
                    held_vol = sum(t.amount for t in txns[-10:]) if txns else 750000.0
                appeal.recovered_amount = round(held_vol, 2)

        audit_entry = AuditLogEntry(
            event_id=f"AUD-RB-{now.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=investigation_id,
            event_type=AuditEventType.ACTION_ROLLED_BACK,
            actor=ActorType.ANALYST,
            actor_id=analyst_id,
            description=f"Analyst {analyst_name} ({analyst_id}) rolled back previous action from '{current_state.value}' to '{new_state.value}'. Justification: {rollback_reason}",
            previous_state=current_state,
            new_state=new_state,
            metadata={"rollback_reason": rollback_reason},
            timestamp=now,
        )
        self.ds.add_audit_log(audit_entry)

        return audit_entry

    def submit_feedback(
        self,
        investigation_id: str,
        feedback_type: DecisionFeedback,
        notes: str,
        analyst_id: str = "analyst_1",
    ) -> AnalystFeedback:
        """Stores analyst feedback for future model retraining datasets."""
        merchant_id = investigation_id.replace("INV-", "") if investigation_id.startswith("INV-") else investigation_id
        now = datetime.now(timezone.utc)

        feedback = AnalystFeedback(
            feedback_id=f"FB-{now.strftime('%Y%m%d%H%M%S%f')}",
            investigation_id=investigation_id,
            merchant_id=merchant_id,
            analyst_id=analyst_id,
            feedback_type=feedback_type,
            notes=notes,
            created_at=now,
        )
        self.ds.add_feedback(feedback)

        # Log Feedback in Audit Trail
        audit = AuditLogEntry(
            event_id=f"AUD-FB-{now.strftime('%Y%m%d%H%M%S%f')}",
            merchant_id=merchant_id,
            investigation_id=investigation_id,
            event_type=AuditEventType.FEEDBACK_RECORDED,
            actor=ActorType.ANALYST,
            actor_id=analyst_id,
            description=f"Analyst recorded feedback '{feedback_type.value}' for model retraining queue. Notes: {notes}",
            previous_state=self.ds.get_merchant_state(merchant_id),
            new_state=self.ds.get_merchant_state(merchant_id),
            metadata={"feedback_type": feedback_type.value, "notes": notes},
            timestamp=now,
        )
        self.ds.add_audit_log(audit)

        return feedback

    def get_audit_log(
        self,
        investigation_id: Optional[str] = None,
        merchant_id: Optional[str] = None,
    ) -> List[AuditLogEntry]:
        """Retrieves persistent chronological audit trail."""
        return self.ds.get_audit_log(merchant_id=merchant_id, investigation_id=investigation_id)

    def get_all_feedback(self) -> List[AnalystFeedback]:
        """Retrieves all stored feedback records."""
        return self.ds.get_all_feedback()


# Global decision service singleton instance
decision_service = DecisionService()
