"""Risk Alerts queue API endpoints."""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.core.config import RiskLevel
from app.core.models import InvestigationState
from app.data.store import store
from app.services.risk_service import risk_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


class AlertItem(BaseModel):
    alert_id: str
    merchant_id: str
    business_name: str
    category: str
    risk_level: str
    overall_score: float
    behavioral_score: float
    network_score: float
    top_reasons: List[str]
    ring_affiliation: Optional[str] = None
    created_timestamp: str
    recommended_action: str
    status: str


class AlertQueueResponse(BaseModel):
    total_alerts: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    alerts: List[AlertItem]


@router.get("", response_model=AlertQueueResponse)
def get_alerts(
    risk_level: Optional[RiskLevel] = Query(None, description="Filter alerts by risk level"),
    status: Optional[InvestigationState] = Query(None, description="Filter alerts by investigation status"),
) -> AlertQueueResponse:
    """Returns real-time risk alert queue requiring analyst investigation."""
    merchants = store.get_all_merchants()
    alerts: List[AlertItem] = []

    critical_c = 0
    high_c = 0
    med_c = 0
    low_c = 0

    for m in merchants:
        breakdown = risk_service.scoring.calculate_merchant_risk(m.id)
        current_state = store.get_merchant_state(m.id)
        
        # Tally tier counts
        if breakdown.risk_level == RiskLevel.CRITICAL:
            critical_c += 1
        elif breakdown.risk_level == RiskLevel.HIGH:
            high_c += 1
        elif breakdown.risk_level == RiskLevel.MEDIUM:
            med_c += 1
        else:
            low_c += 1

        # Apply optional filters
        if risk_level and breakdown.risk_level != risk_level:
            continue
        if status and current_state != status:
            continue

        reasons = [f.title for f in breakdown.top_factors[:3]] if breakdown.top_factors else ["Baseline activity"]

        alert = AlertItem(
            alert_id=f"ALT-{m.id}",
            merchant_id=m.id,
            business_name=m.business_name,
            category=m.category.value,
            risk_level=breakdown.risk_level.value,
            overall_score=breakdown.overall_risk,
            behavioral_score=breakdown.behavioral_risk,
            network_score=breakdown.network_risk,
            top_reasons=reasons,
            ring_affiliation=breakdown.ring_id,
            created_timestamp=breakdown.calculated_at.isoformat(),
            recommended_action=breakdown.recommended_action.value,
            status=current_state.value,
        )
        alerts.append(alert)

    # Sort alerts by overall score descending
    alerts.sort(key=lambda a: a.overall_score, reverse=True)

    return AlertQueueResponse(
        total_alerts=len(alerts),
        critical_count=critical_c,
        high_count=high_c,
        medium_count=med_c,
        low_count=low_c,
        alerts=alerts,
    )
