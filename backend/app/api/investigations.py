"""Investigation Dossier, Decisions, Actions, Briefings, and Audit API endpoints."""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field, field_validator

from app.core.config import DecisionFeedback, ActionType
from app.core.models import (
    InvestigationDossier,
    InvestigationState,
    AICaseBriefing,
    ActionRecommendation,
    AnalystDecision,
    AuditLogEntry,
    AnalystFeedback,
    ActorType,
    AppealRecord,
    AppealRecoverySummary,
)
from app.data.store import store
from app.services.investigation_service import investigation_service
from app.services.decision_service import decision_service

router = APIRouter(prefix="/api/investigations", tags=["Investigations"])


def _extract_merchant_id(investigation_id: str) -> str:
    return investigation_id.replace("INV-", "") if investigation_id.startswith("INV-") else investigation_id


# ==========================================
# Request / Response Schemas
# ==========================================

class DecisionRequest(BaseModel):
    decision: DecisionFeedback
    justification: str = Field(..., min_length=3, description="Mandatory analyst justification")
    analyst_id: str = "analyst_1"
    analyst_name: str = "Risk Lead"

    @field_validator("justification")
    @classmethod
    def validate_justification_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Justification cannot be empty or blank.")
        return v.strip()


class RejectActionRequest(BaseModel):
    justification: str = Field(..., min_length=3, description="Mandatory analyst justification for rejecting recommendation")
    analyst_id: str = "analyst_1"
    analyst_name: str = "Risk Lead"

    @field_validator("justification")
    @classmethod
    def validate_justification_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Justification cannot be empty or blank.")
        return v.strip()


class RollbackActionRequest(BaseModel):
    rollback_reason: str = Field(..., min_length=3, description="Mandatory justification for action rollback")
    analyst_id: str = "analyst_1"
    analyst_name: str = "Risk Lead"

    @field_validator("rollback_reason")
    @classmethod
    def validate_rollback_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Rollback reason cannot be empty or blank.")
        return v.strip()


class FeedbackSubmissionRequest(BaseModel):
    feedback_type: DecisionFeedback
    notes: str = Field(..., min_length=3, description="Analyst feedback notes for model retraining")
    analyst_id: str = "analyst_1"

    @field_validator("notes")
    @classmethod
    def validate_notes_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Feedback notes cannot be empty or blank.")
        return v.strip()



# ==========================================
# Endpoints
# ==========================================

@router.post("/{merchant_id}", response_model=InvestigationDossier)
def open_investigation(merchant_id: str) -> InvestigationDossier:
    """Opens/creates an active investigation case for a merchant."""
    clean_m_id = _extract_merchant_id(merchant_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "MERCHANT_NOT_FOUND", "message": f"Merchant '{clean_m_id}' not found."},
        )

    current_state = store.get_merchant_state(clean_m_id)
    if current_state == InvestigationState.NEW:
        investigation_service.transition_state(
            merchant_id=clean_m_id,
            new_state=InvestigationState.UNDER_REVIEW,
            actor=ActorType.ANALYST,
            actor_id="analyst_1",
            reason="Investigation case opened by analyst.",
        )

    dossier = investigation_service.get_investigation_dossier(clean_m_id)
    return dossier


@router.get("/{investigation_id}", response_model=InvestigationDossier)
def get_investigation(investigation_id: str) -> InvestigationDossier:
    """Returns the complete investigation dossier for an investigation ID or merchant ID."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    dossier = investigation_service.get_investigation_dossier(clean_m_id)
    return dossier


@router.post("/{investigation_id}/briefing", response_model=AICaseBriefing)
def generate_ai_briefing(investigation_id: str) -> AICaseBriefing:
    """Generates a strictly grounded AI case briefing from structured evidence."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    dossier = investigation_service.get_investigation_dossier(clean_m_id)
    if not dossier.ai_briefing:
        briefing = investigation_service.llm.generate_case_briefing(
            merchant_profile=dossier.merchant_profile,
            risk_summary=dossier.risk_summary,
            behavioral_evidence=dossier.behavioral_evidence,
            network_evidence=dossier.network_evidence,
            business_impact=dossier.business_impact,
        )
        return briefing
    return dossier.ai_briefing


@router.get("/{investigation_id}/action", response_model=ActionRecommendation)
def get_action_recommendation(investigation_id: str) -> ActionRecommendation:
    """Returns the current bounded action recommendation for an investigation."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    rec = decision_service.recommend_action(clean_m_id)
    return rec


@router.post("/{investigation_id}/action/approve", response_model=AnalystDecision)
def approve_action(
    investigation_id: str,
    body: Optional[Dict[str, str]] = Body(None),
) -> AnalystDecision:
    """Approves the recommended bounded action (e.g. SETTLEMENT_REVIEW or URGENT_SETTLEMENT_FREEZE)."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    reason = (body.get("notes") if body else "") or "Analyst approved recommended bounded action based on evidence review."
    decision = decision_service.record_decision(
        investigation_id=investigation_id,
        decision=DecisionFeedback.CONFIRMED_FRAUD,
        analyst_reason=reason,
        analyst_id="analyst_1",
        analyst_name="Risk Lead",
    )
    return decision


@router.post("/{investigation_id}/action/reject", response_model=AnalystDecision)
def reject_action(
    investigation_id: str,
    request: RejectActionRequest,
) -> AnalystDecision:
    """Rejects the recommended action with justification, setting status to CLEARED or UNDER_REVIEW."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    decision = decision_service.record_decision(
        investigation_id=investigation_id,
        decision=DecisionFeedback.FALSE_POSITIVE,
        analyst_reason=request.justification,
        analyst_id=request.analyst_id,
        analyst_name=request.analyst_name,
    )
    return decision


@router.post("/{investigation_id}/action/rollback", response_model=AuditLogEntry)
def rollback_action(
    investigation_id: str,
    request: RollbackActionRequest,
) -> AuditLogEntry:
    """Reverses an existing action to CLEARED state, preserving all audit history."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    audit_entry = decision_service.rollback_action(
        investigation_id=investigation_id,
        rollback_reason=request.rollback_reason,
        analyst_id=request.analyst_id,
        analyst_name=request.analyst_name,
    )
    return audit_entry


@router.post("/{investigation_id}/decision", response_model=AnalystDecision)
def record_decision(
    investigation_id: str,
    request: DecisionRequest,
) -> AnalystDecision:
    """Records an analyst decision with mandatory justification."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    decision = decision_service.record_decision(
        investigation_id=investigation_id,
        decision=request.decision,
        analyst_reason=request.justification,
        analyst_id=request.analyst_id,
        analyst_name=request.analyst_name,
    )
    return decision


@router.get("/{investigation_id}/audit-log", response_model=List[AuditLogEntry])
def get_investigation_audit_log(investigation_id: str) -> List[AuditLogEntry]:
    """Returns chronological audit trail events for an investigation."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    logs = decision_service.get_audit_log(merchant_id=clean_m_id)
    return logs


@router.post("/{investigation_id}/feedback", response_model=AnalystFeedback)
def submit_investigation_feedback(
    investigation_id: str,
    request: FeedbackSubmissionRequest,
) -> AnalystFeedback:
    """Stores analyst feedback for future model retraining."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "INVESTIGATION_NOT_FOUND", "message": f"Investigation for '{investigation_id}' not found."},
        )

    fb = decision_service.submit_feedback(
        investigation_id=investigation_id,
        feedback_type=request.feedback_type,
        notes=request.notes,
        analyst_id=request.analyst_id,
    )
    return fb


class MerchantAppealRequest(BaseModel):
    reason: str = Field(..., min_length=5, description="Merchant dispute/appeal rationale")
    contact_email: Optional[str] = "merchant@store.com"

    @field_validator("reason")
    @classmethod
    def validate_appeal_reason_not_empty(cls, v: str) -> str:
        if not v or not v.strip() or len(v.strip()) < 5:
            raise ValueError("Merchant appeal rationale must contain at least 5 non-whitespace characters.")
        return v.strip()


@router.get("/recovery/summary", response_model=AppealRecoverySummary)
def get_appeal_recovery_summary() -> AppealRecoverySummary:
    """Returns operational recovery metrics on capital restored from false-positive settlement holds."""
    return investigation_service.get_recovery_summary()


@router.get("/recovery/appeals", response_model=List[AppealRecord])
def get_all_appeals() -> List[AppealRecord]:
    """Returns complete list of merchant dispute/appeal tickets."""
    return store.get_all_appeals()


@router.post("/{investigation_id}/appeal")
def submit_merchant_appeal(
    investigation_id: str,
    request: MerchantAppealRequest,
) -> Dict[str, Any]:
    """Submits a merchant appeal on a hold/decision and routes to PENDING_APPEAL_REVIEW."""
    clean_m_id = _extract_merchant_id(investigation_id)
    merchant = store.get_merchant(clean_m_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "MERCHANT_NOT_FOUND", "message": f"Merchant '{clean_m_id}' not found."},
        )

    new_state = investigation_service.submit_merchant_appeal(
        merchant_id=clean_m_id,
        reason=request.reason,
        contact_email=request.contact_email or "merchant@store.com",
        actor="Merchant Support Representative",
    )

    return {
        "status": "APPEAL_SUBMITTED",
        "investigation_id": f"INV-{clean_m_id}",
        "merchant_id": clean_m_id,
        "new_state": new_state.value,
        "message": "Merchant appeal submitted successfully. Case routed to human appeal review queue.",
    }

