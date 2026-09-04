"""Hybrid Risk Scoring Engine combining Behavioral ML and Network Graph Intelligence."""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from app.core.config import RiskLevel, ActionType, settings
from app.core.models import RiskScoreBreakdown, RiskFactorContribution
from app.data.store import DataStore, store
from app.ml.feature_extractor import MerchantFeatureExtractor
from app.ml.behavioral_model import BehavioralModelScorer, behavioral_scorer
from app.ml.network_detector import NetworkRiskDetector, network_detector, DetectedRing
from app.ml.explainer import RiskExplainer, risk_explainer


class HybridScoringEngine:
    """Combines behavioral ML probabilities with network entity graph risk into an explainable score."""

    def __init__(
        self,
        datastore: DataStore = store,
        scorer: BehavioralModelScorer = behavioral_scorer,
        net_detector: NetworkRiskDetector = network_detector,
        explainer: Optional[RiskExplainer] = None,
        behavioral_weight: float = 0.60,
        network_weight: float = 0.40,
        feature_extractor: Optional[MerchantFeatureExtractor] = None,
    ):
        self.ds = datastore
        self.feature_extractor = feature_extractor or MerchantFeatureExtractor(self.ds)
        self.scorer = scorer
        self.net_detector = net_detector
        self.explainer = explainer or RiskExplainer(self.ds)
        
        # Configurable hybrid weights (summing to 1.0)
        self.behavioral_weight = behavioral_weight
        self.network_weight = network_weight

        # Ensure model is trained if not already
        if not self.scorer.is_trained:
            self.scorer.fit_from_datastore(self.ds)

    @property
    def behavioral_scorer(self) -> BehavioralModelScorer:
        """Alias for self.scorer."""
        return self.scorer

    def calculate_fast_risk_score(self, merchant_id: str) -> float:
        """Calculates fast overall risk score (0-100) without generating SHAP factor explanations."""
        features = self.feature_extractor.extract_features_for_merchant(merchant_id)
        beh_prob, beh_score = self.scorer.predict_risk(features)
        net_features = self.net_detector.get_merchant_network_risk(merchant_id)
        net_score = net_features.get("network_risk_score", 5.0)

        raw_overall = (self.behavioral_weight * beh_score) + (self.network_weight * net_score)
        if beh_score >= 65.0 and net_score >= 75.0:
            raw_overall = max(raw_overall, 82.0 + (0.15 * (beh_score + net_score - 140.0)))
        return round(float(np.clip(raw_overall, 0.0, 100.0)), 1)

    def calculate_merchant_risk(self, merchant_id: str) -> RiskScoreBreakdown:
        """Calculates end-to-end hybrid risk score, tier, top factors, and bounded action."""
        merchant = self.ds.get_merchant(merchant_id)
        if not merchant:
            return RiskScoreBreakdown(
                merchant_id=merchant_id,
                behavioral_risk=0.0,
                network_risk=0.0,
                overall_risk=0.0,
                risk_level=RiskLevel.LOW,
                confidence=1.0,
                top_factors=[],
                recommended_action=ActionType.CONTINUE_MONITORING,
                action_rationale="Merchant not found in registry.",
                ring_id=None,
                connected_high_risk_count=0,
                calculated_at=datetime.now(timezone.utc),
            )

        # 1. Behavioral Features & ML Score
        features = self.feature_extractor.extract_features_for_merchant(merchant_id)
        beh_prob, beh_score = self.scorer.predict_risk(features)

        # 2. Network Features & Graph Score
        net_features = self.net_detector.get_merchant_network_risk(merchant_id)
        net_score = net_features.get("network_risk_score", 5.0)
        ring = self.net_detector.get_merchant_ring(merchant_id)

        # 3. Hybrid Combination Formula
        raw_overall = (self.behavioral_weight * beh_score) + (self.network_weight * net_score)

        # Multi-factor Co-occurrence Amplification:
        # If BOTH behavioral burst AND strong collusive ring connections exist simultaneously,
        # elevate the overall risk to reflect cross-domain certainty.
        if beh_score >= 65.0 and net_score >= 75.0:
            raw_overall = max(raw_overall, 82.0 + (0.15 * (beh_score + net_score - 140.0)))
        
        overall_score = float(np.clip(raw_overall, 0.0, 100.0))
        overall_score = round(overall_score, 1)

        # 4. Risk Level Tiering
        if overall_score >= 80.0:
            risk_level = RiskLevel.CRITICAL
            recommended_action = ActionType.URGENT_SETTLEMENT_FREEZE
            action_rationale = "High probability of active mule or coordinated ring syndicate. Immediate settlement hold and priority forensic audit required."
        elif overall_score >= 60.0:
            risk_level = RiskLevel.HIGH
            recommended_action = ActionType.SETTLEMENT_REVIEW
            action_rationale = "Elevated risk signals detected. Place 24h review hold on high-velocity settlement tranches and assign to risk analyst queue."
        elif overall_score >= 30.0:
            risk_level = RiskLevel.MEDIUM
            recommended_action = ActionType.ENHANCED_MONITORING
            action_rationale = "Moderate risk indicators observed. Enable dynamic buyer velocity limits and enhanced transaction telemetry."
        else:
            risk_level = RiskLevel.LOW
            recommended_action = ActionType.CONTINUE_MONITORING
            action_rationale = "Operations within standard baseline boundaries. Standard algorithmic surveillance active."

        # 5. Explanations & Evidence Breakdown
        top_factors = self.explainer.generate_risk_explanations(
            merchant_id=merchant_id,
            features=features,
            network_features=net_features,
            ring=ring,
            behavioral_score=beh_score,
            network_score=net_score,
        )

        # 6. Confidence metric calculation (based on data richness and signal alignment)
        txn_count = features.get("transaction_count", 0)
        data_richness = min(1.0, txn_count / 20.0)
        # Agreement between behavioral and network signals enhances confidence
        signal_agreement = 1.0 - (abs(beh_score - net_score) / 150.0)
        confidence = float(np.clip(0.60 + (0.25 * data_richness) + (0.15 * signal_agreement), 0.50, 0.99))

        connected_merchants_count = int(net_features.get("connected_merchant_count", 0))

        return RiskScoreBreakdown(
            merchant_id=merchant_id,
            behavioral_risk=beh_score,
            network_risk=net_score,
            overall_risk=overall_score,
            risk_level=risk_level,
            confidence=round(confidence, 2),
            top_factors=top_factors,
            recommended_action=recommended_action,
            action_rationale=action_rationale,
            ring_id=ring.ring_id if ring else None,
            connected_high_risk_count=connected_merchants_count,
            calculated_at=datetime.now(timezone.utc),
        )

    def calculate_all_merchants_risk(self) -> Dict[str, RiskScoreBreakdown]:
        """Calculates risk breakdowns for all merchants in datastore."""
        merchants = self.ds.get_all_merchants()
        return {m.id: self.calculate_merchant_risk(m.id) for m in merchants}


# Global scoring engine instance
scoring_engine = HybridScoringEngine()
