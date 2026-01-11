# 🤖 ML Model Retraining Guide

**Market Predictor ML - Local Retraining & Model Management**

Version: 1.0 | Last Updated: 2026-01-11

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [When to Retrain](#when-to-retrain)
3. [Quick Start](#quick-start)
4. [Training Pipeline](#training-pipeline)
5. [Feature Engineering](#feature-engineering)
6. [Hyperparameter Tuning](#hyperparameter-tuning)
7. [Model Evaluation](#model-evaluation)
8. [Deployment Workflow](#deployment-workflow)
9. [Monitoring & Alerts](#monitoring--alerts)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What is Model Retraining?

The ML models powering Market Predictor need periodic retraining to:
- **Adapt to market changes:** New patterns emerge (e.g., 2024 AI boom, 2023 rate hikes)
- **Incorporate new data:** Fresh price action, earnings, macro indicators
- **Improve accuracy:** Fix prediction drift as market regimes shift

### Current Models

| Model | Algorithm | Purpose | Retrain Frequency |
|-------|-----------|---------|-------------------|
| **Price Predictor** | XGBoost | Predict 5-day forward returns | Monthly |
| **Regime Classifier** | Random Forest | Classify Risk-On/Neutral/Risk-Off | Quarterly |
| **Momentum Ranker** | LightGBM | Rank stocks by momentum strength | Monthly |

### Model Lifecycle

```
Data Collection → Feature Engineering → Training → Validation → 
  Hyperparameter Tuning → Evaluation → Deployment → Monitoring → Retrain
```

---

## ⏰ When to Retrain

### Scheduled Retraining

**Monthly (Recommended):**
- Price Predictor
- Momentum Ranker

**Quarterly:**
- Regime Classifier (more stable, less frequent changes)

**After Major Events:**
- Market crashes (VIX > 40)
- Policy changes (Fed pivot, new regulations)
- Structural shifts (sector rotation, new market dynamics)

### Drift Detection Signals

**Retrain immediately if you see:**

1. **Prediction Accuracy Drop:**
   ```
   Current Accuracy: 58%
   Historical Baseline: 68%
   Drift: -10% → RETRAIN NOW
   ```

2. **Calibration Mismatch:**
   - Model predicts 70% upside → Actual: 45% upside
   - Systematic over-optimism or pessimism

3. **Feature Drift:**
   - RSI distribution changed (mean shifted by >10%)
   - Correlation breakdown (e.g., VIX no longer predicts returns)

4. **Regime Misclassification:**
   - Model says "Risk-On" but market crashes next week
   - Persistent lag in regime detection (>3 days)

### Monitoring Dashboard

Check these metrics weekly:

```bash
# Run model performance report
python src/training/evaluate_drift.py

# Output
===== Model Drift Report =====
Price Predictor:
  - Accuracy: 65% (baseline: 68%, drift: -3%)
  - Calibration: 0.92 (good)
  - Feature Drift: Low

Regime Classifier:
  - Accuracy: 78% (baseline: 82%, drift: -4%)
  - Calibration: 0.88 (acceptable)
  - Feature Drift: Medium → RETRAIN RECOMMENDED

Momentum Ranker:
  - Spearman Correlation: 0.75 (baseline: 0.72, improvement: +3%)
  - Feature Drift: Low
```

**Decision Rules:**
- **Drift < 5%:** Continue monitoring
- **Drift 5-10%:** Plan retrain within 2 weeks
- **Drift > 10%:** Retrain immediately

---

## 🚀 Quick Start

### Prerequisites

```bash
# Ensure Python environment is active
source venv/bin/activate  # or conda activate market-predictor

# Install required packages
pip install -r requirements.txt

# Verify MLflow is running
mlflow ui --port 5000
# Open: http://localhost:5000
```

### 1-Command Retrain

```bash
# Retrain all models with default settings
python src/training/train_all_models.py --region US --timeframe 5y

# Expected output:
# ✅ Data collected: 500 stocks, 1250 days
# ✅ Features engineered: 45 features
# ✅ Price Predictor trained: 68% accuracy
# ✅ Regime Classifier trained: 82% accuracy
# ✅ Momentum Ranker trained: 0.75 Spearman
# ✅ Models saved to: models/
# ✅ MLflow run: http://localhost:5000/#/experiments/1/runs/abc123
```

### Training Individual Models

```bash
# Price Predictor only
python src/training/train_price_predictor.py --region US --n_estimators 500

# Regime Classifier only
python src/training/train_regime_classifier.py --lookback 30

# Momentum Ranker only
python src/training/train_momentum_ranker.py --features extended
```

---

## 🔧 Training Pipeline

### Step-by-Step Process

#### Step 1: Data Collection

**Script:** `src/data/data_collector.py`

```bash
# Collect historical data
python src/data/data_collector.py \
  --tickers "AAPL,MSFT,GOOGL" \
  --start_date "2019-01-01" \
  --end_date "2024-12-31" \
  --output data/training/raw_prices.parquet
```

**What it does:**
- Fetches OHLCV data from yFinance
- Downloads S&P 500, VIX, US10Y
- Saves to Parquet format (fast, compressed)

**Output:**
```
data/training/
  raw_prices.parquet      # 500 stocks × 1250 days
  market_data.parquet     # S&P 500, VIX, US10Y
  metadata.json           # Collection timestamp, tickers
```

---

#### Step 2: Feature Engineering

**Script:** `src/training/feature_engineering.py`

```bash
# Generate features
python src/training/feature_engineering.py \
  --input data/training/raw_prices.parquet \
  --output data/training/features.parquet \
  --feature_set extended
```

**Feature Categories:**

**1. Technical Indicators (45 features):**
- Trend: SMA20, SMA50, EMA12, EMA26, MACD, MACD Signal
- Momentum: RSI, ROC, MOM, Williams %R
- Volatility: Bollinger Bands, ATR, Historical Volatility
- Volume: OBV, Volume SMA, Volume Spike
- Price Patterns: Candlestick patterns, support/resistance

**2. Statistical Features (12 features):**
- Returns: 1-day, 5-day, 20-day
- Rolling statistics: Mean, std, skew, kurtosis
- Z-scores: Price vs 20-day mean

**3. Market Context (8 features):**
- VIX level & change
- S&P 500 trend & momentum
- US10Y yield & change
- Sector performance

**4. Derived Features (10 features):**
- Price vs SMA20 (%)
- RSI divergence
- Volume vs average
- Volatility regime

**Example Code:**
```python
from src.training.feature_engineering import FeatureEngineer

engineer = FeatureEngineer()

# Load raw data
df = pd.read_parquet("data/training/raw_prices.parquet")

# Generate features
features = engineer.create_features(
    df,
    feature_set="extended",  # or "basic"
    fill_method="forward"     # forward fill NaNs
)

# Save
features.to_parquet("data/training/features.parquet")
```

---

#### Step 3: Training

**Script:** `src/training/train_price_predictor.py`

```bash
# Train with hyperparameter tuning
python src/training/train_price_predictor.py \
  --input data/training/features.parquet \
  --target_days 5 \
  --threshold 0.02 \
  --tune \
  --n_trials 50
```

**Configuration:**

```python
# src/training/train_price_predictor.py
config = {
    "algorithm": "xgboost",
    "target": "5-day forward return",
    "classification_threshold": 0.02,  # +2% = BUY, -2% = SELL
    "train_test_split": 0.8,
    "validation_split": 0.1,
    "hyperparameters": {
        "n_estimators": 500,
        "max_depth": 7,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3
    }
}
```

**Training Process:**

1. **Load features:** Read from `features.parquet`
2. **Create target:** Calculate 5-day forward returns
3. **Split data:**
   - Train: 80% (oldest data)
   - Validation: 10% (middle data)
   - Test: 10% (newest data)
4. **Train model:** XGBoost classifier
5. **Validate:** Check accuracy on validation set
6. **Evaluate:** Final metrics on test set
7. **Save:** Export model to `models/price_predictor.pkl`

**Output:**
```
===== Training Complete =====
Model: Price Predictor (XGBoost)
Target: 5-day forward return > 2%

Training Set:
  Accuracy: 72%
  Precision: 68%
  Recall: 75%

Validation Set:
  Accuracy: 69%
  Precision: 65%
  Recall: 72%

Test Set:
  Accuracy: 68%
  Precision: 64%
  Recall: 70%

Saved to: models/price_predictor_2026-01-11.pkl
MLflow Run: http://localhost:5000/#/experiments/1/runs/abc123
```

---

#### Step 4: Validation

**Script:** `src/training/validate_model.py`

```bash
# Validate on out-of-sample data
python src/training/validate_model.py \
  --model models/price_predictor_2026-01-11.pkl \
  --test_data data/training/features_test.parquet
```

**Validation Checks:**

1. **Accuracy:** > 60% on test set
2. **Calibration:** Predicted probabilities match actual outcomes
3. **Stability:** Performance consistent across time periods
4. **Feature Importance:** No single feature dominates (>30%)

**Example Output:**
```
===== Validation Report =====
Model: Price Predictor

✅ Accuracy: 68% (threshold: 60%)
✅ Calibration: 0.92 (excellent)
✅ Stability: CV std = 3% (acceptable)
✅ Feature Importance: Top feature = 18% (good)

Top 5 Features:
1. RSI (18%)
2. MACD Signal (15%)
3. Price vs SMA20 (12%)
4. Volume Spike (10%)
5. VIX Change (9%)

Recommendation: ✅ DEPLOY
```

---

## 🎯 Feature Engineering

### Feature Creation Best Practices

#### 1. Domain Knowledge First

**Good Features (Based on Trading Logic):**
```python
# Price momentum
df['momentum_5d'] = df['close'].pct_change(5)
df['momentum_20d'] = df['close'].pct_change(20)

# Trend strength
df['sma20'] = df['close'].rolling(20).mean()
df['price_vs_sma20'] = (df['close'] - df['sma20']) / df['sma20']

# Volatility regime
df['volatility_20d'] = df['close'].pct_change().rolling(20).std()
df['volatility_regime'] = pd.qcut(df['volatility_20d'], q=3, labels=['low', 'medium', 'high'])
```

**Bad Features (No Economic Meaning):**
```python
# ❌ Don't do this
df['random_feature'] = df['close'] * df['volume'] / df['open']  # No logic
df['weird_ratio'] = df['high'] ** 2 / df['low']  # Makes no sense
```

#### 2. Avoid Data Leakage

**Leakage Example (WRONG):**
```python
# ❌ Using future data
df['future_return'] = df['close'].shift(-5).pct_change(5)
df['will_go_up'] = df['future_return'] > 0  # This is the TARGET, not a feature!
```

**Correct Approach:**
```python
# ✅ Only use past data
df['past_return_5d'] = df['close'].pct_change(5)
df['past_volatility'] = df['close'].pct_change().rolling(20).std()
```

#### 3. Handle Missing Values

```python
# Forward fill (use last known value)
df['rsi'] = df['rsi'].fillna(method='ffill')

# Fill with neutral value
df['macd'] = df['macd'].fillna(0)

# Drop if >50% missing
if df['feature'].isna().sum() / len(df) > 0.5:
    df.drop('feature', axis=1, inplace=True)
```

#### 4. Feature Scaling

```python
from sklearn.preprocessing import StandardScaler

# Standardize features (mean=0, std=1)
scaler = StandardScaler()
df[['rsi', 'macd', 'volume']] = scaler.fit_transform(df[['rsi', 'macd', 'volume']])
```

---

## 🔬 Hyperparameter Tuning

### Automated Tuning with Optuna

**Script:** `src/training/tune_hyperparameters.py`

```bash
# Run 50 trials to find best hyperparameters
python src/training/tune_hyperparameters.py \
  --model price_predictor \
  --n_trials 50 \
  --timeout 3600
```

**What it does:**
1. Defines search space (e.g., `n_estimators: 100-1000`)
2. Trains model with different hyperparameters
3. Evaluates accuracy on validation set
4. Finds best combination

**Example Code:**
```python
import optuna
from xgboost import XGBClassifier

def objective(trial):
    # Define search space
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
    }
    
    # Train model
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_val, y_val)
    
    return accuracy

# Run optimization
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)

# Best hyperparameters
print("Best params:", study.best_params)
print("Best accuracy:", study.best_value)
```

**Output:**
```
[I 2026-01-11 10:00:00] Trial 0 finished with value: 0.65
[I 2026-01-11 10:02:15] Trial 1 finished with value: 0.67
...
[I 2026-01-11 11:30:00] Trial 49 finished with value: 0.68

Best hyperparameters:
{
  'n_estimators': 450,
  'max_depth': 7,
  'learning_rate': 0.048,
  'subsample': 0.82,
  'colsample_bytree': 0.75
}

Best validation accuracy: 69.2%
```

**Save Best Hyperparameters:**
```bash
# Saved to: best_hyperparameters.json
{
  "price_predictor": {
    "n_estimators": 450,
    "max_depth": 7,
    "learning_rate": 0.048,
    "subsample": 0.82,
    "colsample_bytree": 0.75,
    "validation_accuracy": 0.692,
    "tuned_at": "2026-01-11T11:30:00Z"
  }
}
```

---

## 📊 Model Evaluation

### Metrics to Track

#### Classification Metrics

**For Price Predictor (BUY/SELL/HOLD):**

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Predictions
y_pred = model.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"Accuracy: {accuracy:.2%}")
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print(f"F1 Score: {f1:.2%}")
```

**Confusion Matrix:**
```
Actual \ Predicted | BUY  | HOLD | SELL |
-------------------|------|------|------|
BUY                | 120  |  30  |  10  |
HOLD               |  25  | 180  |  15  |
SELL               |  10  |  35  | 105  |

Interpretation:
- BUY precision: 120/(120+25+10) = 77%
- SELL recall: 105/(10+15+105) = 81%
```

#### Regression Metrics

**For Momentum Ranker (Continuous Scores):**

```python
from scipy.stats import spearmanr

# Predicted ranks
predicted_scores = model.predict(X_test)

# Actual returns
actual_returns = y_test

# Rank correlation
correlation, p_value = spearmanr(predicted_scores, actual_returns)

print(f"Spearman Correlation: {correlation:.3f}")
print(f"P-value: {p_value:.5f}")

# Goal: Correlation > 0.70
```

#### Financial Metrics

**Backtest Performance:**

```python
from src.backtest.historical_validator import HistoricalBacktester

# Run backtest
backtester = HistoricalBacktester(model)
results = backtester.run(
    start_date="2024-01-01",
    end_date="2024-12-31",
    initial_capital=100000
)

# Metrics
print(f"Total Return: {results.total_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.max_drawdown:.2%}")
print(f"Win Rate: {results.win_rate:.2%}")

# Goal: Sharpe > 1.0, Drawdown < 15%
```

---

## 🚢 Deployment Workflow

### Step-by-Step Deployment

#### 1. Evaluate New Model

```bash
# Compare new vs old model
python src/training/compare_models.py \
  --old_model models/price_predictor_old.pkl \
  --new_model models/price_predictor_2026-01-11.pkl \
  --test_data data/training/features_test.parquet
```

**Output:**
```
===== Model Comparison =====

Old Model (2025-12-01):
  Accuracy: 65%
  Sharpe: 1.15
  Drawdown: 12%

New Model (2026-01-11):
  Accuracy: 68% (+3%)
  Sharpe: 1.45 (+0.30)
  Drawdown: 8.5% (-3.5%)

Recommendation: ✅ DEPLOY NEW MODEL
```

#### 2. Backup Current Model

```bash
# Backup before deployment
cp models/price_predictor.pkl models/backups/price_predictor_2025-12-01.pkl
cp models/regime_classifier.pkl models/backups/regime_classifier_2025-12-01.pkl
```

#### 3. Deploy New Model

```bash
# Copy to production path
cp models/price_predictor_2026-01-11.pkl models/price_predictor.pkl

# Restart server to load new model
pm2 restart market-predictor-api

# Or manually
pkill -f "uvicorn src.trading_engine.server:app"
uvicorn src.trading_engine.server:app --host 0.0.0.0 --port 8000
```

#### 4. Smoke Test

```bash
# Test prediction endpoint
curl http://localhost:8000/api/predict/AAPL

# Expected: 200 OK with predictions
{
  "ticker": "AAPL",
  "prediction": {
    "probability": 0.78,
    "signal": "BUY"
  }
}
```

#### 5. Monitor Performance

```bash
# Check logs
tail -f logs/predictions.log

# Monitor accuracy (compare predictions vs actual outcomes)
python src/monitoring/track_accuracy.py --window 7d
```

---

## 📡 Monitoring & Alerts

### MLflow Tracking

**All training runs logged to MLflow:**

```bash
# Start MLflow UI
mlflow ui --port 5000

# Open: http://localhost:5000
```

**What's tracked:**
- Hyperparameters
- Metrics (accuracy, precision, recall)
- Feature importance
- Model artifacts

**Compare Runs:**
```python
import mlflow

# Load runs
runs = mlflow.search_runs(experiment_ids=["1"])

# Compare accuracy
print(runs[['params.n_estimators', 'metrics.accuracy']].sort_values('metrics.accuracy', ascending=False))
```

---

### Drift Detection Alerts

**Script:** `src/monitoring/drift_detector.py`

**Run daily:**
```bash
# Cron job (daily at 6 AM)
0 6 * * * cd /path/to/POC-MarketPredictor-ML && python src/monitoring/drift_detector.py
```

**What it checks:**
1. **Prediction accuracy** (last 7 days vs baseline)
2. **Feature drift** (distribution changes)
3. **Calibration** (predicted probabilities vs actual outcomes)

**Alert Example:**
```
⚠️ DRIFT ALERT ⚠️
Model: Price Predictor
Issue: Accuracy dropped to 58% (baseline: 68%, drift: -10%)
Action: RETRAIN IMMEDIATELY

Details:
- Last 7 days accuracy: 58%
- Last 30 days accuracy: 62%
- Calibration: 0.78 (poor)
- Feature drift: High (RSI distribution shifted)

Recommendation: Run full retrain with latest data
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Training Takes Too Long

**Problem:** Training stuck at 10% for 30 minutes

**Solutions:**
```bash
# Reduce dataset size
python src/training/train_price_predictor.py --sample_size 0.5  # Use 50% of data

# Reduce hyperparameter search space
python src/training/tune_hyperparameters.py --n_trials 10  # Instead of 50

# Use fewer features
python src/training/feature_engineering.py --feature_set basic  # 20 features instead of 75
```

---

#### 2. Model Accuracy Too Low

**Problem:** Test accuracy = 52% (barely better than random)

**Diagnosis:**
```bash
# Check feature importance
python src/training/feature_importance.py --model models/price_predictor.pkl

# If top 5 features contribute < 50%, features are weak
```

**Solutions:**
1. **Add more features:** Include macro indicators (unemployment, GDP)
2. **Increase training data:** Train on 10 years instead of 5
3. **Try different algorithm:** Switch from XGBoost to LightGBM
4. **Change target:** Instead of 5-day return, try 3-day or 10-day

---

#### 3. Model Overfitting

**Problem:** Train accuracy = 95%, Test accuracy = 60%

**Solutions:**
```python
# Increase regularization
params = {
    'max_depth': 5,  # Reduce from 10
    'min_child_weight': 5,  # Increase from 3
    'subsample': 0.7,  # Reduce from 0.9
    'colsample_bytree': 0.7  # Reduce from 0.9
}

# Or enable early stopping
model = XGBClassifier(
    **params,
    early_stopping_rounds=10
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)])
```

---

#### 4. Predictions Not Loading in API

**Problem:** Server returns 500 error when calling `/api/predict/AAPL`

**Diagnosis:**
```bash
# Check server logs
tail -f logs/server.log

# Look for:
# FileNotFoundError: models/price_predictor.pkl not found
```

**Solution:**
```bash
# Verify model exists
ls -lh models/

# If missing, retrain or restore backup
cp models/backups/price_predictor_2025-12-01.pkl models/price_predictor.pkl

# Restart server
pm2 restart market-predictor-api
```

---

## 📚 Advanced Topics

### Ensemble Models

**Combine multiple models for better predictions:**

```python
from sklearn.ensemble import VotingClassifier

# Create ensemble
ensemble = VotingClassifier(
    estimators=[
        ('xgboost', xgb_model),
        ('random_forest', rf_model),
        ('lightgbm', lgbm_model)
    ],
    voting='soft'  # Use probabilities
)

# Train
ensemble.fit(X_train, y_train)

# Predict
predictions = ensemble.predict(X_test)
```

---

### Online Learning (Incremental Training)

**Update model with new data without full retrain:**

```python
import joblib

# Load existing model
model = joblib.load('models/price_predictor.pkl')

# Incremental update (only for compatible models)
model.fit(X_new, y_new, xgb_model=model.get_booster())

# Save updated model
joblib.dump(model, 'models/price_predictor.pkl')
```

**Note:** XGBoost doesn't support true online learning. Use LightGBM or retrain from scratch.

---

### Feature Selection

**Remove weak features to improve performance:**

```python
from sklearn.feature_selection import SelectKBest, mutual_info_classif

# Select top 30 features
selector = SelectKBest(mutual_info_classif, k=30)
X_selected = selector.fit_transform(X_train, y_train)

# Get selected feature names
selected_features = X_train.columns[selector.get_support()]
print(selected_features)
```

---

## 🎯 Quick Reference

### Training Commands

```bash
# Full retrain (all models)
python src/training/train_all_models.py --region US --timeframe 5y

# Price Predictor only
python src/training/train_price_predictor.py --tune --n_trials 50

# Regime Classifier only
python src/training/train_regime_classifier.py --lookback 30

# Hyperparameter tuning
python src/training/tune_hyperparameters.py --model price_predictor --n_trials 50

# Validate model
python src/training/validate_model.py --model models/price_predictor.pkl
```

### Monitoring Commands

```bash
# Check drift
python src/monitoring/drift_detector.py

# Compare models
python src/training/compare_models.py --old_model models/old.pkl --new_model models/new.pkl

# View MLflow runs
mlflow ui --port 5000
```

### Deployment Commands

```bash
# Backup models
cp models/*.pkl models/backups/

# Deploy new model
cp models/price_predictor_2026-01-11.pkl models/price_predictor.pkl

# Restart server
pm2 restart market-predictor-api
```

---

## 📞 Support

**Issues:** [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

**MLflow UI:** http://localhost:5000

**Documentation:** See `docs/architecture/ADR-002-model-training-strategy.md`

---

**Happy Training! 🚀**

*Last Updated: 2026-01-11*
