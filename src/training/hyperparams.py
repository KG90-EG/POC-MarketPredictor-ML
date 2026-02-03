"""
Hyperparameter Search Space Configuration (FR-004 Phase 4).

Defines search spaces for different model types used in Optuna optimization.
"""

from typing import Any

# XGBoost search space
XGBOOST_SEARCH_SPACE = {
    "n_estimators": {
        "type": "int",
        "low": 50,
        "high": 300,
        "step": 25,
    },
    "max_depth": {
        "type": "int",
        "low": 3,
        "high": 12,
    },
    "learning_rate": {
        "type": "float",
        "low": 0.01,
        "high": 0.3,
        "log": True,
    },
    "min_child_weight": {
        "type": "int",
        "low": 1,
        "high": 10,
    },
    "subsample": {
        "type": "float",
        "low": 0.6,
        "high": 1.0,
    },
    "colsample_bytree": {
        "type": "float",
        "low": 0.6,
        "high": 1.0,
    },
    "gamma": {
        "type": "float",
        "low": 0.0,
        "high": 0.5,
    },
    "reg_alpha": {
        "type": "float",
        "low": 0.0,
        "high": 1.0,
    },
    "reg_lambda": {
        "type": "float",
        "low": 0.0,
        "high": 2.0,
    },
}

# Random Forest search space
RANDOM_FOREST_SEARCH_SPACE = {
    "n_estimators": {
        "type": "int",
        "low": 50,
        "high": 500,
        "step": 50,
    },
    "max_depth": {
        "type": "int",
        "low": 3,
        "high": 20,
    },
    "min_samples_split": {
        "type": "int",
        "low": 2,
        "high": 20,
    },
    "min_samples_leaf": {
        "type": "int",
        "low": 1,
        "high": 10,
    },
    "max_features": {
        "type": "categorical",
        "choices": ["sqrt", "log2", None],
    },
    "bootstrap": {
        "type": "categorical",
        "choices": [True, False],
    },
    "class_weight": {
        "type": "categorical",
        "choices": ["balanced", "balanced_subsample", None],
    },
}

# LightGBM search space
LIGHTGBM_SEARCH_SPACE = {
    "n_estimators": {
        "type": "int",
        "low": 50,
        "high": 300,
        "step": 25,
    },
    "max_depth": {
        "type": "int",
        "low": 3,
        "high": 12,
    },
    "learning_rate": {
        "type": "float",
        "low": 0.01,
        "high": 0.3,
        "log": True,
    },
    "num_leaves": {
        "type": "int",
        "low": 20,
        "high": 150,
    },
    "min_child_samples": {
        "type": "int",
        "low": 5,
        "high": 100,
    },
    "subsample": {
        "type": "float",
        "low": 0.6,
        "high": 1.0,
    },
    "colsample_bytree": {
        "type": "float",
        "low": 0.6,
        "high": 1.0,
    },
    "reg_alpha": {
        "type": "float",
        "low": 0.0,
        "high": 1.0,
    },
    "reg_lambda": {
        "type": "float",
        "low": 0.0,
        "high": 2.0,
    },
}


def get_search_space(model_type: str) -> dict[str, Any]:
    """
    Get search space for a model type.

    Args:
        model_type: One of 'xgb', 'rf', 'lgb'

    Returns:
        Search space dictionary
    """
    spaces = {
        "xgb": XGBOOST_SEARCH_SPACE,
        "rf": RANDOM_FOREST_SEARCH_SPACE,
        "lgb": LIGHTGBM_SEARCH_SPACE,
    }
    return spaces.get(model_type, XGBOOST_SEARCH_SPACE)


def sample_params(trial, search_space: dict[str, Any]) -> dict[str, Any]:
    """
    Sample hyperparameters using Optuna trial.

    Args:
        trial: Optuna trial object
        search_space: Search space configuration

    Returns:
        Sampled hyperparameters
    """
    params = {}

    for name, config in search_space.items():
        param_type = config["type"]

        if param_type == "int":
            params[name] = trial.suggest_int(
                name, config["low"], config["high"], step=config.get("step", 1)
            )
        elif param_type == "float":
            params[name] = trial.suggest_float(
                name, config["low"], config["high"], log=config.get("log", False)
            )
        elif param_type == "categorical":
            params[name] = trial.suggest_categorical(name, config["choices"])

    return params


# Default hyperparameters for quick training
DEFAULT_HYPERPARAMS = {
    "xgb": {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "min_child_weight": 1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "gamma": 0.0,
        "reg_alpha": 0.0,
        "reg_lambda": 1.0,
        "use_label_encoder": False,
        "eval_metric": "logloss",
    },
    "rf": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "max_features": "sqrt",
        "bootstrap": True,
        "class_weight": "balanced",
        "n_jobs": -1,
    },
    "lgb": {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "num_leaves": 31,
        "min_child_samples": 20,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.0,
        "reg_lambda": 1.0,
        "verbosity": -1,
    },
}


def get_default_params(model_type: str) -> dict[str, Any]:
    """
    Get default hyperparameters for a model type.

    Args:
        model_type: One of 'xgb', 'rf', 'lgb'

    Returns:
        Default hyperparameters
    """
    return DEFAULT_HYPERPARAMS.get(model_type, DEFAULT_HYPERPARAMS["xgb"]).copy()


# Optuna optimization settings
OPTIMIZATION_CONFIG = {
    "n_trials": 50,  # Default number of trials
    "timeout": 3600,  # Default timeout in seconds (1 hour)
    "n_jobs": 1,  # Parallel jobs (1 for stability)
    "sampler": "TPE",  # Tree-structured Parzen Estimator
    "pruner": "MedianPruner",  # Prune unpromising trials
    "direction": "maximize",  # Maximize accuracy
    "metric": "accuracy",  # Optimization metric
    "cv_folds": 5,  # Cross-validation folds
}
