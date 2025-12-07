# 🎓 Model Training Guide

## Overview

Use the training utilities in this repository to build and compare models that power the ranking and simulation flows. The scripts rely on the same feature pipeline used by the backend so the artifacts are immediately usable.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional settings:
- `MLFLOW_TRACKING_URI` to change where runs are logged (defaults to `file:./mlruns`).
- `S3_BUCKET` to upload trained or promoted models after creation.

## 🚀 Train a Model

Train with the default tickers from the repository root:

```bash
python training/trainer.py
```

This downloads data, computes indicators, trains a Random Forest model, logs metrics to MLflow, and saves an artifact to `models/model_<timestamp>.bin`.

### Train with Your Watchlist

If you already have watchlists saved, reuse them for training:

```bash
python scripts/train_watchlist.py
```

The script will build a dataset from your watchlist tickers before training.

## ✅ Evaluate and Promote

Compare a newly trained model against the current production model and promote it if it performs better:

```bash
python training/evaluate_and_promote.py \
  --new-model models/model_<timestamp>.bin \
  --prod-model models/prod_model.bin \
  --tickers AAPL,MSFT,NVDA
```

The promotion step copies the better model to `models/prod_model.bin` and, when configured, uploads it to S3.

## ⚙️ Training Options

```python
from market_predictor.trading import build_dataset, train_model

# Build a dataset for custom tickers and history
symbols = ["AAPL", "MSFT", "GOOGL", "UBS"]
data = build_dataset(symbols, period="2y")

# Try different model types or hyperparameters
model, metrics = train_model(data, model_type="rf")
model, metrics = train_model(data, model_type="xgb")
model, metrics = train_model(
    data,
    model_type="rf",
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
)
```

## 🔄 When to Retrain

- Weekly or after major market events to keep signals fresh.
- When watchlists change materially.
- After backend feature changes that modify the dataset schema.

Keep the `models/` directory versioned so you can revert to a stable artifact if needed.
