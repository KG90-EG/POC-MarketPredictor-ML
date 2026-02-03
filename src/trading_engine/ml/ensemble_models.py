"""
Ensemble Models for Trading Predictions.

This module implements ensemble learning techniques to combine multiple models
for improved prediction accuracy and robustness.

Features:
- Voting Classifier (XGBoost + RandomForest + GradientBoosting + LightGBM)
- Stacking Classifier with meta-learner
- Confidence calibration
- LSTM integration for time series patterns
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import (GradientBoostingClassifier,
                              RandomForestClassifier, StackingClassifier,
                              VotingClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)

# Try importing optional dependencies
try:
    from xgboost import XGBClassifier

    HAS_XGB = True
except Exception as e:
    XGBClassifier = None
    HAS_XGB = False
    logger.warning(f"XGBoost not available: {e}")

try:
    from lightgbm import LGBMClassifier

    HAS_LGBM = True
except ImportError:
    LGBMClassifier = None
    HAS_LGBM = False
    logger.warning("LightGBM not available - ensemble will use fewer models")

try:
    import torch
    import torch.nn as nn

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("PyTorch not available - LSTM model disabled")


# ============================================================================
# Base Models
# ============================================================================


def create_xgboost_model(**kwargs) -> Optional[object]:
    """Create XGBoost classifier with optimized parameters."""
    if not HAS_XGB:
        return None

    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.8,
        "eval_metric": "logloss",
        "use_label_encoder": False,
        "random_state": 42,
    }
    params.update(kwargs)

    return XGBClassifier(**params)


def create_random_forest_model(**kwargs) -> RandomForestClassifier:
    """Create Random Forest classifier with optimized parameters."""
    params = {
        "n_estimators": 200,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42,
        "n_jobs": -1,
    }
    params.update(kwargs)

    return RandomForestClassifier(**params)


def create_gradient_boosting_model(**kwargs) -> GradientBoostingClassifier:
    """Create Gradient Boosting classifier with optimized parameters."""
    params = {
        "n_estimators": 150,
        "max_depth": 3,
        "learning_rate": 0.1,
        "subsample": 0.9,
        "random_state": 42,
    }
    params.update(kwargs)

    return GradientBoostingClassifier(**params)


def create_lightgbm_model(**kwargs) -> Optional[object]:
    """Create LightGBM classifier with optimized parameters."""
    if not HAS_LGBM:
        return None

    params = {
        "n_estimators": 200,
        "max_depth": 4,
        "learning_rate": 0.05,
        "subsample": 0.9,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "verbose": -1,
    }
    params.update(kwargs)

    return LGBMClassifier(**params)


# ============================================================================
# Voting Ensemble
# ============================================================================


def create_voting_ensemble(
    voting: str = "soft", weights: Optional[List[float]] = None
) -> VotingClassifier:
    """
    Create a Voting Classifier ensemble.

    Args:
        voting: 'soft' (probability averaging) or 'hard' (majority vote)
        weights: List of weights for each model (default: [2, 1, 1, 1.5])

    Returns:
        VotingClassifier ensemble
    """
    estimators = []

    # Add XGBoost (strongest performer - highest weight)
    if HAS_XGB:
        estimators.append(("xgb", create_xgboost_model()))

    # Add Random Forest (robust baseline)
    estimators.append(("rf", create_random_forest_model()))

    # Add Gradient Boosting (alternative boosting)
    estimators.append(("gb", create_gradient_boosting_model()))

    # Add LightGBM (fast boosting)
    if HAS_LGBM:
        estimators.append(("lgbm", create_lightgbm_model()))

    # Default weights: XGBoost=2, RF=1, GB=1, LGBM=1.5
    if weights is None:
        if HAS_XGB and HAS_LGBM:
            weights = [2, 1, 1, 1.5]
        elif HAS_XGB:
            weights = [2, 1, 1]
        elif HAS_LGBM:
            weights = [1, 1, 1.5]
        else:
            weights = [1, 1]

    logger.info(f"Creating voting ensemble with {len(estimators)} models")
    logger.info(f"Models: {[name for name, _ in estimators]}")
    logger.info(f"Weights: {weights}")

    return VotingClassifier(estimators=estimators, voting=voting, weights=weights, n_jobs=-1)


# ============================================================================
# Stacking Ensemble
# ============================================================================


def create_stacking_ensemble(
    meta_learner: Optional[object] = None, cv: int = 5
) -> StackingClassifier:
    """
    Create a Stacking Classifier ensemble with meta-learner.

    Args:
        meta_learner: Meta-learner model (default: LogisticRegression)
        cv: Cross-validation folds for stacking (default: 5)

    Returns:
        StackingClassifier ensemble
    """
    estimators = []

    # Base models
    if HAS_XGB:
        estimators.append(("xgb", create_xgboost_model()))
    estimators.append(("rf", create_random_forest_model()))
    estimators.append(("gb", create_gradient_boosting_model()))
    if HAS_LGBM:
        estimators.append(("lgbm", create_lightgbm_model()))

    # Meta-learner (learns from base model predictions)
    if meta_learner is None:
        meta_learner = LogisticRegression(max_iter=1000, random_state=42)

    logger.info(f"Creating stacking ensemble with {len(estimators)} base models")
    logger.info(f"Meta-learner: {type(meta_learner).__name__}")

    return StackingClassifier(estimators=estimators, final_estimator=meta_learner, cv=cv, n_jobs=-1)


# ============================================================================
# Confidence Calibration
# ============================================================================


def calibrate_model(
    model: object, X: np.ndarray, y: np.ndarray, method: str = "isotonic", cv: int = 5
) -> CalibratedClassifierCV:
    """
    Calibrate model probabilities using cross-validation.

    Args:
        model: Trained classifier
        X: Feature matrix
        y: Target vector
        method: 'isotonic' or 'sigmoid'
        cv: Cross-validation folds

    Returns:
        Calibrated classifier
    """
    logger.info(f"Calibrating model with method={method}, cv={cv}")

    calibrated = CalibratedClassifierCV(model, method=method, cv=cv, n_jobs=-1)

    calibrated.fit(X, y)

    return calibrated


def get_prediction_confidence(
    model: object, X: np.ndarray, threshold: float = 0.65
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Get predictions with confidence scores.

    Args:
        model: Trained classifier with predict_proba
        X: Feature matrix
        threshold: Confidence threshold for high-confidence predictions

    Returns:
        Tuple of (predictions, probabilities, high_confidence_mask)
    """
    # Get probabilities
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[:, 1]
    else:
        # Fallback to decision function
        proba = model.decision_function(X)
        proba = (proba - proba.min()) / (proba.max() - proba.min())

    # Get predictions
    predictions = (proba >= 0.5).astype(int)

    # High confidence: probability far from 0.5
    confidence = np.abs(proba - 0.5) * 2  # Scale to [0, 1]
    high_confidence = confidence >= threshold

    logger.info(f"Predictions with {high_confidence.sum()}/{len(X)} high confidence")

    return predictions, proba, high_confidence


# ============================================================================
# LSTM Model (Optional)
# ============================================================================


if HAS_TORCH:

    class LSTMClassifier(nn.Module):
        """
        LSTM-based classifier for time series patterns.
        """

        def __init__(
            self,
            input_size: int,
            hidden_size: int = 64,
            num_layers: int = 2,
            dropout: float = 0.2,
        ):
            super(LSTMClassifier, self).__init__()

            self.hidden_size = hidden_size
            self.num_layers = num_layers

            self.lstm = nn.LSTM(
                input_size,
                hidden_size,
                num_layers,
                batch_first=True,
                dropout=dropout if num_layers > 1 else 0,
            )

            self.fc = nn.Linear(hidden_size, 1)
            self.sigmoid = nn.Sigmoid()

        def forward(self, x):
            # x shape: (batch, seq_len, features)
            lstm_out, _ = self.lstm(x)

            # Use last output
            last_output = lstm_out[:, -1, :]

            # Fully connected layer
            out = self.fc(last_output)
            out = self.sigmoid(out)

            return out

    class LSTMWrapper:
        """
        Scikit-learn compatible wrapper for LSTM classifier.
        """

        def __init__(
            self,
            input_size: int,
            hidden_size: int = 64,
            num_layers: int = 2,
            seq_length: int = 10,
            epochs: int = 50,
            batch_size: int = 32,
            lr: float = 0.001,
        ):
            self.input_size = input_size
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            self.seq_length = seq_length
            self.epochs = epochs
            self.batch_size = batch_size
            self.lr = lr

            self.model = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        def _prepare_sequences(self, X: np.ndarray) -> torch.Tensor:
            """Convert tabular data to sequences."""
            sequences = []
            for i in range(len(X) - self.seq_length + 1):
                seq = X[i : i + self.seq_length]
                sequences.append(seq)

            return torch.FloatTensor(np.array(sequences)).to(self.device)

        def fit(self, X: np.ndarray, y: np.ndarray):
            """Train LSTM model."""
            self.model = LSTMClassifier(self.input_size, self.hidden_size, self.num_layers).to(
                self.device
            )

            # Prepare data
            X_seq = self._prepare_sequences(X)
            y_seq = torch.FloatTensor(y[self.seq_length - 1 :]).to(self.device)

            # Training setup
            criterion = nn.BCELoss()
            optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

            # Training loop
            self.model.train()
            for epoch in range(self.epochs):
                total_loss = 0

                for i in range(0, len(X_seq), self.batch_size):
                    batch_X = X_seq[i : i + self.batch_size]
                    batch_y = y_seq[i : i + self.batch_size].unsqueeze(1)

                    optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()

                if (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch + 1}/{self.epochs}, Loss: {total_loss:.4f}")

            return self

        def predict_proba(self, X: np.ndarray) -> np.ndarray:
            """Predict probabilities."""
            self.model.eval()

            X_seq = self._prepare_sequences(X)

            with torch.no_grad():
                outputs = self.model(X_seq).cpu().numpy()

            # Pad to match original length
            proba = np.zeros((len(X), 2))
            proba[self.seq_length - 1 :, 1] = outputs.flatten()
            proba[:, 0] = 1 - proba[:, 1]

            return proba

        def predict(self, X: np.ndarray) -> np.ndarray:
            """Predict class labels."""
            proba = self.predict_proba(X)
            return (proba[:, 1] >= 0.5).astype(int)


# ============================================================================
# Ensemble Factory
# ============================================================================


def create_ensemble(ensemble_type: str = "voting", **kwargs) -> object:
    """
    Factory function to create ensemble models.

    Args:
        ensemble_type: 'voting', 'stacking', or 'voting_calibrated'
        **kwargs: Additional arguments for ensemble creation

    Returns:
        Ensemble model
    """
    if ensemble_type == "voting":
        return create_voting_ensemble(**kwargs)

    elif ensemble_type == "stacking":
        return create_stacking_ensemble(**kwargs)

    elif ensemble_type == "voting_calibrated":
        # Create voting ensemble first, then calibrate
        voting = create_voting_ensemble(**kwargs)
        logger.info("Note: Calibration will be applied during training")
        return voting

    else:
        raise ValueError(f"Unknown ensemble type: {ensemble_type}")


def evaluate_ensemble(model: object, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict[str, float]:
    """
    Evaluate ensemble model performance.

    Args:
        model: Ensemble model
        X: Feature matrix
        y: Target vector
        cv: Cross-validation folds

    Returns:
        Dictionary of performance metrics
    """
    from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                                 recall_score, roc_auc_score)
    from sklearn.model_selection import train_test_split

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Train model
    logger.info("Training ensemble model...")
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    # Metrics
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
    }

    if y_proba is not None:
        metrics["roc_auc"] = roc_auc_score(y_test, y_proba)

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring="f1", n_jobs=-1)
    metrics["cv_mean"] = cv_scores.mean()
    metrics["cv_std"] = cv_scores.std()

    logger.info("Ensemble Evaluation Results:")
    for metric, value in metrics.items():
        logger.info(f"  {metric}: {value:.4f}")

    return metrics


def get_feature_importances(ensemble: object, feature_names: List[str]) -> pd.DataFrame:
    """
    Get aggregated feature importances from ensemble.

    Args:
        ensemble: Trained ensemble model
        feature_names: List of feature names

    Returns:
        DataFrame with feature importances
    """
    importances = []

    # Extract importances from each estimator
    if isinstance(ensemble, VotingClassifier):
        estimators = ensemble.estimators_
    elif isinstance(ensemble, StackingClassifier):
        estimators = ensemble.estimators_
    else:
        estimators = [ensemble]

    for estimator in estimators:
        if hasattr(estimator, "feature_importances_"):
            importances.append(estimator.feature_importances_)

    if not importances:
        logger.warning("No feature importances available")
        return pd.DataFrame()

    # Average importances
    avg_importance = np.mean(importances, axis=0)

    # Create DataFrame
    df_importance = pd.DataFrame(
        {"feature": feature_names, "importance": avg_importance}
    ).sort_values("importance", ascending=False)

    return df_importance
