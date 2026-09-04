"""Unit tests for feedback submission, storage, and retrieval."""

import pytest
from app.core.config import DecisionFeedback
from app.data.store import DataStore
from app.services.decision_service import DecisionService


def test_submit_feedback_and_retrieval():
    """Verify analyst feedback is recorded, stored, and queryable for retraining."""
    ds = DataStore(auto_seed=True)
    service = DecisionService(datastore=ds)

    feedback = service.submit_feedback(
        investigation_id="INV-M-ALPHA-01",
        feedback_type=DecisionFeedback.CONFIRMED_FRAUD,
        notes="High confidence mule ring. Rooted emulator fingerprints detected.",
        analyst_id="lead_analyst_01",
    )

    assert feedback.feedback_id.startswith("FB-")
    assert feedback.feedback_type == DecisionFeedback.CONFIRMED_FRAUD
    assert feedback.merchant_id == "M-ALPHA-01"

    all_fb = service.get_all_feedback()
    assert len(all_fb) >= 1
    assert any(f.feedback_id == feedback.feedback_id for f in all_fb)

    # Verify feedback logged in audit trail
    logs = service.get_audit_log(merchant_id="M-ALPHA-01")
    assert any("FEEDBACK_RECORDED" in l.event_type.value for l in logs)
