# Trading-Fun
Support Trading Decision

This repository contains a small machine learning pipeline and a reference frontend to generate a ranked list of tickers based on a model's probability of outperformance.

Quick summary:
- `trading_fun/` — Python package implementing data loading, features, model training, prediction, and a FastAPI server.
- `training/` — Retrain scripts, trainer and utilities (MLflow integration, drift-check, promotion)
- `backtest/` — A very small backtesting helper to simulate buy-hold trades.
- `frontend/` — React UI using Vite that shows ranked tickers from the backend `/ranking` endpoint.
- `01_Trading_Fun/` — Copied legacy content and tests
- `archive/` — Files archived and not used by the main flow

How to push to GitHub and PR (simple flow):
1. Make sure you have a GitHub repo: `KG90-EG/Trading-Fun`.
2. Commit & push on `dev` branch (we already created `dev` and pushed the changes):
```bash
git checkout dev
git add .
git commit -m "WIP: features + frontend"
git push -u origin dev
```
3. Open a PR to `main` using the web link (or `gh` CLI):
```
https://github.com/KG90-EG/Trading-Fun/pull/new/dev
```
4. Review & Merge PR (squash or merge commit) — GitHub Actions will run CI.

Deployment tips:
- Add GitHub secrets: `MLFLOW_TRACKING_URI`, `CR_PAT`, and `S3_BUCKET` if you wish to upload models.
- Configure your production environment to use `models/prod_model.bin` as the production model.

## Lint & Format
Run lint and format checks locally (CI enforces these):
```bash
python -m pip install flake8 black
flake8 . --max-line-length=120
black --check .
```
Auto-format:
```bash
black .
```

## Static Frontend Serving
After building the React app, the FastAPI server will serve it automatically if `frontend/dist` exists.
Build frontend:
```bash
cd frontend
npm ci
npm run build
```
Run API (serves static files):
```bash
uvicorn trading_fun.server:app --reload
```

Access in browser at `http://127.0.0.1:8000` (index served) or development mode via Vite `npm run dev` at `http://localhost:5173`.

## PR Template
A reusable PR template lives at `.github/PULL_REQUEST_TEMPLATE.md`.

## Pre-Commit Hooks
Install and activate:
```bash
pip install pre-commit
pre-commit install
```
Run on all files:
```bash
pre-commit run --all-files
```

## Optional S3 Model Upload
Set `S3_BUCKET` and install `boto3` (already in requirements). Training and promotion scripts will upload model artifacts:
```bash
export S3_BUCKET=my-bucket
python training/trainer.py
```

## Multi-Stage Docker Build
The `Dockerfile` builds the frontend then serves via uvicorn.
Build locally:
```bash
docker build -t trading-fun:latest .
docker run -p 8000:8000 trading-fun:latest
```
Visit `http://localhost:8000`.

## Netlify Frontend Deployment
Add secrets `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` in GitHub, the workflow `.github/workflows/deploy-frontend.yml` deploys on pushes to `main`.

## Environment Variables Summary
- `MLFLOW_TRACKING_URI`: MLflow backend (file:./mlruns by default)
- `PROD_MODEL_PATH`: Path to production model file (default `models/prod_model.bin`)
- `S3_BUCKET`: Optional S3 bucket for artifact upload
- `NETLIFY_AUTH_TOKEN` / `NETLIFY_SITE_ID`: Netlify deploy workflow secrets
- `CR_PAT`: GitHub Container Registry auth token for Docker image push



