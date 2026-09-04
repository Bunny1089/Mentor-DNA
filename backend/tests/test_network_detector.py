"""Unit tests for NetworkRiskDetector and collusive ring detection."""

import pytest
from app.core.models import EntityType
from app.data.store import DataStore
from app.ml.network_detector import NetworkRiskDetector


def test_network_graph_construction():
    """Verify heterogeneous entity graph has all entity types and expected edge counts."""
    ds = DataStore(auto_seed=True)
    detector = NetworkRiskDetector(ds)

    graph = detector.graph
    assert graph.number_of_nodes() > 500
    assert graph.number_of_edges() > 1000

    # Verify presence of entity types
    entity_types = {attrs.get("entity_type") for _, attrs in graph.nodes(data=True)}
    assert EntityType.MERCHANT.value in entity_types
    assert EntityType.DEVICE.value in entity_types
    assert EntityType.PHONE.value in entity_types
    assert EntityType.BANK_ACCOUNT.value in entity_types
    assert EntityType.UPI_HANDLE.value in entity_types
    assert EntityType.ADDRESS.value in entity_types


def test_planted_rings_detected():
    """Verify explicit discovery and identification of all 3 planted fraud rings."""
    ds = DataStore(auto_seed=True)
    detector = NetworkRiskDetector(ds)

    rings = detector.get_all_detected_rings()
    assert len(rings) >= 3

    ring_ids = {r.ring_id for r in rings}
    assert "RING-ALPHA-DEVICE-FARM" in ring_ids
    assert "RING-BETA-PAYOUT-CLUSTER" in ring_ids
    assert "RING-GAMMA-ADDRESS-HUB" in ring_ids

    # Verify Ring Alpha properties
    alpha = next(r for r in rings if r.ring_id == "RING-ALPHA-DEVICE-FARM")
    assert alpha.ring_size == 10
    assert alpha.dominant_shared_identifier in ["DEVICE", "PHONE"]
    assert alpha.network_risk_score >= 80.0
    assert alpha.confidence >= 0.80

    # Verify Ring Beta properties
    beta = next(r for r in rings if r.ring_id == "RING-BETA-PAYOUT-CLUSTER")
    assert beta.ring_size == 10
    assert beta.dominant_shared_identifier in ["BANK_ACCOUNT", "UPI_HANDLE"]
    assert beta.network_risk_score >= 80.0

    # Verify Ring Gamma properties
    gamma = next(r for r in rings if r.ring_id == "RING-GAMMA-ADDRESS-HUB")
    assert gamma.ring_size == 10
    assert gamma.dominant_shared_identifier in ["ADDRESS", "PHONE"]


def test_legitimate_merchant_low_network_risk():
    """Verify isolated legitimate merchants receive low network risk (< 20)."""
    ds = DataStore(auto_seed=True)
    detector = NetworkRiskDetector(ds)

    legit_net = detector.get_merchant_network_risk("M-1001")
    assert legit_net["network_risk_score"] < 20.0
    assert legit_net["shared_identifier_count"] == 0.0
    assert legit_net["connected_merchant_count"] == 0.0


def test_subgraph_generation_for_cytoscape():
    """Verify subgraph response contains proper node and edge structures."""
    ds = DataStore(auto_seed=True)
    detector = NetworkRiskDetector(ds)

    subgraph = detector.get_subgraph_for_merchant("M-ALPHA-01", max_hops=2)
    assert subgraph.merchant_id == "M-ALPHA-01"
    assert len(subgraph.nodes) > 0
    assert subgraph.ring_id == "RING-ALPHA-DEVICE-FARM"
    assert subgraph.cluster_risk_score >= 80.0


def test_shared_infrastructure_false_positive_filter():
    """Verify two unrelated merchants sharing ONLY generic infrastructure are NOT flagged as a ring."""
    ds = DataStore(auto_seed=True)
    
    # Ensure two merchants only share a generic building address without personal identifiers
    m1 = ds.get_merchant("M-1002")
    m2 = ds.get_merchant("M-1003")
    assert m1 and m2
    
    # Give them the same generic address, but distinct devices, phones, and bank accounts
    m2.address_id = m1.address_id
    
    detector = NetworkRiskDetector(ds)
    rings = detector.get_all_detected_rings()
    
    # Verify that M-1002 and M-1003 do not form a 2-merchant ring
    two_merchant_rings = [
        r for r in rings
        if "M-1002" in r.member_merchants and "M-1003" in r.member_merchants
    ]
    assert len(two_merchant_rings) == 0, "Shared infrastructure alone should not create a collusive ring"

