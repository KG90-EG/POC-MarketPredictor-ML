# POC-MarketPredictor-ML

🚀 A production-ready FastAPI + React application for ranking equities/crypto with ML signals and simulating paper trades with real-time analytics.

[![Python CI](https://github.com/KG90-EG/POC-MarketPredictor-ML/actions/workflows/ci.yml/badge.svg)](https://github.com/KG90-EG/POC-MarketPredictor-ML/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📊 Project Status

**Version:** 1.0.0-beta  
**Last Updated:** January 2026  
**Status:** Production-Ready Beta

- ✅ **Backend/Frontend:** Fully integrated with simulation, trading, and real-time updates
- ✅ **Core Features:** Stock/crypto ranking, paper trading, portfolio management
- ⚠️ **Known Issues:** Module import inconsistencies (`trading_fun/` vs `market_predictor/`)
- 🔄 **In Progress:** CI/CD pipeline fixes, PostgreSQL migration, authentication

---

## ✨ Key Features

### Trading & Analytics

- 📈 **Stock & Crypto Rankings** - ML-powered rankings with confidence scores
- 💼 **Paper Trading Simulation** - Risk-free trading with realistic P&L tracking
- 📊 **Portfolio Management** - Real-time position tracking and performance metrics
- 🎯 **AI Recommendations** - Automated buy/sell suggestions with confidence levels
- 📉 **Technical Analysis** - RSI, MACD, Bollinger Bands, Momentum indicators

### Platform Features

- 🌐 **Multi-Language Support** - English, German, Italian, Spanish, French
- 🎨 **Dark/Light Theme** - User-configurable UI themes
- ⚡ **Real-time Updates** - WebSocket-based live data streaming
- 📱 **Responsive Design** - Mobile-friendly interface
- 🔒 **Rate Limiting** - 60 requests/minute per user
- 📊 **Prometheus Metrics** - Production-ready monitoring

---

## 🏗️ Architecture

```
Frontend (React/Vite) → FastAPI Backend (trading_fun/) → ML Models
                              ↓
                    SQLite DB (simulations, watchlists)
                              ↓
                    External APIs (yfinance, CoinGecko)
```

See [**Architecture Documentation**](docs/ARCHITECTURE.md) for detailed diagrams and data flow.

---

## 🚀 Quick Start

### Prerequisites

- **Python:** 3.10 - 3.12 (3.14 supported)
- **Node.js:** 18+ with npm
- **Optional:** Docker, Redis (for production caching)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Frontend dependencies
cd frontend
npm install
cd ..

# 4. Set up environment variables (optional)
cp .env.example .env
# Edit .env with your settings
```

### Running the Application

#### Option 1: Automated Start (Recommended)

```bash
# Start both servers with health checks and auto-recovery
./scripts/start_servers.sh

# Check status
./scripts/start_servers.sh --status

# Stop all servers
./scripts/start_servers.sh --stop
```

**Features:** Automatic port cleanup, health checks, process management, detailed logging

#### Option 2: Manual Start (Development)

```bash
# Terminal 1: Start Backend
python -m trading_fun.server
# Backend runs on http://localhost:8000

# Terminal 2: Start Frontend
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

#### Option 2: Docker (Production)

```bash
docker-compose up
# Access at http://localhost:8000 (backend) and http://localhost:5173 (frontend)
```

#### Option 3: Using Start Script

```bash
./start_servers.sh
# Starts both backend and frontend with health checks
```

### Verify Installation

1. **Backend Health Check:**

   ```bash
   curl http://localhost:8000/health
   ```

   Expected: `{"status": "healthy", ...}`

2. **Frontend:**
   Open <http://localhost:5173> in your browser

3. **API Documentation:**
   Visit <http://localhost:8000/docs> for interactive API docs

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/ARCHITECTURE.md) | System design, data flow, module structure |
| [API Reference](docs/api/simulation.md) | Endpoint documentation with examples |
| [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md) | Production deployment instructions |
| [Development Guide](docs/development/) | Setup, testing, contributing guidelines |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Project Backlog](docs/project/backlog.md) | Current priorities and roadmap |

---

## 🧪 Testing

```bash
# Run all backend tests
pytest

# Run with coverage
pytest --cov=trading_fun --cov-report=html

# Run specific test file
pytest tests/test_simulation.py

# Frontend tests (when available)
cd frontend
npm test
```

---

## 🛠️ Development

### Project Structure

```
POC-MarketPredictor-ML/
├── trading_fun/          # ✅ Active backend module
│   ├── server.py         # FastAPI application
│   ├── simulation.py     # Paper trading engine
│   ├── trading.py        # ML & trading logic
│   └── ...               # Supporting modules
├── market_predictor/     # ⚠️ Legacy module (being phased out)
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── api.js        # API client
│   │   └── translations.js
│   └── package.json
├── tests/                # Backend tests
├── training/             # ML training scripts
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD pipelines
```

### Module Consolidation Notice

⚠️ **Important:** The project currently has two backend modules:

- **`trading_fun/`** - Active, current implementation
- **`market_predictor/`** - Legacy, being phased out

All new development should use `trading_fun/`. See [Migration Plan](docs/ARCHITECTURE.md#migration-plan) for details.

---

## 🐛 Known Issues & Workarounds

### 1. Module Import Inconsistencies

**Issue:** `trading_fun/server.py` imports from `market_predictor.simulation`  
**Status:** Tracked in backlog  
**Workaround:** Both modules currently required

### 2. CI/CD Secret Warnings

**Issue:** GitHub Actions warnings about missing secrets  
**Status:** Non-blocking, CI passes  
**Fix:** Add secrets in GitHub Settings → Secrets → Actions

### 3. Frontend Build Errors

**Issue:** `SimulationDashboard.jsx` async/await issues  
**Status:** Fixed in latest commit  
**Solution:** Updated Promise.all to sequential awaits

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for more solutions.

---

## 🚢 Deployment

### Supported Platforms

- **Railway** - Recommended for backend
- **Render** - Alternative backend hosting
- **Netlify** - Frontend hosting
- **Vercel** - Alternative frontend hosting
- **Docker** - Self-hosted deployment

See [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md) for step-by-step instructions.

---

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **yfinance** - Stock market data
- **CoinGecko API** - Cryptocurrency data
- **FastAPI** - Modern Python web framework
- **React** - Frontend framework
- **scikit-learn** - Machine learning library

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- **Discussions:** [GitHub Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)
- **Documentation:** [Full Docs](docs/index.md)

---

**Made with ❤️ for traders and developers**
