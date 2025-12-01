# Project Backlog

**Last Updated**: December 1, 2025  
**Status**: Active Development

This document tracks planned improvements, feature requests, and technical debt for POC-MarketPredictor-ML.

---

## 🔥 High Priority

### Issue #8: Adjust Digital Assets Section
**Status**: Open  
**Type**: Enhancement  
**Description**: Refinements needed for the Digital Assets/Cryptocurrency portfolio view.

**Context**: The Digital Assets section was recently added with CoinGecko integration, momentum scoring, and pagination. Further adjustments may be needed based on user feedback.

**Related Files**:
- `frontend/src/App.jsx` (Digital Assets UI)
- `trading_fun/crypto.py` (CoinGecko integration)
- `trading_fun/server.py` (crypto endpoints)

---

### Accessibility Improvements
**Status**: In Progress (80% complete)  
**Type**: Enhancement  
**Priority**: High

**Completed**:
- ✅ Skip navigation link with focus styling
- ✅ Semantic HTML (header, main, section, nav, footer)
- ✅ ARIA labels on all interactive elements
- ✅ ARIA states (pressed, expanded) on toggle buttons
- ✅ Table accessibility (scope attributes)
- ✅ Loading state announcements (aria-live)

**Remaining**:
- Color contrast verification (WCAG AA compliance)
- Focus indicator improvements
- Screen reader testing with NVDA/JAWS/VoiceOver
- Keyboard navigation testing

**Files**:
- `frontend/src/App.jsx`
- `frontend/src/styles.css`

---

## 🚀 Feature Enhancements

### Frontend Deployment
**Status**: Planned  
**Type**: Infrastructure  
**Priority**: Medium

**Description**: Deploy frontend to cloud hosting for easier access and testing.

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
**Status**: Planned  
**Type**: Infrastructure  
**Priority**: Medium

**Description**: Add application performance monitoring and metrics.

**Proposed Tools**:
- Backend: Prometheus + Grafana or DataDog
- Frontend: Sentry for error tracking
- API: Response time metrics, error rates
- ML: Model inference latency tracking

**Metrics to Track**:
- API response times (p50, p95, p99)
- Model prediction latency
- Cache hit rates
- Error rates by endpoint
- User engagement metrics

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
