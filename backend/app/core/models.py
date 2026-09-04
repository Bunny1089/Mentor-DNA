"""Domain Models and Pydantic Schemas for Merchant DNA."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
from app.core.config import RiskLevel, ActionType, DecisionFeedback, BusinessCategory


class EntityType(str, Enum):
    MERCHANT = "MERCHANT"
    BUYER = "BUYER"
    DEVICE = "DEVICE"
    PHONE = "PHONE"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    UPI_HANDLE = "UPI_HANDLE"
    ADDRESS = "ADDRESS"
    TRANSACTION = "TRANSACTION"


class RelationType(str, Enum):
    OPERATED_ON_DEVICE = "OPERATED_ON_DEVICE"
    SETTLES_TO_BANK = "SETTLES_TO_BANK"
    REGISTERED_PHONE = "REGISTERED_PHONE"
    USES_UPI = "USES_UPI"
    LOCATED_AT = "LOCATED_AT"
    TRANSACTED_WITH = "TRANSACTED_WITH"
    SHARED_IDENTIFIER = "SHARED_IDENTIFIER"


class TrueLabel(str, Enum):
    LEGITIMATE = "LEGITIMATE"
    MULE_SHELL = "MULE_SHELL"
    RING_MEMBER = "RING_MEMBER"


class FraudScenarioType(str, Enum):
    NONE = "NONE"
    DORMANT_BURST_MULE = "DORMANT_BURST_MULE"
    CATEGORY_MISMATCH_LAUNDERING = "CATEGORY_MISMATCH_LAUNDERING"
    DEVICE_FARM_SYNDICATE = "DEVICE_FARM_SYNDICATE"
    PAYOUT_LAUNDERING_CLUSTER = "PAYOUT_LAUNDERING_CLUSTER"
    BURST_BUST_ADDRESS_HUB = "BURST_BUST_ADDRESS_HUB"


# ==========================================
# 1. Investigation Lifecycle States & Events
# ==========================================

class InvestigationState(str, Enum):
    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    ACTION_RECOMMENDED = "ACTION_RECOMMENDED"
    ACTIONED = "ACTIONED"
    PENDING_APPEAL_REVIEW = "PENDING_APPEAL_REVIEW"
    CLEARED = "CLEARED"
    CLOSED = "CLOSED"


# Strict State Transition Validation Rules
VALID_STATE_TRANSITIONS: Dict[InvestigationState, Set[InvestigationState]] = {
    InvestigationState.NEW: {
        InvestigationState.UNDER_REVIEW,
        InvestigationState.ACTION_RECOMMENDED,
        InvestigationState.CLEARED,
        InvestigationState.CLOSED,
    },
    InvestigationState.UNDER_REVIEW: {
        InvestigationState.ESCALATED,
        InvestigationState.ACTION_RECOMMENDED,
        InvestigationState.ACTIONED,
        InvestigationState.PENDING_APPEAL_REVIEW,
        InvestigationState.CLEARED,
        InvestigationState.CLOSED,
    },
    InvestigationState.ESCALATED: {
        InvestigationState.ACTION_RECOMMENDED,
        InvestigationState.ACTIONED,
        InvestigationState.PENDING_APPEAL_REVIEW,
        InvestigationState.CLEARED,
        InvestigationState.CLOSED,
    },
    InvestigationState.ACTION_RECOMMENDED: {
        InvestigationState.ACTIONED,
        InvestigationState.UNDER_REVIEW,
        InvestigationState.PENDING_APPEAL_REVIEW,
        InvestigationState.CLEARED,
        InvestigationState.CLOSED,
    },
    InvestigationState.ACTIONED: {
        InvestigationState.CLEARED,  # Action Rollback / Reversal
        InvestigationState.UNDER_REVIEW,
        InvestigationState.PENDING_APPEAL_REVIEW,  # Merchant Appeal
        InvestigationState.CLOSED,
    },
    InvestigationState.PENDING_APPEAL_REVIEW: {
        InvestigationState.UNDER_REVIEW,
        InvestigationState.ACTIONED,
        InvestigationState.CLEARED,
        InvestigationState.CLOSED,
    },
    InvestigationState.CLEARED: {
        InvestigationState.UNDER_REVIEW,  # Reopen on new telemetry
        InvestigationState.CLOSED,
    },
    InvestigationState.CLOSED: {
        InvestigationState.UNDER_REVIEW,  # Case Reopened
    },
}


class EvidenceType(str, Enum):
    BEHAVIORAL = "BEHAVIORAL"
    NETWORK = "NETWORK"
    TRANSACTION = "TRANSACTION"
    SETTLEMENT = "SETTLEMENT"
    REFUND = "REFUND"
    IDENTITY = "IDENTITY"
    TEMPORAL = "TEMPORAL"


class AuditEventType(str, Enum):
    RISK_ALERT_CREATED = "RISK_ALERT_CREATED"
    INVESTIGATION_OPENED = "INVESTIGATION_OPENED"
    STATE_TRANSITION = "STATE_TRANSITION"
    ACTION_RECOMMENDED = "ACTION_RECOMMENDED"
    ACTION_APPROVED = "ACTION_APPROVED"
    ACTION_REJECTED = "ACTION_REJECTED"
    ANALYST_DECISION = "ANALYST_DECISION"
    ACTION_ROLLED_BACK = "ACTION_ROLLED_BACK"
    FEEDBACK_RECORDED = "FEEDBACK_RECORDED"
    MERCHANT_NOTIFICATION_DISPATCHED = "MERCHANT_NOTIFICATION_DISPATCHED"
    CASE_CLOSED = "CASE_CLOSED"


class ActorType(str, Enum):
    SYSTEM = "SYSTEM"
    ANALYST = "ANALYST"


# ==========================================
# 2. Physical & Digital Shared Entities
# ==========================================

class Device(BaseModel):
    id: str
    fingerprint_hash: str
    os: str
    user_agent: str
    ip_subnet: str
    is_emulator: bool = False
    created_at: datetime


class Phone(BaseModel):
    id: str
    phone_number: str
    carrier: str
    is_voip: bool = False
    created_at: datetime


class BankAccount(BaseModel):
    id: str
    account_number_masked: str
    ifsc_code: str
    bank_name: str
    beneficiary_name: str
    created_at: datetime


class UPIHandle(BaseModel):
    id: str
    vpa: str
    psp: str
    created_at: datetime


class Address(BaseModel):
    id: str
    address_line: str
    city: str
    state: str
    pincode: str
    geo_lat: float
    geo_lng: float
    is_commercial_hub: bool = False
    created_at: datetime


# ==========================================
# 3. Actors & Commerce Entities
# ==========================================

class Buyer(BaseModel):
    id: str
    name: str
    email: str
    phone_id: str
    account_age_days: int
    trust_score: float = 85.0
    created_at: datetime


class Merchant(BaseModel):
    id: str
    business_name: str
    legal_name: str
    category: BusinessCategory
    business_type: str
    declared_avg_ticket: float
    onboarding_date: datetime
    kyc_status: str = "VERIFIED"
    
    # Core Entity References (Entity Graph anchors)
    device_id: str
    phone_id: str
    bank_account_id: str
    upi_handle_id: str
    address_id: str
    
    is_active: bool = True
    created_at: datetime


class Transaction(BaseModel):
    id: str
    merchant_id: str
    buyer_id: str
    amount: float
    currency: str = "INR"
    status: str = "SUCCESS"  # SUCCESS, FAILED, DISPUTED
    payment_method: str       # UPI, CREDIT_CARD, DEBIT_CARD, NETBANKING
    timestamp: datetime
    is_round_amount: bool
    ip_address: str
    device_id: Optional[str] = None


class Settlement(BaseModel):
    id: str
    merchant_id: str
    bank_account_id: str
    amount: float
    requested_at: datetime
    settled_at: Optional[datetime] = None
    status: str = "SETTLED"  # SETTLED, HELD, PENDING
    velocity_in_out_hours: float = 24.0


class Refund(BaseModel):
    id: str
    transaction_id: str
    merchant_id: str
    amount: float
    reason: str
    requested_at: datetime
    status: str = "PROCESSED"  # PROCESSED, DISPUTED, REJECTED


# ==========================================
# 4. Ground Truth (Strictly Isolated)
# ==========================================

class GroundTruth(BaseModel):
    merchant_id: str
    true_label: TrueLabel
    fraud_scenario: FraudScenarioType
    planted_ring_id: Optional[str] = None
    planted_anomalies: List[str] = []
    expected_risk_tier: RiskLevel
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# 5. Graph & Relationship Models
# ==========================================

class GraphNode(BaseModel):
    id: str
    label: str
    entity_type: EntityType
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[float] = None
    is_ring_member: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation_type: RelationType
    weight: float = 1.0
    label: str
    is_suspicious: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubgraphResponse(BaseModel):
    merchant_id: str
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    ring_id: Optional[str] = None
    cluster_risk_score: float = 0.0
    shared_identifiers_count: int = 0


# ==========================================
# 6. Structured Evidence & Risk Factors
# ==========================================

class EvidenceItem(BaseModel):
    evidence_id: str
    evidence_type: EvidenceType
    title: str
    observed_value: str
    baseline_value: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float
    source: str
    timestamp: Optional[datetime] = None
    explanation: str


class RiskFactorContribution(BaseModel):
    factor_id: str
    title: str
    description: str
    category: str  # BEHAVIORAL, NETWORK, VELOCITY, SETTLEMENT
    weight: float
    value_observed: str
    benchmark: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


class RiskScoreBreakdown(BaseModel):
    merchant_id: str
    behavioral_risk: float = Field(..., ge=0.0, le=100.0)
    network_risk: float = Field(..., ge=0.0, le=100.0)
    overall_risk: float = Field(..., ge=0.0, le=100.0)
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    top_factors: List[RiskFactorContribution] = Field(default_factory=list)
    recommended_action: ActionType
    action_rationale: str
    ring_id: Optional[str] = None
    connected_high_risk_count: int = 0
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# 7. Timeline & Case Briefings
# ==========================================

class TimelineEvent(BaseModel):
    event_id: str
    event_type: str
    title: str
    description: str
    timestamp: datetime
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AICaseBriefing(BaseModel):
    summary: str
    key_evidence: List[str]
    network_context: str
    risk_interpretation: str
    recommended_next_step: str
    evidence_count: int
    evidence_ids_used: List[str]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    grounding_mode: str = "DETERMINISTIC_FALLBACK"  # LLM or DETERMINISTIC_FALLBACK


# ==========================================
# 8. Bounded Action Recommendation
# ==========================================

class ActionRecommendation(BaseModel):
    action: ActionType
    risk_level: RiskLevel
    reason: str
    supporting_evidence: List[str]
    confidence: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reversible: bool = True
    requires_analyst_approval: bool = True
    max_hold_duration_hours: int = 48
    auto_escalation_hours: int = 24
    merchant_notified_at: Optional[datetime] = None
    notification_status: str = "PENDING"


# ==========================================
# 9. Business Impact & Financial Loss Model
# ==========================================

class BusinessImpact(BaseModel):
    merchant_id: str
    total_processed_volume: float
    suspicious_volume: float
    estimated_exposure: float
    potential_loss_prevented: float
    false_positive_cost: float
    expected_net_loss: float
    is_estimated: bool = True


# ==========================================
# 10. Investigation Dossier
# ==========================================

class InvestigationDossier(BaseModel):
    investigation_id: str
    merchant_id: str
    merchant_profile: Dict[str, Any]
    current_state: InvestigationState
    risk_summary: RiskScoreBreakdown
    behavioral_evidence: List[EvidenceItem]
    network_evidence: List[EvidenceItem]
    all_evidence: List[EvidenceItem]
    timeline: List[TimelineEvent]
    action_recommendation: ActionRecommendation
    ai_briefing: Optional[AICaseBriefing] = None
    business_impact: BusinessImpact
    created_at: datetime
    updated_at: datetime


# ==========================================
# 11. Decisions, Audit Trail & Feedback
# ==========================================

class AuditLogEntry(BaseModel):
    event_id: str
    merchant_id: str
    investigation_id: str
    event_type: AuditEventType
    actor: ActorType
    actor_id: str
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    previous_state: Optional[InvestigationState] = None
    new_state: Optional[InvestigationState] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalystDecision(BaseModel):
    decision_id: str
    investigation_id: str
    merchant_id: str
    analyst_id: str
    analyst_name: str
    decision: DecisionFeedback
    action_taken: ActionType
    analyst_reason: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    previous_state: InvestigationState
    new_state: InvestigationState
    reversible: bool = True


class AnalystFeedback(BaseModel):
    feedback_id: str
    investigation_id: str
    merchant_id: str
    analyst_id: str
    feedback_type: DecisionFeedback
    notes: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==========================================
# 12. Appeal Recovery & False-Positive Tracking
# ==========================================

class AppealRecord(BaseModel):
    appeal_id: str
    investigation_id: str
    merchant_id: str
    business_name: str
    reason: str
    contact_email: Optional[str] = "merchant@store.com"
    status: str = "PENDING_REVIEW"  # PENDING_REVIEW, APPROVED_RELEASED, REJECTED_UPHELD
    appeal_submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    appeal_resolved_at: Optional[datetime] = None
    recovered_amount: Optional[float] = None
    resolution_time_hours: Optional[float] = None


class AppealRecoverySummary(BaseModel):
    pending_appeals_count: int
    resolved_appeals_count: int
    total_recovered_amount: float
    avg_resolution_time_hours: float
    recent_appeals: List[AppealRecord]

