"""Analyst Feedback collection and summary API endpoints."""

from typing import Dict, List, Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import DecisionFeedback
from app.core.models import AnalystFeedback
from app.data.store import store

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])


class FeedbackSummaryResponse(BaseModel):
    total_feedback_count: int
    confirmed_fraud_count: int
    false_positive_count: int
    needs_more_data_count: int
    items: List[AnalystFeedback]


@router.get("", response_model=FeedbackSummaryResponse)
def get_all_feedback() -> FeedbackSummaryResponse:
    """Returns all stored analyst feedback records and aggregate statistics."""
    feedbacks = store.get_all_feedback()

    confirmed_c = sum(1 for f in feedbacks if f.feedback_type == DecisionFeedback.CONFIRMED_FRAUD)
    fp_c = sum(1 for f in feedbacks if f.feedback_type == DecisionFeedback.FALSE_POSITIVE)
    needs_c = sum(1 for f in feedbacks if f.feedback_type == DecisionFeedback.NEEDS_INVESTIGATION or f.feedback_type.value == "NEEDS_MORE_DATA")

    return FeedbackSummaryResponse(
        total_feedback_count=len(feedbacks),
        confirmed_fraud_count=confirmed_c,
        false_positive_count=fp_c,
        needs_more_data_count=needs_c,
        items=feedbacks,
    )
