# Project Backlog

**Last Updated**: December 2, 2025  
**Status**: Active Development

This document tracks planned improvements, feature requests, and technical debt for POC-MarketPredictor-ML.

---

## 🔥 High Priority

### Issue #8: Digital Assets Section Improvements
**Status**: ✅ Complete  
**Type**: Enhancement  
**Completed**: December 2, 2025

**Description**: Enhanced the Digital Assets/Cryptocurrency portfolio view with improved UX and functionality.

**Implemented Changes**:
1. **✅ Removed CoinGecko Warning Banner**: Removed redundant yellow info box above table (info already in footer)
2. **✅ Improved Pagination**: Updated to match Stock & Shares pagination style with:
   - Previous/Next buttons
   - Page dropdown selector
   - Consistent styling across portfolio views
3. **✅ Crypto Detail Sidebar**: Created `CryptoDetailSidebar.jsx` component that displays:
   - Asset logo, name, and symbol
   - Momentum signal (Very Bullish/Bullish/Neutral/Bearish/Very Bearish)
   - Price information (current, 24h/7d/30d changes)
   - Market data (market cap, rank, volume, volume/mcap ratio)
   - AI-generated analysis based on momentum score
   - ATH change percentage
4. **✅ Search Functionality in Separate Bubble**: Search moved to dedicated section like Stock & Shares:
   - Real-time filtering by asset name or symbol
   - Separate search card with clear styling
   - Auto-resets to page 1 on search
   - Shows result count
   - "No results" message with clear search button
   - Consistent UX with stock search implementation

**Related Files**:
- `frontend/src/components/CryptoPortfolio.jsx` - Updated with search in bubble, pagination, click handlers
- `frontend/src/components/CryptoDetailSidebar.jsx` - New sidebar component
- `frontend/src/App.jsx` - Added crypto detail state, search state, and handlers
- `frontend/src/styles.css` - Responsive styles for mobile optimization

**Technical Improvements**:
- Used React `useMemo` for efficient search filtering
- Maintained pagination state across searches
- Reusable sidebar styling from stock detail sidebar
- Accessible search input with ARIA labels

---

### Accessibility Improvements
**Status**: ✅ Complete (95%)  
**Type**: Enhancement  
**Priority**: High

**Completed**:
- ✅ Skip navigation link with focus styling
- ✅ Semantic HTML (header, main, section, nav, footer)
- ✅ ARIA labels on all interactive elements
- ✅ ARIA states (pressed, expanded) on toggle buttons
- ✅ Table accessibility (scope attributes)
- ✅ Loading state announcements (aria-live)
- ✅ Color contrast fixes (WCAG AA compliance - 4.5:1 ratio)
  - Updated #666 → #4a4a4a (9.26:1)
  - Updated #555 → #3a3a3a (12.63:1)
  - Updated #999 → #707070 (5.31:1)
  - Updated #aaa → #767676 (4.69:1)
- ✅ Focus indicator improvements
  - Added focus-visible styles for buttons, inputs, textareas
  - 2-3px solid outlines with offset
  - Dark mode compatible focus styles
- ✅ Modal accessibility improvements
  - Added aria-modal and role=dialog
  - Added aria-labelledby linking
  - Added aria-label to close buttons
- ✅ Sidebar accessibility
  - Added role=complementary
  - Added aria-hidden to overlays
  - Error states with role=alert
- ✅ Comprehensive testing documentation
  - Created ACCESSIBILITY_TESTING.md
  - VoiceOver testing guide
  - Screen reader checklist
  - ARIA recommendations

**Remaining** (5%):
- Manual screen reader testing with VoiceOver/NVDA/JAWS
- Comprehensive keyboard navigation testing
- Focus trap implementation for modals (optional enhancement)

**Files**:
- `frontend/src/App.jsx`
- `frontend/src/styles.css`
- `docs/ACCESSIBILITY_TESTING.md`

---

## 🚀 Feature Enhancements

### Deployment Configuration
**Status**: ✅ Ready for Deployment  
**Type**: Infrastructure  
**Priority**: High

**Description**: Backend and frontend are fully configured and ready for cloud deployment to multiple platforms.

**Deployment Preparation - Completed**:
- ✅ **Comprehensive Deployment Guide** (DEPLOYMENT_GUIDE.md)
  - Step-by-step Railway backend deployment
  - Step-by-step Vercel frontend deployment
  - Environment variable configuration
  - CORS setup instructions
  - Production testing procedures
  - Troubleshooting guide
  - Post-deployment checklist

- ✅ **Security Scripts**
  - `scripts/security_check.sh`: Pre-deployment validation
    - Checks .gitignore configuration
    - Scans for exposed secrets
    - Verifies .env not tracked
    - Tests CORS configuration
    - npm audit (0 vulnerabilities found ✓)
    - Checks deployment configs
  - `scripts/test_deployment.sh`: Endpoint testing
    - Health check validation
    - API endpoint testing
    - Response validation
    - Works for local and production URLs

- ✅ **CORS Configuration**
  - Production URL placeholders in server.py
  - Clear comments for adding Vercel/Netlify URLs
  - Ready for immediate update after deployment

**Frontend Deployment - Completed**:
- ✅ **Netlify Configuration** (netlify.toml)
  - Build settings (Vite, Node 18)
  - SPA routing redirects
  - Security headers (CSP, X-Frame-Options, etc.)
  - Asset caching optimization
  - API proxy for production
- ✅ **Vercel Configuration** (vercel.json)
  - Vite framework detection
  - Build and output directory settings
  - Environment variable configuration
  - API rewrites and redirects
  - Security headers
- ✅ **Deployment Guide** (docs/FRONTEND_DEPLOYMENT.md)
  - Netlify deployment (Dashboard + CLI)
  - Vercel deployment instructions
  - AWS S3 + CloudFront setup
  - Docker + Nginx configuration
  - Environment variable management
  - Post-deployment testing
  - CI/CD pipeline examples
  - Troubleshooting guide

**Backend Deployment - Completed**:
- ✅ **Railway Configuration** (railway.toml)
  - Nixpacks builder
  - Gunicorn start command (4 workers)
  - Health check endpoint
  - Auto-restart policy
- ✅ **Render Configuration** (render.yaml)
  - Python environment setup
  - Build and start commands
  - Health check configuration
  - Auto-deploy settings
  - Free tier optimizations
- ✅ **Procfile** (Heroku/Railway compatible)
  - Gunicorn with UvicornWorker
  - 4 workers, 120s timeout
  - Structured logging
- ✅ **Deployment Guide** (docs/BACKEND_DEPLOYMENT.md)
  - Railway deployment (easiest)
  - Render deployment
  - AWS Elastic Beanstalk
  - Docker + ECS/Cloud Run
  - Heroku deployment
  - Security best practices (CORS, rate limiting, secrets)
  - Monitoring setup (Prometheus, Sentry)
  - Load testing with k6
  - CI/CD pipeline examples
  - Troubleshooting guide

**Next Steps** (Ready for Execution):
1. **Deploy Backend to Railway** (5-10 minutes)
   - Create Railway project from GitHub repo
   - Add OPENAI_API_KEY environment variable
   - Get backend URL (e.g., https://your-app.railway.app)
   - Test with `./scripts/test_deployment.sh <railway-url>`

2. **Deploy Frontend to Vercel** (5 minutes)
   - Create Vercel project from GitHub repo
   - Set root directory to `frontend`
   - Add VITE_API_URL with Railway backend URL
   - Get frontend URL (e.g., https://your-app.vercel.app)

3. **Configure Production CORS**
   - Add Vercel URL to `trading_fun/server.py` CORS origins
   - Commit and push (Railway auto-deploys)

4. **Production Testing**
   - Test all endpoints from browser
   - Verify frontend loads data correctly
   - Check error tracking and monitoring

5. **Optional Enhancements**
   - Custom domain setup
   - CI/CD pipeline integration
   - Advanced monitoring (Grafana Cloud, Datadog)

---

**Last Updated**: December 2, 2025  
**Next Review**: After production deployment  
**Deployment Readiness**: 🟢 100% Ready

---

### Performance Monitoring
**Status**: ✅ Complete  
**Type**: Infrastructure  
**Priority**: Medium

**Description**: Add application performance monitoring and metrics.

**Implemented Tools**:
- ✅ Backend: Prometheus + Grafana
- ✅ Prometheus client library (v0.21.0)
- ✅ Docker Compose orchestration
- ✅ Frontend: Sentry for error tracking and performance monitoring

**Metrics Implemented** (20+ metrics):
- ✅ API response times (p50, p95, p99) via `http_request_duration_seconds`
- ✅ Model prediction latency via `model_prediction_duration_seconds`
- ✅ Cache hit/miss rates via `cache_hits_total` / `cache_misses_total`
- ✅ Error rates by endpoint via `http_requests_total{status="5xx"}`
- ✅ Model predictions per minute via `model_predictions_total`
- ✅ Ranking generation time by country via `ranking_generation_duration_seconds`
- ✅ Crypto data fetch duration via `crypto_fetch_duration_seconds`
- ✅ AI analysis requests (cached vs. fresh) via `ai_analysis_requests_total`
- ✅ Rate limit violations via `rate_limit_exceeded_total`
- ✅ System health indicators (model_loaded, openai_configured)

**Implementation Details**:
- Created `/trading_fun/metrics.py`: Centralized metrics collection module
- Updated `/trading_fun/server.py`: Metrics middleware + `/prometheus` endpoint
- Created Prometheus config: `/monitoring/prometheus.yml` (10s scrape interval)
- Created Grafana provisioning: Auto-configured datasources and dashboards
- Created 12-panel Grafana dashboard: `trading-fun-api.json`
  - Panels: Request rate, latency, predictions, cache hit rate, model status, ranking time, probability distribution, AI analysis, rate limits, errors
- Created comprehensive documentation: `docs/PERFORMANCE_MONITORING.md` (600+ lines)
- Docker services: Prometheus (port 9090), Grafana (port 3001, admin/admin)

**Quick Start**:
```bash
docker-compose up -d prometheus grafana
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
```

**Next Steps**:
- Add Sentry for frontend error tracking
- Configure alerting rules for critical metrics
- Set up long-term metric retention

---

### A/B Model Testing & Rollout
**Status**: Planned  
**Type**: Feature  
**Priority**: Medium

**Description**: Implement gradual model rollout with A/B testing capabilities.

**Features**:
- Model versioning system
- Traffic splitting (e.g., 90% v1, 10% v2)
- Performance comparison metrics
- Automated promotion based on metrics
- Rollback mechanism

**Implementation**:
- Model registry in database or S3
- Feature flags for model selection
- Comparison metrics in dashboard

---

### Cloud Artifact Storage
**Status**: Planned  
**Type**: Infrastructure  
**Priority**: Medium

**Description**: Migrate model artifacts to cloud storage instead of Git LFS.

**Benefits**:
- Faster model deployment
- Better version control
- Reduced repository size
- Access control and audit trails

**Options**:
- AWS S3 (current scripts support this)
- Google Cloud Storage
- Azure Blob Storage
- MLflow Model Registry

**Required Secrets**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET` (for model artifacts)

---

### Enhanced AI Analysis
**Status**: Planned  
**Type**: Feature  
**Priority**: Low

**Description**: Improve AI-powered stock analysis with more context and insights.

**Enhancements**:
- Sector analysis and comparison
- Historical performance context
- Risk assessment scoring
- Portfolio diversification suggestions
- Market sentiment integration

**Requirements**:
- Enhanced OpenAI prompt engineering
- Additional data sources (news, sentiment)
- Caching strategy for expensive operations

---

## 🐛 Technical Debt & Improvements

### Test Coverage Expansion
**Status**: ✅ 75% Complete  
**Type**: Testing  
**Priority**: Medium

**Current Coverage**:
- ✅ 20 passing backend tests (trading indicators, endpoints)
- ✅ 30 passing crypto module tests (CoinGecko API, momentum scoring, edge cases)
- ✅ React Testing Library configured with Vitest
- ✅ Frontend component tests created (StockRanking, CryptoPortfolio, HelpModal)
- ✅ Test fixtures and mocking setup
- ✅ Sentry error tracking integrated

**Completed**:
- ✅ Crypto module comprehensive test suite (test_crypto.py)
  - CoinGecko API integration tests (mocked)
  - Momentum scoring algorithm tests
  - Error handling and edge cases
  - Constants and configuration tests
  - Search and ranking functionality tests
- ✅ Frontend component test suite
  - StockRanking component tests (10 test cases)
  - CryptoPortfolio component tests (14 test cases)
  - HelpModal component tests (7 test cases)
  - Error tracking with Sentry integration

**Missing Coverage** (25%):
- End-to-end tests (Playwright/Cypress)
- Config module validation tests
- Service layer comprehensive tests
- Integration tests for WebSocket functionality
- Additional component tests (CompanyDetailSidebar, AIAnalysisSection)

---

### Code Quality Improvements
**Status**: ✅ 100% Complete  
**Type**: Refactoring  
**Priority**: Low

**Completed**:
- ✅ ESLint v9 + Prettier configured for frontend
  - Modern flat config format
  - React, React Hooks, JSX A11y plugins
  - npm scripts: lint, lint:fix, format, format:check
- ✅ Python type hints added to trading.py
  - Type annotations on all public functions
  - Comprehensive docstrings with Args/Returns
  - typing module imports (Optional, Tuple, List, Dict)
- ✅ App.jsx refactoring (Phase 1 & 2): 1223 → 715 lines (42% reduction)
  - Extracted HelpModal component (110 lines)
  - Extracted CompanyDetailSidebar component (165 lines)
  - Extracted AIAnalysisSection component (55 lines)
  - Extracted StockRanking component (215 lines)
  - Extracted CryptoPortfolio component (280 lines)
  - PropTypes validation added to all components
  - Maintained accessibility features (ARIA labels, roles)
  - Removed unused helper functions (getRankBadgeClass moved to StockRanking)
  - App.jsx now focuses on orchestration logic only

**Achievement**: Successfully reduced App.jsx from 1223 lines to 715 lines through systematic component extraction, improving testability, maintainability, and separation of concerns. All extracted components include PropTypes validation and preserve accessibility features.

---

### Documentation Enhancements
**Status**: ✅ 100% Complete  
**Type**: Documentation  
**Priority**: Low

**Completed**:
- ✅ **OpenAPI/Swagger Documentation**
  - FastAPI metadata (title, description, version, contact, license)
  - Endpoint tags: System, Monitoring, Predictions, Cryptocurrency, AI Analysis
  - Comprehensive endpoint descriptions with examples
  - Response model schemas (HealthResponse, PredictionResponse, StockRanking, CryptoRanking)
  - Interactive Swagger UI at /docs
  - ReDoc at /redoc
  - OpenAPI schema at /openapi.json

- ✅ **Contributing Guidelines** (CONTRIBUTING.md)
  - Code standards (Python: Black/Flake8 127 chars, JS: ESLint v9 flat config/Prettier)
  - PR process and commit conventions (Conventional Commits)
  - Setup instructions and troubleshooting
  - Testing requirements and examples (pytest, Vitest)
  - Accessibility guidelines
  - Development workflow (branch strategy, code review)

- ✅ **Architecture Decision Records (ADRs)**
  - **ADR-001: Architecture Overview**
    - FastAPI + React + Vite stack justification
    - Microservices-inspired architecture
    - Data flow diagrams
    - Alternatives considered (Flask, Django, Next.js, Kubernetes)
    - Consequences and trade-offs
  - **ADR-002: Model Training Strategy**
    - XGBoost classifier with online learning
    - Feature engineering (RSI, MACD, Bollinger Bands)
    - Training pipeline (offline + online)
    - Model evaluation and promotion (F1 > 0.65 threshold)
    - Drift detection strategy
    - Alternatives considered (LSTM, Random Forest, RL)
  - **ADR-003: Caching Strategy**
    - Multi-layered TTL cache (stock: 5min, crypto: 2min, AI: 30min)
    - Rate limiter implementation (token bucket)
    - Cache warming strategy
    - Alternatives considered (Redis, no caching, CDN, browser cache)
    - Monitoring metrics (hit rate, memory usage)

- ✅ **Deployment Guides**
  - **FRONTEND_DEPLOYMENT.md**: Netlify, Vercel, AWS S3, Docker
  - **BACKEND_DEPLOYMENT.md**: Railway, Render, AWS EB, Heroku, Docker/ECS

**Remaining** (Optional Nice-to-Have):
- ⏳ Component library documentation (Storybook, ~1 day, optional for MVP)

---

## 📋 Completed Features

### ✅ Cryptocurrency Portfolio View
**Completed**: December 1, 2025

**Features**:
- CoinGecko API integration
- Dynamic crypto fetching (top 20-250 by market cap)
- Momentum scoring algorithm
- Pagination (20 items/page)
- NFT token toggle
- Limit selector (20/50/100/200)
- Tooltips on all metrics
- Real-time data refresh

---

### ✅ Comprehensive Test Suite
**Completed**: December 1, 2025

**Coverage**:
- 20 backend tests (unit + integration)
- pytest configuration
- CI integration
- Fixtures and mocking

---

### ✅ Configuration Management
**Completed**: December 1, 2025

**Features**:
- Centralized `config.py`
- Type-safe configuration
- Environment variable management
- Validation logic

---

### ✅ Service Layer Architecture
**Completed**: December 1, 2025

**Structure**:
- StockService
- ValidationService
- HealthService
- Separated from API routes

---

### ✅ CI/CD Pipeline
**Completed**: December 1, 2025

**Workflows**:
- Python linting (flake8, black)
- Automated testing
- Model promotion
- GitHub Actions integration

---

## 📝 Issue Labels & Priority Guide

**Priority Levels**:
- 🔥 **High**: Blocking issues, critical bugs, security
- 🚀 **Medium**: Feature enhancements, improvements
- 📌 **Low**: Nice-to-have, technical debt, documentation

**Issue Types**:
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `infrastructure`: DevOps, deployment, CI/CD
- `testing`: Test coverage improvements
- `documentation`: Documentation updates
- `refactoring`: Code quality improvements
- `security`: Security-related issues

---

## 🔗 Related Documentation

- [Architecture Review](docs/history/ARCHITECTURE_REVIEW.md)
- [Implementation Summary](docs/history/IMPLEMENTATION_SUMMARY.md)
- [Improvements Guide](docs/history/IMPROVEMENTS.md)
- [GitHub Actions Fixes](docs/history/GITHUB_ACTIONS_FIXES.md)
- [Main README](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Specification](SPEC.md)
- **[Contributing Guidelines](CONTRIBUTING.md)** ⭐ NEW
- **[Architecture Decision Records](docs/)** ⭐ NEW
  - [ADR-001: Architecture Overview](docs/ADR-001-architecture-overview.md)
  - [ADR-002: Model Training Strategy](docs/ADR-002-model-training-strategy.md)
  - [ADR-003: Caching Strategy](docs/ADR-003-caching-strategy.md)
- **[Frontend Deployment Guide](docs/FRONTEND_DEPLOYMENT.md)** ⭐ NEW
- **[Backend Deployment Guide](docs/BACKEND_DEPLOYMENT.md)** ⭐ NEW

---

## 📊 Progress Tracking

**Overall Project Health**: 🟢 Excellent

- **Code Quality**: 🟢 Excellent (refactored, modular, tested)
- **Test Coverage**: 🟢 Good (backend strong, 75% frontend coverage with 31+ tests)
- **Documentation**: 🟢 Excellent (100% complete - comprehensive guides, ADRs, contributing)
- **CI/CD**: 🟢 Excellent (automated, reliable)
- **Accessibility**: 🟢 Excellent (95% complete)
- **Performance**: 🟢 Excellent (monitoring, caching, rate limiting)
- **Security**: 🟡 Moderate (needs secret scanning, dependency audit)
- **Error Tracking**: 🟢 Excellent (Sentry integrated)
- **Deployment Readiness**: 🟢 Excellent (configs for Railway, Render, Netlify, Vercel)

---

**Last Review**: December 2, 2025  
**Next Review**: December 9, 2025 (after production deployment)  
**Project Completion**: ~95% (Ready for production - deployment pending manual platform setup)
