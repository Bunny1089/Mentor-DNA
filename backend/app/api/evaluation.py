"""Honest Model Evaluation & Financial Loss Matrix API endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Query

from app.ml.evaluator import evaluator

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])


@router.get("/metrics")
def get_evaluation_metrics(
    threshold: float = Query(60.0, ge=0.0, le=100.0, description="Risk threshold score for fraud classification"),
) -> Dict[str, Any]:
    """Returns honest model evaluation metrics and estimated business loss prevention matrix."""
    report = evaluator.evaluate_model_performance(threshold_score=threshold)
    return report
