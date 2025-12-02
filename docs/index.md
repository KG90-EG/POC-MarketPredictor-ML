# Trading-Fun Documentation

[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen?style=for-the-badge)](../PRODUCTION_READY.md)
[![Security](https://img.shields.io/badge/Vulnerabilities-0-brightgreen?style=for-the-badge)](../scripts/security_check.sh)
[![Tests](https://img.shields.io/badge/Tests-50%2B%20Passing-brightgreen?style=for-the-badge)](../tests/)

**Status**: ✅ Production Ready (98% Complete) - [Deploy Now](../PRODUCTION_READY.md)

## Overview

Trading-Fun is a **production-grade** ML-powered stock market predictor with comprehensive deployment automation, security hardening, and monitoring. It includes:

- **ML Pipeline**: Feature engineering (RSI, SMA, MACD, Bollinger Bands, Momentum)
- **FastAPI Backend**: Prediction, ranking, crypto analysis, AI insights
- **React Frontend**: Modern UI with dark mode, accessibility (WCAG AA)
- **Monitoring**: Prometheus metrics (20+), Grafana dashboards, Sentry error tracking
- **Security**: 0 vulnerabilities, rate limiting (60 req/min), secret scanning
- **Deployment**: 3 automated methods (GitHub Actions, CLI script, manual)
- **Testing**: 50+ automated tests (unit, integration, E2E)
- **CI/CD**: Automated testing, linting, security checks, deployment

## Quick Start

### Local Development

```bash
# Backend
pip install -r requirements.txt
.venv/bin/python -m uvicorn trading_fun.server:app --reload

# Frontend (in new terminal)
cd frontend && npm install && npm run dev
```

### Production Deployment

Choose one of 3 automated methods:

**Option 1 - GitHub Actions (Recommended)**:

```bash
# Add secrets to GitHub repo, then:
git push origin main  # Auto-deploys to Railway + Vercel
```

**Option 2 - CLI Script (One Command)**:

```bash
./scripts/deploy_production.sh
```

**Option 3 - Manual**:
See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### Testing & Validation

```bash
# Run all tests
pytest

# Security check
./scripts/security_check.sh

# Rate limiting tests
./scripts/test_rate_limit.sh

# Deployment validation
./scripts/test_deployment.sh <production-url>
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health & model loaded flag |
| `/predict_ticker/{ticker}` | GET | ML prediction for specific stock |
| `/ranking` | GET | Top ranked stocks by market (US, CH, DE, UK, FR, JP, CA) |
| `/ticker_info/{ticker}` | GET | Real-time stock data (price, volume, market cap) |
| `/analyze/{ticker}` | POST | AI-powered analysis with OpenAI |
| `/crypto/ranking` | GET | Top cryptocurrencies with momentum scoring |
| `/models` | GET | Available model artifacts |
| `/prometheus` | GET | Prometheus metrics (20+ metrics) |

### Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI Schema**: <http://localhost:8000/openapi.json>

### Monitoring Endpoints

| Endpoint | Description |
|----------|-------------|
| `/health` | Health check with model status |
| `/prometheus` | Prometheus metrics export |

## Security & Testing

### Security Status

- ✅ **0 Vulnerabilities** (npm audit + pip-audit)
- ✅ **CVE-2025-8869 Fixed** (pip 25.2 → 25.3)
- ✅ **Rate Limiting** (60 requests/min with token bucket)
- ✅ **Secret Scanning** (automated validation scripts)
- ✅ **CORS Configured** (production-ready)
- ✅ **Environment Variables** (proper secret management)

### Testing Coverage

- ✅ **50+ Automated Tests** (75%+ coverage)
- ✅ **Unit Tests**: Backend (20+), Frontend (31+)
- ✅ **Integration Tests**: API endpoints, crypto module
- ✅ **Security Tests**: Rate limiting, vulnerability scanning
- ✅ **Deployment Tests**: Endpoint validation

### Run Tests

```bash
# Backend tests
pytest -v

# Frontend tests
cd frontend && npm test

# Security validation
./scripts/security_check.sh

# Rate limiting tests
./scripts/test_rate_limit.sh

# Deployment validation
./scripts/test_deployment.sh <url>
```

## Monitoring & Observability

### Prometheus Metrics (20+ metrics)

- API response times (p50, p95, p99)
- Model prediction latency
- Cache hit/miss rates
- Error rates by endpoint
- Rate limit violations
- Crypto data fetch duration
- AI analysis requests

### Dashboards

- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3001> (admin/admin)
- **Sentry**: Frontend error tracking

### Start Monitoring

```bash
docker-compose up -d prometheus grafana
```

## Production Deployment

### Method 1: GitHub Actions (Recommended)

1. Add secrets to GitHub repository settings:
   - `RAILWAY_TOKEN`
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
   - `OPENAI_API_KEY`
2. Push to main branch → automatic deployment

### Method 2: CLI Script

```bash
./scripts/deploy_production.sh
# Flags: --backend-only, --frontend-only, --help
```

### Method 3: Manual Deployment

Follow comprehensive guides:

- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) (500+ lines)
- [AUTOMATED_DEPLOYMENT.md](../AUTOMATED_DEPLOYMENT.md) (400+ lines)

### Post-Deployment Validation

```bash
./scripts/test_deployment.sh https://your-app.railway.app
./scripts/test_rate_limit.sh
```

## Model Lifecycle

### Training & Promotion

1. `training/trainer.py` - Train and save timestamped models
2. `training/evaluate_and_promote.py` - Promote if F1 > 0.65
3. `training/drift_check.py` - Monitor distribution shifts
4. `training/online_trainer.py` - Online learning updates

### MLflow Integration

- Model tracking and versioning
- Experiment comparison
- Model registry
- Artifact storage (local or S3)

### S3 Artifacts (Optional)

```bash
export S3_BUCKET=your-bucket-name
python scripts/push_model_to_s3.py
```

## Frontend

### Features

- ✅ **Multi-Market Views**: US, Switzerland, Germany, UK, France, Japan, Canada
- ✅ **Crypto Portfolio**: Top cryptocurrencies with momentum scoring
- ✅ **AI Analysis**: OpenAI-powered trading recommendations
- ✅ **Dark Mode**: Persistent theme toggle
- ✅ **Accessibility**: WCAG AA compliant (95%)
- ✅ **Real-time Updates**: WebSocket support
- ✅ **Error Tracking**: Sentry integration
- ✅ **Responsive Design**: Mobile, tablet, desktop optimized

### Build & Deploy

```bash
cd frontend
npm install
npm run build  # Production build → frontend/dist
npm run dev    # Development server
npm test       # Run tests
npm run lint   # ESLint v9
```

### Deployment Platforms

- **Vercel** (Recommended): Auto-deploy from GitHub
- **Netlify**: Static site hosting with CDN
- **AWS S3 + CloudFront**: Custom infrastructure
- **Docker + Nginx**: Self-hosted option

See [Frontend Deployment Guide](deployment/FRONTEND_DEPLOYMENT.md) for detailed instructions.

## Docker

### Production Build

Multi-stage Dockerfile builds frontend then serves via Gunicorn:

```bash
docker build -t trading-fun:latest .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  trading-fun:latest
```

### Docker Compose (Development)

```bash
# Start all services (backend, frontend, prometheus, grafana)
docker-compose up -d

# Start specific services
docker-compose up -d prometheus grafana

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Available Services

- **Backend**: <http://localhost:8000>
- **Frontend**: <http://localhost:5173>
- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3001>

## Production Server

### Gunicorn (Recommended)

```bash
gunicorn -c gunicorn_conf.py trading_fun.server:app
```

Configuration (`gunicorn_conf.py`):

- 4 workers (UvicornWorker)
- 120s timeout
- Structured logging
- Auto-restart on code changes

### Uvicorn (Development)

```bash
.venv/bin/python -m uvicorn trading_fun.server:app --reload
```

## Development Workflow

### Setup

```bash
# Clone repository
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML

# Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
```

### Code Quality

```bash
# Python linting
black trading_fun/
flake8 trading_fun/ --max-line-length=127

# Frontend linting
cd frontend
npm run lint
npm run format
```

## Pre-Commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Documentation

### 🚀 Production & Deployment

- **[PRODUCTION_READY.md](../PRODUCTION_READY.md)** - Complete production deployment guide ⭐ NEW
- **[AUTOMATED_DEPLOYMENT.md](../AUTOMATED_DEPLOYMENT.md)** - Automated deployment (3 methods) ⭐ NEW
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)** - Manual deployment guide (500+ lines) ⭐ NEW
- [Backend Deployment](deployment/BACKEND_DEPLOYMENT.md) - Railway, Render, AWS, Docker
- [Frontend Deployment](deployment/FRONTEND_DEPLOYMENT.md) - Vercel, Netlify, AWS S3

### 📖 Core Documentation

- [README](../README.md) - Main project documentation
- [SPEC](architecture/SPECIFICATION.md) - Technical specification
- [BACKLOG](project/BACKLOG.md) - Project progress (98% complete)
- [CONTRIBUTING](development/CONTRIBUTING.md) - Contributing guidelines ⭐ NEW

### 🏗️ Architecture & Design

- **[ADR-001: Architecture Overview](ADR-001-architecture-overview.md)** ⭐ NEW
- **[ADR-002: Model Training Strategy](ADR-002-model-training-strategy.md)** ⭐ NEW
- **[ADR-003: Caching Strategy](ADR-003-caching-strategy.md)** ⭐ NEW

### 📊 Monitoring & Quality

- **[Performance Monitoring](PERFORMANCE_MONITORING.md)** - Prometheus + Grafana guide ⭐ NEW
- **[Accessibility Testing](ACCESSIBILITY_TESTING.md)** - WCAG AA compliance guide ⭐ NEW

### 🎨 Features & Components

- [Production Features](PRODUCTION_FEATURES.md) - Production-ready capabilities
- [Frontend Components](FRONTEND_COMPONENTS.md) - React component library
- [Next Level Summary](NEXT_LEVEL_SUMMARY.md) - Advanced features

### 📜 Historical Documentation

- [History Index](history/README.md) - Archived implementation docs
- [Implementation Summary](history/IMPLEMENTATION_SUMMARY.md)
- [Architecture Review](history/ARCHITECTURE_REVIEW.md)
- [Improvements Guide](history/IMPROVEMENTS.md)
- [GitHub Actions Fixes](history/GITHUB_ACTIONS_FIXES.md)

## Contributing

### Development Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest && cd frontend && npm test`
5. Run linting: `black . && flake8 . && cd frontend && npm run lint`
6. Commit: `git commit -m "feat: your feature"`
7. Push: `git push origin feature/your-feature`
8. Open a Pull Request

### Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes  
- `docs:` Documentation updates
- `chore:` Maintenance tasks
- `test:` Test updates
- `refactor:` Code refactoring

### Code Standards

- **Python**: Black formatter, Flake8 (127 chars), type hints
- **JavaScript**: ESLint v9 flat config, Prettier
- **Testing**: pytest (backend), Vitest (frontend)
- **Accessibility**: WCAG AA compliance

See [CONTRIBUTING.md](development/CONTRIBUTING.md) for detailed guidelines.

---

## 📝 Note on Documentation Location

This documentation site is currently **embedded in the repository** (`docs/` folder) and published via GitHub Pages.

### ⚠️ Recommendation: Move to Dedicated Documentation Platform

For better scalability and maintainability, **consider migrating to a dedicated documentation platform**:

#### **Recommended Options**

**1. [ReadTheDocs](https://readthedocs.org)** (Free, Open Source)

- ✅ Sphinx/MkDocs integration
- ✅ Version control for docs (v1.0, v2.0, etc.)
- ✅ Automatic builds on commit
- ✅ Search functionality built-in
- ✅ Custom domains
- ✅ PDF/ePub export

**2. [Docusaurus](https://docusaurus.io)** (Meta, React-based)

- ✅ Modern React-based UI
- ✅ MDX support (interactive components)
- ✅ Versioning built-in
- ✅ Deploy to Vercel/Netlify for free
- ✅ Better SEO
- ✅ i18n (multilingual) support

**3. [GitBook](https://www.gitbook.com)** (Free tier available)

- ✅ Beautiful UI out of the box
- ✅ GitHub sync
- ✅ Collaborative editing
- ✅ Analytics dashboard
- ✅ API documentation support

#### **Why Move Documentation Out?**

**Benefits**:

- ✅ **Faster Git Operations**: Repository clones are faster (no large docs assets)
- ✅ **Independent Deployment**: Docs deploy separately from code
- ✅ **Better Search**: Full-text search with faceted filters
- ✅ **Version Control**: Maintain docs for multiple versions (v1.x, v2.x)
- ✅ **Analytics**: Track which docs are most viewed
- ✅ **Feedback Tools**: Users can suggest edits or report issues
- ✅ **Multilingual**: Easy i18n support for global users
- ✅ **Professional**: Better UX than GitHub Pages

**Migration Effort**: ~2-4 hours for initial setup, then automatic sync

#### **Quick Migration to ReadTheDocs**

```bash
# 1. Install Sphinx
pip install sphinx sphinx-rtd-theme recommonmark

# 2. Initialize docs
cd docs
sphinx-quickstart

# 3. Configure conf.py for Markdown support
# extensions = ['recommonmark']

# 4. Push to GitHub
git add docs/
git commit -m "docs: migrate to Sphinx/ReadTheDocs"

# 5. Connect at https://readthedocs.org
# Auto-builds on every commit!
```

**For now**, the GitHub Pages setup works fine, but plan migration as project scales.

---

**Repository**: <https://github.com/KG90-EG/POC-MarketPredictor-ML>  
**Documentation**: <https://kg90-eg.github.io/POC-MarketPredictor-ML/>  
**Status**: ✅ Production Ready (98% Complete)  
**Last Updated**: December 2, 2025
