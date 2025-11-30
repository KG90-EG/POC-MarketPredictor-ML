# Trading-Fun
Support Trading Decision, building a POC. Ideal, with Backend and Frontend

This repository contains a production-grade machine learning pipeline and modern web application for generating ranked lists of stocks with ML-powered predictions and AI-driven analysis.

## Features
- 🤖 **ML-Powered Stock Ranking** - RandomForest/XGBoost models predict stock performance
- 📊 **Real-Time Market Data** - Live prices, volume, market cap via yfinance
- 🌍 **Multi-Market Views** - Analyze stocks from 8 different markets (US, Switzerland, Germany, UK, France, Japan, Canada)
- 🔄 **Dynamic Stock Discovery** - Automatically validates and ranks top companies by market cap
- 🚀 **Auto-Load Rankings** - Top stocks ranked automatically on page load based on selected market
- 📄 **Pagination** - Clean 10-per-page display with easy navigation
- 🎯 **Automated Buy/Sell Signals** - Python-based recommendation engine with 5-tier signal system
- 🧠 **AI Analysis** - OpenAI-powered trading recommendations with retry logic and caching
- ⚛️ **Modern React UI** - Real-time updates with color-coded indicators and dark/light theme toggle
- 🌓 **Dark Mode Support** - Persistent theme toggle with smooth transitions
- 🔍 **Company Detail Sidebar** - Comprehensive stock information with country domicile
- 🚄 **High Performance** - Batch API endpoints, parallel processing, Redis caching
- 🔒 **Rate Limiting** - Built-in API protection with configurable limits
- 📊 **Structured Logging** - Request tracking, performance metrics, audit trails
- 🔴 **WebSocket Support** - Real-time price updates via WebSocket connections
- 📈 **Monitoring** - Health checks and metrics endpoints for observability
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
   - Select a market view (Global, Switzerland, Germany, UK, France, Japan, Canada)
   - Rankings load automatically showing top stocks from selected market
   - Browse paginated results (10 per page)
   - Click any stock for detailed analysis with country information
   - Use search to look up specific stocks

### What You'll See
- **Market View Selector**: Choose from 8 different markets (US, Switzerland, Germany, UK, France, Japan, Canada)
- **Dynamic Rankings**: Top 30 companies from selected market, validated by market cap
- **Diversified Portfolio**: Build portfolio from multiple countries for global diversification
- **Buy/Sell Signals**: Each stock shows STRONG BUY, BUY, HOLD, or SELL recommendation
- **Live Market Data**: Real-time prices, changes, volumes, market caps, and country domicile
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
gunicorn -c gunicorn_conf.py trading_fun.server:app
```

## Documentation Site
Markdown docs in `docs/` deployed to GitHub Pages via `.github/workflows/pages.yml`. After enabling Pages for the repository (Settings -> Pages) the workflow publishes updates on pushes to `main`.

