# 📈 POC Market Predictor ML

**Decision Support System for Capital Allocation**

AI-Powered Stock Ranking & Trading Analysis Platform with Market Regime Awareness

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

## 🎯 Purpose

This system helps identify **where capital should be allocated and where it should not**, based on:
- **Quantitative signals** (20 technical indicators)
- **Market regime awareness** (VIX + S&P 500 trend)
- **Risk management** (position limits, exposure tracking)
- **Composite scoring** (Technical 40%, ML 30%, Momentum 20%, Regime 10%)

**Philosophy:** Relative strength beats absolute price prediction. Market regime and risk control are mandatory.

**Note:** This is a **Decision Support System** - it provides data-driven signals, NOT automated trading.

## 🚀 Quick Start

\`\`\`bash
# Clone and setup
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Configure environment
cp .env.example .env

# Start servers
./scripts/start.sh

# Check health
./scripts/health_check.sh
\`\`\`

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ✨ Features

### 🎯 Core Features
| Feature | Description | Status |
|---------|-------------|--------|
| **Market Regime Detection** | VIX + S&P 500 trend analysis | ✅ |
| **Composite Scoring** | Multi-factor ranking (Tech/ML/Momentum/Regime) | ✅ |
| **Stock Ranking** | 50 stocks with BUY/SELL/HOLD signals | ✅ |
| **Crypto Ranking** | Top 50 cryptocurrencies | ✅ |
| **Risk Management** | Position limits, exposure tracking | ✅ |
| **Defensive Mode** | BUY signals blocked in Risk-Off | ✅ |

### 📊 Frontend Views (4 Active)
1. **Trading Signals** - Stock rankings with composite scores
2. **Top Stocks** - Filtered view of best opportunities
3. **Crypto** - Cryptocurrency rankings
4. **Backtest** - Historical performance validation

### 🔌 API Endpoints (Core)
\`\`\`
GET  /health              - Health check
GET  /api/ranking         - Stock rankings with scores
GET  /api/market-regime   - Current regime (RISK_ON/OFF/NEUTRAL)
GET  /api/crypto/ranking  - Crypto rankings
GET  /api/portfolio/exposure - Portfolio exposure tracking
POST /api/portfolio/validate - Validate allocation
\`\`\`

Full API documentation: http://localhost:8000/docs

## 📁 Project Structure

\`\`\`
POC-MarketPredictor-ML/
├── src/
│   ├── trading_engine/   # FastAPI backend
│   ├── training/         # ML model training
│   ├── backtest/         # Backtesting engine
│   └── data/             # Data processing
├── frontend/             # React + Vite
├── tests/                # pytest test suite
├── docs/                 # Documentation
│   ├── TRADER_GUIDE.md   # User guide
│   └── architecture/     # ADRs, specs
├── scripts/              # Utility scripts
├── models/               # Trained ML models
└── .specify/             # Spec-Kit specifications
\`\`\`

## 🛠️ Development

### Commands

```bash
# Server management
./scripts/start.sh        # Start backend + frontend
./scripts/stop.sh         # Stop all servers
./scripts/health_check.sh # Check if services are healthy

# Testing
pytest tests/ -v          # Run all tests

# Formatting
black --line-length=100 src/ tests/
npm run format --prefix frontend

# Model training (FR-004)
python scripts/train_production.py              # Standard training
python scripts/train_production.py --optimize   # With hyperparameter optimization
python scripts/optimize_hyperparams.py --trials 50  # Optimize hyperparameters

# Model versioning (FR-004)
python scripts/version_model.py list            # List model versions
python scripts/version_model.py promote --model model.bin --to production
python scripts/rollback_model.py --previous     # Rollback to previous version

# Model validation (FR-004)
python scripts/validate_model.py --staging --compare-production
```

### Quality Gates

All commits must pass:
- ✅ Python tests (pytest)
- ✅ Formatting (Black, Prettier)
- ✅ Linting (Flake8, ESLint)
- ✅ Security scan (Bandit)

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [TRADER_GUIDE.md](docs/TRADER_GUIDE.md) | How to use the system |
| [Architecture](docs/architecture/) | System design, ADRs |
| [Specifications](.specify/specs/) | Feature specs (Spec-Kit) |

### Specifications (Spec-Kit)

| Spec | Description | Status |
|------|-------------|--------|
| [001 - Risk Management](.specify/specs/001-risk-management/) | Phase 4 features | ✅ Done |
| [002 - NFRs](.specify/specs/002-non-functional-requirements/) | Quality automation | ✅ Done |
| [003 - LLM Analysis](.specify/specs/003-llm-analysis/) | AI explanations | ✅ Done |
| [004 - ML Pipeline](.specify/specs/004-ml-training-pipeline/) | Training automation | ✅ Done |

## 📊 Metrics

| Metric | Value |
|--------|-------|
| ML Accuracy | 82.61% (30 US), 78.37% (50 total) |
| API Response | < 500ms median |
| Test Coverage | > 80% |
| Stocks Tracked | 50 (US + Swiss) |
| Cryptos Tracked | Top 50 by market cap |

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Made with ❤️ for traders**
