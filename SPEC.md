# POC-MarketPredictor-ML Technical Specification

**Project Name:** POC-MarketPredictor-ML  
**Version:** 2.0  
**Last Updated:** December 1, 2025  
**Status:** Production-Ready  

---

## 1. Project Overview

### 1.1 Purpose
POC-MarketPredictor-ML is a production-grade machine learning application that provides stock ranking, prediction, and AI-powered trading recommendations. The system analyzes global markets and generates buy/sell signals using ML models and real-time market data.

### 1.2 Key Objectives
- Provide ML-powered stock rankings across multiple global markets
- Generate automated buy/sell signals with 5-tier recommendation system
- Deliver real-time market data and analysis via modern web interface
- Support multi-market portfolio diversification strategies
- Maintain production-grade reliability with comprehensive monitoring

### 1.3 Target Users
- Retail investors seeking data-driven stock recommendations
- Portfolio managers analyzing multi-market opportunities
- Developers building trading tools and integrations
- Data scientists evaluating ML prediction models

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Vite + UI)   │
└────────┬────────┘
         │ HTTP/REST
         │ WebSocket
┌────────▼────────┐
│  FastAPI Server │
│   (Port 8000)   │
├─────────────────┤
│ • Rate Limiter  │
│ • Cache Layer   │
│ • Request Logger│
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
┌───▼───┐ ┌──▼──┐ ┌────▼────┐ ┌──▼───┐
│ Model │ │Redis│ │ yfinance│ │OpenAI│
│  .bin │ │Cache│ │   API   │ │ API  │
└───────┘ └─────┘ └─────────┘ └──────┘
```

### 2.2 Technology Stack

**Backend:**
- **Framework:** FastAPI (Python 3.10+)
- **ML Models:** scikit-learn 1.7.2, XGBoost 3.1.2
- **Model Tracking:** MLflow 2.10.0
- **Data Source:** yfinance 0.2.66
- **AI Integration:** OpenAI API (GPT-4o-mini)
- **Cache:** Redis (optional, in-memory fallback)
- **Server:** uvicorn / gunicorn

**Frontend:**
- **Framework:** React 18
- **Build Tool:** Vite v5.4.21
- **State Management:** @tanstack/react-query v5.0.0
- **HTTP Client:** Axios
- **UI:** Custom CSS with dark/light theme support

**Infrastructure:**
- **CI/CD:** GitHub Actions (4 workflows)
- **Deployment:** GitHub Pages (docs), Netlify (frontend)
- **Containerization:** Docker (multi-stage builds)
- **Monitoring:** Health checks, metrics endpoints, structured logging

---

## 3. Feature Specifications

### 3.1 Multi-Market Stock Ranking

**FR-001: Market View Selection**
- **Description:** Users can select from 8 global market views
- **Markets:** Global (US), United States, Switzerland, Germany, United Kingdom, France, Japan, Canada
- **Behavior:** 
  - Multiple markets can be selected simultaneously
  - Rankings merge and deduplicate across selected markets
  - Automatic validation of stock availability
  - Top 30 companies by market cap per market
  - Results cached for 1 hour per market

**FR-002: Dynamic Stock Discovery**
- **Description:** System automatically validates and ranks stocks
- **Process:**
  1. Fetch curated stock list for selected country
  2. Validate each stock has real market data
  3. Sort by market capitalization
  4. Return top liquid companies
  5. Cache results to reduce API calls

**FR-003: ML-Powered Probability Ranking**
- **Description:** Generate probability scores for stock outperformance
- **Model Features:**
  - RSI (Relative Strength Index)
  - SMA50/SMA200 (Simple Moving Averages)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Momentum indicators
  - Volatility measures
- **Output:** Probability score (0-100%) for each stock

### 3.2 Buy/Sell Signal Generation

**FR-004: Automated Signal Classification**
- **Description:** Generate trading signals based on ML probability
- **Signal Tiers:**
  - **STRONG BUY:** prob ≥ 0.65 (65%+)
  - **BUY:** 0.55 ≤ prob < 0.65 (55-64%)
  - **HOLD:** 0.45 ≤ prob < 0.55 (45-54%)
  - **CONSIDER SELLING:** 0.35 ≤ prob < 0.45 (35-44%)
  - **SELL:** prob < 0.35 (<35%)
- **Visual Indicators:**
  - Green badge with 🟢 for BUY signals (≥50%)
  - Red badge with 🔴 for SELL signals (<50%)

**FR-005: AI-Powered Analysis**
- **Description:** OpenAI-powered detailed trading recommendations
- **Endpoint:** `POST /analyze`
- **Features:**
  - Enriched with real-time market data (P/E ratio, 52-week range, volume)
  - Top 10 stock analysis with specific recommendations
  - Risk assessment and action plan
  - Response caching (1 hour per unique ranking + context)
- **Input:**
  ```json
  {
    "ranking": [{"ticker": "AAPL", "prob": 0.65}, ...],
    "user_context": "Focus on growth stocks"
  }
  ```

### 3.3 Real-Time Market Data

**FR-006: Live Stock Information**
- **Description:** Fetch comprehensive market data for stocks
- **Data Points:**
  - Current price
  - Price change ($ and %)
  - Trading volume
  - Market capitalization
  - P/E ratio
  - 52-week high/low
  - Country domicile
  - Company name
- **Endpoints:**
  - `GET /ticker_info/{ticker}` - Single stock
  - `POST /ticker_info_batch` - Batch (parallel processing)

**FR-007: WebSocket Real-Time Updates**
- **Description:** Live price updates via WebSocket
- **Endpoint:** `WS /ws/{client_id}`
- **Features:**
  - Subscribe to multiple tickers
  - Real-time price streaming
  - Connection management
  - Automatic cleanup on disconnect

### 3.4 User Interface Features

**FR-008: Market View Selector**
- **Description:** Interactive buttons for market selection
- **Behavior:**
  - Click to toggle selection (checkmark indicator)
  - Multiple simultaneous selections
  - Dynamic title showing selected markets
  - Result count display

**FR-009: Stock Rankings Table**
- **Description:** Paginated display of ranked stocks
- **Columns:**
  - Rank (with gold/silver/bronze badges for top 3)
  - Ticker symbol (clickable)
  - Company name
  - Country (with flag emoji filter)
  - Buy/Sell signal badge
  - Probability percentage
  - Current price
  - Price change %
  - Trading volume
  - Market cap
- **Pagination:** 10 items per page with page navigation

**FR-010: Company Detail Sidebar**
- **Description:** Comprehensive stock information overlay
- **Sections:**
  - Trading signal badge with color coding
  - Company name and country with flag emoji
  - Price information grid (current, change, 52-week range)
  - Market data grid (cap, volume, P/E ratio)
  - ML probability percentage
  - Recommendation text based on signal
- **Interaction:** Click anywhere outside to close

**FR-011: Stock Search**
- **Description:** Individual stock lookup functionality
- **Features:**
  - Symbol input with Enter key support
  - Results in table format matching main rankings
  - Live market data fetch
  - ML probability calculation
  - Error handling for invalid symbols

**FR-012: Theme Toggle**
- **Description:** Dark/light mode with persistence
- **Implementation:**
  - Toggle button in header (☀️/🌙)
  - Smooth CSS transitions
  - localStorage persistence
  - Full UI theming support

**FR-013: Health Status Indicator**
- **Description:** Real-time system health monitoring
- **Visual States:**
  - 🟢 Green: All systems operational
  - 🟡 Yellow: Degraded performance
  - 🔴 Red: Critical issues
  - ⚪ Gray: Checking status
- **Features:**
  - Auto-refresh every 30 seconds
  - Clickable for detailed diagnostics modal
  - Header position for constant visibility

**FR-014: Health Diagnostics Modal**
- **Description:** Comprehensive system status overlay
- **Information:**
  - Backend API status and response time
  - ML model loading status
  - OpenAI API availability
  - Cache backend type (Redis/in-memory)
  - Redis connection status
  - WebSocket manager status
  - Timestamp of last check
- **Interaction:** Click anywhere to close

---

## 4. API Specifications

### 4.1 Core Endpoints

#### GET /health
**Purpose:** System health check with dependency status

**Response:**
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

#### GET /metrics
**Purpose:** System metrics for monitoring

**Response:**
```json
{
  "cache_stats": {
    "backend": "redis",
    "redis_keys": 1247,
    "redis_hits": 45632,
    "redis_misses": 3421
  },
  "rate_limiter_stats": {
    "tracked_ips": 23,
    "requests_per_minute": 60
  },
  "websocket_stats": {
    "active_connections": 5,
    "subscribed_tickers": 12
  },
  "model_info": {
    "path": "models/prod_model.bin",
    "loaded": true
  }
}
```

#### GET /ranking
**Purpose:** Get ML-ranked stocks for a market

**Parameters:**
- `country` (optional): Market selection (default: "Global")
  - Options: Global, United States, Switzerland, Germany, United Kingdom, France, Japan, Canada
- `tickers` (optional): Comma-separated ticker override

**Response:**
```json
{
  "ranking": [
    {"ticker": "AAPL", "prob": 0.712},
    {"ticker": "MSFT", "prob": 0.685},
    ...
  ]
}
```

**Behavior:**
- Without tickers: Returns top 30 stocks for specified country
- With tickers: Ranks provided list
- Cached for 1 hour per country
- Validates all stocks have real market data

#### GET /predict_ticker/{ticker}
**Purpose:** Get ML probability for single stock

**Response:**
```json
{
  "ticker": "AAPL",
  "prob": 0.712,
  "features": {
    "RSI": 65.3,
    "SMA50": 278.5,
    "MACD": 2.1,
    ...
  }
}
```

#### GET /ticker_info/{ticker}
**Purpose:** Fetch comprehensive market data

**Response:**
```json
{
  "name": "Apple Inc.",
  "price": 278.45,
  "change": 2.3,
  "volume": 45832100,
  "market_cap": 4320000000000,
  "pe_ratio": 28.5,
  "country": "United States",
  "fifty_two_week_high": 299.50,
  "fifty_two_week_low": 164.08
}
```

#### POST /ticker_info_batch
**Purpose:** Batch fetch ticker information (parallel)

**Request:**
```json
{
  "tickers": ["AAPL", "MSFT", "NVDA"]
}
```

**Response:**
```json
{
  "AAPL": {...},
  "MSFT": {...},
  "NVDA": {...}
}
```

#### POST /analyze
**Purpose:** AI-powered buy/sell recommendations

**Request:**
```json
{
  "ranking": [{"ticker": "AAPL", "prob": 0.65}, ...],
  "user_context": "Focus on growth stocks for long-term holding"
}
```

**Response:**
```json
{
  "analysis": "TOP 3 BUY RECOMMENDATIONS:\n1. AAPL - Strong buy at $278...",
  "model": "gpt-4o-mini",
  "cached": false
}
```

**Features:**
- Enriches with real-time market data
- Generates Python-based signals before AI analysis
- Caches results for 1 hour
- Includes risk assessment and action plan

#### GET /models
**Purpose:** List available model artifacts

**Response:**
```json
{
  "current_model": "prod_model.bin",
  "available_models": [
    {"name": "model_20251201_143022.bin", "size": "2.4 MB"},
    {"name": "model_20251130_120000.bin", "size": "2.3 MB"}
  ]
}
```

#### WS /ws/{client_id}
**Purpose:** Real-time price updates via WebSocket

**Message Format:**
```json
{
  "action": "subscribe",
  "tickers": ["AAPL", "MSFT"]
}
```

**Update Format:**
```json
{
  "ticker": "AAPL",
  "price": 278.45,
  "change": 2.3,
  "timestamp": 1701234567.89
}
```

### 4.2 Rate Limiting

**Configuration:**
- Default: 60 requests/minute per IP
- Environment variable: `RATE_LIMIT_RPM`
- Headers: `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Response on limit: HTTP 429 with retry-after

### 4.3 Caching Strategy

**Backend Cache:**
- Primary: Redis (if configured via `REDIS_URL`)
- Fallback: In-memory LRU cache
- TTL: 1 hour for rankings, 30 minutes for ticker info

**Cache Keys:**
- `ranking:{country}` - Market rankings
- `ticker_info:{ticker}` - Stock information
- `analysis:{hash}` - AI analysis results

---

## 5. ML Model Specifications

### 5.1 Model Architecture

**Type:** RandomForest or XGBoost classifier

**Features (Input):**
- RSI (14-period)
- SMA50, SMA200 (Simple Moving Averages)
- MACD, MACD Signal
- Bollinger Bands (upper, lower)
- Momentum (10-day)
- Volatility (30-day rolling std)

**Target (Output):**
- Binary classification: Outperform vs. Underperform
- Probability score: 0-1 (converted to percentage)

### 5.2 Training Pipeline

**Location:** `training/trainer.py`

**Process:**
1. Fetch historical price data (yfinance)
2. Compute technical indicators
3. Generate binary labels (future return > threshold)
4. Train model with cross-validation
5. Log metrics to MLflow
6. Save model artifact with timestamp

**Model Naming:** `model_YYYYMMDD_HHMMSS.bin`

**Evaluation Metrics:**
- Accuracy
- Precision, Recall, F1-Score
- ROC-AUC
- Confusion matrix

### 5.3 Model Promotion

**Workflow:** `.github/workflows/promotion.yml`

**Schedule:** Daily at midnight UTC

**Process:**
1. Train new model on latest data
2. Evaluate performance metrics
3. Compare with current production model
4. Promote if metrics improve
5. Update `models/prod_model.bin`
6. Optional: Upload to S3 bucket

**Selection Logic:**
```bash
NEWMODEL=$(ls -t models/model_*.bin 2>/dev/null | head -n1 | xargs basename)
```

---

## 6. Production Features

### 6.1 Monitoring & Observability

**Health Checks:**
- Endpoint: `GET /health`
- Monitors: Model loading, Redis connection, OpenAI API
- Auto-refresh: Every 30 seconds
- Alerting: Visual indicators in UI

**Metrics Collection:**
- Endpoint: `GET /metrics`
- Data: Cache stats, rate limiter, WebSocket connections
- Integration: Prometheus-compatible format

**Structured Logging:**
- Format: JSON with correlation IDs
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Context: Request timing, cache hits, errors
- Configuration: `LOG_LEVEL` environment variable

### 6.2 Performance Optimization

**Batch Processing:**
- Parallel ticker info fetching
- Reduces API calls by 90%
- Timeout: 30 seconds per request

**Caching:**
- Redis for distributed cache
- In-memory fallback for reliability
- TTL management per data type

**Rate Limiting:**
- Per-IP request tracking
- Configurable thresholds
- Graceful error responses

### 6.3 Error Handling

**Backend:**
- HTTP 503 for unavailable services
- HTTP 429 for rate limits
- HTTP 404 for invalid tickers
- Detailed error messages with context

**Frontend:**
- Network error detection
- Retry logic for failed requests
- User-friendly error messages
- Fallback UI states

**Error Boundary:**
- React error boundary component
- Catches rendering errors
- Displays recovery options
- Logs errors for debugging

---

## 7. Deployment Specifications

### 7.1 Environment Variables

**Backend:**
```bash
PROD_MODEL_PATH=models/prod_model.bin
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
RATE_LIMIT_RPM=60
REDIS_URL=redis://localhost:6379/0  # Optional
MLFLOW_TRACKING_URI=file:./mlruns
S3_BUCKET=your-bucket-name  # Optional
```

**Frontend:**
```bash
VITE_API_URL=http://localhost:8000  # Production URL for deployment
```

### 7.2 CI/CD Workflows

**1. ci.yml - Backend Testing**
- Trigger: Push to main/dev, Pull requests
- Jobs: Linting (flake8), testing (pytest), type checking
- Python version: 3.10

**2. pages.yml - Documentation Deployment**
- Trigger: Push to main
- Target: GitHub Pages
- Source: `docs/` folder
- Output: https://kg90-eg.github.io/Trading-Fun/

**3. deploy-frontend.yml - Frontend Deployment**
- Trigger: Push to main
- Target: Netlify
- Build: `npm run build`
- Environment: Production

**4. promotion.yml - Model Training**
- Trigger: Daily (00:00 UTC)
- Process: Train, evaluate, promote best model
- Artifact: Timestamped .bin file

### 7.3 Docker Deployment

**Multi-Stage Build:**
```dockerfile
# Stage 1: Build frontend
FROM node:20-alpine AS frontend
RUN npm ci && npm run build

# Stage 2: Python backend
FROM python:3.10-slim AS backend
COPY --from=frontend /frontend/dist /app/frontend/dist
CMD ["uvicorn", "trading_fun.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Ports:**
- Backend: 8000
- Frontend (dev): 5173

---

## 8. Security Considerations

### 8.1 API Security

**CORS Configuration:**
- Allowed origins: localhost:5173, localhost:3000 (configurable)
- Credentials: Enabled
- Methods: All
- Headers: All

**Rate Limiting:**
- Per-IP tracking
- Configurable limits
- Protection against abuse

**Input Validation:**
- Pydantic models for request validation
- Ticker format validation
- Country parameter whitelisting

### 8.2 Secrets Management

**Environment Variables:**
- `.env` file for local development (gitignored)
- GitHub Secrets for CI/CD
- Never commit API keys

**OpenAI API Key:**
- Required for `/analyze` endpoint
- Validated on startup
- Graceful fallback if unavailable

---

## 9. Testing Strategy

### 9.1 Backend Tests

**Location:** `01_Trading_Fun/tests/`

**Test Files:**
- `test_features_training.py` - Feature engineering
- `test_server.py` - API endpoints
- `test_integration_server.py` - Integration tests

**Coverage:**
- Feature computation
- Model training/prediction
- API responses
- Error handling

**Run Tests:**
```bash
pytest 01_Trading_Fun/tests/ -v
```

### 9.2 Frontend Testing

**Manual Testing:**
- Market view selection
- Pagination navigation
- Stock search functionality
- Company detail sidebar
- Theme toggle
- Health status indicator

**Browser Compatibility:**
- Chrome/Edge (Chromium)
- Firefox
- Safari

### 9.3 Integration Testing

**Test Scenarios:**
1. End-to-end ranking flow
2. Multi-market selection and merge
3. Batch ticker info fetching
4. AI analysis with caching
5. WebSocket connections
6. Health check and metrics

---

## 10. Known Limitations & Future Enhancements

### 10.1 Current Limitations

1. **Model Accuracy:** Dependent on historical data quality
2. **API Rate Limits:** yfinance has informal rate limits
3. **Market Hours:** Data freshness varies by market open/close
4. **Geographic Coverage:** Limited to 8 major markets
5. **Real-Time Data:** WebSocket updates on polling interval

### 10.2 Planned Enhancements

**Phase 1 (Q1 2026):**
- [ ] Add more international markets (China, India, Brazil)
- [ ] Implement user authentication and portfolios
- [ ] Add historical backtesting visualization
- [ ] Enhance AI analysis with more context

**Phase 2 (Q2 2026):**
- [ ] Mobile app (React Native)
- [ ] Email/SMS alerts for signal changes
- [ ] Integration with trading platforms APIs
- [ ] Advanced portfolio optimization

**Phase 3 (Q3 2026):**
- [ ] Options and derivatives analysis
- [ ] Sentiment analysis from news/social media
- [ ] Custom model training interface
- [ ] Multi-user collaboration features

---

## 11. Glossary

**Terms:**
- **ML Probability:** Model confidence score (0-100%) for stock outperformance
- **Market View:** Geographic/regional stock market grouping
- **Signal:** Trading recommendation tier (STRONG BUY to SELL)
- **Ticker:** Stock symbol (e.g., AAPL, MSFT)
- **Feature:** Technical indicator used in ML model
- **Artifact:** Saved model file (.bin format)
- **Promotion:** Process of deploying new model to production

**Technical Indicators:**
- **RSI:** Relative Strength Index (momentum oscillator)
- **SMA:** Simple Moving Average
- **MACD:** Moving Average Convergence Divergence
- **Bollinger Bands:** Volatility indicator
- **P/E Ratio:** Price-to-Earnings ratio

---

## 12. Contact & Support

**Repository:** https://github.com/KG90-EG/POC-MarketPredictor-ML

**Documentation:**
- Main: `README.md`
- Deployment: `DEPLOYMENT.md`
- Frontend: `docs/FRONTEND_COMPONENTS.md`
- Production: `docs/PRODUCTION_FEATURES.md`

**Issues:** GitHub Issues tracker

**License:** (Specify license if applicable)

---

**Document Control:**
- **Version:** 2.0
- **Author:** Development Team
- **Last Review:** December 1, 2025
- **Next Review:** March 1, 2026
