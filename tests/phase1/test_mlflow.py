#!/usr/bin/env python3
"""
Test Suite for MLflow Integration (Week 4).

Tests experiment tracking, model registry, and run comparison.
"""

import os
import sys

sys.path.insert(0, os.path.abspath("."))

import logging

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.trading_engine.ml.mlflow_integration import MLflowTracker, track_training_run
from src.trading_engine.ml.trading import features, load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def build_dataset(ticker="AAPL", period="2y"):
    """Build training dataset."""
    print(f"🔄 Loading {ticker} data ({period})...")
    data = load_data(ticker, period=period, use_advanced_features=False)
    data = data.dropna()
    print(f"✅ Dataset: {len(data)} samples")
    return data


def test_mlflow_basic_tracking():
    """Test basic MLflow tracking."""
    print_header("Basic MLflow Tracking")

    # Initialize tracker
    tracker = MLflowTracker(experiment_name="test_basic_tracking")
    print(f"✅ MLflow tracker initialized")
    print(f"   Experiment: {tracker.experiment_name}")

    # Start run
    run_id = tracker.start_run(run_name="test_run_1", tags={"test": "basic"})
    print(f"✅ Started run: {run_id}")

    # Log parameters
    params = {
        "model_type": "random_forest",
        "n_estimators": 100,
        "max_depth": 5,
        "test_param": "value",
    }
    tracker.log_params(params)
    print(f"✅ Logged {len(params)} parameters")

    # Log metrics
    metrics = {
        "accuracy": 0.85,
        "f1_score": 0.82,
        "roc_auc": 0.88,
    }
    tracker.log_metrics(metrics)
    print(f"✅ Logged {len(metrics)} metrics")

    # End run
    tracker.end_run()
    print(f"✅ Run ended successfully")

    print("\n✅ Basic tracking test PASSED")
    return tracker


def test_mlflow_model_logging():
    """Test model logging to MLflow."""
    print_header("MLflow Model Logging")

    # Build dataset and train model
    data = build_dataset("AAPL", period="2y")

    X = data[[f for f in features if f in data.columns]]
    y = data["Outperform"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"🤖 Training model...")
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    print(f"✅ Model trained")

    # Track with MLflow
    tracker = MLflowTracker(experiment_name="test_model_logging")
    run_id = tracker.start_run(run_name="model_test")

    # Log model
    tracker.log_model(model, artifact_path="rf_model")
    print(f"✅ Model logged")

    # Log feature importance
    feature_list = [f for f in features if f in data.columns]
    tracker.log_feature_importance(feature_list, model.feature_importances_)
    print(f"✅ Feature importance logged")

    # Log confusion matrix
    y_pred = model.predict(X_test)
    tracker.log_confusion_matrix(y_test, y_pred, labels=["Down", "Up"])
    print(f"✅ Confusion matrix logged")

    tracker.end_run()

    # Load model back
    print(f"\n🔄 Loading model from MLflow...")
    loaded_model = tracker.load_model(run_id, artifact_path="rf_model")
    print(f"✅ Model loaded successfully")

    # Verify predictions match
    original_preds = model.predict(X_test[:5])
    loaded_preds = loaded_model.predict(X_test[:5])

    assert all(original_preds == loaded_preds), "Predictions should match"
    print(f"✅ Loaded model predictions match original")

    print("\n✅ Model logging test PASSED")


def test_mlflow_full_training_run():
    """Test complete training run tracking with convenience function."""
    print_header("Complete Training Run Tracking")

    # Build dataset
    data = build_dataset("MSFT", period="2y")

    X = data[[f for f in features if f in data.columns]]
    y = data["Outperform"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    print(f"🤖 Training RandomForest...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    print(f"✅ Model trained")
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   F1 Score: {metrics['f1_score']:.4f}")

    # Track complete run
    print(f"\n📊 Tracking complete run with MLflow...")
    tracker = MLflowTracker(experiment_name="test_full_tracking")

    params = {
        "model_type": "random_forest",
        "n_estimators": 100,
        "max_depth": 10,
        "test_size": 0.2,
    }

    feature_list = [f for f in features if f in data.columns]

    run_id = track_training_run(
        tracker=tracker,
        model=model,
        params=params,
        metrics=metrics,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        run_name="full_run_test",
        feature_names=feature_list,
    )

    print(f"✅ Complete run tracked: {run_id}")
    print("\n✅ Full training run test PASSED")


def test_mlflow_run_comparison():
    """Test comparing multiple runs."""
    print_header("Run Comparison")

    tracker = MLflowTracker(experiment_name="test_comparison")

    # Create 3 test runs
    run_ids = []

    for i in range(3):
        run_id = tracker.start_run(run_name=f"comparison_run_{i+1}")

        # Different parameters
        params = {
            "n_estimators": 50 * (i + 1),
            "max_depth": 5 + i * 2,
        }
        tracker.log_params(params)

        # Simulated metrics (improving)
        metrics = {
            "accuracy": 0.70 + i * 0.05,
            "f1_score": 0.68 + i * 0.05,
        }
        tracker.log_metrics(metrics)

        tracker.end_run()
        run_ids.append(run_id)

    print(f"✅ Created {len(run_ids)} runs for comparison")

    # Compare runs
    print(f"\n📊 Comparing runs...")
    comparison = tracker.compare_runs(run_ids, metrics=["accuracy", "f1_score"])

    print(comparison[["run_name", "accuracy", "f1_score"]])

    assert len(comparison) == 3, "Should have 3 runs"
    print(f"\n✅ Run comparison test PASSED")


def test_mlflow_best_run():
    """Test finding best run by metric."""
    print_header("Best Run Selection")

    tracker = MLflowTracker(experiment_name="test_best_run")

    # Create runs with different scores
    scores = [0.75, 0.82, 0.79, 0.88, 0.81]

    for i, score in enumerate(scores):
        run_id = tracker.start_run(run_name=f"run_{i+1}")
        tracker.log_metrics({"f1_score": score, "accuracy": score - 0.02})
        tracker.end_run()

    print(f"✅ Created {len(scores)} runs")

    # Find best run
    best_run = tracker.get_best_run(metric="f1_score")

    if best_run:
        best_f1 = best_run.data.metrics["f1_score"]
        print(f"\n📊 Best Run:")
        print(f"   Run ID: {best_run.info.run_id}")
        print(f"   F1 Score: {best_f1:.4f}")

        assert best_f1 == max(scores), "Should find run with highest F1"
        print(f"\n✅ Best run selection test PASSED")
    else:
        raise ValueError("Failed to find best run")


def main():
    """Run all tests."""
    print_header("Week 4: MLflow Integration - Test Suite")

    tests = [
        ("1️⃣  Basic Tracking", test_mlflow_basic_tracking),
        ("2️⃣  Model Logging", test_mlflow_model_logging),
        ("3️⃣  Full Training Run", test_mlflow_full_training_run),
        ("4️⃣  Run Comparison", test_mlflow_run_comparison),
        ("5️⃣  Best Run Selection", test_mlflow_best_run),
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

    # Cleanup note
    print(f"\n💡 MLflow artifacts stored in: mlruns/")
    print(f"   View UI with: mlflow ui")


if __name__ == "__main__":
    main()
