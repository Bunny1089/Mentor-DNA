"""System Status & Health Check endpoints."""

from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings
from app.data.store import store
from app.ml.behavioral_model import behavioral_scorer
from app.ml.network_detector import network_detector

router = APIRouter(tags=["System"])


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Basic service health check."""
    return {
        "status": "ok",
        "service": "merchant-dna",
        "version": settings.VERSION,
    }


@router.get("/api/system/status")
def system_status() -> Dict[str, Any]:
    """Detailed telemetry and runtime graph/model status for operations dashboard."""
    merchants = store.get_all_merchants()
    txns = store.transactions
    rings = network_detector.get_all_detected_rings()
    graph = network_detector.graph

    return {
        "backend_status": "ONLINE",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "data_loaded": len(merchants) > 0,
        "merchant_count": len(merchants),
        "transaction_count": len(txns),
        "graph_nodes_count": graph.number_of_nodes(),
        "graph_edges_count": graph.number_of_edges(),
        "detected_rings_count": len(rings),
        "behavioral_model_loaded": behavioral_scorer.is_trained,
        "server_time": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/api/system/reset")
def system_reset() -> Dict[str, Any]:
    """Resets entire in-memory database to initial state."""
    from app.services.simulation_service import simulation_service
    return simulation_service.reset_demo_state()

