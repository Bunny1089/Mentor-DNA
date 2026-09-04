"""Unit tests for bounded actions, analyst decisions, and reversible rollbacks."""

import pytest
from app.core.config import ActionType, DecisionFeedback
from app.core.models import InvestigationState
from app.data.store import DataStore
from app.services.decision_service import DecisionService


def test_action_recommendation_requires_analyst_approval():
    """Verify system recommendations require human approval and are marked reversible."""
    ds = DataStore(auto_seed=True)
    service = DecisionService(datastore=ds)

    rec = service.recommend_action("M-ALPHA-01")
    assert rec.action in [ActionType.URGENT_SETTLEMENT_FREEZE, ActionType.SETTLEMENT_REVIEW]
    assert rec.requires_analyst_approval is True
    assert rec.reversible is True
    assert len(rec.supporting_evidence) > 0


def test_analyst_decision_requires_reason():
    """Verify decision submission fails without explicit justification."""
    ds = DataStore(auto_seed=True)
    service = DecisionService(datastore=ds)

    # Empty reason should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        service.record_decision(
            investigation_id="INV-M-ALPHA-01",
            decision=DecisionFeedback.CONFIRMED_FRAUD,
            analyst_reason="",
        )
    assert "requires a valid non-empty reason" in str(excinfo.value)


def test_record_confirmed_fraud_decision():
    """Verify CONFIRMED_FRAUD decision transitions state to ACTIONED."""
    ds = DataStore(auto_seed=True)
    service = DecisionService(datastore=ds)

    decision = service.record_decision(
        investigation_id="INV-M-ALPHA-01",
        decision=DecisionFeedback.CONFIRMED_FRAUD,
        analyst_reason="Verified device farm linkage with 9 other storefronts and 48h volume surge.",
        analyst_id="analyst_99",
        analyst_name="Senior Risk Officer",
    )

    assert decision.decision == DecisionFeedback.CONFIRMED_FRAUD
    assert decision.new_state == InvestigationState.ACTIONED
    assert ds.get_merchant_state("M-ALPHA-01") == InvestigationState.ACTIONED

    # Verify decision in store
    all_decisions = ds.get_all_decisions()
    assert any(d.decision_id == decision.decision_id for d in all_decisions)


def test_rollback_action_preserves_history():
    """Verify action rollback changes state to CLEARED and records audit entry without deleting history."""
    ds = DataStore(auto_seed=True)
    service = DecisionService(datastore=ds)

    # 1. First record an action
    service.record_decision(
        investigation_id="INV-M-ALPHA-02",
        decision=DecisionFeedback.CONFIRMED_FRAUD,
        analyst_reason="Initial high risk escalation",
    )
    assert ds.get_merchant_state("M-ALPHA-02") == InvestigationState.ACTIONED

    # 2. Rollback the action
    audit_rb = service.rollback_action(
        investigation_id="INV-M-ALPHA-02",
        rollback_reason="Merchant provided verified wholesale supply contracts and physical shop photos.",
        analyst_id="lead_analyst",
    )

    assert ds.get_merchant_state("M-ALPHA-02") == InvestigationState.CLEARED
    assert audit_rb.new_state == InvestigationState.CLEARED

    # Verify all audit history remains intact
    logs = ds.get_audit_log(merchant_id="M-ALPHA-02")
    assert len(logs) >= 2  # Action Decision + Rollback entry
