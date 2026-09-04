"""Network entity graph and ring exploration API endpoints."""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.models import SubgraphResponse, GraphNode, GraphEdge, EntityType, RelationType
from app.data.store import store
from app.ml.network_detector import network_detector

router = APIRouter(prefix="/api/graph", tags=["Graph & Rings"])


class RingSummaryItem(BaseModel):
    ring_id: str
    name: str
    members: List[str]
    shared_entities: List[Dict[str, str]]
    ring_size: int
    density: float
    dominant_shared_identifier: str
    network_risk: float
    confidence: float


@router.get("/merchant/{merchant_id}", response_model=SubgraphResponse)
@router.get("/merchants/{merchant_id}", response_model=SubgraphResponse)
def get_merchant_graph(merchant_id: str) -> SubgraphResponse:
    """Returns Cytoscape-compatible multi-entity ego subgraph around a merchant."""
    merchant = store.get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "MERCHANT_NOT_FOUND", "message": f"Merchant '{merchant_id}' does not exist."},
        )

    subgraph = network_detector.get_subgraph_for_merchant(merchant_id, max_hops=2)
    return subgraph


@router.get("/rings", response_model=List[RingSummaryItem])
def get_detected_rings() -> List[RingSummaryItem]:
    """Returns all detected collusive merchant rings and syndicates."""
    rings = network_detector.get_all_detected_rings()
    results = []
    for r in rings:
        results.append(
            RingSummaryItem(
                ring_id=r.ring_id,
                name=r.ring_id.replace("RING-", "").replace("-", " ").title(),
                members=r.member_merchants,
                shared_entities=r.shared_entities,
                ring_size=r.ring_size,
                density=round(r.ring_density, 3),
                dominant_shared_identifier=r.dominant_shared_identifier,
                network_risk=round(r.network_risk_score, 1),
                confidence=round(r.confidence, 2),
            )
        )
    return results


@router.get("/rings/{ring_id}", response_model=SubgraphResponse)
def get_ring_cluster_subgraph(ring_id: str) -> SubgraphResponse:
    """Returns full multi-node subgraph containing all member merchants and shared infrastructure for a ring."""
    rings = network_detector.get_all_detected_rings()
    target_ring = next((r for r in rings if r.ring_id == ring_id), None)
    if not target_ring:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "RING_NOT_FOUND", "message": f"Ring '{ring_id}' not found."},
        )

    # Union subgraphs of all member merchants
    nodes_map: Dict[str, GraphNode] = {}
    edges_map: Dict[str, GraphEdge] = {}

    for m_id in target_ring.member_merchants:
        sub = network_detector.get_subgraph_for_merchant(m_id, max_hops=1)
        for n in sub.nodes:
            nodes_map[n.id] = n
        for e in sub.edges:
            edges_map[e.id] = e

    return SubgraphResponse(
        merchant_id=target_ring.member_merchants[0],
        nodes=list(nodes_map.values()),
        edges=list(edges_map.values()),
        ring_id=target_ring.ring_id,
        cluster_risk_score=target_ring.network_risk_score,
        shared_identifiers_count=len(target_ring.shared_entities),
    )
