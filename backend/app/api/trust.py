"""Public Merchant Trust Signal API endpoint for Agentic Commerce and Instant Settlement."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from app.core.config import RiskLevel
from app.core.security import trust_rate_limiter
from app.data.store import store
from app.ml.scoring_engine import scoring_engine

router = APIRouter(prefix="/api/trust", tags=["Trust Signal"])


class TrustSignalResponse(BaseModel):
    merchant_id: str
    business_name: str
    category: str
    trust_tier: Optional[str] = Field(
        None,
        description="Public trust tier: 'VERIFIED', 'STANDARD', 'CAUTION', or null if elevated risk profile.",
    )
    short_reason: str = Field(
        ...,
        description="Human-readable justification for the trust tier assignment.",
    )
    instant_settlement_eligible: bool = Field(
        ...,
        description="Whether this merchant qualifies for instant/same-day settlement holds bypass.",
    )
    agentic_purchasing_approved: bool = Field(
        ...,
        description="Whether autonomous AI purchasing agents are cleared to transact with this merchant.",
    )
    last_updated: str = Field(
        ...,
        description="ISO 8601 timestamp of when this trust assessment was generated.",
    )


@router.get("/{merchant_id}", response_model=TrustSignalResponse)
def get_merchant_trust_signal(
    merchant_id: str,
    request: Request,
    response: Response,
) -> TrustSignalResponse:
    """Returns a clean, public trust evaluation for autonomous commerce and settlement routing.
    
    Exposes no raw behavioral or network internals, framing the platform's risk intelligence
    as a positive growth and agentic commerce enablement signal. Includes automated anti-probing
    rate limiting to protect scoring models from reverse-engineering attacks.
    """
    clean_id = merchant_id.replace("INV-", "").replace("ALT-", "").strip()

    # Rate limiting & reverse-engineering abuse detection
    forwarded = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
    client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "127.0.0.1")
    allowed, remaining, retry_after, is_abuse = trust_rate_limiter.check_rate_limit(client_ip, clean_id)
    
    response.headers["X-RateLimit-Limit"] = str(trust_rate_limiter.max_requests)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RATE_LIMIT_EXCEEDED" if not is_abuse else "ABUSE_DETECTED_SCORE_PROBING",
                "message": "Too many requests. Automated threshold probing and excessive queries are throttled."
                if is_abuse
                else "Rate limit exceeded. Please try again shortly.",
                "retry_after_seconds": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )

    merchant = store.get_merchant(clean_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "MERCHANT_NOT_FOUND", "message": f"Merchant '{clean_id}' not found."},
        )

    # Compute risk profile
    risk = scoring_engine.calculate_merchant_risk(clean_id)
    current_state = store.get_merchant_state(clean_id)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Rule 1: Elevated / Actioned risk merchants get NO trust signal (null)
    if risk.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH) or current_state.value == "ACTIONED":
        return TrustSignalResponse(
            merchant_id=merchant.id,
            business_name=merchant.business_name,
            category=merchant.category.value,
            trust_tier=None,
            short_reason="Trust signal withheld due to active risk review or compliance action.",
            instant_settlement_eligible=False,
            agentic_purchasing_approved=False,
            last_updated=now_iso,
        )

    # Rule 2: Medium risk merchants get CAUTION tier
    if risk.risk_level == RiskLevel.MEDIUM or current_state.value in ("UNDER_REVIEW", "PENDING_APPEAL_REVIEW"):
        return TrustSignalResponse(
            merchant_id=merchant.id,
            business_name=merchant.business_name,
            category=merchant.category.value,
            trust_tier="CAUTION",
            short_reason="Standard transaction monitoring active with precautionary velocity caps.",
            instant_settlement_eligible=False,
            agentic_purchasing_approved=True,
            last_updated=now_iso,
        )

    # Rule 3: Low risk merchants get VERIFIED or STANDARD tier
    if risk.overall_risk <= 20.0 and risk.network_risk <= 10.0 and risk.behavioral_risk <= 25.0:
        return TrustSignalResponse(
            merchant_id=merchant.id,
            business_name=merchant.business_name,
            category=merchant.category.value,
            trust_tier="VERIFIED",
            short_reason="Established merchant with zero syndicate links and low dispute rate. Eligible for instant settlement & autonomous AI purchasing agent approvals.",
            instant_settlement_eligible=True,
            agentic_purchasing_approved=True,
            last_updated=now_iso,
        )

    return TrustSignalResponse(
        merchant_id=merchant.id,
        business_name=merchant.business_name,
        category=merchant.category.value,
        trust_tier="STANDARD",
        short_reason="Healthy operational profile within expected industry baseline parameters.",
        instant_settlement_eligible=True,
        agentic_purchasing_approved=True,
        last_updated=now_iso,
    )
