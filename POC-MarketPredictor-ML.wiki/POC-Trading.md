# POC-MarketPredictor-ML Wiki

Welcome to the **Market Predictor ML** project wiki! This comprehensive guide covers everything you need to know about our AI-powered stock and cryptocurrency analysis platform.

---

## 📚 Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Features](#features)
- [Development Guide](#development-guide)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key
- Alpha Vantage API key (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

**Backend:**
```bash
python -m market_predictor.server
# Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

**Docker (Production):**
```bash
docker-compose up
```

---

## 🎯 Project Overview

Market Predictor ML is a full-stack financial analysis platform that combines machine learning with real-time market data to provide intelligent investment insights.

### Core Capabilities
- **Stock Analysis**: Real-time price tracking and momentum scoring for stocks
- **Cryptocurrency Rankings**: CoinGecko-powered crypto portfolio with NFT filtering
- **AI-Powered Insights**: GPT-4 integration for contextual market analysis
- **Portfolio Tracking**: Side-by-side comparison of stocks and digital assets
- **WebSocket Support**: Real-time data streaming for live updates

### Technology Stack
- **Backend**: FastAPI, Python 3.9+, Scikit-learn
- **Frontend**: React 18, Vite, Modern ES6+
- **ML/AI**: OpenAI GPT-4, Custom momentum scoring models
- **APIs**: Alpha Vantage, CoinGecko, OpenAI
- **Infrastructure**: Docker, GitHub Actions CI/CD
- **Caching**: Redis-compatible in-memory cache

---

## 🏗️ Architecture

### System Design

```
┌─────────────────┐
│  React Frontend │
│   (Port 5173)   │
└────────┬────────┘
         │ HTTP/WebSocket
         ▼
┌─────────────────┐
│  FastAPI Server │
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐
│OpenAI  │ │Cache │ │CoinGecko│ │Alpha   │
│API     │ │Layer │ │API      │ │Vantage │
└────────┘ └──────┘ └────────┘ └────────┘
```

### Key Components

#### Backend (`market_predictor/`)
- **server.py**: FastAPI application with CORS, health checks, and endpoints
- **trading.py**: Core trading logic, data fetching, ML model integration
- **cache.py**: Redis-compatible caching with TTL support
- **websocket.py**: Real-time data streaming
- **rate_limiter.py**: API rate limiting and request throttling
- **logging_config.py**: Structured logging configuration

#### Frontend (`frontend/src/`)
- **App.jsx**: Main React component with portfolio and market views
- **api.js**: API client with error handling and retry logic
- **components/**: Reusable UI components (ErrorBoundary, HealthCheck)
- **styles.css**: Responsive design with dark mode support

#### ML/Training (`training/`)
- **trainer.py**: Model training pipeline
- **online_trainer.py**: Incremental learning
- **evaluate_and_promote.py**: Model validation and deployment
- **drift_check.py**: Data drift detection

#### Backtesting (`backtest/`)
- **backtester.py**: Historical strategy validation

---

## ✨ Features

### Current Features (Production)

#### 1. **Dual Portfolio View**
- Toggle between Stocks and Cryptocurrency portfolios
- Unified interface for both asset classes
- Real-time price updates

#### 2. **Cryptocurrency Rankings**
- Top 250 cryptocurrencies by market cap
- Pagination support (20/50/100/250 per page)
- NFT token filtering
- Momentum scoring algorithm
- Price change tracking (24h)

#### 3. **Stock Market Analysis**
- Multi-market support (FTSE 100, S&P 500, NASDAQ)
- Individual stock search
- Company detail modals with full metrics
- Momentum-based ranking

#### 4. **AI Analysis Engine**
- Context-aware GPT-4 integration
- Custom analysis based on user queries
- Ranked stock recommendations
- Reasoning and confidence scores

#### 5. **Accessibility (WCAG 2.1 AA)**
- Skip navigation links
- ARIA labels on all interactive elements
- Semantic HTML structure
- Keyboard navigation support
- Screen reader compatible
- Focus management

#### 6. **Developer Experience**
- Comprehensive test suite (20+ tests)
- CI/CD with GitHub Actions
- Docker containerization
- Health monitoring endpoint
- Structured logging

### Upcoming Features (Backlog)

See [BACKLOG.md](../BACKLOG.md) for detailed roadmap including:
- Frontend deployment (Netlify/Vercel)
- Performance monitoring (Prometheus/Grafana)
- A/B testing framework
- Cloud storage integration (S3/GCS)
- Enhanced AI capabilities

---

## 💻 Development Guide

### Project Structure

```
POC-MarketPredictor-ML/
├── market_predictor/          # Backend application
│   ├── server.py         # FastAPI server
│   ├── trading.py        # Trading logic
│   ├── cache.py          # Caching layer
│   ├── websocket.py      # WebSocket handlers
│   └── ...
├── frontend/             # React frontend
│   ├── src/
│   │   ├── App.jsx       # Main component
│   │   ├── api.js        # API client
│   │   └── components/   # UI components
│   └── package.json
├── training/             # ML training scripts
├── backtest/             # Backtesting tools
├── models/               # Trained models
├── tests/                # Test suite
└── docs/                 # Documentation

```

### Configuration

Configuration is managed through environment variables and `pyproject.toml`:

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...           # Required for AI analysis
ALPHA_VANTAGE_API_KEY=...       # Optional, for stock data
LOG_LEVEL=INFO                   # Logging verbosity
CACHE_ENABLED=true               # Enable caching
```

**Key Settings (pyproject.toml):**
- Cache TTLs (market data, AI analysis, crypto data)
- Rate limiting thresholds
- Model paths and configurations
- API retry policies

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Run Tests**
   ```bash
   # Backend tests
   pytest
   
   # Frontend tests (when available)
   cd frontend && npm test
   ```

4. **Lint & Format**
   ```bash
   # Python
   flake8 market_predictor/
   black market_predictor/
   
   # JavaScript
   cd frontend && npm run lint
   ```

5. **Create Pull Request**
   - Reference related issues
   - Provide clear description
   - Ensure CI passes

### Testing

**Backend Testing:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=market_predictor --cov-report=html

# Run specific test file
pytest tests/test_trading.py
```

**Test Categories:**
- Unit tests for trading logic
- API endpoint tests
- Cache behavior tests
- Rate limiter tests
- WebSocket connection tests

---

## 📖 API Reference

### Health Check
```http
GET /health
```
Returns system status including model load state and OpenAI configuration.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "openai_configured": true
}
```

### Get Stocks
```http
GET /stocks?market={market_id}
```
Fetch ranked stocks for a specific market.

**Parameters:**
- `market_id` (string): Market identifier (ftse100, sp500, nasdaq)

**Response:**
```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "price": 178.23,
    "momentum_score": 0.85,
    "change_percent": 2.34
  }
]
```

### Search Stock
```http
POST /search
Content-Type: application/json

{
  "ticker": "AAPL"
}
```

### AI Analysis
```http
POST /analyze
Content-Type: application/json

{
  "context": "What are the best tech stocks?",
  "market": "nasdaq"
}
```

**Response:**
```json
{
  "analysis": "Based on current market conditions...",
  "ranked_stocks": [
    {
      "ticker": "AAPL",
      "score": 0.92,
      "reasoning": "Strong momentum..."
    }
  ]
}
```

### Cryptocurrency Rankings
```http
GET /crypto?limit={limit}&include_nft={bool}
```

**Parameters:**
- `limit` (int): Number of results (20, 50, 100, 250)
- `include_nft` (bool): Include NFT tokens

### WebSocket
```javascript
ws://localhost:8000/ws/{client_id}
```
Real-time data streaming for live market updates.

---

## 🚢 Deployment

### Docker Deployment

**Build and Run:**
```bash
docker-compose up --build
```

**Environment Variables:**
Create `.env` file:
```env
OPENAI_API_KEY=sk-...
ALPHA_VANTAGE_API_KEY=...
```

**Services:**
- **Backend**: Exposed on port 8000
- **Frontend**: Served by backend in production mode

### Production Checklist

- [ ] Set secure API keys
- [ ] Configure CORS for production domain
- [ ] Enable HTTPS
- [ ] Set up monitoring (health endpoint)
- [ ] Configure logging
- [ ] Set cache TTLs appropriately
- [ ] Review rate limits
- [ ] Test backup/restore procedures

### Cloud Deployment Options

**Backend:**
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Apps
- Heroku

**Frontend:**
- Netlify (recommended)
- Vercel
- AWS S3 + CloudFront
- GitHub Pages

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed instructions.

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch** from `main`
3. **Make your changes** with clear commit messages
4. **Add tests** for new functionality
5. **Ensure CI passes** (linting, tests)
6. **Submit a pull request** with detailed description

### Code Standards

**Python:**
- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Maximum line length: 88 (Black formatter)

**JavaScript/React:**
- Use functional components with hooks
- Prop validation with PropTypes
- ES6+ syntax
- Consistent naming conventions

### Reporting Issues

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)
- Relevant logs or error messages

### Feature Requests

For new features:
- Check existing issues first
- Describe the use case
- Explain expected benefits
- Consider implementation approach

---

## 📝 Additional Resources

- **[README.md](../README.md)**: Project overview and quick start
- **[SPEC.md](../SPEC.md)**: Technical specifications
- **[BACKLOG.md](../BACKLOG.md)**: Feature roadmap and priorities
- **[DEPLOYMENT.md](../DEPLOYMENT.md)**: Deployment guides
- **[docs/](../docs/)**: Detailed documentation
- **[docs/history/](../docs/history/)**: Historical implementation docs

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- **Project Board**: [GitHub Projects](https://github.com/KG90-EG/POC-MarketPredictor-ML/projects)
- **Discussions**: [GitHub Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Last Updated**: December 1, 2025  
**Version**: 1.0.0  
**Maintainer**: KG90-EG
