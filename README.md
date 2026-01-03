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
src/           # Source code (trading_engine, training, backtest)
frontend/      # React UI
tests/         # Test suite
scripts/       # Utilities
config/        # All configs (deployment, monitoring)
docs/          # Documentation
```

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

**See:** [Training Guide](docs/TRAINING_GUIDE.md) for complete instructions.

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

- [Getting Started](docs/getting-started/)
- [Server Management](docs/SERVER_MANAGEMENT.md)
- [Model Training](docs/TRAINING_GUIDE.md)
- [Architecture](docs/architecture/)
- [API Reference](docs/api/)
- [Deployment](docs/deployment/)

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Made with ❤️ for traders**
