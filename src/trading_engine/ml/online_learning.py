"""
Online Learning Module for Incremental Model Updates.

Implements streaming/incremental learning to adapt to market changes
without full retraining. Uses sklearn's partial_fit for memory-efficient
updates on new data batches.
"""

import logging
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import PassiveAggressiveClassifier, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


class OnlineLearner:
    """
    Incremental learning with partial_fit for streaming updates.

    Supports:
    - SGDClassifier (fast, good for large datasets)
    - PassiveAggressiveClassifier (robust to outliers)
    - MultinomialNB (probabilistic, handles class imbalance)
    - Rolling window to prevent catastrophic forgetting
    """

    def __init__(
        self,
        model_type: str = "sgd",
        window_size: int = 5000,
        learning_rate: str = "optimal",
        random_state: int = 42,
    ):
        """
        Initialize online learner.

        Args:
            model_type: Type of incremental model ('sgd', 'passive_aggressive', 'naive_bayes')
            window_size: Max samples to keep in rolling window
            learning_rate: Learning rate schedule for SGD
            random_state: Random seed for reproducibility
        """
        self.model_type = model_type
        self.window_size = window_size
        self.learning_rate = learning_rate
        self.random_state = random_state

        self.model = self._create_model()
        self.scaler = MinMaxScaler()
        self.is_fitted = False
        self.classes_ = np.array([0, 1])  # Binary classification

        # Rolling window to prevent catastrophic forgetting
        self.X_buffer: List[np.ndarray] = []
        self.y_buffer: List[int] = []

        # Metrics tracking
        self.n_updates = 0
        self.total_samples = 0
        self.update_history: List[Dict[str, Any]] = []

        logger.info(
            f"OnlineLearner initialized: model={model_type}, window={window_size}"
        )

    def _create_model(self) -> Any:
        """Create incremental learning model based on type."""
        if self.model_type == "sgd":
            return SGDClassifier(
                loss="log_loss",  # For probability estimates
                learning_rate=self.learning_rate,
                random_state=self.random_state,
                warm_start=True,  # Keep previous state
                max_iter=1000,
                tol=1e-3,
            )
        elif self.model_type == "passive_aggressive":
            return PassiveAggressiveClassifier(
                C=1.0,
                random_state=self.random_state,
                warm_start=True,
                max_iter=1000,
            )
        elif self.model_type == "naive_bayes":
            return MultinomialNB(alpha=1.0)  # Laplace smoothing
        else:
            raise ValueError(
                f"Unknown model_type: {self.model_type}. "
                f"Choose from: sgd, passive_aggressive, naive_bayes"
            )

    def partial_fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        update_scaler: bool = False,
    ) -> Dict[str, Any]:
        """
        Incrementally update model with new data batch.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target labels (n_samples,)
            update_scaler: Whether to update scaler with new data

        Returns:
            Dict with update metrics
        """
        if len(X) == 0:
            logger.warning("Empty batch provided to partial_fit")
            return {"status": "skipped", "reason": "empty_batch"}

        # Scale features
        if not self.is_fitted or update_scaler:
            X_scaled = self.scaler.fit_transform(X)
            logger.info("Scaler fitted on new data")
        else:
            X_scaled = self.scaler.transform(X)

        # Handle non-negative features for MultinomialNB
        if self.model_type == "naive_bayes":
            X_scaled = np.abs(X_scaled)  # NB requires non-negative features

        # Incremental update
        start_time = datetime.now()

        if not self.is_fitted:
            # First fit
            self.model.partial_fit(X_scaled, y, classes=self.classes_)
            self.is_fitted = True
            logger.info(f"Model fitted with {len(X)} initial samples")
        else:
            # Incremental update
            self.model.partial_fit(X_scaled, y)

        # Update rolling window buffer
        self._update_buffer(X_scaled, y)

        # Track metrics
        elapsed = (datetime.now() - start_time).total_seconds()
        self.n_updates += 1
        self.total_samples += len(X)

        metrics = {
            "status": "success",
            "n_samples": len(X),
            "n_updates": self.n_updates,
            "total_samples": self.total_samples,
            "buffer_size": len(self.X_buffer),
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat(),
        }

        self.update_history.append(metrics)
        logger.info(
            f"Partial fit complete: {len(X)} samples in {elapsed:.3f}s "
            f"(total: {self.total_samples})"
        )

        return metrics

    def _update_buffer(self, X: np.ndarray, y: np.ndarray) -> None:
        """Update rolling window buffer with new samples."""
        self.X_buffer.extend(X)
        self.y_buffer.extend(y)

        # Maintain window size
        if len(self.X_buffer) > self.window_size:
            excess = len(self.X_buffer) - self.window_size
            self.X_buffer = self.X_buffer[excess:]
            self.y_buffer = self.y_buffer[excess:]
            logger.debug(f"Buffer trimmed to {self.window_size} samples")

    def replay_buffer(self) -> Dict[str, Any]:
        """
        Replay buffered samples to prevent catastrophic forgetting.

        Returns:
            Dict with replay metrics
        """
        if len(self.X_buffer) == 0:
            return {"status": "skipped", "reason": "empty_buffer"}

        X_replay = np.array(self.X_buffer)
        y_replay = np.array(self.y_buffer)

        logger.info(f"Replaying {len(X_replay)} buffered samples")
        return self.partial_fit(X_replay, y_replay, update_scaler=False)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet. Call partial_fit first.")

        X_scaled = self.scaler.transform(X)
        if self.model_type == "naive_bayes":
            X_scaled = np.abs(X_scaled)

        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet. Call partial_fit first.")

        X_scaled = self.scaler.transform(X)
        if self.model_type == "naive_bayes":
            X_scaled = np.abs(X_scaled)

        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X_scaled)
        elif hasattr(self.model, "decision_function"):
            # Convert decision function to probabilities
            decision = self.model.decision_function(X_scaled)
            proba = 1 / (1 + np.exp(-decision))  # Sigmoid
            return np.column_stack([1 - proba, proba])
        else:
            raise RuntimeError("Model does not support probability prediction")

    def save(self, filepath: str) -> None:
        """Save online learner to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "model": self.model,
            "scaler": self.scaler,
            "model_type": self.model_type,
            "window_size": self.window_size,
            "is_fitted": self.is_fitted,
            "n_updates": self.n_updates,
            "total_samples": self.total_samples,
            "X_buffer": (
                self.X_buffer[-1000:] if len(self.X_buffer) > 1000 else self.X_buffer
            ),
            "y_buffer": (
                self.y_buffer[-1000:] if len(self.y_buffer) > 1000 else self.y_buffer
            ),
            "update_history": self.update_history[-100:],  # Keep recent history
        }

        with open(filepath, "wb") as f:
            pickle.dump(state, f)

        logger.info(f"OnlineLearner saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "OnlineLearner":
        """Load online learner from disk."""
        with open(filepath, "rb") as f:
            state = pickle.load(f)

        learner = cls(model_type=state["model_type"], window_size=state["window_size"])
        learner.model = state["model"]
        learner.scaler = state["scaler"]
        learner.is_fitted = state["is_fitted"]
        learner.n_updates = state["n_updates"]
        learner.total_samples = state["total_samples"]
        learner.X_buffer = state["X_buffer"]
        learner.y_buffer = state["y_buffer"]
        learner.update_history = state["update_history"]

        logger.info(f"OnlineLearner loaded from {filepath}")
        return learner

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            "model_type": self.model_type,
            "is_fitted": self.is_fitted,
            "n_updates": self.n_updates,
            "total_samples": self.total_samples,
            "buffer_size": len(self.X_buffer),
            "window_size": self.window_size,
            "update_history_length": len(self.update_history),
        }


def create_online_ensemble(
    models: Optional[List[str]] = None,
    window_size: int = 5000,
) -> Dict[str, OnlineLearner]:
    """
    Create ensemble of online learners.

    Args:
        models: List of model types. Defaults to ['sgd', 'passive_aggressive']
        window_size: Rolling window size for each learner

    Returns:
        Dict mapping model names to OnlineLearner instances
    """
    if models is None:
        models = ["sgd", "passive_aggressive"]

    ensemble = {}
    for model_type in models:
        ensemble[model_type] = OnlineLearner(
            model_type=model_type, window_size=window_size
        )

    logger.info(f"Online ensemble created with {len(ensemble)} models: {models}")
    return ensemble


def ensemble_predict(
    ensemble: Dict[str, OnlineLearner],
    X: np.ndarray,
    method: str = "voting",
) -> np.ndarray:
    """
    Predict using ensemble of online learners.

    Args:
        ensemble: Dict of OnlineLearner instances
        X: Feature matrix
        method: Ensemble method ('voting' or 'average_proba')

    Returns:
        Ensemble predictions
    """
    if method == "voting":
        # Hard voting
        predictions = [learner.predict(X) for learner in ensemble.values()]
        predictions = np.array(predictions)
        # Majority vote
        return np.apply_along_axis(
            lambda x: np.argmax(np.bincount(x)), axis=0, arr=predictions
        )
    elif method == "average_proba":
        # Soft voting with probability averaging
        probas = [learner.predict_proba(X) for learner in ensemble.values()]
        avg_proba = np.mean(probas, axis=0)
        return np.argmax(avg_proba, axis=1)
    else:
        raise ValueError(f"Unknown method: {method}")
