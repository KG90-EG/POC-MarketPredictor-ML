# Trading-Fun
Support Trading Decision, building a POC. Ideal, with Backend and Frontend

This repository contains a small machine learning pipeline and a reference frontend to generate a ranked list of tickers based on a model's probability of outperformance.

## Features
- 🤖 **ML-Powered Stock Ranking** - RandomForest/XGBoost models predict stock performance
- 📊 **Real-Time Market Data** - Live prices, volume, market cap via yfinance
- 🧠 **AI Analysis** - OpenAI-powered recommendations with retry logic and caching
- ⚛️ **Modern React UI** - Real-time updates with color-coded indicators and dark/light theme toggle
- 🌓 **Dark Mode Support** - Persistent theme toggle with smooth transitions
- 🔄 **CI/CD Pipeline** - Automated testing, linting, Docker builds
- 📈 **MLflow Integration** - Model tracking, versioning, and promotion
- 🐳 **Docker Support** - Multi-stage builds with frontend and backend

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
- `OPENAI_API_KEY`: OpenAI API key for LLM-powered analysis (required for `/analyze` endpoint)
- `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4o-mini`)

## LLM-Powered Analysis
The UI now includes AI-powered recommendations using OpenAI's API. To enable:

1. Set your API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

Or add it to `.env` file in the project root:
```
OPENAI_API_KEY=sk-proj-your-key-here
```

2. (Optional) Choose a different model:
```bash
export OPENAI_MODEL='gpt-4o'  # or gpt-3.5-turbo, etc.
```

3. Start the server and use the "Get AI Recommendations" button in the UI.

The `/analyze` endpoint accepts ranking data and optional user context to provide:
- Summary of top opportunities
- Risk considerations
- Actionable recommendations

**Features:**
- **Automatic retry logic**: Retries up to 3 times with exponential backoff on failures
- **Rate limit handling**: Returns clear error messages for OpenAI 429 errors
- **5-minute caching**: Identical requests within 5 minutes use cached results (reduces API calls)
- **User context**: Add custom context like "focus on tech stocks" or "conservative portfolio"

## Additional Endpoints
- `/models` — Lists available model artifact files and indicates the current production model
- `/ticker_info/{ticker}` — Fetch current price, change %, volume, and market cap
- `/analyze` — POST endpoint for LLM-powered stock analysis

## Search Ticker (New)
- Enter a ticker in the UI search input (e.g., `AMD`) and click Search.
- Backend endpoints used:
	- `GET /ticker_info/{ticker}`: live name, price, change %, volume, market cap
	- `GET /predict_ticker/{ticker}`: model probability for the ticker
- Results render in a panel showing all the above plus probability.
- Use this to explore tickers outside the ranking list.

## UI Features
- **Gradient Theme Design**: Purple gradient background with clean, modern card-based layout
- **Dark/Light Mode Toggle**: Click the sun/moon icon in the header to switch themes
  - Theme preference is automatically saved to localStorage
  - Smooth transitions between themes
  - Optimized color schemes for both modes
- **Rank Badges**: Top 3 stocks get special gold/silver/bronze styling
- **Real-Time Updates**: Live market data with color-coded positive/negative indicators
- **Search Functionality**: Quick ticker lookup with Enter key support
- **Loading States**: Animated spinners for better user experience

## Integration Tests
Added `test_integration_server.py` to validate `/health` and `/models` using a temporary dummy model.
Run all tests:
```bash
python -m pytest -q
```

## Gunicorn (Production Option)
Use process management for higher concurrency:
```bash
gunicorn -c gunicorn_conf.py trading_fun.server:app
```

## Documentation Site
Markdown docs in `docs/` deployed to GitHub Pages via `.github/workflows/pages.yml`. After enabling Pages for the repository (Settings -> Pages) the workflow publishes updates on pushes to `main`.

