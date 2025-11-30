# Trading-Fun
Support Trading Decision, building a POC. Ideal, with Backend and Frontend

This repository contains a small machine learning pipeline and a reference frontend to generate a ranked list of tickers based on a model's probability of outperformance.

## Features
- 🤖 **ML-Powered Stock Ranking** - RandomForest/XGBoost models predict stock performance
- 📊 **Real-Time Market Data** - Live prices, volume, market cap via yfinance
- 🚀 **Auto-Load Rankings** - Top 50 popular stocks ranked automatically on page load
- 📄 **Pagination** - Clean 10-per-page display with easy navigation
- 🎯 **Automated Buy/Sell Signals** - Python-based recommendation engine with 5-tier signal system
- 🧠 **AI Analysis** - OpenAI-powered trading recommendations with retry logic and caching
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

## Quick Start

### First Time Setup
1. **Install dependencies:**
```bash
pip install -r requirements.txt
cd frontend && npm install
```

2. **Start the backend:**
```bash
uvicorn trading_fun.server:app --reload
```

3. **Start the frontend (in new terminal):**
```bash
cd frontend && npm run dev
```

4. **Open browser:** Navigate to `http://localhost:5173`
   - Rankings load automatically showing top 50 stocks
   - Browse paginated results (10 per page)
   - Click any stock for detailed analysis
   - Use search to look up specific stocks

### What You'll See
- **Immediate Rankings**: Top 50 popular stocks ranked by AI prediction (no manual entry needed)
- **Buy/Sell Signals**: Each stock shows STRONG BUY, BUY, HOLD, or SELL recommendation
- **Live Market Data**: Real-time prices, changes, volumes, and market caps
- **Pagination**: Clean 10-per-page display with easy navigation
- **AI Analysis**: Optional OpenAI-powered recommendations (requires API key)

## How to push to GitHub and PR (simple flow):
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

## Automated Trading Recommendations

The system provides a **dual-layer recommendation engine** combining algorithmic signals with AI-powered analysis:

### 1. Python-Based Buy/Sell Signals

The backend automatically generates trading signals based on ML model probability scores:

- **STRONG BUY** (≥65%): High confidence buy opportunity
- **BUY** (≥55%): Good buying opportunity
- **HOLD** (45-54%): Maintain current position
- **CONSIDER SELLING** (35-44%): Weak position, consider exit
- **SELL** (<35%): Exit recommended

These signals are computed in Python and provide immediate, algorithmic guidance even without LLM analysis.

### 2. AI-Powered Analysis

The `/analyze` endpoint enriches signals with comprehensive market context:

**Market Data Included:**
- Stock name and current price
- Price change percentage
- Trading volume and market capitalization
- P/E ratio and valuation metrics
- 52-week high/low ranges
- Python-generated buy/sell signals

**AI Recommendations Include:**
1. **TOP 3 BUY RECOMMENDATIONS** - Specific stocks to buy NOW with reasoning
2. **SELL/AVOID** - Stocks to exit or avoid with justification
3. **KEY RISKS** - Important market risks to monitor
4. **ACTION PLAN** - Clear, concrete next steps for investors

### Setup Instructions

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

**Enhanced Features:**
- **Automatic retry logic**: Retries up to 3 times with exponential backoff on failures
- **Rate limit handling**: Returns clear error messages for OpenAI 429 errors
- **5-minute caching**: Identical requests within 5 minutes use cached results (reduces API calls)
- **Rich market context**: Includes prices, volumes, P/E ratios, and technical signals
- **Actionable output**: Specific buy/sell recommendations, not just analysis
- **User context**: Add custom context like "focus on tech stocks" or "conservative portfolio"

## API Endpoints

### Core Endpoints
- `GET /health` — Health check with model status
- `GET /ranking?tickers=` — Rank stocks by ML probability
  - **Default behavior**: When called without tickers parameter (or empty), automatically ranks 50 popular large-cap stocks including:
    - Tech: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, AMD, NFLX, ADBE, CRM, ORCL, INTC, CSCO, IBM, QCOM
    - Finance: JPM, BAC, WFC, V, MA
    - Healthcare: JNJ, UNH, LLY, ABBV, MRK, TMO, ABT
    - Consumer: WMT, PG, KO, PEP, COST, MCD, NKE, DIS, PM
    - Industrial: HON, BA, GE, UPS, ACN
    - And more (50 total)
  - **Custom tickers**: Pass comma-separated list to rank specific stocks: `/ranking?tickers=AAPL,TSLA,NVDA`
- `GET /predict_ticker/{ticker}` — Get ML probability for single stock
- `GET /ticker_info/{ticker}` — Fetch live market data (price, volume, market cap, P/E ratio)
- `POST /analyze` — AI-powered buy/sell recommendations with enriched market context
- `GET /models` — Lists available model artifact files and current production model

### `/analyze` Endpoint Details

**Request Body:**
```json
{
  "ranking": [{"ticker": "AAPL", "prob": 0.65}, ...],
  "user_context": "Focus on growth stocks for long-term holding"
}
```

**Response Includes:**
- Python-generated buy/sell signals (STRONG BUY, BUY, HOLD, SELL)
- Rich market data (prices, P/E ratios, 52-week ranges, volumes)
- AI analysis with specific buy/sell recommendations
- Risk assessment and action plan
- Caching indicator (shows if result is from cache)

**Example Response:**
```json
{
  "analysis": "TOP 3 BUY RECOMMENDATIONS:\n1. AAPL - Strong buy at $278...",
  "model": "gpt-4o-mini",
  "cached": false
}
```

## Search Individual Stocks
- Enter a stock symbol in the UI search input (e.g., `AMD`, `META`, `NFLX`) and click Search
- Backend endpoints used:
  - `GET /ticker_info/{ticker}`: live name, price, change %, volume, market cap
  - `GET /predict_ticker/{ticker}`: ML probability and recommendation signal
- Results render in a panel showing all market data plus probability score
- Use this to explore stocks outside the main ranking list
- Supports Enter key for quick searches

## UI Features
- **Auto-Load on Start**: Rankings automatically load when the app opens - no manual input required
- **Smart Pagination**: Display 10 stocks per page with Previous/Next navigation
  - Page counter shows current position ("Page 1 of 5")
  - Maintains rank order across pages (rank 11-20 on page 2, etc.)
- **One-Click Refresh**: Refresh button reloads latest market data and rankings
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

