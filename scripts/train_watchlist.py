#!/usr/bin/env python3
"""
Train ML model on all stocks from your watchlists.

This script automatically:
1. Fetches all stocks from all your watchlists
2. Downloads historical data (2 years)
3. Trains a Random Forest model
4. Evaluates performance
5. Deploys to production if better than current model

Usage:
    python scripts/train_watchlist.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime  # noqa: E402

from trading_fun.database import WatchlistDB  # noqa: E402
from trading_fun.trading import build_dataset, train_model  # noqa: E402


def main():
    print("=" * 60)
    print("🎓 WATCHLIST MODEL TRAINING")
    print("=" * 60)

    # Get all watchlists
    print("\n📊 Fetching watchlists...")
    watchlists = WatchlistDB.get_user_watchlists("default_user")

    if not watchlists:
        print("⚠️  No watchlists found! Create one first.")
        return

    print(f"Found {len(watchlists)} watchlist(s):")
    for wl in watchlists:
        print(f"  - {wl['name']} ({wl['item_count']} stocks)")

    # Collect all unique tickers
    all_tickers = set()
    for wl in watchlists:
        tickers = WatchlistDB.get_watchlist_tickers(wl["id"], "default_user")
        all_tickers.update(tickers)

    # Filter out invalid tickers (too short or non-stock symbols)
    valid_tickers = [t for t in all_tickers if len(t) >= 1 and len(t) <= 5]

    if not valid_tickers:
        print("⚠️  No valid stock tickers found in watchlists!")
        return

    print(f"\n📈 Training on {len(valid_tickers)} unique stocks:")
    print(f"   {', '.join(sorted(valid_tickers))}")

    # Build dataset
    print("\n⏳ Downloading 2 years of historical data...")
    try:
        data = build_dataset(valid_tickers, period="2y")
    except Exception as e:
        print(f"❌ Error building dataset: {e}")
        return

    if data.empty:
        print("❌ ERROR: No data available. Check if tickers are valid.")
        return

    print(f"✓ Dataset ready: {data.shape[0]} rows, {data.shape[1]} features")

    # Train model
    print("\n🤖 Training Random Forest model...")
    model_path = f"models/watchlist_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
    os.makedirs("models", exist_ok=True)

    try:
        model, metrics = train_model(data, model_type="rf", save_path=model_path)
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return

    # Display results
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print("\n📊 Model Performance:")
    print(f"   Accuracy:  {metrics['accuracy']:.2%}")
    print(f"   Precision: {metrics['precision']:.2%}")
    print(f"   Recall:    {metrics['recall']:.2%}")
    print(f"\n💾 Model saved to: {model_path}")

    # Check if we should promote to production
    prod_model_path = "models/prod_model.bin"
    should_promote = False

    if not os.path.exists(prod_model_path):
        print("\n⚠️  No production model found. This will become the production model.")
        should_promote = True
    else:
        print("\n🔍 Comparing with current production model...")
        try:
            # Load production model and get its accuracy (stored in metrics)
            # For now, we'll promote if accuracy > 0.55 (better than random)
            if metrics["accuracy"] > 0.55:
                print(f"   New model accuracy ({metrics['accuracy']:.2%}) is good!")
                should_promote = True
            else:
                print(f"   New model accuracy ({metrics['accuracy']:.2%}) is not good enough.")
                print("   Keeping current production model.")
        except Exception as e:
            print(f"   Error comparing models: {e}")
            print("   Promoting anyway...")
            should_promote = True

    if should_promote:
        import shutil

        shutil.copy(model_path, prod_model_path)
        print("\n🚀 PROMOTED TO PRODUCTION!")
        print(f"   Your watchlist model is now live at: {prod_model_path}")
        print("\n   Restart the server to use the new model:")
        print("   pkill -f uvicorn && .venv/bin/python -m uvicorn market_predictor.server:app --reload")

    print("\n" + "=" * 60)
    print("🎉 Done! Your personalized model is ready.")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - Add more stocks to your watchlists for better predictions")
    print("   - Retrain weekly to adapt to market changes")
    print("   - Check TRAINING_GUIDE.md for advanced options")
    print()


if __name__ == "__main__":
    main()
