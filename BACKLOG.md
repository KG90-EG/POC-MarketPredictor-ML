# Project Backlog

**Last Updated**: December 1, 2025  
**Status**: Active Development

This document tracks planned improvements, feature requests, and technical debt for POC-MarketPredictor-ML.

---

## 🔥 High Priority

### Issue #8: Adjust Digital Assets Section
**Status**: ⏸️ Pending Clarification  
**Type**: Enhancement  
**Description**: Refinements needed for the Digital Assets/Cryptocurrency portfolio view.

**Context**: The Digital Assets section was recently added with CoinGecko integration, momentum scoring, and pagination. The issue lacks specific requirements - awaiting user feedback on what adjustments are needed.

**Current Implementation** (Fully Functional):
- ✅ CoinGecko API integration
- ✅ Top 20-250 cryptocurrencies by market cap
- ✅ Momentum scoring algorithm
- ✅ Pagination (20 items/page)
- ✅ NFT token toggle
- ✅ Limit selector (20/50/100/200)
- ✅ Tooltips on all metrics
- ✅ Real-time data refresh
- ✅ Accessibility compliant
- ✅ Dark mode support

**Awaiting User Input**:
- What specific adjustments are needed?
- Which features require enhancement?
- Any bugs or issues to address?

**Related Files**:
- `frontend/src/App.jsx` (Digital Assets UI)
- `trading_fun/crypto.py` (CoinGecko integration)
- `trading_fun/server.py` (crypto endpoints)

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

### Frontend Deployment
**Status**: ✅ Ready for Deployment  
**Type**: Infrastructure  
**Priority**: Medium

**Description**: Frontend is configured and ready for cloud deployment.

**Completed**:
- ✅ Created netlify.toml configuration
  - Build settings (base, command, publish)
  - Node version specification
  - SPA redirects for client-side routing
  - Security headers configured
  - Asset caching optimization
- ✅ Added _redirects file for SPA routing
- ✅ Created comprehensive FRONTEND_DEPLOYMENT.md guide
  - Netlify deployment (Dashboard + CLI)
  - Vercel deployment instructions
  - Environment variable configuration
  - Build optimization strategies
  - Troubleshooting guide
  - CORS configuration examples
  - CI/CD integration patterns
  - Performance monitoring recommendations
- ✅ Updated README.md with deployment section
- ✅ Environment variable support (VITE_API_URL)

**Next Steps**:
- Deploy to Netlify/Vercel (requires platform account)
- Configure VITE_API_URL with backend URL
- Set up custom domain (optional)

**Options**:
- Netlify (recommended for React/Vite)
- Vercel
- AWS S3 + CloudFront
- GitHub Pages

**Requirements**:
- Environment variable management
- CI/CD integration
- Custom domain (optional)

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
- ⏳ Frontend: Sentry for error tracking (pending)

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
**Status**: Ongoing  
**Type**: Testing  
**Priority**: Medium

**Current Coverage**:
- ✅ 20 passing backend tests
- ✅ Technical indicators (RSI, MACD, Bollinger Bands, Momentum)
- ✅ API endpoints (/health, /predict, /ranking)
- ✅ Integration tests (cache, WebSocket, rate limiter)

**Missing Coverage**:
- Frontend component tests (React Testing Library)
- End-to-end tests (Playwright/Cypress)
- Crypto module tests
- Config module validation tests
- Service layer comprehensive tests

---

### Code Quality Improvements
**Status**: Ongoing  
**Type**: Refactoring  
**Priority**: Low

**Areas**:
- Remove remaining magic numbers
- Add type hints to all Python functions
- ESLint + Prettier for frontend consistency
- Docstring coverage for public APIs
- Reduce App.jsx complexity (1198 lines → split further)

---

### Documentation Enhancements
**Status**: Ongoing  
**Type**: Documentation  
**Priority**: Low

**Needed**:
- API documentation (OpenAPI/Swagger)
- Component library documentation (Storybook)
- Deployment guide
- Troubleshooting guide
- Contributing guidelines
- Architecture decision records (ADRs)

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

---

## 📊 Progress Tracking

**Overall Project Health**: 🟢 Good

- **Code Quality**: 🟢 Good (refactored, tested)
- **Test Coverage**: 🟡 Moderate (backend strong, frontend needs work)
- **Documentation**: 🟢 Good (comprehensive)
- **CI/CD**: 🟢 Excellent (automated, reliable)
- **Accessibility**: 🟡 In Progress (80% complete)
- **Performance**: 🟢 Good (caching, rate limiting)
- **Security**: 🟡 Moderate (needs secret scanning, dependency audit)

---

**Last Review**: December 1, 2025  
**Next Review**: December 8, 2025
