# 📋 Project Backlog - Market Predictor ML

**Master Document:** [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md)  
**Last Updated:** 2026-01-03  
**Current Week:** Week 1  
**Project Start:** 2026-01-02

---

## 🎯 Project Goal

Build an intelligent, self-learning trading platform that generates profit by accurately predicting market movements across Stocks, Digital Assets, and Commodities with CHF currency support for Swiss traders.

---

## ✅ Week 1: Foundation & Swiss Market Integration (Jan 2-8, 2026)

### Day 1-2: Data Accuracy Fix ✅ COMPLETED

- [x] Fix price duplicates (parallel processing bug)
- [x] Achieve 100% unique prices for all stocks
- [x] Validate data accuracy layer
- [x] Model retrained: 82.61% accuracy with 30 US stocks

### Day 3-4: Swiss Stocks Integration ✅ COMPLETED

- [x] Add 20 Swiss SMI stocks (NESN.SW, NOVN.SW, ROG.SW, etc.)
- [x] Update config files with Swiss tickers
- [x] Validate yfinance downloads for Swiss stocks
- [x] Retrain model with 50 stocks (30 US + 20 Swiss)
- [x] Verify 100% unique prices maintained

### Day 5: CHF Currency Support ✅ COMPLETED

- [x] Integrate exchange rate API (ExchangeRate-API.com)
- [x] Create currency conversion module (`utils/currency.py`)
- [x] Add `/currency` endpoint to backend
- [x] Frontend currency toggle button (USD/CHF)
- [x] Update BuyOpportunities component with price conversion
- [x] Test with real USD/CHF rates

### Day 6: Bug Fixes & Stabilization ✅ COMPLETED

- [x] Fix DataFrame bug in ranking endpoint
- [x] Ensure Swiss stocks return correct data structure
- [x] Both servers running stable (backend:8000, frontend:5173)
- [x] User confirmed frontend accessible
- [x] Created SWISS_CHF_INTEGRATION.md documentation

### Day 7: Documentation Cleanup 🔄 IN PROGRESS

- [x] Create BACKLOG.md with weekly checkboxes
- [ ] Create assessments/ folder for technical docs
- [ ] Consolidate duplicate roadmap files
- [ ] Update PRODUCT_REQUIREMENTS.md with backlog link
- [ ] Archive outdated documentation

**Week 1 Metrics:**

- ✅ Stock Coverage: 30 → 50 stocks (+67%)
- ✅ Model Accuracy: 82.61% → 78.37% (retrained with more stocks)
- ✅ Currency Support: USD only → USD + CHF
- ✅ Data Accuracy: 100% unique prices
- ✅ System Stability: Both servers running

---

## 📅 Week 2: European Market Expansion (Jan 9-15, 2026)

### European Stocks Integration

- [ ] Add Germany DAX stocks (30 stocks)
  - SAP.DE, VOW3.DE, SIE.DE, BAS.DE, ALV.DE, DTE.DE, BMW.DE, MUV2.DE, BEI.DE, ADS.DE
  - DAI.DE, DB1.DE, HEN3.DE, VON3.DE, MBG.DE, FRE.DE, HEI.DE, RWE.DE, ENR.DE, LIN.DE
  - IFX.DE, CON.DE, 1COV.DE, PAH3.DE, SHL.DE, ZAL.DE, PUM.DE, MRK.DE, QIA.DE, SRT3.DE

- [ ] Add UK FTSE 100 stocks (20 stocks)
  - SHEL.L, AZN.L, HSBA.L, BP.L, ULVR.L, DGE.L, GSK.L, RIO.L, BATS.L, RELX.L
  - NG.L, LSEG.L, VOD.L, PRU.L, BARC.L, LLOY.L, AAL.L, GLEN.L, IMB.L, CRH.L

- [ ] Add France CAC 40 stocks (20 stocks)
  - MC.PA, OR.PA, SAN.PA, AIR.PA, TTE.PA, BNP.PA, SAF.PA, SU.PA, EL.PA, CA.PA
  - ACA.PA, ORA.PA, VIE.PA, BN.PA, RMS.PA, DG.PA, CS.PA, EN.PA, SGO.PA, STLA.PA

### Database & Performance

- [ ] PostgreSQL setup for production
- [ ] Redis caching for European stocks
- [ ] Smart rate limiting (< 1% errors)
- [ ] Background jobs for data refresh

### EUR Currency Support

- [ ] Add EUR to currency conversion
- [ ] Frontend support for USD/CHF/EUR toggle
- [ ] Store user currency preference

**Week 2 Target Metrics:**

- 📊 Stock Coverage: 50 → 120 stocks (+140%)
- 💱 Currencies: USD + CHF + EUR
- ⚡ Processing Time: <10s for 120 stocks
- 🎯 Model Accuracy: Maintain 75%+ with expanded coverage

---

## 📅 Week 3: Asian Markets & Self-Learning Foundation (Jan 16-22, 2026)

### Asian Stocks Integration

- [ ] Add Japan Nikkei stocks (20 stocks)
  - 7203.T (Toyota), 6758.T (Sony), 9984.T (SoftBank), 6861.T (Keyence), etc.

- [ ] Add Hong Kong Hang Seng stocks (10 stocks)
  - 0700.HK (Tencent), 9988.HK (Alibaba), 0941.HK (China Mobile), etc.

### Additional Currency Support

- [ ] Add JPY (Japanese Yen)
- [ ] Add HKD (Hong Kong Dollar)
- [ ] Multi-currency selector in UI

### Self-Learning AI - Phase 1: Prediction Tracking

- [ ] Create `predictions` database table
- [ ] Track every prediction made (ticker, action, probability, price)
- [ ] Daily job to validate 7-day and 30-day outcomes
- [ ] Calculate prediction accuracy metrics
- [ ] Dashboard showing accuracy trends

**Week 3 Target Metrics:**

- 📊 Stock Coverage: 120 → 150 stocks (+25%)
- 💱 Currencies: USD + CHF + EUR + JPY + HKD
- 🧠 Prediction Tracking: Active and storing data
- 📈 Accuracy Dashboard: Live metrics visible

---

## 📅 Week 4: Self-Learning AI - Auto-Retraining (Jan 23-29, 2026)

### Auto-Retraining Logic

- [ ] Monitor prediction accuracy per stock/sector/region
- [ ] Trigger automatic retraining when accuracy < 75%
- [ ] A/B testing framework (old model vs new model)
- [ ] Gradual rollout of new models
- [ ] Model version tracking

### Feature Optimization

- [ ] Feature importance analysis
- [ ] Test removing low-importance features
- [ ] Test adding new technical indicators:
  - EMA (12, 26), MFI, TSI, CMF, Williams %R
- [ ] Keep features that improve accuracy
- [ ] Auto-update feature list based on performance

### News Sentiment Integration

- [ ] Integrate News API or Alpha Vantage
- [ ] Sentiment analysis (positive/negative/neutral)
- [ ] Add sentiment score as model feature
- [ ] Test impact on prediction accuracy

**Week 4 Target Metrics:**

- 🧠 Auto-Retraining: Active and triggered by accuracy drops
- 🎯 Model Accuracy: 80%+ with optimized features
- 📰 News Sentiment: Integrated as feature
- 🔄 Feature Count: Optimized (remove weak, add strong)

---

## 📅 Week 5: Complete Asset Coverage - Crypto ML (Jan 30 - Feb 5, 2026)

### Crypto ML Model

- [ ] Train ML model for top 50 cryptocurrencies
- [ ] Crypto-specific features:
  - 24h trading volume, market cap changes
  - RSI, MACD, Bollinger Bands for crypto
  - On-chain metrics (Bitcoin/Ethereum)
  - Social sentiment (Twitter, Reddit)
- [ ] Replace momentum scoring with real ML predictions
- [ ] BUY/HOLD/SELL signals for crypto

### Crypto Data Sources

- [ ] Integrate CoinGecko API (free tier)
- [ ] Binance API for real-time prices
- [ ] Crypto-specific rate limiting

**Week 5 Target Metrics:**

- 🪙 Crypto Coverage: 50 cryptocurrencies with ML
- 🎯 Crypto Model Accuracy: 70%+ (lower than stocks is expected)
- 📊 Total Assets: 150 stocks + 50 crypto = 200 assets

---

## 📅 Week 6: Commodities & Unified Digital Assets (Feb 6-12, 2026)

### Commodities Integration

- [ ] Add commodity tickers:
  - GC=F (Gold Futures)
  - SI=F (Silver Futures)
  - CL=F (Crude Oil)
  - NG=F (Natural Gas)
  - HG=F (Copper)
  - PL=F (Platinum)
- [ ] Train ML model for commodities
- [ ] Commodity-specific features (seasonality, industrial demand)

### Unified Digital Assets View

- [ ] Merge Crypto + Commodities into "Digital Assets" tab
- [ ] Unified ranking across crypto and commodities
- [ ] Cross-asset diversification recommendations
- [ ] Portfolio optimization across all asset types

**Week 6 Target Metrics:**

- 📊 Total Coverage: 150 stocks + 50 crypto + 6 commodities = 206 assets
- 🎯 Overall Model Accuracy: 75%+ across all asset types
- 💼 Portfolio Optimizer: Active and providing recommendations

---

## 📅 Week 7-8: Advanced Features & Alerts (Feb 13-26, 2026)

### Price Alerts

- [ ] User-defined price targets
- [ ] Probability threshold alerts (e.g., notify when BUY signal > 85%)
- [ ] Email/SMS notifications
- [ ] Alert history and management

### Portfolio Optimization

- [ ] Diversification score calculation
- [ ] Risk assessment per portfolio
- [ ] Recommended portfolio rebalancing
- [ ] Backtesting with historical data

### Fundamental Analysis Integration

- [ ] P/E ratio, EPS growth, Revenue growth
- [ ] Debt-to-equity, ROE, Profit margin
- [ ] Add as model features (test impact on accuracy)
- [ ] Display fundamentals in company sidebar

**Week 7-8 Target Metrics:**

- 🔔 Alerts: Active notification system
- 💼 Portfolio Optimizer: Recommendations generating profit
- 📊 Fundamentals: Integrated and tested

---

## 📅 Week 9-10: Performance & Scalability (Feb 27 - Mar 12, 2026)

### Backend Optimization

- [ ] ProcessPoolExecutor for parallel processing
- [ ] Redis distributed caching
- [ ] Database query optimization
- [ ] API response time < 1s for all endpoints

### Frontend Optimization

- [ ] Code splitting and lazy loading
- [ ] PWA (Progressive Web App) support
- [ ] Offline mode with cached data
- [ ] Mobile-responsive design

### Infrastructure

- [ ] Production deployment (Railway + Vercel)
- [ ] Auto-scaling setup
- [ ] Monitoring and alerting (Prometheus + Grafana)
- [ ] Backup and disaster recovery

**Week 9-10 Target Metrics:**

- ⚡ API Response: <1s for 200+ assets
- 📱 Mobile: Fully responsive
- 🌐 PWA: Installable on mobile
- 🚀 Uptime: 99.9%

---

## 📅 Week 11-12: Final Testing & Launch (Mar 13-26, 2026)

### Testing & Quality Assurance

- [ ] 200+ unit tests passing
- [ ] Integration tests for all features
- [ ] Load testing (1000+ concurrent users)
- [ ] Security audit
- [ ] Accessibility compliance

### Documentation & User Guides

- [ ] User guide for traders
- [ ] API documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide

### Launch Preparation

- [ ] Beta testing with real users
- [ ] Gather feedback and iterate
- [ ] Performance tuning
- [ ] Final production deployment

**Week 11-12 Target Metrics:**

- ✅ 200+ tests passing
- 📊 200+ assets live
- 🧠 Self-learning active
- 💰 Proven profit generation

---

## 📊 Overall Success Metrics

| Metric | Start (Week 0) | Week 1 | Week 6 Target | Week 12 Target |
|--------|---------------|--------|---------------|----------------|
| **Stock Coverage** | 30 US | 50 (US+Swiss) | 150 worldwide | 150 worldwide |
| **Asset Types** | Stocks only | Stocks only | Stocks + Crypto + Commodities | All 3 types |
| **Currency Support** | USD only | USD + CHF | USD + CHF + EUR + JPY + HKD | All 5 |
| **Model Accuracy** | 82.61% | 78.37% | 80%+ | 85%+ |
| **Prediction Tracking** | None | None | Active | Active + Auto-improving |
| **API Response Time** | 30s | 30s | <10s | <1s |
| **Self-Learning** | Manual retrain | Manual retrain | Active tracking | Fully autonomous |

---

## 🔗 Related Documentation

- **Master Document:** [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md)
- **Technical Assessment:** [assessments/TECHNICAL_ASSESSMENT_2026.md](assessments/TECHNICAL_ASSESSMENT_2026.md)
- **Implementation Details:** [SWISS_CHF_INTEGRATION.md](SWISS_CHF_INTEGRATION.md)
- **Deployment Guide:** [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)

---

**Next Review:** End of Week 1 (2026-01-08)
