# POC-MarketPredictor-ML

Support Trading Decision, building a POC. Ideal, with Backend and Frontend

[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen?style=for-the-badge)](PRODUCTION_READY.md)
[![Security](https://img.shields.io/badge/Vulnerabilities-0-brightgreen?style=for-the-badge)](scripts/security_check.sh)
[![Tests](https://img.shields.io/badge/Tests-50%2B%20Passing-brightgreen?style=for-the-badge)](tests/)
[![Deployment](https://img.shields.io/badge/Deployment-Automated-blue?style=for-the-badge)](AUTOMATED_DEPLOYMENT.md)

This repository contains a production-grade machine learning pipeline and modern web application for generating ranked lists of stocks with ML-powered predictions and AI-driven analysis.

**🚀 Status**: Production Ready (98% Complete) - [Deploy Now](PRODUCTION_READY.md)

## Features

- 🤖 **ML-Powered Stock Ranking** - RandomForest/XGBoost models predict stock performance
- 📊 **Real-Time Market Data** - Live prices, volume, market cap via yfinance
- 🔍 **Enhanced Stock Search** - Dynamic lookup with yfinance fallback, supports European exchanges (.SW, .DE, .L, .PA)
- 🌍 **Multi-Market Views** - Analyze stocks from 8 different markets (US, Switzerland, Germany, UK, France, Japan, Canada)
- 🎯 **Dynamic Country Selector** - Beautiful card-based country selection with flag emojis
- 🔄 **Dynamic Stock Discovery** - Automatically validates and ranks top companies by market cap
- 🚀 **Auto-Load Rankings** - Top stocks ranked automatically on page load based on selected market
- 📄 **Pagination** - Clean 10-per-page display with easy navigation
- ⭐ **Watchlists & Portfolios** - Create custom watchlists with **mixed stocks and crypto**, track favorites, get actionable insights
- 💎 **Mixed Asset Support** - Add both stocks and cryptocurrencies to the same watchlist
- 🔍 **Smart Asset Search** - Separate dropdowns for stocks (50+) and crypto (30+) with live filtering
- 💰 **Investment Insights** - Live prices, buy/sell recommendations, confidence scores, momentum indicators
- ✅ **Fixed Crypto Display** - Ethereum and other crypto assets now show accurate price/change data
- 🎯 **Automated Buy/Sell Signals** - Python-based recommendation engine with 5-tier signal system
- 🧠 **AI Analysis** - OpenAI-powered trading recommendations with retry logic and caching
- ⚛️ **Modern React UI** - Real-time updates with color-coded indicators and dark/light theme toggle
- 🌓 **Dark Mode Support** - Persistent theme toggle with smooth transitions
- 🔍 **Company Detail Sidebar** - Comprehensive stock information with country domicile
- 💊 **Health Status Indicator** - Real-time system health monitoring with icon-based status display
- 📋 **Health Check Modal** - Comprehensive system diagnostics overlay with performance metrics
- 🚄 **High Performance** - Batch API endpoints, parallel processing, Redis caching
- 🔒 **Rate Limiting** - Built-in API protection with configurable limits
- 📊 **Structured Logging** - Request tracking, performance metrics, audit trails
- 🔴 **WebSocket Support** - Real-time price updates via WebSocket connections
- 📈 **Monitoring** - Health checks and metrics endpoints for observability
- 🛡️ **Error Boundary** - Graceful error handling with retry logic and user-friendly messages
- 🔄 **CI/CD Pipeline** - Automated testing, linting, Docker builds
- 📈 **MLflow Integration** - Model tracking, versioning, and promotion
- 🐳 **Docker Support** - Multi-stage builds with frontend and backend
- 💾 **Crypto/Digital Assets** - Track 200+ cryptocurrencies with live CoinGecko data, NFT tokens included
- 🎨 **Improved Crypto UX** - Simplified interface, removed unnecessary dropdowns, clean pagination

Quick summary:

- `market_predictor/` — Python package implementing data loading, features, model training, prediction, and a FastAPI server.
- `training/` — Retrain scripts, trainer and utilities (MLflow integration, drift-check, promotion)
- `backtest/` — A very small backtesting helper to simulate buy-hold trades.
- `frontend/` — React UI using Vite that shows ranked tickers from the backend `/ranking` endpoint.
- `01_Trading_Fun/` — Copied legacy content and tests
- `archive/` — Files archived and not used by the main flow

## Quick Start

### Requirements

- **Python 3.10 - 3.12** (recommended for best compatibility)
- **Node.js 18+** (for frontend)
- Note: Python 3.14 requires source builds for some dependencies

### First Time Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
cd frontend && npm install
```

2. **Optional - Configure environment variables:**

```bash
# Copy example environment file (everything works without this!)
cp .env.example .env

# Edit .env if you want to enable optional features:
# - OpenAI API for AI analysis
# - Redis for distributed caching
# - AWS S3 for model storage
# See .env.example and SECRETS.md for details
```

3. **Start the backend:**

```bash
uvicorn market_predictor.server:app --reload
```

4. **Start the frontend (in new terminal):**

```bash
cd frontend && npm run dev
```

5. **Open browser:** Navigate to `http://localhost:5173`
   - Select a market view with beautiful card-based country selector
   - Rankings load automatically showing top stocks from selected market
   - Browse paginated results (10 per page)
   - Click any stock for detailed analysis with country information
   - Use search to look up specific stocks
   - **NEW: Watchlists tab** - Create custom watchlists with **mixed stocks and crypto**
   - Add both AAPL (stocks) and bitcoin (crypto) to the same watchlist
   - Get live prices, predictions, and investment insights for all assets
   - Toggle between stock and crypto search modes with visual indicators

### Training Your Model

See [docs/TRAINING_GUIDE.md](docs/TRAINING_GUIDE.md) for comprehensive training instructions:

```bash
# Quick start - train on your watchlist stocks
python scripts/train_watchlist.py

# Train on specific tickers
python -m training.trainer --tickers AAPL,MSFT,GOOGL --period 2y

# Evaluate and promote to production
python -m training.evaluate_and_promote
```

The training guide includes:

- Quick start commands
- Technical indicators explanation (RSI, MACD, Bollinger Bands)
- Training workflow and best practices
- MLflow monitoring
- Troubleshooting tips

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_trading.py

# Run tests with coverage (if pytest-cov installed)
pytest --cov=market_predictor --cov-report=html
```

### What You'll See

- **Market View Selector**: Choose from 8 different markets (US, Switzerland, Germany, UK, France, Japan, Canada)
- **Dynamic Rankings**: Top 30 companies from selected market, validated by market cap
- **Diversified Portfolio**: Build portfolio from multiple countries for global diversification
- **Buy/Sell Signals**: Each stock shows STRONG BUY, BUY, HOLD, or SELL recommendation
- **Live Market Data**: Real-time prices, changes, volumes, market caps, and country domicile
- **Pagination**: Clean 10-per-page display with easy navigation
- **Watchlists & Portfolios**:
  - Create unlimited custom watchlists with names and descriptions
  - Smart stock search with 50+ popular stocks (Apple, Microsoft, Tesla, Swiss stocks, etc.)
  - Live search/autocomplete - type "apple" or "AAPL" to find stocks instantly
  - Automatic ticker validation and correction (e.g., "APPLE" → "AAPL")
  - Real-time investment insights for each watchlist stock:
    - Current price and 24h price change (with ▲/▼ indicators)
    - BUY/SELL/HOLD recommendations based on ML model confidence
    - Confidence scores (probability × 100)
    - Momentum indicators
    - Distance from 52-week high
  - Easy stock management (add/remove with one click)
- **Health Status Icon**: Real-time system health indicator in header (green/yellow/red/gray)
  - Auto-refreshes every 30 seconds
  - Click to view comprehensive diagnostics
  - Shows API, model, cache, and WebSocket status
- **Health Check Modal**: Full system diagnostics overlay with:
  - Backend API status and response time
  - ML model loading status
  - OpenAI API availability
  - Cache backend type and Redis connection
  - Performance metrics (cache hit rate, rate limiter stats, WebSocket connections)
  - Auto-refresh capability
- **AI Analysis**: Optional OpenAI-powered recommendations (requires API key)

## How to push to GitHub and PR (simple flow)

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

## Configuration

### Environment Variables

The application is configured via environment variables. See `.env.example` for all options:

- Copy `.env.example` to `.env` to customize settings
- **Everything works with defaults** - no configuration needed!
- Optional features: OpenAI API, Redis caching, AWS S3 storage
- See detailed docs in `.env.example`

### GitHub Secrets (for CI/CD)

For automated deployments, add secrets in GitHub repository settings:

- **NETLIFY_AUTH_TOKEN**, **NETLIFY_SITE_ID** - Frontend deployment
- **AWS_ACCESS_KEY_ID**, **AWS_SECRET_ACCESS_KEY**, **S3_BUCKET** - Model storage
- **CR_PAT** - Docker image publishing
- **MLFLOW_TRACKING_URI** - ML experiment tracking

📚 **See [SECRETS.md](SECRETS.md) for detailed setup instructions**

Deployment tips:

- All secrets are **optional** - CI works without them
- Workflows gracefully skip steps when secrets aren't configured
- Configure only the features you need

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
uvicorn market_predictor.server:app --reload
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

## Deployment

### 🚀 **Production Ready** - 3 Automated Deployment Methods

This application is **fully production-ready** with comprehensive deployment automation. See [PRODUCTION_READY.md](PRODUCTION_READY.md) for complete deployment guide.

**Quick Deploy Options**:

1. **GitHub Actions (Recommended - Fully Automated)**:
   - Add secrets to GitHub repo (RAILWAY_TOKEN, VERCEL_TOKEN, OPENAI_API_KEY)
   - Push to main → Auto-deploys backend to Railway + frontend to Vercel
   - See: [AUTOMATED_DEPLOYMENT.md](AUTOMATED_DEPLOYMENT.md)

2. **CLI Script (One Command)**:

   ```bash
   ./scripts/deploy_production.sh
   ```

   - Deploys backend to Railway
   - Deploys frontend to Vercel
   - Updates CORS automatically
   - Runs production tests

3. **Manual Deployment** (Step-by-Step):
   - Backend: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) (Railway/Render)
   - Frontend: [docs/deployment/FRONTEND_DEPLOYMENT.md](docs/deployment/FRONTEND_DEPLOYMENT.md) (Vercel/Netlify)

**Security & Testing**:

```bash
# Pre-deployment security check
./scripts/security_check.sh

# Post-deployment validation
./scripts/test_deployment.sh <production-url>

# Rate limiting tests
./scripts/test_rate_limit.sh

# GitHub security features
./scripts/setup_github_security.sh
```

**Status**: ✅ 0 vulnerabilities | ✅ 50+ tests passing | ✅ Production monitoring ready

---

### Deployment Documentation

**Comprehensive Guides**:

- 📋 [PRODUCTION_READY.md](PRODUCTION_READY.md) - Complete production readiness summary
- 🚀 [AUTOMATED_DEPLOYMENT.md](AUTOMATED_DEPLOYMENT.md) - Automated deployment guide (400+ lines)
- 📖 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Manual deployment guide (500+ lines)
- 🎯 [docs/BACKEND_DEPLOYMENT.md](docs/BACKEND_DEPLOYMENT.md) - Backend deployment options
- 🎨 [docs/FRONTEND_DEPLOYMENT.md](docs/FRONTEND_DEPLOYMENT.md) - Frontend deployment options

**Deployment Configs**:

- ✅ Railway: `railway.toml`, `Procfile`
- ✅ Vercel: `vercel.json`
- ✅ Netlify: `netlify.toml`
- ✅ Docker: `Dockerfile`, `docker-compose.yml`
- ✅ GitHub Actions: `.github/workflows/deploy.yml`

## Environment Variables Summary

**Backend Configuration:**

- `PROD_MODEL_PATH`: Path to production model file (default `models/prod_model.bin`)
- `OPENAI_API_KEY`: OpenAI API key for LLM-powered analysis (required for `/analyze` endpoint)
- `OPENAI_MODEL`: OpenAI model to use (default: `gpt-4o-mini`)
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: `INFO`)
- `RATE_LIMIT_RPM`: Rate limit requests per minute per IP (default: `60`)
- `REDIS_URL`: Redis connection URL (optional, falls back to in-memory cache if not set)

**MLflow & Model Management:**

- `MLFLOW_TRACKING_URI`: MLflow backend (default: `file:./mlruns`)
- `S3_BUCKET`: Optional S3 bucket for artifact upload

**Frontend Configuration:**

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`, set to production URL for deployment)

**CI/CD & Deployment:**

- `NETLIFY_AUTH_TOKEN` / `NETLIFY_SITE_ID`: Netlify deploy workflow secrets
- `CR_PAT`: GitHub Container Registry auth token for Docker image push

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

## Multi-Market View System

The application supports **8 different market views** for building a diversified global portfolio:

### Available Markets

- 🌐 **Global** - Top 50 US large-cap stocks (technology-dominated)
- 🇺🇸 **United States** - US market leaders across all sectors
- 🇨🇭 **Switzerland** - Top 30 Swiss companies (Nestle, Novartis, Roche, UBS, etc.)
- 🇩🇪 **Germany** - Top 20 German companies (SAP, Siemens, BMW, Rheinmetall, etc.)
- 🇬🇧 **United Kingdom** - Top 20 UK companies (Shell, AstraZeneca, HSBC, BP, etc.)
- 🇫🇷 **France** - Top 20 French companies (LVMH, L'Oreal, TotalEnergies, Airbus, etc.)
- 🇯🇵 **Japan** - Top 20 Japanese companies (Toyota, Sony, Nintendo, SoftBank, etc.)
- 🇨🇦 **Canada** - Top 20 Canadian companies (Shopify, Royal Bank, Enbridge, etc.)

### Dynamic Stock Discovery

Instead of hardcoded lists, the system **dynamically discovers and validates** top stocks:

1. **Seed Lists**: Curated starting lists for each country (20-30 companies)
2. **Real-Time Validation**: For each stock:
   - Fetches current market data from yfinance
   - Validates market cap exists and is positive
   - Confirms company country matches expected market
3. **Market Cap Ranking**: Automatically sorts by market capitalization (largest first)
4. **Top N Selection**: Returns the top companies ensuring you get the most liquid, established stocks
5. **Smart Caching**: Results cached for 1 hour to optimize performance and reduce API calls

### Benefits

- ✅ **Always Current**: Automatically filters out delisted or invalid stocks
- ✅ **Market Cap Validated**: Only includes companies with verified market data
- ✅ **Global Diversification**: Build portfolios across multiple countries and regions
- ✅ **No Manual Updates**: System automatically maintains current company lists
- ✅ **Performance Optimized**: 1-hour caching reduces API calls while keeping data fresh

### Usage

**Via UI:**

1. Select a market view button at the top of the page
2. System automatically fetches and ranks top stocks for that market
3. View rankings with country filter dropdown for additional filtering
4. Click any stock to see detailed company information including domicile

**Via API:**

```bash
# Get Swiss market rankings
curl "http://localhost:8000/ranking?country=Switzerland"

# Get German market rankings
curl "http://localhost:8000/ranking?country=Germany"

# Global (US) rankings
curl "http://localhost:8000/ranking?country=Global"
```

## API Endpoints

### Core Endpoints

- `GET /health` — Enhanced health check with dependency status (model, Redis, OpenAI)
- `GET /metrics` — System metrics for monitoring (cache stats, rate limiter, WebSocket connections)
- `GET /ranking?country=` — Rank stocks by ML probability with dynamic market selection
  - **Country parameter**: `Global`, `United States`, `Switzerland`, `Germany`, `United Kingdom`, `France`, `Japan`, `Canada`
  - **Default behavior**: When called without tickers parameter, dynamically fetches and ranks top stocks for specified country:
    - Validates each stock has real market data
    - Sorts by market capitalization
    - Returns top 30 most liquid companies
    - Results cached for 1 hour per country
  - **Examples**:
    - `/ranking?country=Switzerland` — Top 30 Swiss companies
    - `/ranking?country=Germany` — Top 20 German companies
    - `/ranking?country=Global` — Top 50 US large-caps (default)
  - **Custom tickers**: Override with specific tickers: `/ranking?tickers=AAPL,TSLA,NVDA`
- `GET /predict_ticker/{ticker}` — Get ML probability for single stock
- `GET /ticker_info/{ticker}` — Fetch live market data (price, volume, market cap, P/E ratio, country domicile, 52-week range)
- `POST /ticker_info_batch` — Batch fetch market data for multiple tickers (parallel processing)
- `POST /analyze` — AI-powered buy/sell recommendations with enriched market context
- `GET /models` — Lists available model artifact files and current production model
- `WS /ws/{client_id}` — WebSocket endpoint for real-time price updates

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

## Production Features

### 🚄 High Performance Architecture

**Batch API Endpoints**

- `POST /ticker_info_batch`: Fetch multiple tickers in parallel (10 concurrent workers)
- Reduces 30-ticker load time from ~45s to ~4s (11x improvement)
- Graceful degradation: Falls back to sequential fetching if batch fails
- Progress indicators show real-time loading status

**Parallel Processing**

- Stock validation uses ThreadPoolExecutor with 15 concurrent workers
- Country stock discovery improved from ~60s to ~10s (6x improvement)
- Concurrent API calls to yfinance for optimal throughput

**Performance Benchmarks**

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Load 30 stocks | ~45s | ~4s | 11x faster |
| Validate country stocks | ~60s | ~10s | 6x faster |
| Search multiple stocks | ~6s | ~1.5s | 4x faster |

### 💾 Redis Caching Layer

**Intelligent Caching Strategy**

- Primary: Redis backend for distributed caching
- Fallback: In-memory cache if Redis unavailable
- Automatic failover ensures zero downtime
- Configurable TTLs per data type:
  - Country stocks: 1 hour
  - AI analysis: 5 minutes
  - Ticker info: Configurable

**Cache Configuration**

```bash
# .env file
REDIS_URL=redis://localhost:6379/0  # Optional, falls back to in-memory
```

**Benefits**

- Share cache across multiple server instances
- Persist cache through server restarts
- Reduce external API calls (yfinance, OpenAI)
- Lower costs and improve response times

### 🔒 Rate Limiting

**Built-in API Protection**

- Configurable requests per minute (default: 60 RPM)
- Per-IP, per-endpoint tracking
- Sliding window algorithm for accuracy
- Automatic 429 responses with `Retry-After` headers

**Rate Limit Headers**

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701234567
```

**Configuration**

```bash
# .env file
RATE_LIMIT_RPM=60  # Requests per minute per IP
```

### 📊 Structured Logging

**Comprehensive Request Tracking**

- Unique request IDs for distributed tracing
- Performance metrics (request duration, throughput)
- Error tracking with stack traces
- Audit trails for security and compliance

**Log Format**

```
[2024-01-15 10:30:45] [INFO    ] [a1b2c3d4] Request started: GET /ranking {"endpoint": "/ranking", "event": "request_start"}
[2024-01-15 10:30:46] [INFO    ] [a1b2c3d4] Request completed: GET /ranking {"endpoint": "/ranking", "event": "request_complete", "duration_ms": 1234.56}
```

**Configuration**

```bash
# .env file
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 🔴 WebSocket Real-Time Updates

**Live Price Streaming**

- WebSocket endpoint: `ws://localhost:8000/ws/{client_id}`
- Subscribe to specific tickers for real-time updates
- 30-second update interval
- Automatic reconnection handling

**WebSocket Protocol**

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/client123');

// Subscribe to ticker
ws.send(JSON.stringify({action: 'subscribe', ticker: 'AAPL'}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {type: 'price_update', ticker: 'AAPL', price: 178.50, change: 2.35, change_percent: 1.33}
};

// Unsubscribe
ws.send(JSON.stringify({action: 'unsubscribe', ticker: 'AAPL'}));
```

**Features**

- Multiple concurrent subscriptions per client
- Broadcast updates only to subscribed clients
- Automatic client cleanup on disconnect
- Heartbeat/ping support for connection monitoring

### 📈 Monitoring & Observability

**Health Check Endpoint** (`GET /health`)

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_path": "models/prod_model.bin",
  "openai_available": true,
  "cache_backend": "redis",
  "redis_status": "connected",
  "timestamp": 1701234567.89
}
```

**Metrics Endpoint** (`GET /metrics`)

```json
{
  "cache_stats": {
    "backend": "redis",
    "redis_keys": 1247,
    "redis_hits": 45632,
    "redis_misses": 3421,
    "in_memory_keys": 0
  },
  "rate_limiter_stats": {
    "tracked_ips": 23,
    "tracked_endpoints": 87,
    "requests_per_minute": 60
  },
  "websocket_stats": {
    "active_connections": 5,
    "subscribed_tickers": 12,
    "total_subscriptions": 18
  },
  "model_info": {
    "path": "models/prod_model.bin",
    "loaded": true
  }
}
```

### 🔧 Configuration Management

**Environment Variables**

```bash
# Backend API
PROD_MODEL_PATH=models/prod_model.bin
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
RATE_LIMIT_RPM=60
REDIS_URL=redis://localhost:6379/0  # Optional

# MLflow (optional)
MLFLOW_TRACKING_URI=file:./mlruns
S3_BUCKET=your-bucket-name

# Frontend
VITE_API_URL=http://localhost:8000  # Set to production URL for deployment
```

### 🚀 Deployment Considerations

**Production Checklist**

- ✅ Set `VITE_API_URL` to production backend URL
- ✅ Configure Redis for distributed caching
- ✅ Adjust `RATE_LIMIT_RPM` based on capacity
- ✅ Set appropriate `LOG_LEVEL` (INFO or WARNING)
- ✅ Configure OpenAI API key securely
- ✅ Use gunicorn or uvicorn workers for concurrency
- ✅ Set up monitoring alerts on `/health` and `/metrics`
- ✅ Configure CORS origins for production domains
- ✅ Enable HTTPS/TLS for WebSocket connections
- ✅ Set up log aggregation (ELK, Splunk, CloudWatch)

**Recommended Architecture**

```
[Load Balancer]
      |
[Multiple Backend Instances]
      |
[Redis Cache Cluster]
      |
[External APIs: yfinance, OpenAI]
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

- **Multi-Market View Selector**: 8 market buttons to switch between global regions (US, Switzerland, Germany, UK, France, Japan, Canada)
- **Auto-Load on Start**: Rankings automatically load when the app opens based on selected market view
- **Dynamic Country Filter**: Dropdown shows only countries present in current dataset
- **Smart Pagination**: Display 10 stocks per page with page jump dropdown and Previous/Next navigation
  - Page counter shows current position ("Page 1 of 5")
  - Maintains rank order across pages (rank 11-20 on page 2, etc.)
- **Company Detail Sidebar**: Click any stock row to view comprehensive details:
  - Trading signal badge (STRONG BUY, BUY, HOLD, SELL)
  - Company name and country domicile with flag emoji
  - Price information grid (current, change %, 52-week high/low)
  - Market data grid (market cap, volume, P/E ratio)
  - Recommendation text based on ML probability
- **Search with Table View**: Search individual stocks displays results in table format
  - Click search result row to open detailed sidebar
  - Shows all market data including country
- **One-Click Refresh**: Refresh button reloads latest market data and rankings for current view
- **Gradient Theme Design**: Purple gradient background with clean, modern card-based layout
- **Dark/Light Mode Toggle**: Click the sun/moon icon in the header to switch themes
  - Theme preference is automatically saved to localStorage
  - Smooth transitions between themes
  - Optimized color schemes for both modes
- **Help/Guide Modal**: ? button provides comprehensive usage instructions
- **Rank Badges**: Top 3 stocks get special gold/silver/bronze styling
- **Real-Time Updates**: Live market data with color-coded positive/negative indicators
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
gunicorn -c gunicorn_conf.py market_predictor.server:app
```

## Documentation

### 📚 **Comprehensive Documentation** (2000+ lines)

**Getting Started**:

- 📖 [README.md](README.md) - Project overview and quick start
- 🎯 [SPEC.md](docs/architecture/SPECIFICATION.md) - Technical specification
- 🚀 [PRODUCTION_READY.md](PRODUCTION_READY.md) - Production deployment summary

**Deployment Guides**:

- 🤖 [AUTOMATED_DEPLOYMENT.md](AUTOMATED_DEPLOYMENT.md) - Automated deployment (3 methods)
- 📋 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Manual deployment guide (500+ lines)
- 🎯 [docs/BACKEND_DEPLOYMENT.md](docs/BACKEND_DEPLOYMENT.md) - Backend deployment options
- 🎨 [docs/FRONTEND_DEPLOYMENT.md](docs/FRONTEND_DEPLOYMENT.md) - Frontend deployment options

**Architecture & Development**:

- 🏗️ [docs/ADR-001-architecture-overview.md](docs/ADR-001-architecture-overview.md) - Architecture decisions
- 🤖 [docs/ADR-002-model-training-strategy.md](docs/ADR-002-model-training-strategy.md) - ML strategy
- 💾 [docs/ADR-003-caching-strategy.md](docs/ADR-003-caching-strategy.md) - Caching implementation
- 🤝 [CONTRIBUTING.md](docs/development/CONTRIBUTING.md) - Contributing guidelines

**Monitoring & Quality**:

- 📊 [docs/PERFORMANCE_MONITORING.md](docs/PERFORMANCE_MONITORING.md) - Monitoring guide
- ♿ [docs/ACCESSIBILITY_TESTING.md](docs/ACCESSIBILITY_TESTING.md) - Accessibility testing
- 📋 [BACKLOG.md](docs/project/BACKLOG.md) - Project backlog and progress tracking

**API Documentation**:

- Interactive Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- OpenAPI schema: <http://localhost:8000/openapi.json>

---

## Documentation Site

Markdown docs in `docs/` deployed to GitHub Pages via `.github/workflows/pages.yml`. After enabling Pages for the repository (Settings -> Pages) the workflow publishes updates on pushes to `main`.
