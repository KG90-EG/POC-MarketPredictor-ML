# 📈 POC Market Predictor ML

AI-Powered Stock Ranking & Trading Analysis Platform

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)

## 🚀 Quick Links

- 📚 [Documentation](docs/)
- ⚡ [Quick Start](docs/getting-started/QUICKSTART.md)
- 🐳 [Deployment](docs/deployment/DEPLOYMENT.md)
- 📊 [API Docs](http://localhost:8000/docs)

## ✨ Features

- **AI Stock Ranking** - ML-powered buy/sell signals
- **Real-time Data** - Live stocks & crypto tracking
- **Trading Simulation** - Paper trading with auto-execution
- **Portfolio Management** - Multi-asset tracking
- **Alert System** - Price & volatility alerts
- **Modern UI** - Responsive React frontend

## 📁 Project Structure

```
src/           # Source code (trading_fun, training, backtest)
frontend/      # React UI
tests/         # Test suite
scripts/       # Utilities
config/        # All configs (deployment, monitoring)
docs/          # Documentation
```

## 🛠️ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Set up environment
cp .env.example .env

# Start servers
./scripts/start_servers.sh
```

**Access:**

- Frontend: <http://localhost:5173>
- Backend: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

## 🚀 Commands

```bash
# Train model
python -m src.training.trainer

# Run tests
pytest tests/ -v

# Stop servers
./scripts/start_servers.sh --stop

# Docker
docker-compose -f config/deployment/docker-compose.yml up
```

## 📖 Documentation

- [Getting Started](docs/getting-started/)
- [Architecture](docs/architecture/)
- [API Reference](docs/api/)
- [Deployment](docs/deployment/)

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Made with ❤️ for traders**
