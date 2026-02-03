#!/usr/bin/env python3
"""
Hyperparameter Optimization Script (FR-004 Phase 4).

Uses Optuna for Bayesian optimization of ML model hyperparameters.

Features:
    - Bayesian optimization with TPE sampler
    - Cross-validation for robust evaluation
    - Early stopping with pruning
    - MLflow integration for tracking
    - Best parameters saved to JSON

Usage:
    # Run optimization with defaults
    python scripts/optimize_hyperparams.py

    # Specify number of trials
    python scripts/optimize_hyperparams.py --trials 100

    # Different model type
    python scripts/optimize_hyperparams.py --model-type rf --trials 50

    # With timeout
    python scripts/optimize_hyperparams.py --trials 100 --timeout 3600

Exit Codes:
    0: Success
    1: Optimization failed
    2: Data error
    3: Configuration error
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import mlflow  # noqa: E402
import optuna  # noqa: E402
from sklearn.model_selection import cross_val_score  # noqa: E402

from src.training.hyperparams import (  # noqa: E402
    OPTIMIZATION_CONFIG,
    get_search_space,
    sample_params,
)

# Exit codes
EXIT_SUCCESS = 0
EXIT_OPTIMIZATION_FAILED = 1
EXIT_DATA_ERROR = 2
EXIT_CONFIG_ERROR = 3

# Stock universe for optimization (subset for speed)
OPTIMIZATION_TICKERS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "JPM",
    "BAC",
    "GS",
    "NESN.SW",
    "NOVN.SW",
    "ROG.SW",
    "UBSG.SW",
]


def create_model(model_type: str, params: dict):
    """Create model with given parameters."""
    if model_type == "xgb":
        from xgboost import XGBClassifier

        return XGBClassifier(**params)
    elif model_type == "rf":
        from sklearn.ensemble import RandomForestClassifier

        return RandomForestClassifier(**params)
    elif model_type == "lgb":
        from lightgbm import LGBMClassifier

        return LGBMClassifier(**params)
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def objective(trial, X, y, model_type: str, cv_folds: int = 5) -> float:
    """
    Optuna objective function.

    Args:
        trial: Optuna trial
        X: Feature matrix
        y: Target vector
        model_type: Model type
        cv_folds: Number of CV folds

    Returns:
        Mean cross-validation accuracy
    """
    # Sample hyperparameters
    search_space = get_search_space(model_type)
    params = sample_params(trial, search_space)

    # Add fixed parameters based on model type
    if model_type == "xgb":
        params["use_label_encoder"] = False
        params["eval_metric"] = "logloss"
        params["verbosity"] = 0
    elif model_type == "lgb":
        params["verbosity"] = -1

    # Create model
    try:
        model = create_model(model_type, params)
    except Exception as e:
        raise optuna.TrialPruned(f"Model creation failed: {e}")

    # Cross-validation
    try:
        scores = cross_val_score(model, X, y, cv=cv_folds, scoring="accuracy", n_jobs=-1)
        mean_score = scores.mean()

        # Report intermediate value for pruning
        trial.report(mean_score, 0)

        if trial.should_prune():
            raise optuna.TrialPruned()

        return mean_score

    except Exception as e:
        if isinstance(e, optuna.TrialPruned):
            raise
        raise optuna.TrialPruned(f"CV failed: {e}")


def run_optimization(
    X, y, model_type: str, n_trials: int, timeout: int | None = None, study_name: str | None = None
) -> tuple[dict, optuna.Study]:
    """
    Run hyperparameter optimization.

    Args:
        X: Feature matrix
        y: Target vector
        model_type: Model type
        n_trials: Number of trials
        timeout: Timeout in seconds
        study_name: Optional study name

    Returns:
        Tuple of (best_params, study)
    """
    # Create study with TPE sampler and median pruner
    sampler = optuna.samplers.TPESampler(seed=42)
    pruner = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=0)

    study = optuna.create_study(
        study_name=study_name or f"{model_type}_optimization",
        direction="maximize",
        sampler=sampler,
        pruner=pruner,
    )

    # Run optimization
    cv_folds = OPTIMIZATION_CONFIG["cv_folds"]

    study.optimize(
        lambda trial: objective(trial, X, y, model_type, cv_folds),
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=True,
        n_jobs=1,  # Sequential for stability
    )

    return study.best_params, study


def save_best_params(params: dict, metrics: dict, model_type: str, output_path: Path) -> None:
    """Save best parameters to JSON file."""
    result = {
        "model_type": model_type,
        "best_params": params,
        "optimization_metrics": metrics,
        "optimized_at": datetime.utcnow().isoformat(),
        "config": OPTIMIZATION_CONFIG,
    }

    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"✓ Best parameters saved to: {output_path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Optimize hyperparameters with Optuna",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --trials 50
    %(prog)s --model-type rf --trials 100
    %(prog)s --trials 200 --timeout 7200
        """,
    )

    parser.add_argument(
        "--model-type",
        type=str,
        default="xgb",
        choices=["xgb", "rf", "lgb"],
        help="Model type to optimize (default: xgb)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=OPTIMIZATION_CONFIG["n_trials"],
        help=f"Number of optimization trials (default: {OPTIMIZATION_CONFIG['n_trials']})",
    )
    parser.add_argument(
        "--timeout", type=int, default=None, help="Timeout in seconds (default: no timeout)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="3y",
        choices=["1y", "2y", "3y", "5y"],
        help="Historical data period (default: 3y)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="best_hyperparameters.json",
        help="Output file for best parameters",
    )
    parser.add_argument("--mlflow", action="store_true", help="Enable MLflow tracking")
    parser.add_argument("--study-name", type=str, help="Optuna study name")

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    print("\n" + "=" * 60)
    print("HYPERPARAMETER OPTIMIZATION")
    print("=" * 60)
    print(f"Model Type: {args.model_type}")
    print(f"Trials: {args.trials}")
    print(f"Timeout: {args.timeout or 'None'}")
    print(f"Data Period: {args.period}")

    # Suppress Optuna logs except warnings
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    # Build dataset
    print(f"\nBuilding dataset for {len(OPTIMIZATION_TICKERS)} tickers...")
    try:
        from src.trading_engine.trading import build_dataset

        data = build_dataset(OPTIMIZATION_TICKERS, period=args.period)

        if data.empty:
            print("Error: Dataset is empty")
            return EXIT_DATA_ERROR

        print(f"Dataset: {data.shape[0]:,} samples, {data.shape[1]} features")

    except Exception as e:
        print(f"Error building dataset: {e}")
        return EXIT_DATA_ERROR

    # Prepare features and target
    feature_cols = [c for c in data.columns if c not in ["Outperform", "Ticker", "Date"]]
    X = data[feature_cols]
    y = data["Outperform"]

    print(f"Features: {len(feature_cols)}")
    print(f"Class distribution: {y.value_counts().to_dict()}")

    # Setup MLflow if enabled
    if args.mlflow:
        mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "file:./mlruns")
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment(f"hyperopt_{args.model_type}")
        print(f"MLflow tracking: {mlflow_uri}")

    # Run optimization
    print(f"\nStarting optimization ({args.trials} trials)...")
    print("-" * 60)

    try:
        if args.mlflow:
            with mlflow.start_run(run_name=f"optimization_{args.model_type}"):
                best_params, study = run_optimization(
                    X, y, args.model_type, args.trials, args.timeout, args.study_name
                )

                # Log to MLflow
                mlflow.log_params(best_params)
                mlflow.log_metric("best_accuracy", study.best_value)
                mlflow.log_metric("n_trials", len(study.trials))
        else:
            best_params, study = run_optimization(
                X, y, args.model_type, args.trials, args.timeout, args.study_name
            )

    except Exception as e:
        print(f"Optimization failed: {e}")
        return EXIT_OPTIMIZATION_FAILED

    # Results
    print("\n" + "=" * 60)
    print("OPTIMIZATION COMPLETE")
    print("=" * 60)
    print(f"\nBest Accuracy: {study.best_value:.4f}")
    print(f"Completed Trials: {len(study.trials)}")
    print(
        f"Pruned Trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])}"
    )  # noqa: E501

    print("\nBest Parameters:")
    for param, value in best_params.items():
        print(f"  {param}: {value}")

    # Save results
    output_path = ROOT_DIR / args.output
    optimization_metrics = {
        "best_accuracy": study.best_value,
        "n_trials": len(study.trials),
        "n_pruned": len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED]),
    }
    save_best_params(best_params, optimization_metrics, args.model_type, output_path)

    # Print top 5 trials
    print("\nTop 5 Trials:")
    trials_df = study.trials_dataframe()
    if not trials_df.empty:
        top_trials = trials_df.nlargest(5, "value")[["number", "value", "state"]]
        print(top_trials.to_string(index=False))

    print("\nNext steps:")
    print(f"  1. Review best parameters in {args.output}")
    print("  2. Train production model: python scripts/train_production.py")
    print("  3. The training script will use optimized parameters if available")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
