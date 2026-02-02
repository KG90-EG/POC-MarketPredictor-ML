# 📈 POC Market Predictor ML

**Decision Support System for Capital Allocation**

AI-Powered Stock Ranking & Trading Analysis Platform with Market Regime Awareness

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![Requirements Compliance](https://img.shields.io/badge/Requirements-100%25-brightgreen.svg)](docs/DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md)

## 🎯 Purpose

This system helps identify **where capital should be allocated and where it should not**, based on:
- **Quantitative signals** (20 technical indicators)
- **Market regime awareness** (VIX + S&P 500 trend)
- **Risk management** (position limits, exposure tracking)
- **Composite scoring** (Technical 40%, ML 30%, Momentum 20%, Regime 10%)

**Philosophy:** Relative strength beats absolute price prediction. Market regime and risk control are mandatory.

**Note:** This is a **Decision Support System** - it provides recommendations, NOT automated trading.

## 🚀 Quick Links

- 📚 [Trader Guide](docs/TRADER_GUIDE.md)
- 🏗️ [Architecture](docs/architecture/)
- 📊 [API Docs](http://localhost:8000/docs)
- 📋 [Specifications](.specify/specs/)

## ✨ Core Features

### 🎯 Decision Support (Phase 1-2 ✅)
- **Market Regime Detection** - VIX volatility + S&P 500 trend analysis
- **Composite Scoring** - Multi-factor ranking (Technical, ML, Momentum, Regime)
- **AI Stock Ranking** - 50 stocks (30 US + 20 Swiss) with buy/sell signals
- **Risk-Aware Signals** - BUY signals blocked in Risk-Off regimes

### 💼 Portfolio Risk Management ✅ NEW
- **Exposure Tracking** - Real-time portfolio allocation (Stocks 70%, Crypto 20%, Cash 10%)
- **Allocation Limits** - Position size enforcement (max 10% per stock, 5% per crypto)
- **Regime Adjustments** - Limits reduce automatically in Risk-Off mode
- **Compliance Validation** - Validate proposed allocations before execution

### 🔍 Asset Discovery ✅ NEW
- **Stock Search** - Search across US, Switzerland, Germany, UK, France
- **Market Overview** - 5 markets, 50+ stocks tracked
- **Crypto Discovery** - Top cryptocurrencies by market cap (CoinGecko API)
- **Country Filter** - Filter stocks by market/exchange

### 🤖 MLOps Dashboard ✅ NEW
- **Model Monitoring** - Feature importance, training metrics
- **Retraining Management** - Manual trigger, status tracking
- **Model Versioning** - Rollback capability (in development)
- **Performance Metrics** - Accuracy, precision, recall tracking

### 📊 Real-Time Data
- **Live Stocks** - 30 US (S&P 500) + 20 Swiss (SMI) stocks
- **Cryptocurrency** - Bitcoin, Ethereum, top 50 by market cap
- **Multi-Currency** - USD/CHF conversion support
- **Technical Indicators** - RSI, MACD, Bollinger Bands, ADX, +17 more

### 🎮 Trading Simulation
- **Paper Trading** - Risk-free testing with virtual capital
- **Portfolio Tracking** - Multi-asset position management
- **Trade History** - Complete audit trail
- **Performance Analytics** - P&L tracking, win rate analysis

### 🔔 Alert System
- **Price Alerts** - Trigger on price thresholds
- **Volatility Alerts** - High ATR/VIX warnings
- **Regime Changes** - Notifications on Risk-On/Risk-Off transitions
- **Smart Alerts** - Context-aware notifications

### 🎨 Modern UI
- **Dark/Light Mode** - Adaptive theming
- **Responsive Design** - Mobile-friendly
- **Real-Time Updates** - Live data streaming
- **Market Regime Badge** - Visible regime status (🟢 Risk-On / 🟡 Neutral / 🔴 Risk-Off)

## 📊 System Architecture

**Core Philosophy:** Decision Support, NOT Automated Trading

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  Market Regime Badge | Stock Rankings | Portfolio Dashboard │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                       │
│  • 43 Active Endpoints (100% Requirements Compliance)       │
│  • Market Regime Detector (VIX + S&P 500 Trend)            │
│  • Composite Scorer (Tech 40% + ML 30% + Mom 20% + Reg 10%)│
│  • Portfolio Risk Manager (Limits + Validation)             │
│  • LLM Context Provider (Market & Asset Context)            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              ML Model (Random Forest)                        │
│  • 20 Technical Features                                    │
│  • 82.61% Accuracy (30 US stocks)                          │
│  • 78.37% Accuracy (50 stocks total)                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           Data Sources                                       │
│  • yfinance (Stocks)  • CoinGecko (Crypto)  • ExchangeRate │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**
- **Market Regime Detector:** VIX < 20 = Risk-On, > 30 = Risk-Off
- **Composite Scorer:** Multi-signal aggregation with explainability
- **Portfolio Manager:** Exposure limits + regime-based adjustments
- **MLOps Dashboard:** Model monitoring + retraining management

## 📁 Project Structure

```
POC-MarketPredictor-ML/
├── src/
│   ├── trading_engine/       # Backend API server
│   │   ├── server.py         # 41 REST endpoints
│   │   ├── market_regime.py  # Regime detection (Week 2)
│   │   ├── composite_scoring.py  # Multi-factor scoring
│   │   └── portfolio_management.py  # Risk limits
│   ├── training/             # ML model training
│   ├── backtest/             # Historical validation
│   └── data/                 # Stock configs & data
├── frontend/                 # React UI
│   ├── src/
│   │   ├── components/       # MarketRegimeStatus, StockRanking
│   │   ├── App.jsx          # Main application
│   │   └── api.js           # API client
│   └── public/
├── tests/                    # Test suite
├── scripts/                  # Utilities (start.sh, cleanup.sh)
├── config/                   # Deployment configs
├── docs/                     # Documentation
│   ├── DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md  # Master requirements
│   ├── BACKLOG.md           # Weekly tasks
│   ├── ENDPOINT_IMPLEMENTATION_STATUS.md  # API inventory
│   └── architecture/        # ADRs
└── models/                   # Trained ML models
```

## 📊 Endpoints by Category (43 Total)

### System (4)
- `GET /` - API root
- `GET /health` - Health check
- `GET /metrics` - System metrics
- `GET /prometheus` - Prometheus metrics

### Predictions (3)
- `GET /api/predict/{ticker}` - ML prediction
- `GET /ranking` - Stock rankings (composite score)
- `GET /ticker_info/{ticker}` - Stock details

### Market Analysis (2)
- `GET /regime` - Market regime status ⚡ **CRITICAL**
- `GET /api/regime/summary` - Regime summary

### Portfolio Risk Management (3) ✨ **NEW**
- `GET /api/portfolio/summary` - Exposure tracking
- `GET /api/portfolio/limits` - Allocation limits
- `POST /api/portfolio/validate` - Validate allocation

### Stock Discovery (5) ✨ **NEW**
- `GET /search_stocks` - Search by name/ticker
- `GET /countries` - Available markets
- `GET /api/stocks/{ticker}` - Stock details
- `GET /api/stocks/popular` - Popular stocks
- `GET /api/stocks/trending` - Trending stocks

### Cryptocurrency (4)
- `GET /crypto/ranking` - Crypto rankings
- `GET /popular_cryptos` - Top cryptos ✨ **NEW**
- `GET /crypto/search` - Search crypto
- `GET /crypto/{id}` - Crypto details

### Simulation (7)
- `GET /api/simulations` - List simulations
- `POST /api/simulations` - Create simulation
- `GET /api/simulations/{id}` - Get simulation
- `DELETE /api/simulations/{id}` - Delete simulation
- `GET /api/simulations/{id}/portfolio` - Portfolio state
- `POST /api/simulations/{id}/trade` - Execute trade
- `POST /api/simulations/{id}/reset` - Reset simulation

### Alerts (4)
- `GET /alerts` - Get alerts
- `POST /alerts` - Create alert
- `POST /alerts/{id}/read` - Mark read
- `DELETE /alerts/{id}` - Delete alert

### Watchlists (5)
- `GET /watchlists` - List watchlists
- `POST /watchlists` - Create watchlist
- `GET /watchlists/{id}` - Get watchlist
- `PUT /watchlists/{id}` - Update watchlist
- `DELETE /watchlists/{id}` - Delete watchlist

### MLOps (4) ✨ **NEW**
- `GET /api/ml/model/info` - Model metrics
- `GET /api/ml/retraining/status` - Retraining status
- `POST /api/ml/retraining/trigger` - Trigger retraining
- `POST /api/ml/retraining/rollback` - Rollback model

### LLM Context (2) ✨ **NEW**
- `GET /api/context/market` - Market overview context
- `GET /api/context/asset/{ticker}` - Asset-specific context

**Removed (2026-01-11):** 3 endpoints that violated Non-Goals
- ❌ `POST /api/simulations/{id}/auto-trade` (automated trading)
- ❌ `POST /api/simulations/{id}/autopilot` (automated trading)
- ❌ `POST /predict_raw` (redundant)

**Deprecated (2026-01-11):** 1 endpoint violating Decision Support principle
- ⚠️ `POST /analyze` → Use `/api/context/market` instead (no buy/sell recommendations)

**See:** [Endpoint Implementation Status](docs/ENDPOINT_IMPLEMENTATION_STATUS.md)

## 🚀 Quick Start

### Using Makefile (Recommended)

```bash
# Complete setup
make setup

# Start servers
make start

# Stop servers
make stop

# Restart servers
make restart

# View all commands
make help
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Set up environment
cp .env.example .env

# Start servers
./scripts/start.sh
```

**Access:**

- Frontend: <http://localhost:5173>
- Backend: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

## 🤖 Model Training

The ML model should be retrained regularly for accurate predictions:

```bash
# Train production model (50 stocks, 5 years data)
make train-model

# Setup automatic weekly retraining
make auto-retrain-setup

# View training metrics
make mlflow-ui
```

**Training metrics tracked in MLflow UI (`make mlflow-ui`).**

## 🚀 Commands

### Server Management

```bash
make start           # Start backend + frontend
make stop            # Stop all servers
make restart         # Restart servers
make status          # Check server status
make logs            # View server logs
```

### Model Training

```bash
make train-model         # Train production model
make auto-retrain-setup  # Setup weekly auto-retraining
make mlflow-ui           # View training metrics
```

### Development

```bash
make test            # Run test suite
make clean           # Clean caches
make docker-up       # Start with Docker
```

### Legacy Commands

```bash
# Train model
python -m src.training.trainer

# Run tests
pytest tests/ -v

# Docker
docker-compose -f config/deployment/docker-compose.yml up
```

## 📖 Documentation

### Getting Started
- **Quick Start:** Run `make setup && make start` or `./scripts/start.sh`
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** `./scripts/health_check.sh`

### Guides
- [Trader Guide](docs/TRADER_GUIDE.md) - How to use the system

### Technical Documentation
- [Architecture](docs/architecture/) - System design & ADRs
- [API Reference](docs/api/openapi.json) - OpenAPI spec

### Specifications (Spec-Kit)
- [001 - Risk Management](.specify/specs/001-risk-management/) - Phase 4 ✅
- [002 - NFRs](.specify/specs/002-non-functional-requirements/) - Quality & Automation
- [003 - LLM Analysis](.specify/specs/003-llm-analysis/) - AI Explanations
- [004 - ML Pipeline](.specify/specs/004-ml-training-pipeline/) - Training Automation

## 🎯 Requirements Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Market Data Ingestion | ✅ Implemented | yfinance (300d lookback) |
| Quantitative Signals | ✅ Implemented | 20 technical features |
| Market Regime Detection | ✅ Implemented | VIX + S&P 500 trend |
| Composite Scoring | ✅ Implemented | Tech 40% + ML 30% + Mom 20% + Reg 10% |
| Risk Management | ✅ Implemented | Portfolio limits + validation |
| Decision Interface | ✅ Implemented | React UI with regime badge |
| Explainability | ✅ Implemented | Score breakdown modal |

**Overall Compliance:** ✅ **100%**

**See:** [Architecture Docs](docs/architecture/)

## 🚀 Current Status

### ✅ Completed Phases

**Phase 1-3: Core Features ✅**
- ✅ Market Regime Detection (VIX + S&P 500 trend)
- ✅ Composite Scoring System (4-factor weighted)
- ✅ Capital Allocation Framework (position limits)

**Phase 4: Risk Management ✅**
- ✅ Risk Scoring Service
- ✅ Exposure Tracking API
- ✅ Frontend Risk Components (DefensiveModeBar, RiskBadge, ExposureChart)

### 🔜 Next Steps

See [Specifications](.specify/specs/) for upcoming work:
- **FR-003:** LLM-Powered Market Analysis
- **NFR-010:** ML Training Pipeline Automation

## 📊 Metrics

### System Performance
- **Backend Response:** < 500ms (median)
- **Model Inference:** < 100ms per stock
- **Data Freshness:** 5-minute cache TTL
- **Uptime:** 99.9% target

### Model Performance
- **Accuracy:** 82.61% (30 US stocks), 78.37% (50 stocks)
- **Feature Count:** 20 technical indicators
- **Training Time:** ~30-60 minutes (50 stocks)
- **Last Trained:** 2026-01-11

### Coverage
- **Markets:** 5 (US, CH, DE, UK, FR)
- **Stocks:** 50 (30 US + 20 Swiss)
- **Cryptocurrencies:** Top 50 by market cap
- **Endpoints:** 43 active (42 implemented + 1 deprecated), 100% requirements compliance

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Made with ❤️ for traders**
