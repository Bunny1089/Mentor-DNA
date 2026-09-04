"""Merchant query and risk profile API endpoints."""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

from app.core.config import RiskLevel, BusinessCategory
from app.core.models import RiskScoreBreakdown
from app.data.store import store
from app.services.risk_service import risk_service

router = APIRouter(prefix="/api/merchants", tags=["Merchants"])


class MerchantSummaryItem(BaseModel):
    merchant_id: str
    business_name: str
    category: str
    business_type: str
    onboarding_date: str
    transaction_count: int
    total_volume: float
    behavioral_risk: float
    network_risk: float
    overall_risk: float
    risk_level: str
    confidence: float
    recommended_action: str
    ring_id: Optional[str] = None
    top_factor: str


class PaginatedMerchantsResponse(BaseModel):
    total_count: int
    page: int
    page_size: int
    total_pages: int
    merchants: List[MerchantSummaryItem]


@router.get("", response_model=PaginatedMerchantsResponse)
def get_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    risk_level: Optional[RiskLevel] = Query(None, description="Filter by risk tier"),
    category: Optional[BusinessCategory] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by merchant ID or business name"),
    ring_id: Optional[str] = Query(None, description="Filter by ring affiliation"),
) -> PaginatedMerchantsResponse:
    """Returns a filtered, paginated list of all monitored merchants with risk summaries."""
    all_merchants = risk_service.get_all_merchant_risks()

    # Apply filters
    filtered = all_merchants
    if risk_level:
        filtered = [m for m in filtered if m["risk_level"] == risk_level.value]
    if category:
        filtered = [m for m in filtered if m["category"] == category.value]
    if ring_id:
        filtered = [m for m in filtered if m["ring_id"] == ring_id]
    if search:
        s_lower = search.strip().lower()
        filtered = [
            m for m in filtered
            if s_lower in m["merchant_id"].lower() or s_lower in m["business_name"].lower()
        ]

    total_count = len(filtered)
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = filtered[start_idx:end_idx]

    return PaginatedMerchantsResponse(
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        merchants=[MerchantSummaryItem(**item) for item in page_items],
    )


@router.get("/{merchant_id}", response_model=Dict[str, Any])
def get_merchant_detail(merchant_id: str) -> Dict[str, Any]:
    """Returns detailed merchant profile, activity metrics, and current risk status."""
    merchant = store.get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "MERCHANT_NOT_FOUND", "message": f"Merchant '{merchant_id}' does not exist."},
        )

    risk_dossier = risk_service.get_merchant_risk(merchant_id)
    txns = store.get_merchant_transactions(merchant_id)
    settlements = store.get_merchant_settlements(merchant_id)
    current_state = store.get_merchant_state(merchant_id)

    return {
        "merchant_id": merchant.id,
        "business_name": merchant.business_name,
        "legal_name": merchant.legal_name,
        "category": merchant.category.value,
        "business_type": merchant.business_type,
        "declared_avg_ticket": merchant.declared_avg_ticket,
        "onboarding_date": merchant.onboarding_date.isoformat(),
        "kyc_status": merchant.kyc_status,
        "is_active": merchant.is_active,
        "current_state": current_state.value,
        "transaction_count": len(txns),
        "total_volume": round(sum(t.amount for t in txns), 2),
        "settlement_count": len(settlements),
        "risk_summary": risk_dossier,
    }


@router.get("/{merchant_id}/risk", response_model=RiskScoreBreakdown)
def get_merchant_risk_score(merchant_id: str) -> RiskScoreBreakdown:
    """Returns full explainable RiskScoreBreakdown for a single merchant."""
    merchant = store.get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "MERCHANT_NOT_FOUND", "message": f"Merchant '{merchant_id}' does not exist."},
        )

    breakdown = risk_service.scoring.calculate_merchant_risk(merchant_id)
    return breakdown
