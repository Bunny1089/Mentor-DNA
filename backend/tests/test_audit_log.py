"""Unit tests for persistent audit trail logging and history preservation."""

import pytest
from app.core.config import DecisionFeedback
from app.core.models import AuditEventType, ActorType, InvestigationState
from app.data.store import DataStore
from app.services.decision_service import DecisionService
from app.services.investigation_service import InvestigationService


def test_audit_trail_records_lifecycle_events():
    """Verify all state transitions and analyst actions create structured audit events."""
    ds = DataStore(auto_seed=True)
    inv_service = InvestigationService(datastore=ds)
    dec_service = DecisionService(datastore=ds, investigation=inv_service)

    m_id = "M-1003"
    initial_log_count = len(ds.get_audit_log(merchant_id=m_id))

    # 1. State transition (logs STATE_TRANSITION)
    inv_service.transition_state(
        m_id,
        InvestigationState.UNDER_REVIEW,
        actor=ActorType.ANALYST,
        actor_id="analyst_1",
        reason="Manual queue assignment",
    )

    # 2. Recommendation (logs ACTION_RECOMMENDED)
    dec_service.recommend_action(m_id)

    # 3. Decision (logs STATE_TRANSITION + ANALYST_DECISION)
    dec_service.record_decision(
        investigation_id=f"INV-{m_id}",
        decision=DecisionFeedback.CLEARED,
        analyst_reason="Verified organic business activity",
        analyst_id="analyst_1",
    )

    logs = ds.get_audit_log(merchant_id=m_id)
    assert len(logs) == initial_log_count + 4

    event_types = [l.event_type for l in logs]
    assert AuditEventType.STATE_TRANSITION in event_types
    assert AuditEventType.ACTION_RECOMMENDED in event_types
    assert AuditEventType.ANALYST_DECISION in event_types


def test_audit_records_contain_required_metadata():
    """Verify audit records contain timestamps, actors, actor_ids, and state diffs."""
    ds = DataStore(auto_seed=True)
    dec_service = DecisionService(datastore=ds)

    dec_service.record_decision(
        investigation_id="INV-M-1004",
        decision=DecisionFeedback.NEEDS_INVESTIGATION,
        analyst_reason="Requesting additional tax filings",
        analyst_id="analyst_42",
        analyst_name="Specialist Investigator",
    )

    logs = ds.get_audit_log(merchant_id="M-1004")
    assert len(logs) >= 1

    last_log = logs[-1]
    assert last_log.actor == ActorType.ANALYST
    assert last_log.actor_id == "analyst_42"
    assert last_log.previous_state is not None
    assert last_log.new_state is not None
    assert last_log.timestamp is not None
    assert "additional tax filings" in last_log.description
