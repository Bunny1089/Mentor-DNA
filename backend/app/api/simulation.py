"""Live Risk Scenario Simulation API endpoints for demos."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Body
from pydantic import BaseModel

from app.services.simulation_service import simulation_service

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class MuleSimulationRequest(BaseModel):
    merchant_id: Optional[str] = None
    seed: int = 42


class RingSimulationRequest(BaseModel):
    seed: int = 42


@router.post("/mule", response_model=Dict[str, Any])
def trigger_mule_simulation(
    request: MuleSimulationRequest = Body(default_factory=MuleSimulationRequest),
) -> Dict[str, Any]:
    """Simulates real-time dormant-to-burst mule behavior on a merchant."""
    result = simulation_service.simulate_mule_spike(
        merchant_id=request.merchant_id,
        seed=request.seed,
    )
    return result


@router.post("/ring", response_model=Dict[str, Any])
def trigger_ring_simulation(
    request: RingSimulationRequest = Body(default_factory=RingSimulationRequest),
) -> Dict[str, Any]:
    """Simulates real-time emergence of a new cross-merchant coordinated fraud syndicate."""
    result = simulation_service.simulate_ring_emergence(seed=request.seed)
    return result


@router.post("/reset", response_model=Dict[str, Any])
def reset_simulation_state() -> Dict[str, Any]:
    """Resets the in-memory prototype database and network topology back to clean deterministic baseline."""
    return simulation_service.reset_demo_state()

