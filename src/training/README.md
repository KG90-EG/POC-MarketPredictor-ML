# ML Training Pipeline

> Part of FR-004: Automated ML Training Pipeline

This module provides automated model training, validation, and deployment for the
MarketPredictor ML system.

## Overview

The training pipeline supports:
- **Automated weekly retraining** via GitHub Actions
- **Hyperparameter optimization** using Optuna
- **Model versioning** with MLflow tracking
- **Automatic validation** against production metrics
- **Safe promotion** to production with rollback capability

## Quick Start

```bash
# Standard training
python scripts/train_production.py

# With hyperparameter optimization
python scripts/train_production.py --optimize --trials 50

# Dry run (no promotion)
python scripts/train_production.py --dry-run

# Force training with lower threshold
python scripts/train_production.py --force --min-accuracy 0.55
```

## Training Script Options

```
Usage: python scripts/train_production.py [OPTIONS]

Options:
  --optimize              Run hyperparameter optimization before training
  --trials N              Number of optimization trials (default: 20)
  --period PERIOD         Historical data period: 1y, 2y, 3y, 5y, 10y (default: 5y)
  --force                 Force training even if current model is better
  --min-accuracy FLOAT    Minimum accuracy for production promotion (default: 0.60)
  --model-type TYPE       Model type: xgb, rf, lgb (default: xgb)
  --log-level LEVEL       Logging level: DEBUG, INFO, WARNING, ERROR
  --dry-run               Run training but don't promote to production
  --output-json PATH      Write training results as JSON
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Training failed (dataset error, model error) |
| 2 | Validation failed (metrics below threshold) |
| 3 | Configuration error (invalid arguments) |

## Automated Training (GitHub Actions)

Training runs automatically via `.github/workflows/train-model.yml`:

- **Schedule**: Every Sunday at 02:00 UTC
- **Manual trigger**: Via GitHub Actions UI with configurable options
- **Inputs**:
  - `force_retrain`: Skip comparison with current model
  - `optimization_trials`: Number of Optuna trials
  - `skip_validation`: Skip backtesting validation

### Manual Trigger

```bash
# Via GitHub CLI
gh workflow run train-model.yml \
  -f force_retrain=true \
  -f optimization_trials=30
```

## Model Versioning

Models are stored with timestamps:

```
models/
├── prod_model.bin          # Current production model
├── model_20250127_143022.bin  # Timestamped versions
├── model_20250120_020015.bin
└── ...
```

### MLflow Tracking

All training runs are tracked in MLflow:

```bash
# View MLflow UI
mlflow ui --port 5000
```

Tracked metrics:
- `accuracy`, `precision`, `recall`, `f1`
- `n_samples`, `n_features`
- Model artifacts and parameters

## Model Architecture

### Default: XGBoost

```python
XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric='logloss'
)
```

### Feature Set

The model uses 20+ technical features:
- **Momentum**: RSI, MACD, Stochastic, ROC
- **Volatility**: ATR, Bollinger Bands, Standard Deviation
- **Volume**: OBV, VWAP, Volume SMA
- **Trend**: ADX, Moving Averages (SMA, EMA)

## Validation Pipeline

New models are validated before promotion:

1. **Backtest**: Run on last 6 months of data
2. **Metric comparison**: Must meet minimum thresholds
3. **Production comparison**: Compare with current prod model
4. **Report generation**: Generate comparison report

### Validation Thresholds

| Metric | Minimum |
|--------|---------|
| Accuracy | 60% |
| Precision | 55% |
| Recall | 50% |
| F1 Score | 52% |

## Hyperparameter Optimization

Uses Optuna for Bayesian optimization:

```bash
python scripts/train_production.py --optimize --trials 50
```

### Search Space

| Parameter | Range |
|-----------|-------|
| n_estimators | 50-300 |
| max_depth | 3-10 |
| learning_rate | 0.01-0.3 |
| min_child_weight | 1-10 |
| subsample | 0.6-1.0 |
| colsample_bytree | 0.6-1.0 |

Optimal hyperparameters are saved to `best_hyperparameters.json`.

## Rollback

If a new model causes issues:

```bash
# List available models
ls -la models/model_*.bin

# Rollback to specific version
python scripts/rollback_model.py --version 20250120_020015

# Or manually
cp models/model_20250120_020015.bin models/prod_model.bin
make restart
```

## Monitoring

Training logs are saved to:
- Console output (structured)
- `logs/training.log` (JSON format)
- MLflow UI (metrics dashboard)

### JSON Log Format

```json
{
  "timestamp": "2025-01-27T14:30:22.123456",
  "level": "INFO",
  "message": "Training complete - Accuracy: 67.50%",
  "module": "train_production",
  "function": "train_and_evaluate",
  "metrics": {
    "accuracy": 0.675,
    "precision": 0.682,
    "recall": 0.671,
    "f1": 0.676
  }
}
```

## Troubleshooting

### Dataset Build Fails

```
ERROR: Dataset is empty after build_dataset
```

**Solutions**:
1. Check internet connection
2. Verify Yahoo Finance API is accessible
3. Try with fewer stocks: `--period 1y`

### Training Fails

```
ERROR: Training failed - insufficient data
```

**Solutions**:
1. Use longer data period: `--period 5y`
2. Check class distribution in data
3. Try different model type: `--model-type rf`

### Validation Fails

```
Model NOT promoted - accuracy below threshold
```

**Solutions**:
1. Lower threshold: `--min-accuracy 0.55`
2. Force promotion: `--force`
3. Run optimization: `--optimize --trials 50`

## API Reference

### `scripts/train_production.py`

Main training script with CLI interface.

### `scripts/validate_model.py`

Standalone validation script for backtesting.

### `scripts/rollback_model.py`

Model version rollback utility.

### `scripts/optimize_hyperparams.py`

Hyperparameter optimization with Optuna.

## See Also

- [TRADER_GUIDE.md](../../docs/TRADER_GUIDE.md) - User-facing documentation
- [ADR-002](../../docs/architecture/ADR-002-model-training-strategy.md) - Architecture decision
- [train-model.yml](../../.github/workflows/train-model.yml) - GitHub Actions workflow
