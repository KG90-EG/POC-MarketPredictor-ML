# Project Backlog - POC-MarketPredictor-ML

**Last Updated**: January 2026  
**Project Status**: Production-Ready Beta  
**Current Version**: 1.0.0-beta

---

## 🚨 Critical Priority (P0) - Immediate Action Required

### 1. Fix Module Import Inconsistencies ⚠️

**Issue:** Mixed imports between `trading_fun/` and `market_predictor/`

- `trading_fun/server.py` imports from `market_predictor.simulation`
- Documentation references `market_predictor`, code uses `trading_fun`
- Tests import from both modules

**Impact:** High - Confusion, maintenance burden, deployment issues

**Solution:**

- [ ] Consolidate all code to `trading_fun/` module
- [ ] Move `market_predictor/simulation.py` → `trading_fun/simulation.py`
- [ ] Update all imports to use `trading_fun`
- [ ] Archive `market_predictor/` directory
- [ ] Update all documentation references

**ETA:** 1 day  
**Owner:** Backend Team

---

### 2. Fix CI/CD Pipeline Errors 🔧

**Issues Identified:**

1. **GitHub Secrets Warnings** (Non-blocking but noisy)
   - Missing: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`
   - Missing: `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`
   - Missing: `RAILWAY_TOKEN`, `VERCEL_TOKEN`, etc.

2. **Pre-commit Hook Failures**
   - `detect-secrets` baseline outdated
   - Version mismatch between hook and installed package

3. **Test Failures**
   - Some tests importing from wrong module
   - Database file permissions in CI environment

**Solutions:**

- [ ] Document required secrets in `.github/SECRET_SETUP.md`
- [ ] Make secrets optional with fallbacks in workflows
- [ ] Update `.secrets.baseline`
- [ ] Fix test imports to use `trading_fun`
- [ ] Add database initialization in CI workflow

**ETA:** 1-2 days  
**Owner:** DevOps Team

---

### 3. Frontend Build & Runtime Errors 🐛

**Issues:**

1. **SimulationDashboard.jsx async/await bug**
   - Status: ✅ Fixed
   - Solution: Replaced Promise.all with sequential awaits

2. **Port conflicts**
   - Frontend (5173) and Backend (8000) sometimes conflict
   - Need better port detection and error messages

3. **API connection handling**
   - No retry logic on failed requests
   - Poor error messages for network failures

**Solutions:**

- [x] Fix Promise.all bug in SimulationDashboard.jsx
- [ ] Add port availability check in start script
- [ ] Implement API retry logic with exponential backoff
- [ ] Add user-friendly error messages
- [ ] Create connection status indicator in UI

**ETA:** 2 days  
**Owner:** Frontend Team

---

## 🎯 High Priority (P1) - Next Sprint

### 4. Create Automated Server Start Script 🚀

**Goal:** Single command to start both backend and frontend with health checks

**Requirements:**

- Automated port checking and cleanup
- Health verification before "ready" status
- UI reachability test
- Clear error messages
- Cross-platform support (macOS, Linux, Windows)

**Implementation:**

```bash
./scripts/start_servers.sh
```

**Features:**

- [ ] Kill existing processes on ports 8000, 5173
- [ ] Start backend in background
- [ ] Wait for `/health` endpoint (max 30s)
- [ ] Start frontend in background
- [ ] Wait for UI to be reachable
- [ ] Display URLs and status
- [ ] Provide shutdown command

**ETA:** 1 day  
**Owner:** DevOps Team

---

### 5. PostgreSQL Migration 🗄️

**Current:** SQLite (single file, limited concurrency)  
**Target:** PostgreSQL (production-ready, multi-user)

**Benefits:**

- Better concurrency handling
- User isolation ready
- Production-grade reliability
- Better backup/recovery

**Tasks:**

- [ ] Set up SQLAlchemy models
- [ ] Create Alembic migrations
- [ ] Add PostgreSQL connection pooling
- [ ] Update database.py and simulation_db.py
- [ ] Add migration guide
- [ ] Test rollback procedures
- [ ] Update deployment docs

**ETA:** 3-4 days  
**Owner:** Backend Team

---

### 6. User Authentication & Authorization 🔐

**Current:** Single user ("default_user")  
**Target:** Multi-user with proper auth

**Features:**

- [ ] JWT-based authentication
- [ ] User registration/login
- [ ] Password hashing (bcrypt)
- [ ] Session management
- [ ] User-specific simulations
- [ ] API key support for programmatic access

**Dependencies:** PostgreSQL migration (P1.5)

**ETA:** 4-5 days  
**Owner:** Backend Team

---

### 7. Comprehensive Testing Suite 🧪

**Current Coverage:** ~30% (estimated)  
**Target:** >80%

**Areas to Cover:**

- [ ] Simulation lifecycle (create, trade, reset)
- [ ] Trading logic (buy/sell thresholds, position sizing)
- [ ] Database operations (concurrent writes, rollbacks)
- [ ] API endpoints (all routes)
- [ ] Frontend components (React Testing Library)
- [ ] E2E flows (Playwright)

**Test Types:**

- Unit tests (pytest)
- Integration tests (API + DB)
- E2E tests (Playwright)
- Load tests (Locust)

**ETA:** 1 week  
**Owner:** QA Team

---

## 📊 Medium Priority (P2) - Planned

### 8. Performance Optimization ⚡

**Identified Bottlenecks:**

1. Stock data fetching (yfinance API calls)
2. ML model predictions (no batching)
3. Frontend re-renders (React optimization needed)
4. Database queries (no indexing)

**Solutions:**

- [ ] Implement Redis caching layer
- [ ] Batch ML predictions
- [ ] Add React.memo and useMemo where needed
- [ ] Add database indexes on frequently queried columns
- [ ] Implement pagination for large datasets

**ETA:** 3-4 days  
**Owner:** Backend + Frontend Teams

---

### 9. Monitoring & Alerting 📈

**Current:** Basic Prometheus metrics  
**Target:** Full observability stack

**Features:**

- [ ] Grafana dashboards
- [ ] Alert rules (error rate, latency, downtime)
- [ ] Structured logging to ELK/Loki
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Uptime monitoring (UptimeRobot)

**ETA:** 1 week  
**Owner:** DevOps Team

---

### 10. Documentation Improvements 📚

**Completed:**

- [x] Architecture documentation with diagrams
- [x] Updated README with correct module info
- [x] Troubleshooting guide
- [x] Updated backlog (this file)

**Remaining:**

- [ ] API documentation (OpenAPI/Swagger improvements)
- [ ] Deployment step-by-step guide with screenshots
- [ ] Video tutorials for setup
- [ ] Contributing guidelines
- [ ] Code comments and docstrings
- [ ] Architecture decision records (ADRs)

**ETA:** Ongoing  
**Owner:** Documentation Team

---

## 🌟 Nice-to-Have (P3) - Future Enhancements

### 11. Advanced Trading Features

- [ ] Stop-loss and take-profit automation
- [ ] Portfolio rebalancing
- [ ] Risk management rules
- [ ] Backtesting with historical data
- [ ] Paper trading competitions

### 12. Social Features

- [ ] Leaderboard
- [ ] Share portfolio performance
- [ ] Follow other traders
- [ ] Community discussions

### 13. Mobile App

- [ ] React Native app
- [ ] Push notifications
- [ ] Mobile-optimized charts

### 14. Advanced Analytics

- [ ] Custom indicators
- [ ] Strategy builder
- [ ] AI-powered insights
- [ ] Sentiment analysis

---

## ✅ Recently Completed

### Sprint 1 (December 2025)

- [x] Core simulation engine
- [x] Backend API endpoints
- [x] Frontend React app
- [x] Multi-language support
- [x] WebSocket real-time updates

### Sprint 2 (January 2026)

- [x] Architecture documentation
- [x] Updated README
- [x] Troubleshooting guide
- [x] Identified all critical issues
- [x] Fixed SimulationDashboard async bug

---

## 📋 Definition of Done

### For Code Changes

- [ ] Code reviewed by at least 1 team member
- [ ] Tests added/updated (>80% coverage for new code)
- [ ] Documentation updated
- [ ] CI/CD pipeline passes
- [ ] No new linting warnings
- [ ] Manual testing completed

### For Features

- [ ] User acceptance criteria met
- [ ] E2E tests added
- [ ] Performance impact measured
- [ ] Security review completed
- [ ] Deployment guide updated

---

## 🔄 Sprint Planning

### Current Sprint (January 2026)

**Focus:** Stabilization & Critical Fixes

**Goals:**

1. Fix module import inconsistencies (P0.1)
2. Fix CI/CD pipeline (P0.2)
3. Create server start script (P1.4)

**Capacity:** 10 developer-days

---

### Next Sprint (February 2026)

**Focus:** Production Readiness

**Goals:**

1. PostgreSQL migration (P1.5)
2. User authentication (P1.6)
3. Testing suite (P1.7)
4. Performance optimization (P2.8)

**Capacity:** 15 developer-days

---

## 📈 Metrics & KPIs

### Code Quality

- Test Coverage: 30% → Target: 80%
- Linting Warnings: 15 → Target: 0
- Security Vulnerabilities: 0 ✅

### Performance

- API Response Time: 500ms avg → Target: 200ms
- Frontend Load Time: 2s → Target: 1s
- Uptime: 95% → Target: 99.9%

### Development

- Deploy Frequency: Weekly → Target: Daily
- Lead Time: 3 days → Target: 1 day
- MTTR: 2 hours → Target: 30 minutes

---

## 📚 Reference Links

- [Architecture Documentation](../ARCHITECTURE.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [API Documentation](../api/simulation.md)
- [Deployment Guide](../deployment/DEPLOYMENT_GUIDE.md)
- [GitHub Repository](https://github.com/KG90-EG/POC-MarketPredictor-ML)

---

**Questions or suggestions?** Open an issue or start a discussion on GitHub!
