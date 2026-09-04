"""Behavioral ML Risk Scoring Model for Merchant DNA."""

import warnings
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance

from app.core.config import settings
from app.core.models import TrueLabel
from app.data.store import DataStore
from app.ml.feature_extractor import MerchantFeatureExtractor


class BehavioralModelScorer:
    """Supervised gradient boosted model predicting merchant behavioral risk scores (0-100)."""

    def __init__(self, seed: int = settings.RANDOM_SEED):
        self.seed = seed
        self.model = HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.08,
            max_depth=6,
            min_samples_leaf=5,
            random_state=seed,
        )
        self.is_trained = False
        self.feature_names: List[str] = []
        self.feature_importances_: Dict[str, float] = {}
        self.train_score: float = 0.0
        self.val_score: float = 0.0

    def fit_from_datastore(
        self,
        datastore: DataStore,
        merchant_ids: Optional[List[str]] = None,
        compute_importances: bool = True,
    ) -> Dict[str, Any]:
        """Trains the behavioral model using features and isolated ground truth."""
        extractor = MerchantFeatureExtractor(datastore)
        X_df, all_mids = extractor.extract_feature_matrix()
        
        if merchant_ids is not None:
            m_set = set(merchant_ids)
            mask = [mid in m_set for mid in all_mids]
            X_df = X_df[mask].reset_index(drop=True)
            all_mids = [mid for mid in all_mids if mid in m_set]

        self.feature_names = list(X_df.columns)

        # Ground truth binary label: 1 if MULE_SHELL or RING_MEMBER else 0
        gts = datastore.get_all_ground_truths()
        y_list = [1 if gts[m_id].true_label != TrueLabel.LEGITIMATE else 0 for m_id in all_mids]
        y = np.array(y_list)

        # Stratified train/test split with fixed seed for honest validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_df, y, test_size=0.25, random_state=self.seed, stratify=y
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        self.train_score = float(self.model.score(X_train, y_train))
        self.val_score = float(self.model.score(X_val, y_val))

        if compute_importances:
            # Compute permutation feature importances
            perm_importance = permutation_importance(
                self.model, X_val, y_val, n_repeats=5, random_state=self.seed
            )
            importances = perm_importance.importances_mean
            total_imp = np.sum(np.maximum(0, importances))
            if total_imp > 0:
                norm_imp = np.maximum(0, importances) / total_imp
            else:
                norm_imp = np.ones(len(self.feature_names)) / len(self.feature_names)

            self.feature_importances_ = {
                feat: float(norm_imp[i]) for i, feat in enumerate(self.feature_names)
            }
        else:
            self.feature_importances_ = {feat: 1.0 / len(self.feature_names) for feat in self.feature_names}

        return {
            "train_accuracy": self.train_score,
            "val_accuracy": self.val_score,
            "top_features": sorted(
                self.feature_importances_.items(), key=lambda x: x[1], reverse=True
            )[:10],
        }

    def predict_risk(self, features: Dict[str, float]) -> Tuple[float, float]:
        """Predicts risk probability and calibrated behavioral risk score (0-100)."""
        if not self.is_trained:
            heuristic_prob = self._heuristic_fallback(features)
            return heuristic_prob, round(heuristic_prob * 100.0, 1)

        vec = np.array([[features.get(f, 0.0) for f in self.feature_names]], dtype=np.float64)
        # Predict class 1 (suspicious) probability
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            prob = float(self.model.predict_proba(vec)[0, 1])

        # Non-linear calibration for fine-grained risk separation in tails
        score = float(np.clip(prob * 100.0, 0.0, 100.0))
        return prob, round(score, 1)

    def _heuristic_fallback(self, features: Dict[str, float]) -> float:
        """Deterministic rule-based baseline fallback."""
        score = 0.1
        if features.get("volume_growth_48h", 0) > 3.0:
            score += 0.3
        if features.get("round_transaction_ratio", 0) > 0.6:
            score += 0.25
        if features.get("buyer_hhi", 0) > 0.3:
            score += 0.25
        if features.get("category_mismatch_score", 0) > 2.0:
            score += 0.2
        return float(min(1.0, score))


# Global behavioral scorer singleton instance
behavioral_scorer = BehavioralModelScorer()
