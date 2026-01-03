# Product Requirements Document (PRD)

## Smart Trading Platform - Market Prediction for Profit Generation

**Last Updated:** 2026-01-03  
**Status:** In Development  
**Target Market:** CHF-based Swiss traders + Global USD traders  
**📋 Backlog:** [BACKLOG.md](BACKLOG.md) - Weekly tasks with completion tracking  
**📊 Technical Assessment:** [assessments/TECHNICAL_ASSESSMENT_2026.md](assessments/TECHNICAL_ASSESSMENT_2026.md)

---

## 🎯 Vision & Purpose

**Core Mission:**  
Build an intelligent, self-learning trading platform that generates profit by accurately predicting market movements across Stocks, Digital Assets, and Commodities - helping users know WHEN to BUY, HOLD, or SELL.

**Key Differentiator:**  
The system must continuously learn and improve itself, gathering information autonomously to make increasingly accurate predictions.

---

## 📋 Project Status Tracking

**Current Week:** Week 1 (Jan 2-8, 2026)  
**Sprint:** Foundation & Swiss Market Integration  
**Progress:** See [BACKLOG.md](BACKLOG.md) for detailed week-by-week tracking with checkboxes.

**Quick Status:**

- ✅ Phase 1: Data Accuracy (100% unique prices)
- ✅ Phase 2: Swiss Stocks (50 stocks total)
- ✅ Phase 2: CHF Currency Support
- 🔄 Documentation Cleanup (in progress)
- ❌ Week 2: European Markets (pending)
- ❌ Week 3: Self-Learning AI (pending)

---

## 📊 Current Status Assessment (2026-01-03)

### ✅ What's Working

1. **ML Model Training**
   - XGBoost model with 82.61% accuracy
   - 30 US stocks coverage
   - 20 technical features (RSI, MACD, Bollinger, ATR, ADX, Stochastic, OBV, VWAP, etc.)
   - Auto-retraining scheduler (daily 2:00 AM, weekly full retrain)

2. **Backend Infrastructure**
   - FastAPI server (production-ready)
   - Parallel processing (10 workers, ~80 stocks/sec)
   - Caching system (5-min TTL for features)
   - Health monitoring (Prometheus + Grafana)
   - Rate limiting protection

3. **Frontend Features**
   - Stock rankings with probability scores
   - Crypto rankings (momentum-based)
   - Watchlist management
   - Trading simulation
   - Company detail sidebar
   - Real-time health monitoring

4. **Repository Maintenance**
   - Automated cleanup scripts
   - Structure validation (pre-commit hooks + CI)
   - Documentation

### ❌ Critical Issues Identified

#### 1. **Data Accuracy Problem** 🚨 HIGH PRIORITY

**Current State:**

- Multiple stocks showing identical prices (e.g., ADM and BA have same price)
- "Hold" recommendations show "N/A" prices
- "Sell" signals have duplicate prices

**Root Cause:**

- Parallel processing not correctly passing OHLCV data
- Some stocks fail to download (rate limiting or delisted)
- Price data from yfinance not properly mapped to individual stocks

**Impact:** Users cannot trust the system - **BLOCKS PROFIT GENERATION**

#### 2. **Limited Geographic Coverage** 🌍

**Current State:**

- Only 30 US stocks in production
- Config supports 73 global stocks but disabled due to rate limiting
- No European, Asian, or Swiss stocks in active model

**Required:**

- Swiss stocks (SMI index: Nestlé, Novartis, Roche, UBS, Zurich, etc.)
- European stocks (DAX, CAC 40, FTSE 100)
- Asian stocks (Nikkei, Hang Seng)
- Worldwide coverage with smart rate limiting

#### 3. **Currency Support Missing** 💱

**Current State:**

- All prices displayed in USD
- No CHF conversion
- No multi-currency support

**Required:**

- CHF as primary currency (Swiss trader focus)
- USD as secondary
- Real-time exchange rate conversion
- User preference selection

#### 4. **Self-Learning Limited** 🧠

**Current State:**

- Model retrains on schedule (daily/weekly)
- Uses only technical features (no fundamentals, no news)
- No adaptive learning based on prediction accuracy

**Required:**

- Continuous learning from prediction outcomes
- Feedback loop: track predictions vs actual results
- Auto-improve feature selection
- Incorporate news sentiment, fundamentals, macro indicators

#### 5. **Incomplete Asset Coverage** 📈

**Current State:**

- Stocks: 30 US only
- Crypto: Momentum scoring (not ML-based)
- Commodities: Not implemented

**Required:**

- Stocks: Worldwide (500+ stocks)
- Digital Assets: Real ML predictions for crypto
- Commodities: Gold, Silver, Oil, Natural Gas
- Merged view: "Digital Assets" (Crypto + Commodities)

---

## 🎯 Requirements Breakdown

### Phase 1: Fix Data Accuracy (Week 1) 🚨 CRITICAL

**Goal:** Make data trustworthy - different stocks must show different prices

**Requirements:**

- [ ] R1.1: Fix parallel processing to correctly map prices to tickers
- [ ] R1.2: Validate each stock has unique OHLCV data
- [ ] R1.3: Add data validation layer (reject duplicate prices)
- [ ] R1.4: Display data source timestamp per stock
- [ ] R1.5: Add "Last Updated" indicator
- [ ] R1.6: Log and alert on data quality issues

**Success Criteria:**

- ✅ Each stock displays its actual current price
- ✅ No duplicate prices across different stocks
- ✅ "N/A" only appears for genuinely unavailable data
- ✅ 95%+ data accuracy rate

**Tests:**

```python
def test_unique_prices():
    ranking = get_ranking()
    prices = [stock['price'] for stock in ranking]
    assert len(prices) == len(set(prices))  # All unique

def test_price_matches_ticker():
    aapl = get_ticker_info('AAPL')
    tsla = get_ticker_info('TSLA')
    assert aapl['price'] != tsla['price']
    assert aapl['price'] > 0
    assert tsla['price'] > 0
```

---

### Phase 2: Global Stock Coverage (Week 2-3)

**Goal:** Expand to worldwide stocks without hitting rate limits

**Requirements:**

- [ ] R2.1: Implement smart rate limiting (max 2000 requests/hour for Yahoo Finance)
- [ ] R2.2: Add distributed caching (Redis) for price data
- [ ] R2.3: Stagger data fetching across time zones
- [ ] R2.4: Swiss stocks (SMI index: 20 stocks)
  - Nestlé (NESN.SW), Novartis (NOVN.SW), Roche (ROG.SW), UBS (UBSG.SW), Zurich Insurance (ZURN.SW)
  - ABB (ABBN.SW), Credit Suisse (CSGN.SW), Swiss Re (SREN.SW), Lonza (LONN.SW), Givaudan (GIVN.SW)
- [ ] R2.5: European stocks (50 stocks: Germany, France, UK, Netherlands)
- [ ] R2.6: Asian stocks (30 stocks: Japan, China, Hong Kong, Singapore)
- [ ] R2.7: Total target: 200+ stocks worldwide

**Success Criteria:**

- ✅ 200+ stocks from 5+ regions
- ✅ < 1% rate limit errors
- ✅ Data refreshes every 5 minutes
- ✅ Model retrains weekly with all regions

---

### Phase 3: Multi-Currency Support (Week 3)

**Goal:** Support CHF and USD with real-time conversion

**Requirements:**

- [ ] R3.1: Integrate exchange rate API (e.g., exchangerate-api.io or ECB)
- [ ] R3.2: Currency selector in UI (CHF / USD)
- [ ] R3.3: Convert all prices to selected currency
- [ ] R3.4: Store user preference in localStorage
- [ ] R3.5: Display exchange rate and last update time
- [ ] R3.6: Handle offline mode (cache last known rates)

**Success Criteria:**

- ✅ Seamless currency switching
- ✅ Accurate conversions (< 0.01% error)
- ✅ Updates every 1 hour
- ✅ User preference persists

**Implementation:**

```python
# Backend
@app.get("/exchange_rate/{from_currency}/{to_currency}")
def get_exchange_rate(from_currency: str, to_currency: str):
    # Cache for 1 hour
    rate = fetch_exchange_rate(from_currency, to_currency)
    return {"rate": rate, "timestamp": datetime.now()}

# Frontend
const convertPrice = (price, fromCurrency, toCurrency, rate) => {
    if (fromCurrency === toCurrency) return price
    return price * rate
}
```

---

### Phase 4: Self-Learning Intelligence (Week 4-5)

**Goal:** System learns from its own predictions and improves over time

**Requirements:**

- [ ] R4.1: Track prediction accuracy
  - Store: {ticker, predicted_prob, timestamp, actual_outcome_7d, actual_outcome_30d}
  - Calculate: accuracy rate per ticker, per sector, per region
- [ ] R4.2: Adaptive feature selection
  - Test different feature combinations
  - Keep features that improve accuracy
  - Drop features that don't correlate
- [ ] R4.3: Incorporate news sentiment
  - Fetch news for top stocks (News API, Alpha Vantage)
  - Sentiment analysis (positive/negative/neutral)
  - Add as model feature
- [ ] R4.4: Add fundamental features
  - P/E ratio, EPS growth, Revenue growth
  - Debt-to-equity, ROE, Profit margin
  - Use only if improves accuracy
- [ ] R4.5: Macro indicators
  - VIX (volatility index)
  - Treasury yields
  - USD index
  - Market breadth
- [ ] R4.6: Auto-retrain when accuracy drops below 75%

**Success Criteria:**

- ✅ Prediction accuracy improves 5%+ per quarter
- ✅ System identifies best-performing features automatically
- ✅ Model adapts to changing market conditions
- ✅ Accuracy tracking dashboard shows improvement trends

**Architecture:**

```
┌─────────────────────────────────────────┐
│  Prediction Tracker                     │
│  - Store predictions with timestamps    │
│  - Fetch actual outcomes after 7/30 days│
│  - Calculate accuracy metrics           │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│  Feature Optimizer                      │
│  - Test feature combinations            │
│  - A/B testing new features             │
│  - Select best performers               │
└─────────────────────────────────────────┘
           │
           ↓
┌─────────────────────────────────────────┐
│  Auto-Retrainer                         │
│  - Triggered by accuracy drop           │
│  - Uses optimized features              │
│  - Validates on test set                │
└─────────────────────────────────────────┘
```

---

### Phase 5: Complete Asset Coverage (Week 5-6)

**Goal:** Cover Stocks, Crypto, and Commodities with ML predictions

**Requirements:**

#### 5A: Digital Assets (Crypto)

- [ ] R5.1: Train ML model for top 50 cryptocurrencies
- [ ] R5.2: Technical features: RSI, MACD, volume trends, on-chain metrics
- [ ] R5.3: Replace momentum scoring with real ML predictions
- [ ] R5.4: BUY/HOLD/SELL signals for crypto

#### 5B: Commodities

- [ ] R5.5: Add commodity support
  - Gold (GC=F), Silver (SI=F)
  - Crude Oil (CL=F), Natural Gas (NG=F)
  - Copper (HG=F), Platinum (PL=F)
- [ ] R5.6: Train ML model for commodities
- [ ] R5.7: Commodity-specific features (seasonality, industrial demand)

#### 5C: Unified Digital Assets View

- [ ] R5.8: Merge Crypto + Commodities into "Digital Assets" tab
- [ ] R5.9: Unified ranking across asset types
- [ ] R5.10: Cross-asset diversification recommendations

**Success Criteria:**

- ✅ 50+ crypto with ML predictions
- ✅ 6+ commodities with ML predictions
- ✅ Unified view ranks all assets by probability
- ✅ Diversification score per portfolio

---

## 🏗️ Technical Architecture

### Current Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │ ───► │   Backend    │ ───► │  ML Model   │
│  React/Vite │      │   FastAPI    │      │  XGBoost    │
│  Port 5173  │      │   Port 8000  │      │  prod_model │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ↓
                     ┌──────────────┐
                     │ Yahoo Finance│
                     │  (Rate Limit)│
                     └──────────────┘
```

### Target Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Frontend   │ ───► │   Backend    │ ───► │  ML Pipeline    │
│  React/Vite │      │   FastAPI    │      │  - Stock Model  │
│  Multi-Curr │      │  + Redis     │      │  - Crypto Model │
│  CHF/USD    │      │  + Celery    │      │  - Commodity    │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │                       │
                            ↓                       ↓
                     ┌──────────────┐      ┌─────────────────┐
                     │ Data Sources │      │ Prediction DB   │
                     │- Yahoo Fin   │      │ - Track Results │
                     │- News API    │      │ - Calc Accuracy │
                     │- Alpha Vant  │      │ - Auto-Improve  │
                     │- CoinGecko   │      └─────────────────┘
                     └──────────────┘
```

---

## 📋 Implementation Roadmap

### Week 1: Data Accuracy Fix (CRITICAL) 🚨

- Day 1-2: Debug parallel processing price mapping
- Day 3: Add data validation layer
- Day 4: Test with 30 US stocks
- Day 5: Deploy and monitor

### Week 2: Swiss Stocks + European Coverage

- Day 1-2: Implement smart rate limiting
- Day 3: Add Swiss SMI stocks (20)
- Day 4: Add European stocks (50)
- Day 5: Retrain model with 100 stocks

### Week 3: Multi-Currency Support

- Day 1-2: Integrate exchange rate API
- Day 3: Update UI for CHF/USD toggle
- Day 4: Test conversions
- Day 5: Deploy currency support

### Week 4-5: Self-Learning Features

- Week 4: Prediction tracking + accuracy metrics
- Week 5: Feature optimization + auto-retraining

### Week 6: Full Asset Coverage

- Crypto ML model + Commodities + Unified view

---

## 🎯 Success Metrics (KPIs)

### Data Quality

- **Target:** 99% data accuracy (unique prices per stock)
- **Current:** ~40% (many duplicates)

### Prediction Accuracy

- **Target:** 85%+ for 7-day price movement
- **Current:** 82.61% on training data (needs validation on real trades)

### Geographic Coverage

- **Target:** 200+ stocks from 5+ regions
- **Current:** 30 US stocks

### Currency Support

- **Target:** CHF + USD seamless switching
- **Current:** USD only

### User Value

- **Target:** Users generate 15%+ annual return following recommendations
- **Current:** Not tracked (need to implement)

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Data accuracy
test_unique_prices_per_stock()
test_price_matches_ticker()
test_no_null_prices_for_active_stocks()

# Currency conversion
test_chf_usd_conversion()
test_exchange_rate_caching()

# ML accuracy
test_prediction_accuracy_above_threshold()
test_model_improves_over_time()
```

### Integration Tests

```python
# End-to-end
test_buy_signal_generates_profit()
test_sell_signal_prevents_loss()
test_hold_signal_maintains_position()
```

### Performance Tests

```python
# Scalability
test_200_stocks_load_under_3_seconds()
test_rate_limit_respected()
test_concurrent_users_supported()
```

---

## 📝 Next Steps (Immediate Actions)

1. **TODAY (2026-01-03):**
   - ✅ Create this PRD
   - [ ] Fix parallel processing price bug
   - [ ] Add data validation
   - [ ] Test unique prices

2. **WEEK 1:**
   - [ ] Complete data accuracy fix
   - [ ] Deploy validated version
   - [ ] Begin Swiss stocks integration

3. **DOCUMENTATION:**
   - [ ] Create technical design doc for self-learning
   - [ ] Create API documentation for currency conversion
   - [ ] Create testing plan for worldwide stocks

---

## 💡 Key Decisions to Make

1. **Exchange Rate Provider:**
   - Option A: exchangerate-api.io (free tier: 1500 requests/month)
   - Option B: ECB API (free, official, but EUR-based)
   - Option C: Alpha Vantage (free tier: 500 requests/day)
   - **Recommendation:** Start with ECB, add Alpha Vantage as backup

2. **News Sentiment Provider:**
   - Option A: News API (free tier: 100 requests/day)
   - Option B: Alpha Vantage News Sentiment
   - Option C: Scrape financial news sites
   - **Recommendation:** Alpha Vantage (combines news + sentiment)

3. **Caching Strategy:**
   - Option A: In-memory (current, limited)
   - Option B: Redis (scalable, persistent)
   - **Recommendation:** Migrate to Redis for production

4. **Database for Predictions:**
   - Option A: SQLite (simple, local)
   - Option B: PostgreSQL (scalable, production)
   - **Recommendation:** Start SQLite, migrate to PostgreSQL for scale

---

## 📚 References

- Current Model: `models/prod_model.bin` (82.61% accuracy, 30 stocks, 20 features)
- Training Script: `scripts/train_production.py`
- Server: `src/trading_engine/server.py`
- Frontend: `frontend/src/App.jsx`
- Cleanup Scripts: `scripts/deep_cleanup.sh`, `scripts/validate_structure.sh`

---

**Document Owner:** Product Team  
**Technical Lead:** ML Engineering Team  
**Review Cycle:** Weekly  
**Status Updates:** Daily during Week 1 (Critical Bug Fix)
