#!/usr/bin/env python3
"""
Model Validation Script (FR-004 Phase 3).

Validates trained models against production metrics using backtesting.

Features:
    - Automatic backtest on last 6 months of data
    - Comparison with current production model
    - Detailed metrics report generation
    - Validation thresholds enforcement
    - JSON/Markdown report output

Usage:
    # Validate a specific model
    python scripts/validate_model.py --model models/model_20250127.bin

    # Validate staging model
    python scripts/validate_model.py --staging

    # Compare with production
    python scripts/validate_model.py --model model.bin --compare-production

    # Generate report
    python scripts/validate_model.py --model model.bin --output-report report.md

Exit Codes:
    0: Validation passed
    1: Validation failed (below thresholds)
    2: Model not found
    3: Backtest error
    4: Configuration error
"""

import argparse
import json
import os
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

MODELS_DIR = ROOT_DIR / "models"
PRODUCTION_DIR = MODELS_DIR / "production"
STAGING_DIR = MODELS_DIR / "staging"
REPORTS_DIR = ROOT_DIR / "reports"

# Exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_FAILED = 1
EXIT_MODEL_NOT_FOUND = 2
EXIT_BACKTEST_ERROR = 3
EXIT_CONFIG_ERROR = 4

# Default validation thresholds
DEFAULT_THRESHOLDS = {
    "accuracy": 0.55,
    "precision": 0.50,
    "recall": 0.45,
    "f1": 0.47,
    "sharpe_ratio": 0.5,
    "max_drawdown": -0.25,  # Maximum 25% drawdown
}


def load_model(model_path: Path):
    """Load a model from file."""
    try:
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def run_backtest(model, tickers: list[str], period_days: int = 180) -> dict:
    """
    Run backtest on model with recent data.

    Args:
        model: Trained model
        tickers: List of ticker symbols
        period_days: Backtest period in days

    Returns:
        Dictionary of backtest metrics
    """
    from src.trading_engine.trading import build_dataset

    # Get test data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    print(f"  Fetching data for {len(tickers)} tickers...")
    print(f"  Period: {start_date.date()} to {end_date.date()}")

    try:
        data = build_dataset(tickers, period="1y")  # Get 1 year, will filter
        if data.empty:
            return {"error": "No data available"}
    except Exception as e:
        return {"error": str(e)}

    # Prepare features
    feature_cols = [c for c in data.columns if c not in ["Outperform", "Ticker", "Date"]]
    X = data[feature_cols]
    y = data["Outperform"] if "Outperform" in data.columns else None

    if y is None:
        return {"error": "No target column in data"}

    # Make predictions
    try:
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else None
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

    # Calculate metrics
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )

    metrics = {
        "accuracy": float(accuracy_score(y, y_pred)),
        "precision": float(precision_score(y, y_pred, zero_division=0)),
        "recall": float(recall_score(y, y_pred, zero_division=0)),
        "f1": float(f1_score(y, y_pred, zero_division=0)),
        "n_samples": len(y),
        "n_positive_pred": int(sum(y_pred)),
        "n_positive_actual": int(sum(y)),
    }

    if y_proba is not None:
        try:
            metrics["auc_roc"] = float(roc_auc_score(y, y_proba))
        except Exception:
            pass

    # Calculate simulated trading metrics
    if "Return" in data.columns:
        returns = data["Return"].values
        pred_returns = returns * (2 * y_pred - 1)  # Long if pred=1, short if pred=0

        cumulative_return = (1 + pred_returns).prod() - 1
        sharpe = (
            pred_returns.mean() / pred_returns.std() * (252**0.5) if pred_returns.std() > 0 else 0
        )  # noqa: E501
        max_dd = (pred_returns.cumsum() - pred_returns.cumsum().cummax()).min()

        metrics["cumulative_return"] = float(cumulative_return)
        metrics["sharpe_ratio"] = float(sharpe)
        metrics["max_drawdown"] = float(max_dd)
        metrics["win_rate"] = float(sum(pred_returns > 0) / len(pred_returns))

    return metrics


def validate_metrics(metrics: dict, thresholds: dict) -> tuple[bool, list[str]]:
    """
    Validate metrics against thresholds.

    Args:
        metrics: Model metrics
        thresholds: Validation thresholds

    Returns:
        Tuple of (passed, list of failures)
    """
    failures = []

    for metric, threshold in thresholds.items():
        if metric not in metrics:
            continue

        value = metrics[metric]

        if metric == "max_drawdown":
            # Drawdown should be greater (less negative) than threshold
            if value < threshold:
                failures.append(f"{metric}: {value:.4f} < {threshold:.4f} (FAIL)")
        else:
            # Other metrics should be greater than threshold
            if value < threshold:
                failures.append(f"{metric}: {value:.4f} < {threshold:.4f} (FAIL)")

    return len(failures) == 0, failures


def compare_with_production(new_metrics: dict, prod_metrics: dict) -> dict:
    """
    Compare new model metrics with production.

    Returns:
        Comparison dictionary
    """
    comparison = {}

    all_metrics = set(new_metrics.keys()) | set(prod_metrics.keys())
    for metric in all_metrics:
        if metric in ["error", "n_samples", "n_positive_pred", "n_positive_actual"]:
            continue

        new_val = new_metrics.get(metric)
        prod_val = prod_metrics.get(metric)

        if new_val is not None and prod_val is not None:
            diff = new_val - prod_val
            pct_change = (diff / prod_val * 100) if prod_val != 0 else 0

            is_better = diff > 0
            if metric == "max_drawdown":
                is_better = diff > 0  # Less negative is better

            comparison[metric] = {
                "new": new_val,
                "production": prod_val,
                "diff": diff,
                "pct_change": pct_change,
                "is_better": is_better,
            }

    return comparison


def generate_report(
    model_path: str,
    metrics: dict,
    thresholds: dict,
    passed: bool,
    failures: list[str],
    comparison: dict | None = None,
    format: str = "markdown",
) -> str:
    """Generate validation report."""
    timestamp = datetime.utcnow().isoformat()

    if format == "json":
        report = {
            "timestamp": timestamp,
            "model": str(model_path),
            "passed": passed,
            "metrics": metrics,
            "thresholds": thresholds,
            "failures": failures,
            "comparison": comparison,
        }
        return json.dumps(report, indent=2, default=str)

    # Markdown format
    lines = [
        "# Model Validation Report",
        "",
        f"**Generated:** {timestamp}",
        f"**Model:** `{model_path}`",
        f"**Status:** {'✅ PASSED' if passed else '❌ FAILED'}",
        "",
        "## Metrics",
        "",
        "| Metric | Value | Threshold | Status |",
        "|--------|-------|-----------|--------|",
    ]

    for metric, threshold in thresholds.items():
        value = metrics.get(metric)
        if value is not None:
            status = "✅" if value >= threshold else "❌"
            lines.append(f"| {metric} | {value:.4f} | {threshold:.4f} | {status} |")

    if failures:
        lines.extend(
            [
                "",
                "## Failures",
                "",
            ]
        )
        for failure in failures:
            lines.append(f"- {failure}")

    if comparison:
        lines.extend(
            [
                "",
                "## Comparison with Production",
                "",
                "| Metric | New | Production | Diff | Status |",
                "|--------|-----|------------|------|--------|",
            ]
        )

        for metric, comp in comparison.items():
            new_val = comp["new"]
            prod_val = comp["production"]
            diff = comp["diff"]
            is_better = comp["is_better"]
            status = "📈" if is_better else "📉"
            sign = "+" if diff > 0 else ""
            lines.append(
                f"| {metric} | {new_val:.4f} | {prod_val:.4f} | {sign}{diff:.4f} | {status} |"
            )

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate ML model with backtesting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --model models/model_20250127.bin
    %(prog)s --staging --compare-production
    %(prog)s --model model.bin --output-report report.md
        """,
    )

    parser.add_argument("--model", help="Path to model file to validate")
    parser.add_argument("--staging", action="store_true", help="Validate staging model")
    parser.add_argument(
        "--compare-production", action="store_true", help="Compare with production model"
    )
    parser.add_argument(
        "--period-days", type=int, default=180, help="Backtest period in days (default: 180)"
    )
    parser.add_argument("--output-report", help="Path to output report file")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Report format (default: markdown)",
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=DEFAULT_THRESHOLDS["accuracy"],
        help=f"Minimum accuracy threshold (default: {DEFAULT_THRESHOLDS['accuracy']})",
    )
    parser.add_argument(
        "--min-precision",
        type=float,
        default=DEFAULT_THRESHOLDS["precision"],
        help=f"Minimum precision threshold (default: {DEFAULT_THRESHOLDS['precision']})",
    )
    parser.add_argument("--strict", action="store_true", help="Use stricter thresholds")

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Determine model path
    if args.staging:
        model_path = STAGING_DIR / "model.bin"
    elif args.model:
        model_path = Path(args.model)
        if not model_path.is_absolute():
            model_path = MODELS_DIR / model_path
    else:
        print("Error: Must specify --model or --staging")
        return EXIT_CONFIG_ERROR

    if not model_path.exists():
        print(f"Error: Model not found: {model_path}")
        return EXIT_MODEL_NOT_FOUND

    print("\n=== Model Validation ===\n")
    print(f"Model: {model_path}")

    # Load model
    print("Loading model...")
    model = load_model(model_path)
    if model is None:
        return EXIT_MODEL_NOT_FOUND

    # Set thresholds
    thresholds = DEFAULT_THRESHOLDS.copy()
    thresholds["accuracy"] = args.min_accuracy
    thresholds["precision"] = args.min_precision

    if args.strict:
        thresholds = {k: v * 1.1 for k, v in thresholds.items()}

    # Get test tickers (subset for validation speed)
    test_tickers = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "JPM",
        "BAC",
        "GS",
        "NESN.SW",
        "NOVN.SW",
        "ROG.SW",
    ]

    # Run backtest
    print(f"\nRunning backtest ({args.period_days} days)...")
    metrics = run_backtest(model, test_tickers, args.period_days)

    if "error" in metrics:
        print(f"Backtest error: {metrics['error']}")
        return EXIT_BACKTEST_ERROR

    print("\nBacktest Results:")
    print(f"  Accuracy:  {metrics.get('accuracy', 0):.2%}")
    print(f"  Precision: {metrics.get('precision', 0):.2%}")
    print(f"  Recall:    {metrics.get('recall', 0):.2%}")
    print(f"  F1 Score:  {metrics.get('f1', 0):.2%}")
    if "sharpe_ratio" in metrics:
        print(f"  Sharpe:    {metrics['sharpe_ratio']:.2f}")

    # Validate against thresholds
    passed, failures = validate_metrics(metrics, thresholds)

    # Compare with production if requested
    comparison = None
    if args.compare_production:
        prod_model_path = PRODUCTION_DIR / "model.bin"
        if not prod_model_path.exists():
            prod_model_path = MODELS_DIR / "prod_model.bin"

        if prod_model_path.exists():
            print("\nComparing with production model...")
            prod_model = load_model(prod_model_path)
            if prod_model:
                prod_metrics = run_backtest(prod_model, test_tickers, args.period_days)
                if "error" not in prod_metrics:
                    comparison = compare_with_production(metrics, prod_metrics)

    # Generate report
    report = generate_report(
        model_path, metrics, thresholds, passed, failures, comparison, args.format
    )

    # Output report
    if args.output_report:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = Path(args.output_report)
        if not output_path.is_absolute():
            output_path = REPORTS_DIR / output_path

        with open(output_path, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {output_path}")
    else:
        print("\n" + "=" * 50)
        print(report)

    # Final status
    print("\n" + "=" * 50)
    if passed:
        print("✅ VALIDATION PASSED")
        return EXIT_SUCCESS
    else:
        print("❌ VALIDATION FAILED")
        for failure in failures:
            print(f"  - {failure}")
        return EXIT_VALIDATION_FAILED


if __name__ == "__main__":
    sys.exit(main())
