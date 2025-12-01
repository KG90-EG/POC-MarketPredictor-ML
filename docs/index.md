# Trading-Fun Documentation

## Overview
Trading-Fun provides a lightweight ML pipeline for ranking stocks by probability of short-term outperformance. It includes:
- Feature engineering (RSI, SMA, MACD, Bollinger Bands, Momentum)
- Model training & evaluation scripts (with MLflow tracking)
- FastAPI service (prediction, ranking, model inventory)
- React frontend (optional)
- CI workflows (tests, lint, deployment)

## Quick Start
```bash
pip install -r requirements.txt
python trading_fun/trading.py --tickers AAPL,MSFT,NVDA --top-n 5
uvicorn trading_fun.server:app --reload
```

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health & model loaded flag |
| `/predict_raw` | POST | Probability from raw feature payload |
| `/predict_ticker/{ticker}` | GET | Fetch recent data, compute features, predict |
| `/ranking` | GET | Ranked probabilities for list of tickers |
| `/models` | GET | List available model artifacts |

## Model Lifecycle
1. `training/trainer.py` trains and saves timestamped models (`models/model_YYYYMMDD_HHMMSS.bin`).
2. `training/evaluate_and_promote.py` promotes if accuracy improves, updating `prod_model.bin`.
3. Drift detection script monitors baseline vs current distributions.

## S3 Artifacts (Optional)
Set `S3_BUCKET` and ensure `boto3` installed for automatic uploads during training & promotion.

## Frontend
Build with Vite:
```bash
cd frontend
npm ci
npm run build
```
Static assets served automatically if `frontend/dist` exists.

## Docker
Multi-stage Dockerfile builds frontend then runs API:
```bash
docker build -t trading-fun:latest .
docker run -p 8000:8000 trading-fun:latest
```

## Gunicorn (Production Option)
Run with process manager:
```bash
gunicorn -c gunicorn_conf.py trading_fun.server:app
```

## Pre-Commit Hooks
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Documentation

### Core Documentation
- [README](../README.md) - Main project documentation
- [SPEC](../SPEC.md) - Technical specification
- [DEPLOYMENT](../DEPLOYMENT.md) - Deployment guide
- [BACKLOG](../BACKLOG.md) - Project backlog and planned features

### Current Features
- [Production Features](PRODUCTION_FEATURES.md) - Production-ready capabilities
- [Frontend Components](FRONTEND_COMPONENTS.md) - React component library
- [Next Level Summary](NEXT_LEVEL_SUMMARY.md) - Advanced features

### Historical Documentation
- [History Index](history/README.md) - Archived implementation docs
- [Implementation Summary](history/IMPLEMENTATION_SUMMARY.md)
- [Architecture Review](history/ARCHITECTURE_REVIEW.md)
- [Improvements Guide](history/IMPROVEMENTS.md)

## Contributing
Open a PR from `dev` to `main`. Use the template and ensure CI passes. See [BACKLOG.md](../BACKLOG.md) for planned features and issues.

---
Generated docs are published via GitHub Pages workflow.