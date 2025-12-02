# 🎓 Model Training Guide

## Overview

Your ML model predicts stock movements based on technical indicators. Training it with more data and your watchlist stocks makes it **personalized to your investment strategy**.

## 🚀 Quick Start

### 1. Train a New Model (5 minutes)

```bash
# Activate your environment
cd /Users/kevingarcia/Documents/POC-MarketPredictor-ML
source .venv/bin/activate

# Run training with default stocks
python training/trainer.py
```

This will:

- Download 2 years of historical data
- Calculate technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Train a Random Forest model
- Save to `models/model_YYYYMMDD_HHMMSS.bin`
- Track metrics with MLflow

### 2. Train with YOUR Watchlist Stocks

```bash
# Train with your favorite stocks
python scripts/train_watchlist.py
```

This will automatically train on ALL stocks in your watchlists!

### 3. Evaluate and Deploy

```bash
# Compare new model vs current production model
python training/evaluate_and_promote.py

# If better, it will automatically promote to prod_model.bin
```

## 📊 Training Options

### Basic Training

```python
from market_predictor.trading import build_dataset, train_model

# Build dataset
tickers = ["AAPL", "MSFT", "GOOGL", "UBS"]
data = build_dataset(tickers, period="2y")

# Train model
model, metrics = train_model(data, model_type="rf")
print(f"Accuracy: {metrics['accuracy']:.2%}")
```

### Advanced Training Options

```python
# 1. Different model types
train_model(data, model_type="rf")      # Random Forest (default, best)
train_model(data, model_type="xgb")     # XGBoost (faster)
train_model(data, model_type="lgbm")    # LightGBM (memory efficient)

# 2. Custom parameters
train_model(data,
    model_type="rf",
    n_estimators=200,      # More trees = better but slower
    max_depth=20,          # Deeper = more complex
    min_samples_split=5    # Regularization
)

# 3. More data
data = build_dataset(tickers, period="5y")  # 5 years of data
```

## 🎯 What Gets Trained?

The model learns from these **technical indicators**:

1. **Price Features**
   - Open, High, Low, Close, Volume
   - Price changes and returns

2. **Technical Indicators**
   - **RSI** (Relative Strength Index) - Overbought/oversold
   - **MACD** - Trend momentum
   - **Bollinger Bands** - Volatility
   - **SMA** (Simple Moving Averages) - 20, 50, 200 day
   - **Momentum** - Price acceleration

3. **Target Variable**
   - Binary: Will price go up or down in next 90 days?

## 📈 Training Workflow

```
┌─────────────────┐
│ 1. Fetch Data   │ ← Download historical prices
│    (2-5 years)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Calculate    │ ← Compute RSI, MACD, etc.
│    Indicators   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Create       │ ← Label: up/down in 90 days
│    Labels       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Train Model  │ ← Random Forest learns patterns
│    (ML Training)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Evaluate     │ ← Test accuracy, precision, recall
│    Performance  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 6. Deploy       │ ← Replace prod_model.bin if better
└─────────────────┘
```

## 🔄 Retraining Schedule

### Recommended Schedule

1. **Weekly** - Quick retrain with recent data
2. **Monthly** - Full retrain with expanded tickers
3. **After major market events** - Immediate retrain

### Automated Training (CI/CD)

Already configured in `.github/workflows/retrain.yml`:

- Runs every Monday at 2 AM
- Trains on expanded stock list
- Auto-deploys if accuracy improves

## 📊 Monitoring Training

### View Training History

```bash
# Start MLflow UI
mlflow ui

# Open browser to http://localhost:5000
# View all training runs, compare metrics
```

### Check Model Performance

```python
from market_predictor.trading import train_model
import joblib

# Load your model
model = joblib.load('models/prod_model.bin')

# Predict on new data
from market_predictor.trading import compute_features
features = compute_features(df)
predictions = model.predict(features)
probabilities = model.predict_proba(features)
```

## 🎓 Training Tips

### 1. **More Stocks = Better Model**

Add diverse stocks to your watchlist:

- Tech: AAPL, MSFT, GOOGL
- Finance: JPM, GS, UBS
- Energy: XOM, CVX
- Healthcare: JNJ, PFE

### 2. **More History = Better Predictions**

```python
# Good: 2 years
data = build_dataset(tickers, period="2y")

# Better: 5 years
data = build_dataset(tickers, period="5y")

# Best: Max available
data = build_dataset(tickers, period="max")
```

### 3. **Regular Retraining**

Markets change! Retrain monthly to adapt to:

- New market conditions
- Changing volatility
- Sector rotation
- Economic cycles

## 🐛 Troubleshooting

### "Dataset is empty"

**Fix**: Some tickers don't have enough history. Use period="5y" or add more tickers.

### "Training failed - not enough samples"

**Fix**: After calculating indicators and forward-looking labels, some rows are dropped. Add more tickers or longer period.

### "Model accuracy < 0.55"

**Fix**: This is expected! Stock prediction is hard. Anything > 0.55 is valuable for trading.

### "Out of memory"

**Fix**: Use fewer tickers, shorter period, or model_type="lgbm"

## 🚀 Advanced: Custom Training Script

Create `scripts/train_watchlist.py`:

```python
#!/usr/bin/env python3
"""Train model on all stocks from all watchlists."""

import sys
sys.path.insert(0, '.')

from market_predictor.database import WatchlistDB
from market_predictor.trading import build_dataset, train_model
from datetime import datetime
import os

def main():
    # Get all watchlists
    watchlists = WatchlistDB.get_user_watchlists('default_user')

    # Collect all unique tickers
    all_tickers = set()
    for wl in watchlists:
        tickers = WatchlistDB.get_watchlist_tickers(wl['id'], 'default_user')
        all_tickers.update(tickers)

    print(f"Training on {len(all_tickers)} stocks from your watchlists:")
    print(", ".join(sorted(all_tickers)))

    # Build dataset
    data = build_dataset(list(all_tickers), period="2y")

    if data.empty:
        print("ERROR: No data available")
        return

    print(f"Dataset shape: {data.shape}")

    # Train
    model_path = f"models/watchlist_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bin"
    os.makedirs("models", exist_ok=True)

    model, metrics = train_model(data, model_type="rf", save_path=model_path)

    print(f"✓ Model trained!")
    print(f"  Accuracy: {metrics['accuracy']:.2%}")
    print(f"  Precision: {metrics['precision']:.2%}")
    print(f"  Saved to: {model_path}")

    # Promote to production if accuracy > 0.55
    if metrics['accuracy'] > 0.55:
        import shutil
        shutil.copy(model_path, 'models/prod_model.bin')
        print(f"✓ Promoted to production!")

if __name__ == '__main__':
    main()
```

## 📚 Next Steps

1. **Run your first training**: `python training/trainer.py`
2. **Check MLflow UI**: `mlflow ui` (view at <http://localhost:5000>)
3. **Set up automated retraining**: Already configured in GitHub Actions!
4. **Monitor drift**: `python training/drift_check.py` weekly

---

**Pro Tip**: The more you use the app and add stocks to your watchlists, the better the model becomes for YOUR investment style! 🎯💰
