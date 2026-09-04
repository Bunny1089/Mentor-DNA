"""Risk intelligence service providing unified interface for scoring, graph, and evidence."""

from typing import Dict, List, Any, Optional
from app.core.config import RiskLevel, ActionType
from app.core.models import RiskScoreBreakdown, SubgraphResponse
from app.data.store import DataStore, store
from app.ml.scoring_engine import HybridScoringEngine, scoring_engine
from app.ml.network_detector import NetworkRiskDetector, network_detector, DetectedRing
from app.ml.evaluator import ModelEvaluator, evaluator


class RiskIntelligenceService:
    """Coordinates risk scoring, network graph detection, and evidence retrieval."""

    def __init__(
        self,
        datastore: DataStore = store,
        scoring: HybridScoringEngine = scoring_engine,
        network: NetworkRiskDetector = network_detector,
        eval_engine: ModelEvaluator = evaluator,
    ):
        self.ds = datastore
        self.scoring = scoring
        self.network = network
        self.evaluator = eval_engine

    def get_merchant_risk(self, merchant_id: str) -> Dict[str, Any]:
        """Returns comprehensive merchant risk intelligence dossier."""
        breakdown = self.scoring.calculate_merchant_risk(merchant_id)
        net_info = self.network.get_merchant_network_risk(merchant_id)
        ring = self.network.get_merchant_ring(merchant_id)
        shared_info = self.ds.get_merchant_shared_identifiers(merchant_id)

        detected_rings_list = []
        if ring:
            detected_rings_list.append(
                {
                    "ring_id": ring.ring_id,
                    "ring_size": ring.ring_size,
                    "ring_density": ring.ring_density,
                    "dominant_shared_identifier": ring.dominant_shared_identifier,
                    "confidence": ring.confidence,
                    "member_merchants": ring.member_merchants,
                    "shared_entities": ring.shared_entities,
                }
            )

        return {
            "merchant_id": merchant_id,
            "behavioral_risk": breakdown.behavioral_risk,
            "network_risk": breakdown.network_risk,
            "overall_risk": breakdown.overall_risk,
            "risk_level": breakdown.risk_level.value,
            "confidence": breakdown.confidence,
            "recommended_action": breakdown.recommended_action.value,
            "action_rationale": breakdown.action_rationale,
            "ring_id": breakdown.ring_id,
            "connected_high_risk_count": breakdown.connected_high_risk_count,
            "calculated_at": breakdown.calculated_at.isoformat(),
            "top_risk_factors": [f.model_dump() for f in breakdown.top_factors],
            "network_summary": {
                **net_info,
                "shared_identifiers": shared_info,
            },
            "detected_rings": detected_rings_list,
        }

    def get_all_merchant_risks(self) -> List[Dict[str, Any]]:
        """Returns risk profiles for all merchants."""
        merchants = self.ds.get_all_merchants()
        results = []
        for m in merchants:
            breakdown = self.scoring.calculate_merchant_risk(m.id)
            txns = self.ds.get_merchant_transactions(m.id)
            total_vol = sum(t.amount for t in txns)
            results.append(
                {
                    "merchant_id": m.id,
                    "business_name": m.business_name,
                    "category": m.category.value,
                    "business_type": m.business_type,
                    "onboarding_date": m.onboarding_date.isoformat(),
                    "transaction_count": len(txns),
                    "total_volume": round(total_vol, 2),
                    "behavioral_risk": breakdown.behavioral_risk,
                    "network_risk": breakdown.network_risk,
                    "overall_risk": breakdown.overall_risk,
                    "risk_level": breakdown.risk_level.value,
                    "confidence": breakdown.confidence,
                    "recommended_action": breakdown.recommended_action.value,
                    "ring_id": breakdown.ring_id,
                    "top_factor": breakdown.top_factors[0].title if breakdown.top_factors else "Standard Baseline",
                }
            )
        # Sort by overall risk descending
        results.sort(key=lambda x: x["overall_risk"], reverse=True)
        return results

    def get_network_subgraph(self, merchant_id: str, max_hops: int = 2) -> SubgraphResponse:
        """Returns ego-subgraph representation for network exploration."""
        return self.network.get_subgraph_for_merchant(merchant_id, max_hops=max_hops)

    def get_all_detected_rings(self) -> List[Dict[str, Any]]:
        """Returns list of all detected collusive merchant rings."""
        rings = self.network.get_all_detected_rings()
        return [
            {
                "ring_id": r.ring_id,
                "ring_size": r.ring_size,
                "ring_density": r.ring_density,
                "dominant_shared_identifier": r.dominant_shared_identifier,
                "average_member_risk": r.average_member_risk,
                "network_risk_score": r.network_risk_score,
                "confidence": r.confidence,
                "member_merchants": r.member_merchants,
                "shared_entities": r.shared_entities,
                "metadata": r.metadata,
            }
            for r in rings
        ]

    def get_evaluation_metrics(self, threshold: float = 60.0) -> Dict[str, Any]:
        """Returns honest evaluation metrics and financial matrix."""
        return self.evaluator.evaluate_model_performance(threshold_score=threshold)


# Global service singleton instance
risk_service = RiskIntelligenceService()
