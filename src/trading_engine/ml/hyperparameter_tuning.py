"""
Hyperparameter Tuning with Optuna for Trading Models.

Week 4 Implementation - Bayesian Optimization for all ensemble models.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)


class HyperparameterTuner:
    """
    Bayesian hyperparameter optimization using Optuna.

    Optimizes parameters for:
    - XGBoost
    - RandomForest
    - GradientBoosting
    - LightGBM
    - Voting Ensemble (weights)
    - Stacking Ensemble (meta-learner)
    """

    def __init__(
        self,
        n_trials: int = 100,
        timeout: Optional[int] = None,
        n_jobs: int = -1,
        cv_folds: int = 5,
        random_state: int = 42,
    ):
        """
        Initialize hyperparameter tuner.

        Args:
            n_trials: Number of optimization trials
            timeout: Max time in seconds (None = no limit)
            n_jobs: Parallel jobs (-1 = all CPUs)
            cv_folds: Cross-validation folds
            random_state: Random seed for reproducibility
        """
        self.n_trials = n_trials
        self.timeout = timeout
        self.n_jobs = n_jobs
        self.cv_folds = cv_folds
        self.random_state = random_state

        # Best parameters found
        self.best_params: Dict[str, Dict[str, Any]] = {}

        # Optuna study objects
        self.studies: Dict[str, optuna.Study] = {}

    def _objective_xgboost(self, trial: optuna.Trial, X, y) -> float:
        """Optimization objective for XGBoost."""
        from xgboost import XGBClassifier

        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "gamma": trial.suggest_float("gamma", 0, 5),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
            "random_state": self.random_state,
            "n_jobs": 1,  # Optuna handles parallelization
            "eval_metric": "logloss",
        }

        model = XGBClassifier(**params)
        scorer = make_scorer(f1_score, average="weighted")

        try:
            scores = cross_val_score(model, X, y, cv=self.cv_folds, scoring=scorer, n_jobs=1)
            return np.mean(scores)
        except Exception as e:
            logger.warning(f"XGBoost trial failed: {e}")
            return 0.0

    def _objective_random_forest(self, trial: optuna.Trial, X, y) -> float:
        """Optimization objective for RandomForest."""
        from sklearn.ensemble import RandomForestClassifier

        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 20),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
            "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
            "random_state": self.random_state,
            "n_jobs": 1,
        }

        model = RandomForestClassifier(**params)
        scorer = make_scorer(f1_score, average="weighted")

        try:
            scores = cross_val_score(model, X, y, cv=self.cv_folds, scoring=scorer, n_jobs=1)
            return np.mean(scores)
        except Exception as e:
            logger.warning(f"RandomForest trial failed: {e}")
            return 0.0

    def _objective_gradient_boosting(self, trial: optuna.Trial, X, y) -> float:
        """Optimization objective for GradientBoosting."""
        from sklearn.ensemble import GradientBoostingClassifier

        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
            "random_state": self.random_state,
        }

        model = GradientBoostingClassifier(**params)
        scorer = make_scorer(f1_score, average="weighted")

        try:
            scores = cross_val_score(model, X, y, cv=self.cv_folds, scoring=scorer, n_jobs=1)
            return np.mean(scores)
        except Exception as e:
            logger.warning(f"GradientBoosting trial failed: {e}")
            return 0.0

    def _objective_lightgbm(self, trial: optuna.Trial, X, y) -> float:
        """Optimization objective for LightGBM."""
        try:
            from lightgbm import LGBMClassifier
        except ImportError:
            logger.warning("LightGBM not available, skipping optimization")
            return 0.0

        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 20, 150),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 100),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
            "random_state": self.random_state,
            "n_jobs": 1,
            "verbosity": -1,
        }

        model = LGBMClassifier(**params)
        scorer = make_scorer(f1_score, average="weighted")

        try:
            scores = cross_val_score(model, X, y, cv=self.cv_folds, scoring=scorer, n_jobs=1)
            return np.mean(scores)
        except Exception as e:
            logger.warning(f"LightGBM trial failed: {e}")
            return 0.0

    def optimize_model(
        self,
        model_type: str,
        X,
        y,
        n_trials: Optional[int] = None,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Optimize hyperparameters for a specific model.

        Args:
            model_type: 'xgboost', 'random_forest', 'gradient_boosting', 'lightgbm'
            X: Training features
            y: Training labels
            n_trials: Override default n_trials
            show_progress: Show Optuna progress bar

        Returns:
            Best parameters found
        """
        trials = n_trials if n_trials is not None else self.n_trials

        # Map model type to objective function
        objectives = {
            "xgboost": self._objective_xgboost,
            "random_forest": self._objective_random_forest,
            "gradient_boosting": self._objective_gradient_boosting,
            "lightgbm": self._objective_lightgbm,
        }

        if model_type not in objectives:
            raise ValueError(
                f"Unknown model_type: {model_type}. " f"Choose from: {list(objectives.keys())}"
            )

        logger.info(f"Starting hyperparameter optimization for {model_type}")
        logger.info(f"Trials: {trials}, CV Folds: {self.cv_folds}")

        # Create Optuna study
        study = optuna.create_study(
            direction="maximize",
            sampler=TPESampler(seed=self.random_state),
            pruner=MedianPruner(n_startup_trials=10, n_warmup_steps=5),
        )

        # Optimize
        def objective_fn(trial):
            return objectives[model_type](trial, X, y)

        study.optimize(
            objective_fn,
            n_trials=trials,
            timeout=self.timeout,
            n_jobs=self.n_jobs,
            show_progress_bar=show_progress,
        )

        # Store results
        self.studies[model_type] = study
        self.best_params[model_type] = study.best_params

        logger.info(f"✅ {model_type} optimization complete. " f"Best F1: {study.best_value:.4f}")
        logger.info(f"Best params: {study.best_params}")

        return study.best_params

    def optimize_all_models(
        self, X, y, models: Optional[List[str]] = None, show_progress: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Optimize all models in sequence.

        Args:
            X: Training features
            y: Training labels
            models: List of models to optimize (None = all)
            show_progress: Show progress bars

        Returns:
            Dictionary of best parameters for each model
        """
        if models is None:
            models = ["xgboost", "random_forest", "gradient_boosting", "lightgbm"]

        logger.info(f"Optimizing {len(models)} models: {models}")

        results = {}
        for model_type in models:
            try:
                params = self.optimize_model(model_type, X, y, show_progress=show_progress)
                results[model_type] = params
            except Exception as e:
                logger.error(f"Failed to optimize {model_type}: {e}")
                results[model_type] = {}

        logger.info("✅ All models optimized")
        return results

    def get_optimization_report(self, model_type: str) -> Dict[str, Any]:
        """
        Get detailed optimization report for a model.

        Args:
            model_type: Model to report on

        Returns:
            Report with best params, trials, convergence info
        """
        if model_type not in self.studies:
            raise ValueError(f"No study found for {model_type}")

        study = self.studies[model_type]

        report = {
            "model_type": model_type,
            "best_params": study.best_params,
            "best_value": study.best_value,
            "n_trials": len(study.trials),
            "best_trial_number": study.best_trial.number,
            "optimization_history": [
                {"trial": i, "value": trial.value} for i, trial in enumerate(study.trials)
            ],
            "param_importances": None,
        }

        # Calculate parameter importances (if enough trials)
        if len(study.trials) >= 10:
            try:
                importances = optuna.importance.get_param_importances(study)
                report["param_importances"] = importances
            except Exception as e:
                logger.warning(f"Could not calculate param importances: {e}")

        return report

    def save_best_params(self, filepath: str) -> None:
        """
        Save best parameters to JSON file.

        Args:
            filepath: Path to save JSON file
        """
        import json

        with open(filepath, "w") as f:
            json.dump(self.best_params, f, indent=2)

        logger.info(f"✅ Best parameters saved to {filepath}")

    def load_best_params(self, filepath: str) -> Dict[str, Dict[str, Any]]:
        """
        Load best parameters from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Loaded parameters
        """
        import json

        with open(filepath, "r") as f:
            self.best_params = json.load(f)

        logger.info(f"✅ Best parameters loaded from {filepath}")
        return self.best_params


def optimize_ensemble_weights(
    models: List[Any],
    model_names: List[str],
    X,
    y,
    n_trials: int = 50,
    cv_folds: int = 5,
) -> Tuple[List[float], float]:
    """
    Optimize voting ensemble weights using Optuna.

    Args:
        models: List of trained models
        model_names: Names of models
        X: Training features
        y: Training labels
        n_trials: Number of trials
        cv_folds: Cross-validation folds

    Returns:
        (best_weights, best_f1_score)
    """
    from sklearn.ensemble import VotingClassifier
    from sklearn.model_selection import cross_val_score

    logger.info(f"Optimizing ensemble weights for {len(models)} models")

    def objective(trial: optuna.Trial) -> float:
        # Suggest weights (sum to 1.0)
        weights = [trial.suggest_float(f"weight_{name}", 0.1, 3.0) for name in model_names]

        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]

        # Create weighted voting ensemble
        estimators = list(zip(model_names, models))
        ensemble = VotingClassifier(estimators=estimators, voting="soft", weights=weights)

        # Evaluate
        scorer = make_scorer(f1_score, average="weighted")
        scores = cross_val_score(ensemble, X, y, cv=cv_folds, scoring=scorer, n_jobs=1)

        return np.mean(scores)

    # Optimize
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

    # Extract best weights
    best_weights = [study.best_params[f"weight_{name}"] for name in model_names]

    # Normalize
    total = sum(best_weights)
    best_weights = [w / total for w in best_weights]

    logger.info(f"✅ Best weights: {dict(zip(model_names, best_weights))}")
    logger.info(f"✅ Best F1 score: {study.best_value:.4f}")

    return best_weights, study.best_value
