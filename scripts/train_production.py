#!/usr/bin/env python3
"""
Production Model Training Script

Trains ML model on all DEFAULT_STOCKS (50 stocks) to ensure proper predictions
across the entire stock universe used in the application.

This script:
1. Uses all DEFAULT_STOCKS from server.py (50 major stocks)
2. Downloads 5 years of historical data for robust training
3. Trains XGBoost model with optimized parameters
4. Evaluates model performance with detailed metrics
5. Automatically deploys to production if accuracy > 60%
6. Logs all metrics to MLflow for tracking

Usage:
    python scripts/train_production.py

    # Or use Makefile:
    make train-model

Output:
    - New model saved to: models/model_YYYYMMDD_HHMMSS.bin
    - Production model: models/prod_model.bin (auto-updated if better)
    - MLflow tracking: mlruns/ directory
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import mlflow

from src.trading_engine.trading import build_dataset, train_model

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


def main():
    """Train production model on all DEFAULT_STOCKS."""
    print("=" * 80)
    print("🤖 PRODUCTION MODEL TRAINING - US + SWISS STOCKS")
    print("=" * 80)
    print(f"\n📊 Training on {len(DEFAULT_STOCKS)} stocks:")
    print(f"   US Stocks (30): {', '.join([s for s in DEFAULT_STOCKS if not s.endswith('.SW')][:5])}...")
    print(f"   Swiss SMI (20): {', '.join([s for s in DEFAULT_STOCKS if s.endswith('.SW')][:5])}...")
    print(f"   (Total: {len(DEFAULT_STOCKS)} - 30 US + 20 Swiss)")

    # Setup MLflow tracking
    mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "file:./mlruns")
    mlflow.set_tracking_uri(mlflow_uri)
    print(f"\n📈 MLflow tracking URI: {mlflow_uri}")

    # Build dataset with enhanced features for better performance
    print("\n⏳ Downloading 5 years of historical data for 50 stocks (US + Swiss)...")
    print("   Using sequential downloads with 0.5s delay to avoid rate limiting...")
    print("   This may take 3-4 minutes...")

    try:
        # Use 5y period for robust training data
        print(f"   Fetching data for {len(DEFAULT_STOCKS)} stocks...")

        # Enable ALL features for maximum model performance (20 technical features)
        from src.trading_engine import trading as trading_module

        original_use_all = trading_module.USE_ALL_FEATURES
        trading_module.USE_ALL_FEATURES = True  # Use 20 advanced technical features

        print(f"   ✓ Advanced technical features enabled: 20 features")
        print(f"     Technical: RSI, MACD, Bollinger, ATR, ADX, Stochastic, OBV, VWAP, etc.")
        print(f"     Note: No external API calls (fundamentals/sentiment) to avoid rate limiting")

        try:
            data = build_dataset(DEFAULT_STOCKS, period="5y")
        finally:
            # Restore original setting
            trading_module.USE_ALL_FEATURES = original_use_all

        if data.empty:
            print("❌ ERROR: Dataset is empty after build_dataset")
            print("   This usually happens when:")
            print("   1. No internet connection")
            print("   2. Yahoo Finance API is down")
            print("   3. All ticker symbols are invalid")
            print("\n   Try running with fewer stocks first:")
            print("   python3 scripts/train_production.py --test")
            return 1

        print(f"✓ Dataset ready: {data.shape[0]:,} samples, {data.shape[1]} features")

        # Check class distribution
        if "Outperform" in data.columns:
            class_counts = data["Outperform"].value_counts()
            print(f"\n📊 Class distribution:")
            print(f"   Outperform: {class_counts.get(1, 0):,} ({class_counts.get(1, 0)/len(data)*100:.1f}%)")
            print(f"   Underperform: {class_counts.get(0, 0):,} ({class_counts.get(0, 0)/len(data)*100:.1f}%)")

    except Exception as e:
        print(f"❌ ERROR: Failed to build dataset: {e}")
        return 1

    # Create models directory
    os.makedirs("models", exist_ok=True)

    # Generate timestamp for model versioning
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    model_path = os.path.abspath(f"models/model_{timestamp}.bin")

    print(f"\n🔧 Training XGBoost model...")
    print(f"   Model will be saved to: {model_path}")

    # Train model with MLflow tracking
    try:
        with mlflow.start_run(run_name=f"production_training_{timestamp}"):
            # Train with XGBoost for better performance
            model, metrics = train_model(
                data,
                model_type="xgb",  # XGBoost generally performs better
                save_path=model_path,
                use_feature_selection=True,
                n_features=30,  # Top 30 most important features
            )

            # Log parameters to MLflow
            mlflow.log_param("tickers", ",".join(DEFAULT_STOCKS))
            mlflow.log_param("n_stocks", len(DEFAULT_STOCKS))
            mlflow.log_param("period", "5y")
            mlflow.log_param("model_type", "xgb")
            mlflow.log_param("n_samples", data.shape[0])

            # Log all metrics to MLflow
            for k, v in metrics.items():
                if v is not None:
                    mlflow.log_metric(k, v)

            # Log the model artifact
            try:
                mlflow.sklearn.log_model(model, "model")
            except Exception:
                # Fallback for XGBoost models
                mlflow.xgboost.log_model(model, "model")

            print("\n" + "=" * 80)
            print("✅ TRAINING COMPLETE!")
            print("=" * 80)
            print("\n📊 Model Performance:")
            print(f"   Accuracy:  {metrics.get('accuracy', 0):.2%}")
            print(f"   Precision: {metrics.get('precision', 0):.2%}")
            print(f"   Recall:    {metrics.get('recall', 0):.2%}")
            print(f"   F1 Score:  {metrics.get('f1', 0):.2%}")

            # Check if we should promote to production
            prod_model_path = os.path.abspath("models/prod_model.bin")
            accuracy = metrics.get("accuracy", 0)

            # Promote if accuracy > 60% or if no production model exists
            should_promote = accuracy > 0.60 or not os.path.exists(prod_model_path)

            if not os.path.exists(prod_model_path):
                print(f"\n⚠️  No production model found.")
                print(f"   This will become the production model.")
                should_promote = True
            elif accuracy > 0.60:
                print(f"\n✅ Model accuracy ({accuracy:.2%}) exceeds 60% threshold!")
                should_promote = True
            else:
                print(f"\n⚠️  Model accuracy ({accuracy:.2%}) is below 60% threshold.")
                print(f"   Keeping current production model.")
                should_promote = False

            if should_promote:
                import shutil

                shutil.copy(model_path, prod_model_path)
                print(f"\n🚀 PROMOTED TO PRODUCTION!")
                print(f"   Production model updated: {prod_model_path}")
                print(f"\n   ⚠️  Restart the server to use the new model:")
                print(f"   make restart")
            else:
                print(f"\n💾 Model saved but not promoted to production.")
                print(f"   You can manually promote it later if needed:")
                print(f"   cp {model_path} {prod_model_path}")

    except ValueError as e:
        print(f"\n❌ ERROR: Training failed - {e}")
        print("   This may be due to insufficient data or all same class labels")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected training error - {e}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 80)
    print("🎉 Done!")
    print("=" * 80)
    print("\n💡 Next Steps:")
    print("   1. Restart server: make restart")
    print("   2. Check predictions: curl http://localhost:8000/ranking")
    print("   3. View MLflow UI: mlflow ui --port 5000")
    print("   4. Setup auto-retraining: See docs/TRAINING_GUIDE.md")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
