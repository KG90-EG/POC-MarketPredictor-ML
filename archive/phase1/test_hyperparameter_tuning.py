#!/usr/bin/env python3
"""
Test Suite for Hyperparameter Tuning (Week 4).

Tests Optuna optimization for XGBoost, RandomForest, GradientBoosting, LightGBM.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import logging

import numpy as np
import pandas as pd

from src.trading_engine.ml.hyperparameter_tuning import HyperparameterTuner, optimize_ensemble_weights
from src.trading_engine.ml.trading import load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def build_dataset(tickers=["AAPL", "MSFT"], period="2y"):
    """Build training dataset from multiple tickers."""
    print(f"🔄 Building dataset for {tickers}...")

    all_data = []
    for ticker in tickers:
        try:
            data = load_data(ticker, period=period, use_advanced_features=False)
            if len(data) > 0:
                all_data.append(data)
        except Exception as e:
            logger.warning(f"Failed to load {ticker}: {e}")

    if not all_data:
        raise ValueError("No data loaded")

    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.dropna()

    print(f"✅ Dataset: {len(combined)} samples")
    return combined


def test_xgboost_optimization():
    """Test XGBoost hyperparameter optimization."""
    print_header("XGBoost Hyperparameter Optimization")

    # Build dataset
    data = build_dataset(tickers=["AAPL"], period="2y")

    from src.trading_engine.trading import features

    X = data[[f for f in features if f in data.columns]]
    y = data["Outperform"]

    print(f"Features: {len(X.columns)}")
    print(f"Samples: {len(X)}")
    print(f"Class distribution: {y.value_counts().to_dict()}")

    # Optimize (small n_trials for testing)
    print("\n🤖 Optimizing XGBoost hyperparameters...")
    print("   (10 trials for speed, use 100+ for production)")

    tuner = HyperparameterTuner(n_trials=10, cv_folds=3, n_jobs=-1)
    best_params = tuner.optimize_model("xgboost", X, y, show_progress=True)

    print(f"\n📊 Best Parameters:")
    for param, value in best_params.items():
        print(f"   {param}: {value}")

    # Get report
    report = tuner.get_optimization_report("xgboost")
    print(f"\n📈 Optimization Report:")
    print(f"   Best F1 Score: {report['best_value']:.4f}")
    print(f"   Best Trial: {report['best_trial_number']}/{report['n_trials']}")

    if report["param_importances"]:
        print(f"\n🔍 Parameter Importances:")
        for param, importance in list(report["param_importances"].items())[:5]:
            print(f"   {param}: {importance:.4f}")

    print("\n✅ XGBoost optimization test PASSED")


def test_random_forest_optimization():
    """Test RandomForest hyperparameter optimization."""
    print_header("RandomForest Hyperparameter Optimization")

    data = build_dataset(tickers=["MSFT"], period="2y")

    from src.trading_engine.trading import features

    X = data[[f for f in features if f in data.columns]]
    y = data["Outperform"]

    print(f"Features: {len(X.columns)}, Samples: {len(X)}")

    print("\n🤖 Optimizing RandomForest...")
    tuner = HyperparameterTuner(n_trials=10, cv_folds=3, n_jobs=-1)
    best_params = tuner.optimize_model("random_forest", X, y, show_progress=True)

    print(f"\n📊 Best Parameters:")
    for param, value in best_params.items():
        print(f"   {param}: {value}")

    report = tuner.get_optimization_report("random_forest")
    print(f"\n📈 Best F1 Score: {report['best_value']:.4f}")

    print("\n✅ RandomForest optimization test PASSED")


def test_optimize_all_models():
    """Test optimizing all models at once."""
    print_header("Optimize All Models")

    data = build_dataset(tickers=["AAPL", "MSFT"], period="2y")

    from src.trading_engine.trading import features

    X = data[[f for f in features if f in data.columns]]
    y = data["Outperform"]

    print(f"Dataset: {len(X)} samples, {len(X.columns)} features")

    # Optimize all (small trials for testing)
    print("\n🤖 Optimizing all 4 models...")
    print("   XGBoost, RandomForest, GradientBoosting, LightGBM")
    print("   (5 trials each for speed)")

    tuner = HyperparameterTuner(n_trials=5, cv_folds=3, n_jobs=-1)
    results = tuner.optimize_all_models(X, y, show_progress=False)

    print(f"\n📊 Optimization Results:")
    for model_type, params in results.items():
        if params:
            study = tuner.studies[model_type]
            print(f"\n   {model_type.upper()}:")
            print(f"      Best F1: {study.best_value:.4f}")
            print(f"      Params: {list(params.keys())[:3]}...")
        else:
            print(f"\n   {model_type.upper()}: FAILED")

    # Save results
    output_path = "best_hyperparameters.json"
    tuner.save_best_params(output_path)
    print(f"\n💾 Saved best parameters to: {output_path}")

    # Test loading
    loaded_params = tuner.load_best_params(output_path)
    print(f"✅ Loaded {len(loaded_params)} model configurations")

    print("\n✅ Optimize all models test PASSED")


def test_ensemble_weights_optimization():
    """Test ensemble weight optimization."""
    print_header("Ensemble Weights Optimization")

    data = build_dataset(tickers=["AAPL", "MSFT"], period="2y")

    from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier

    from src.trading_engine.trading import features

    X = data[[f for f in features if f in data.columns]]
    y = data["Outperform"]

    # Train base models
    print("🤖 Training base models...")
    models = [
        RandomForestClassifier(n_estimators=50, random_state=42),
        GradientBoostingClassifier(n_estimators=50, random_state=42),
    ]
    model_names = ["rf", "gb"]

    for model in models:
        model.fit(X, y)

    print("✅ Base models trained")

    # Optimize weights
    print("\n🔍 Optimizing ensemble weights (10 trials)...")
    best_weights, best_f1 = optimize_ensemble_weights(models, model_names, X, y, n_trials=10, cv_folds=3)

    print(f"\n📊 Optimal Weights:")
    for name, weight in zip(model_names, best_weights):
        print(f"   {name}: {weight:.4f}")
    print(f"\n📈 Best F1 Score: {best_f1:.4f}")

    assert sum(best_weights) > 0.99, "Weights should sum to ~1.0"
    print("\n✅ Ensemble weights optimization test PASSED")


def main():
    """Run all tests."""
    print_header("Week 4: Hyperparameter Tuning - Test Suite")

    tests = [
        ("1️⃣  XGBoost Optimization", test_xgboost_optimization),
        ("2️⃣  RandomForest Optimization", test_random_forest_optimization),
        ("3️⃣  Optimize All Models", test_optimize_all_models),
        ("4️⃣  Ensemble Weights", test_ensemble_weights_optimization),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
            import traceback

            traceback.print_exc()

    # Summary
    print_header("Test Summary")
    print(f"✅ PASS  {passed}/{len(tests)} tests")
    if failed > 0:
        print(f"❌ FAIL  {failed}/{len(tests)} tests")

    print(f"\n{'=' * 60}")
    print(f"Results: {passed}/{len(tests)} tests passed ({100*passed//len(tests)}%)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
