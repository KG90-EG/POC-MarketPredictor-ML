#!/usr/bin/env python3
"""
Production Model Training Script (FR-004).

Trains ML model on all DEFAULT_STOCKS (50 stocks) for production deployment.

Features:
    - CLI arguments for configuration
    - Structured JSON logging
    - MLflow experiment tracking
    - Automatic promotion to production (accuracy > 60%)
    - Hyperparameter optimization (via --optimize flag)
    - Model versioning with timestamps

Usage:
    # Standard training
    python scripts/train_production.py

    # With optimization
    python scripts/train_production.py --optimize --trials 50

    # Force retrain (skip comparison)
    python scripts/train_production.py --force

    # Using Makefile
    make train-model

Exit Codes:
    0: Success
    1: Training failed (dataset error, model error)
    2: Validation failed (metrics below threshold)
    3: Configuration error (invalid arguments)

Output:
    - New model: models/model_YYYYMMDD_HHMMSS.bin
    - Production model: models/prod_model.bin
    - MLflow tracking: mlruns/
    - Logs: logs/training.log
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import mlflow

# Add project root to path FIRST
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.trading_engine.trading import build_dataset, train_model  # noqa: E402

# Exit codes
EXIT_SUCCESS = 0
EXIT_TRAINING_FAILED = 1
EXIT_VALIDATION_FAILED = 2
EXIT_CONFIG_ERROR = 3


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Configure structured logging for training."""
    logger = logging.getLogger("train_production")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers = []

    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler with JSON format
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                }
                if hasattr(record, "metrics"):
                    log_data["metrics"] = record.metrics
                return json.dumps(log_data)

        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Train production ML model for stock predictions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                         # Standard training
    %(prog)s --optimize --trials 50  # With hyperparameter optimization
    %(prog)s --force --period 3y     # Force retrain with 3 years data
    %(prog)s --min-accuracy 0.65     # Require 65% accuracy for promotion
        """,
    )

    parser.add_argument(
        "--optimize", action="store_true", help="Run hyperparameter optimization before training"
    )
    parser.add_argument(
        "--trials", type=int, default=20, help="Number of optimization trials (default: 20)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="5y",
        choices=["1y", "2y", "3y", "5y", "10y"],
        help="Historical data period (default: 5y)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force training even if current model is better"
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        default=0.60,
        help="Minimum accuracy for production promotion (default: 0.60)",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="xgb",
        choices=["xgb", "rf", "lgb"],
        help="Model type: xgb (XGBoost), rf (RandomForest), lgb (LightGBM)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run training but don't promote to production"
    )
    parser.add_argument("--output-json", type=str, help="Path to write training results as JSON")

    return parser.parse_args()


# Global stocks - US + Swiss coverage for worldwide trading
# 30 US stocks + 20 Swiss SMI stocks = 50 total
DEFAULT_STOCKS = [
    # === US Tech Giants (10) ===
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "NFLX",
    "ADBE",
    "CRM",
    # === US Finance (8) ===
    "JPM",
    "BAC",
    "WFC",
    "GS",
    "MS",
    "V",
    "MA",
    "PYPL",
    # === US Healthcare & Pharma (4) ===
    "UNH",
    "JNJ",
    "PFE",
    "ABBV",
    # === US Consumer & Retail (5) ===
    "WMT",
    "COST",
    "HD",
    "NKE",
    "MCD",
    # === US Energy & Industrial (3) ===
    "XOM",
    "CVX",
    "BA",
    # === Swiss SMI Index (20) - Switzerland's top stocks ===
    "NESN.SW",  # Nestlé - Food & Beverage
    "NOVN.SW",  # Novartis - Pharmaceuticals
    "ROG.SW",  # Roche - Pharmaceuticals
    "UBSG.SW",  # UBS - Banking
    "ZURN.SW",  # Zurich Insurance
    "ABBN.SW",  # ABB - Engineering
    "CFR.SW",  # Richemont - Luxury Goods
    "LONN.SW",  # Lonza - Life Sciences
    "SIKA.SW",  # Sika - Chemicals
    "GIVN.SW",  # Givaudan - Flavors & Fragrances
    "SREN.SW",  # Swiss Re - Reinsurance
    "GEBN.SW",  # Geberit - Sanitary Technology
    "PGHN.SW",  # Partners Group - Private Equity
    "SGSN.SW",  # SGS - Testing & Certification
    "SCMN.SW",  # Swisscom - Telecommunications
    "HOLN.SW",  # Holcim - Building Materials
    "ALC.SW",  # Alcon - Eye Care
    "KNIN.SW",  # Kühne + Nagel - Logistics
    "UHR.SW",  # Swatch - Watches
    "ADEN.SW",  # Adecco - Staffing
]


def build_training_dataset(
    stocks: list[str], period: str, logger: logging.Logger
) -> tuple[any, dict]:
    """
    Build training dataset with enhanced features.

    Returns:
        Tuple of (DataFrame, metadata dict)
    """
    logger.info(f"Building dataset for {len(stocks)} stocks with {period} history")

    # Enable advanced features
    from src.trading_engine import trading as trading_module

    original_use_all = trading_module.USE_ALL_FEATURES
    trading_module.USE_ALL_FEATURES = True

    metadata = {
        "n_stocks": len(stocks),
        "period": period,
        "us_stocks": len([s for s in stocks if not s.endswith(".SW")]),
        "swiss_stocks": len([s for s in stocks if s.endswith(".SW")]),
        "features_enabled": "all_20",
    }

    try:
        data = build_dataset(stocks, period=period)
        if data.empty:
            raise ValueError("Dataset is empty - check internet connection or tickers")

        metadata["n_samples"] = data.shape[0]
        metadata["n_features"] = data.shape[1]

        if "Outperform" in data.columns:
            class_counts = data["Outperform"].value_counts()
            metadata["class_outperform"] = int(class_counts.get(1, 0))
            metadata["class_underperform"] = int(class_counts.get(0, 0))
            metadata["class_balance"] = round(class_counts.get(1, 0) / len(data) * 100, 2)

        logger.info(f"Dataset ready: {data.shape[0]:,} samples, {data.shape[1]} features")
        return data, metadata

    finally:
        trading_module.USE_ALL_FEATURES = original_use_all


def train_and_evaluate(
    data, model_type: str, model_path: str, timestamp: str, logger: logging.Logger
) -> tuple[any, dict]:
    """
    Train model with MLflow tracking.

    Returns:
        Tuple of (model, metrics dict)
    """
    mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "file:./mlruns")
    mlflow.set_tracking_uri(mlflow_uri)

    logger.info(f"Training {model_type.upper()} model with MLflow tracking")

    with mlflow.start_run(run_name=f"production_training_{timestamp}"):
        model, metrics = train_model(
            data,
            model_type=model_type,
            save_path=model_path,
            use_feature_selection=True,
            n_features=30,
        )

        # Log parameters
        mlflow.log_param("n_stocks", len(DEFAULT_STOCKS))
        mlflow.log_param("period", "5y")
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("n_samples", data.shape[0])
        mlflow.log_param("timestamp", timestamp)

        # Log metrics
        for k, v in metrics.items():
            if v is not None:
                mlflow.log_metric(k, v)

        # Log model artifact
        try:
            mlflow.sklearn.log_model(model, "model")
        except Exception:
            mlflow.xgboost.log_model(model, "model")

        # Get run ID for reference
        metrics["mlflow_run_id"] = mlflow.active_run().info.run_id

    logger.info(f"Training complete - Accuracy: {metrics.get('accuracy', 0):.2%}")
    return model, metrics


def promote_model(
    model_path: str,
    metrics: dict,
    min_accuracy: float,
    force: bool,
    dry_run: bool,
    logger: logging.Logger,
) -> bool:
    """
    Promote model to production if criteria met.

    Returns:
        True if promoted, False otherwise
    """
    import shutil

    prod_model_path = os.path.abspath("models/prod_model.bin")
    accuracy = metrics.get("accuracy", 0)

    # Determine promotion
    no_prod_model = not os.path.exists(prod_model_path)
    meets_threshold = accuracy >= min_accuracy

    if dry_run:
        logger.info(f"DRY RUN: Would promote model (accuracy: {accuracy:.2%})")
        return False

    if no_prod_model:
        logger.warning("No production model found - promoting new model")
        shutil.copy(model_path, prod_model_path)
        logger.info(f"PROMOTED to production: {prod_model_path}")
        return True

    if force:
        logger.warning("FORCE flag set - promoting regardless of accuracy")
        shutil.copy(model_path, prod_model_path)
        logger.info(f"PROMOTED to production: {prod_model_path}")
        return True

    if meets_threshold:
        shutil.copy(model_path, prod_model_path)
        logger.info(f"PROMOTED to production (accuracy: {accuracy:.2%} >= {min_accuracy:.0%})")
        return True

    logger.warning(
        f"Model NOT promoted - accuracy {accuracy:.2%} below threshold {min_accuracy:.0%}"
    )
    return False


def write_results_json(output_path: str, results: dict, logger: logging.Logger) -> None:
    """Write training results to JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info(f"Results written to {output_path}")


def main() -> int:
    """Train production model with CLI configuration."""
    args = parse_args()

    # Setup logging
    log_file = str(ROOT_DIR / "logs" / "training.log")
    logger = setup_logging(args.log_level, log_file)

    logger.info("=" * 60)
    logger.info("PRODUCTION MODEL TRAINING - US + SWISS STOCKS")
    logger.info("=" * 60)
    logger.info(f"Configuration: period={args.period}, model={args.model_type}")
    logger.info(f"Stocks: {len(DEFAULT_STOCKS)} total (30 US + 20 Swiss)")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    model_path = os.path.abspath(f"models/model_{timestamp}.bin")
    os.makedirs("models", exist_ok=True)

    results = {
        "timestamp": timestamp,
        "config": vars(args),
        "status": "started",
    }

    try:
        # Build dataset
        logger.info("Building training dataset...")
        data, dataset_meta = build_training_dataset(DEFAULT_STOCKS, args.period, logger)
        results["dataset"] = dataset_meta

    except Exception as e:
        logger.error(f"Dataset build failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        if args.output_json:
            write_results_json(args.output_json, results, logger)
        return EXIT_TRAINING_FAILED

    try:
        # Train model
        logger.info("Training model...")
        model, metrics = train_and_evaluate(data, args.model_type, model_path, timestamp, logger)
        results["metrics"] = metrics
        results["model_path"] = model_path

    except ValueError as e:
        logger.error(f"Training failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        if args.output_json:
            write_results_json(args.output_json, results, logger)
        return EXIT_TRAINING_FAILED

    except Exception as e:
        logger.error(f"Unexpected training error: {e}")
        import traceback

        logger.debug(traceback.format_exc())
        results["status"] = "failed"
        results["error"] = str(e)
        if args.output_json:
            write_results_json(args.output_json, results, logger)
        return EXIT_TRAINING_FAILED

    # Validate metrics
    accuracy = metrics.get("accuracy", 0)
    if accuracy < args.min_accuracy and not args.force:
        logger.warning(f"Accuracy {accuracy:.2%} below threshold {args.min_accuracy:.0%}")
        results["status"] = "validation_failed"
        if args.output_json:
            write_results_json(args.output_json, results, logger)
        return EXIT_VALIDATION_FAILED

    # Promote to production
    promoted = promote_model(
        model_path, metrics, args.min_accuracy, args.force, args.dry_run, logger
    )
    results["promoted"] = promoted
    results["status"] = "success"

    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Model saved: {model_path}")
    logger.info(f"Accuracy: {accuracy:.2%}")
    logger.info(f"Promoted: {'Yes' if promoted else 'No'}")

    if args.output_json:
        write_results_json(args.output_json, results, logger)

    if promoted:
        logger.info("Next: Restart server with 'make restart'")

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
