"""Unit tests for InvestigationDossier, evidence, timeline, and state transitions."""

import pytest
from app.core.models import InvestigationState, EvidenceType
from app.data.store import DataStore
from app.services.investigation_service import InvestigationService


def test_dossier_generation():
    """Verify complete dossier is generated with profile, risk summary, evidence, and timeline."""
    ds = DataStore(auto_seed=True)
    service = InvestigationService(datastore=ds)

    dossier = service.get_investigation_dossier("M-ALPHA-01")
    assert dossier.merchant_id == "M-ALPHA-01"
    assert dossier.investigation_id == "INV-M-ALPHA-01"
    assert dossier.merchant_profile["business_name"] is not None
    assert dossier.risk_summary.overall_risk >= 80.0
    assert len(dossier.all_evidence) > 0
    assert len(dossier.timeline) > 0
    assert dossier.action_recommendation.requires_analyst_approval is True
    assert dossier.ai_briefing is not None


def test_evidence_structure_and_types():
    """Verify structured evidence items have observed and baseline values."""
    ds = DataStore(auto_seed=True)
    service = InvestigationService(datastore=ds)

    dossier = service.get_investigation_dossier("M-2001")
    evidence_types = {e.evidence_type for e in dossier.all_evidence}

    assert EvidenceType.BEHAVIORAL in evidence_types or EvidenceType.TRANSACTION in evidence_types
    for e in dossier.all_evidence:
        assert e.evidence_id is not None
        assert e.observed_value is not None
        assert e.baseline_value is not None
        assert e.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_timeline_chronology():
    """Verify timeline events are strictly in chronological ascending order."""
    ds = DataStore(auto_seed=True)
    service = InvestigationService(datastore=ds)

    timeline = service.get_investigation_timeline("M-ALPHA-01")
    assert len(timeline) >= 3

    timestamps = [e.timestamp for e in timeline]
    assert timestamps == sorted(timestamps)


def test_valid_state_transitions():
    """Verify valid investigation lifecycle state transitions."""
    ds = DataStore(auto_seed=True)
    service = InvestigationService(datastore=ds)

    m_id = "M-1001"
    assert ds.get_merchant_state(m_id) == InvestigationState.NEW

    # NEW -> UNDER_REVIEW
    s1 = service.transition_state(m_id, InvestigationState.UNDER_REVIEW, reason="Analyst opened review")
    assert s1 == InvestigationState.UNDER_REVIEW
    assert ds.get_merchant_state(m_id) == InvestigationState.UNDER_REVIEW

    # UNDER_REVIEW -> ACTION_RECOMMENDED
    s2 = service.transition_state(m_id, InvestigationState.ACTION_RECOMMENDED, reason="Algorithm recommended action")
    assert s2 == InvestigationState.ACTION_RECOMMENDED

    # ACTION_RECOMMENDED -> ACTIONED
    s3 = service.transition_state(m_id, InvestigationState.ACTIONED, reason="Analyst confirmed hold")
    assert s3 == InvestigationState.ACTIONED

    # ACTIONED -> CLEARED (Rollback)
    s4 = service.transition_state(m_id, InvestigationState.CLEARED, reason="Cleared following KYC proof")
    assert s4 == InvestigationState.CLEARED

    # CLEARED -> CLOSED
    s5 = service.transition_state(m_id, InvestigationState.CLOSED, reason="Case closed")
    assert s5 == InvestigationState.CLOSED


def test_invalid_state_transitions_rejected():
    """Verify invalid state transitions raise ValueError and preserve previous state."""
    ds = DataStore(auto_seed=True)
    service = InvestigationService(datastore=ds)

    m_id = "M-1002"
    assert ds.get_merchant_state(m_id) == InvestigationState.NEW

    # Attempting invalid jump from NEW directly to ACTIONED
    with pytest.raises(ValueError) as excinfo:
        service.transition_state(m_id, InvestigationState.ACTIONED, reason="Illegal direct action")
    assert "Invalid state transition" in str(excinfo.value)
    assert ds.get_merchant_state(m_id) == InvestigationState.NEW


def test_business_impact_calculation():
    """Verify business impact numbers are estimated properly."""
    ds = DataStore(auto_seed=True)
    service = InvestigationService(datastore=ds)

    impact_alpha = service.calculate_investigation_business_impact("M-ALPHA-01")
    assert impact_alpha.total_processed_volume > 0.0
    assert impact_alpha.suspicious_volume == impact_alpha.total_processed_volume
    assert impact_alpha.potential_loss_prevented > 0.0
    assert impact_alpha.is_estimated is True
