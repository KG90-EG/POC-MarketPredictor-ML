# Product Requirements – Decision Support System for Capital Allocation

**Document Version:** 1.0  
**Created:** 2026-01-06  
**Status:** Active - Master Requirements Document  
**Owner:** Kevin Garcia  
**Related:** [Gap Analysis](#-implementation-gap-analysis) | [Priority Roadmap](#-priority-roadmap)

---

## 1. Purpose (Why this system exists)

The purpose of this system is to **support personal investment decisions** by identifying where capital should be allocated and where it should not.

The system is designed to:
- Reduce decision noise and emotional bias
- Provide a daily, explainable ranking of investable assets
- Support risk-aware capital allocation decisions

**The system does not attempt to predict exact prices or automate trades.**

---

## 2. Core Question

Every execution of the system must answer one question clearly:

> **"If I were to invest today, which assets are the most rational candidates for capital allocation, and which should be avoided?"**

If a feature does not improve the quality of this decision, it is out of scope.

---

## 3. Investment Philosophy

The system is based on the following principles:

1. **Relative strength beats absolute price prediction**
2. **Ranking assets is more robust than forecasting prices**
3. **Market regime and risk control are mandatory**
4. **Quantitative signals dominate; qualitative context modifies**
5. **Explainability is required for every recommendation**

---

## 4. Scope

### 4.1 Asset Universe

The system shall operate on a **fixed, explicitly defined asset universe**, versioned and reviewed periodically.

**Initial scope:**
- **Equities:** Selected major indices
  - S&P 500 (30 US stocks) ✅
  - SMI Switzerland (20 Swiss stocks) ✅
  - DAX Germany (30 stocks) - *Planned Week 2*
  - FTSE 100 UK (20 stocks) - *Planned Week 2*
  - CAC 40 France (20 stocks) - *Planned Week 2*

- **Digital Assets:** Top cryptocurrencies by market capitalization ✅
  - Bitcoin, Ethereum, and top 50 by market cap

**The system shall not attempt to cover all global assets.**

### 4.2 Investment Horizon

The system shall target a **medium-term investment horizon**, typically:
- **10–60 days**

All signals, evaluations and backtests must align with this horizon.

---

## 5. Functional Requirements

### 5.1 Market Data ✅ IMPLEMENTED

The system shall ingest and normalize:
- Historical price data (OHLC)
- Volume data
- Benchmark index data
- Trading calendar information

**Data processing shall be:**
- Deterministic
- Reproducible
- Suitable for daily batch execution

**Current Implementation:**
- ✅ yfinance for historical OHLC data (300 days lookback)
- ✅ Volume data included in all features
- ⚠️ No explicit benchmark index tracking (S&P 500, SMI)
- ⚠️ No trading calendar validation (weekends/holidays)

**Action Required:**
- [ ] Add benchmark index data (SPY for US, ^SSMI for Switzerland)
- [ ] Implement trading calendar awareness

---

### 5.2 Quantitative Signal Engine (Primary Decision Layer) ⚠️ PARTIAL

The system shall compute **objective, numerical signals** per asset, including:
- Momentum (multiple lookback periods)
- Trend indicators
- Relative strength vs benchmark
- Volatility measures

**These signals shall:**
- Be explainable
- Be comparable across assets
- Form the primary basis for ranking decisions

**Current Implementation:**
- ✅ 20 technical features computed:
  - Momentum: RSI (14), Stochastic (14,3), ROC (12)
  - Trend: MACD (12,26,9), ADX (14), Parabolic SAR
  - Volatility: Bollinger Bands (20,2), ATR (14)
  - Volume: OBV, VWAP, Volume MA
  - Additional: Williams %R, CCI, Money Flow Index
- ✅ Features are deterministic and reproducible
- ❌ **No explicit relative strength vs benchmark**
- ❌ **No multi-period momentum analysis (10d, 30d, 60d)**
- ⚠️ Features used for ML model input, **not directly for ranking**

**Gap:** System uses ML probability as ranking metric, not direct signal aggregation.

**Action Required:**
- [ ] Add relative strength ratio (asset vs SPY/SSMI)
- [ ] Compute momentum across 3 periods (10d, 30d, 60d)
- [ ] Create composite signal score (not just ML probability)

---

### 5.3 Market Regime Detection ❌ MISSING - **CRITICAL**

The system shall identify overall market conditions, such as:
- Risk-on vs risk-off environments
- High-volatility regimes
- Unfavorable trend phases

**Market regime signals shall:**
- Influence or limit capital allocation
- Override individual asset attractiveness when required

**Current Implementation:**
- ⚠️ Drift detection module exists (`ml/drift_detection.py`) - not integrated
- ❌ **No risk-on/risk-off detection**
- ❌ **No volatility regime classification**
- ❌ **No regime-based portfolio protection**
- ❌ **Regime not displayed in UI or used in decisions**

**Gap:** **CRITICAL MISSING FEATURE** - No market regime awareness in current system.

**Action Required (HIGH PRIORITY):**
- [ ] Implement VIX-based volatility regime (low/medium/high)
- [ ] Add S&P 500 trend classification (bull/bear via 50-day/200-day MA)
- [ ] Create regime score (0-100 scale)
- [ ] **Block BUY signals in risk-off regimes (VIX > 30 or bear market)**
- [ ] Display regime status prominently in UI
- [ ] Log regime changes for post-analysis

---

### 5.4 LLM-Assisted Contextual Analysis (Secondary Layer) ⚠️ VIOLATES DESIGN

A Large Language Model shall be used **only for contextual analysis**, including:
- Summarization of recent asset-specific news
- Identification of dominant narratives
- Detection of relevant risk events

**The LLM shall:**
- Provide structured, deterministic output
- **Never generate direct buy/sell decisions**
- **Never override quantitative signals**

**LLM output shall be used to:**
- Modify asset scores within strict bounds (±5% maximum)
- Improve explainability and confidence assessment

**Current Implementation:**
- ✅ `/analyze` endpoint uses OpenAI GPT-4
- ❌ **LLM provides direct recommendations** (violates "never generate buy/sell")
- ❌ **No strict bounds on LLM influence**
- ❌ **LLM not used for news summarization** (generates opinions instead)
- ❌ **No narrative detection** (just general analysis)

**Gap:** LLM currently **makes decisions** instead of **providing context**. This **violates the core philosophy**.

**Action Required (HIGH PRIORITY):**
- [ ] **Redesign LLM role**: Context provider, not decision maker
- [ ] Implement news API integration (NewsAPI or similar)
- [ ] LLM summarizes last 7 days of news per asset (3-sentence max)
- [ ] LLM detects risk events (earnings warnings, regulatory changes)
- [ ] **Strict rule**: LLM can only adjust score by ±5% maximum
- [ ] Remove "AI recommendations" - show only "Contextual Notes"

**Example Output (Correct):**
```
JNJ - Quantitative Score: 72/100 (BUY)
Context: Recent FDA approval for new drug (positive). Earnings beat expectations by 8%. No major risk events detected.
LLM Adjustment: +3% (positive catalysts)
Final Score: 75/100
```

---

### 5.5 Scoring & Ranking ⚠️ PARTIAL

The system shall aggregate all signals into a **single composite score** per asset.

**The output shall be:**
- A ranked list of assets
- Confidence levels per asset
- Maximum recommended capital allocation per asset
- A concise explanation of the ranking

**Current Implementation:**
- ✅ Ranked list by ML probability (0-1 scale)
- ✅ Confidence = probability × 100
- ✅ Action signals (BUY/HOLD/SELL) based on thresholds:
  - BUY: prob ≥ 0.60
  - HOLD: 0.40 ≤ prob < 0.60
  - SELL: prob < 0.40
- ❌ **No maximum capital allocation per asset**
- ⚠️ **Explanation limited to "AI Confidence: X%"**
- ❌ **No signal breakdown** (user doesn't see why score is X)

**Gap:** Ranking is purely ML-based, not a composite of multiple signals. No allocation limits.

**Action Required:**
- [ ] Create composite score formula:
  ```
  Final Score = (Technical Signals × 0.40) +
                (ML Probability × 0.30) +
                (Momentum × 0.20) +
                (Regime Adjustment × 0.10)
  ```
- [ ] Add allocation limits:
  - Single stock: Max 10% of portfolio
  - Single crypto: Max 5% of portfolio
  - Asset class limits: Stocks 70%, Crypto 20%, Cash 10%
- [ ] Show score breakdown in UI:
  - "Score: 75/100 (Technical: 80, ML: 72, Momentum: 68, Regime: +5)"

---

### 5.6 Risk Management ⚠️ SIMULATION ONLY

The system shall enforce:
- Maximum position sizes
- Exposure limits per asset class
- Regime-based risk reduction rules

**Risk controls shall:**
- Be deterministic
- Take precedence over signal strength

**Current Implementation:**
- ⚠️ Simulation module has max 10 positions rule (not in core ranking)
- ⚠️ Equal weight allocation in simulation (1/10th of capital each)
- ❌ **No exposure limits per asset class**
- ❌ **No regime-based risk reduction** (no "defensive mode")
- ❌ **Not enforced in ranking/recommendation layer**

**Gap:** Risk management exists only in **simulation**, not in core decision system.

**Action Required (HIGH PRIORITY):**
- [ ] Enforce position limits in ranking:
  - Display "Max Allocation: 10%" next to each stock
  - Display "Max Allocation: 5%" next to each crypto
- [ ] Add regime-based rules:
  - **Risk-Off Regime:** Reduce max position to 5% (stocks), 2% (crypto)
  - **High Volatility:** Show "CAUTION" badge, suggest 50% normal allocation
- [ ] Create risk score per asset (0-100):
  - Factors: Volatility (ATR), drawdown risk, correlation to portfolio
- [ ] Block recommendations if total exposure > limits:
  - "Portfolio limit reached: 70% stocks allocated"

---

## 6. Output & Decision Interface ⚠️ INFORMATIONAL, NOT ACTIONABLE

The system shall present results in a **clear, decision-focused format**, including:
- Asset ranking
- Score and confidence
- Allocation limits
- Qualitative explanation

**The interface shall support:**
- Daily review
- Historical comparison
- Post-decision analysis

**Current Implementation:**
- ✅ Asset ranking displayed in UI (sorted by probability)
- ✅ Score (probability) and confidence shown
- ❌ **No allocation limits shown** (user doesn't know how much to invest)
- ⚠️ **Explanation is minimal** ("AI Confidence: 72%" - not helpful)
- ❌ **No historical comparison view** (can't see yesterday's ranking)
- ❌ **No post-decision analysis tracking** (can't see if following advice paid off)

**Gap:** UI is **informational**, not **decision-focused**. Missing allocation guidance.

**Action Required:**
- [ ] Redesign ranking table to show:
  ```
  Rank | Ticker | Score | Signal | Allocation | Explanation
  1    | AAPL   | 82/100| BUY    | Max 10%   | Strong momentum + positive regime
  2    | MSFT   | 78/100| BUY    | Max 10%   | Technical breakout + earnings beat
  ```
- [ ] Add "Decision Dashboard" view:
  - Top 5 Buy candidates with allocation % and reasoning
  - Top 5 Sell candidates if held
  - Current regime status (Risk-On/Risk-Off)
  - Portfolio exposure summary
- [ ] Add historical comparison:
  - "Yesterday's Top 5" vs "Today's Top 5"
  - Performance tracking: "Following last week's recommendations: +2.3%"
- [ ] Add decision log:
  - User can mark "Bought AAPL at $180, 10% allocation"
  - System tracks performance vs recommendation

---

## 7. Non-Functional Requirements

### 7.1 Explainability ❌ BLACK BOX

Every output must be explainable using:
- Quantitative signal breakdown
- Contextual summary

**Current Implementation:**
- ⚠️ 20 technical features computed but **not shown to user**
- ⚠️ Probability score shown but **not decomposed**
- ❌ **No signal breakdown in UI** (user sees 72% but doesn't know why)
- ❌ **No feature importance display**

**Gap:** System is a **black box**. User sees probability but not why.

**Action Required (HIGH PRIORITY):**
- [ ] Add "Explain Score" button per asset:
  ```
  AAPL - Score: 82/100

  Score Breakdown:
  ✅ Momentum (20 points): Strong 30-day uptrend (+15%)
  ✅ Technical (32 points): RSI bullish (62), MACD crossover
  ✅ ML Prediction (24 points): 80% buy probability
  ✅ Regime (6 points): Risk-on environment

  Risk Factors:
  ⚠️ High volatility (ATR 3.2% - above average)
  ✅ Low correlation to portfolio (0.35)
  ```
- [ ] Show top 3 contributing factors on hover
- [ ] Add "Learn More" link explaining what each signal means

### 7.2 Simplicity ⚠️ POTENTIALLY OVER-COMPLEX

The system shall prefer:
- Fewer, robust signals
- Clear rules
- Modular architecture

**Over-complexity without decision benefit is explicitly rejected.**

**Current Implementation:**
- ✅ Modular architecture (clean separation: data, ML, API, UI)
- ⚠️ 20 technical features (potentially over-complex)
- ⚠️ Random Forest model (non-linear, harder to explain than linear)
- ✅ Clear API structure

**Assessment:** Architecture is good, but feature set may be over-engineered.

**Action Required:**
- [ ] Feature audit: Which of 20 features actually matter?
  - Run feature importance analysis
  - Remove features with <5% importance
  - Target: 10-12 core features
- [ ] Consider simpler model for explainability:
  - Logistic Regression (linear, fully explainable)
  - Compare accuracy vs Random Forest
  - If <5% accuracy loss, switch for better explainability

---

## 8. Explicit Non-Goals ✅ COMPLIANT

The system shall **not**:
- ❌ Predict exact future prices → ✅ Current system complies (predicts probability)
- ❌ Perform automated trading → ✅ Complies (simulation only)
- ❌ Operate in real-time → ✅ Complies (daily batch)
- ❌ Optimize portfolios at institutional complexity → ✅ Complies (simple equal-weight)
- ❌ Provide advice to third parties → ✅ Complies (personal use)

**Status:** ✅ All non-goals respected.

---

## 9. Success Criteria

The system is successful if:
1. ✅ It produces consistent, explainable rankings
2. ⚠️ It improves capital allocation discipline (not measured yet)
3. ❌ It reduces drawdowns relative to naive strategies (no comparison data)
4. ❌ The user trusts the system enough to allocate real capital (TBD)

**Current Status:** 1/4 criteria met, 2 in progress, 1 not started.

**Measurement Plan:**
- [ ] Run 1-year backtest vs S&P 500 buy-and-hold
- [ ] Calculate max drawdown (target: <20% vs 30% for S&P 500)
- [ ] Measure Sharpe ratio (target: >1.0)
- [ ] Track user adherence to recommendations (target: >70%)

---

## 10. Guiding Principle

> **"This system exists to improve decision quality, not to eliminate uncertainty."**

---

## 📊 Implementation Gap Analysis

### ✅ Fully Implemented (5/12 Requirements)
1. ✅ Market data ingestion (yfinance)
2. ✅ Quantitative signal computation (20 technical features)
3. ✅ ML-based ranking (Random Forest)
4. ✅ Daily batch execution capability
5. ✅ Non-goals compliance

### ⚠️ Partially Implemented (4/12 Requirements)
6. ⚠️ LLM contextual analysis (exists but **violates design**)
7. ⚠️ Explainability (features computed but **not shown**)
8. ⚠️ Risk management (simulation only, **not in core ranking**)
9. ⚠️ Decision interface (informational, **not actionable**)

### ❌ Missing (3/12 Requirements) - **CRITICAL**
10. ❌ **Market regime detection** (no risk-on/risk-off awareness)
11. ❌ **Composite scoring** (currently only ML probability)
12. ❌ **Capital allocation limits** (no position sizing guidance)

**Compliance Score:** 42% (5/12 fully implemented)  
**Critical Gaps:** 3 (Market Regime, Composite Scoring, Allocation Limits)

---

## 🎯 Priority Roadmap

### **Phase 1: Critical Gaps (Week 2-3) - HIGHEST PRIORITY**
**Goal:** Implement missing core requirements that block decision quality

**Tasks:**
1. **Market Regime Detection** ⚠️ CRITICAL
   - [ ] Implement VIX-based volatility regime (API: Yahoo Finance ^VIX)
   - [ ] Add S&P 500 trend classification (50-day MA vs 200-day MA)
   - [ ] Create regime score: Risk-On (>70), Neutral (40-70), Risk-Off (<40)
   - [ ] **Rule**: Block all BUY signals when regime = Risk-Off
   - [ ] Display regime status in UI: "🟢 Risk-On" or "🔴 Risk-Off"
   - **Estimated Time:** 2 days
   - **Success Metric:** No BUY recommendations when VIX > 30

2. **Composite Scoring System** ⚠️ CRITICAL
   - [ ] Replace pure ML probability with weighted composite
   - [ ] Formula: Technical (40%) + ML (30%) + Momentum (20%) + Regime (10%)
   - [ ] Add transparency: Show score breakdown per asset
   - [ ] Validate: Backtest composite vs ML-only (target: +5% Sharpe ratio)
   - **Estimated Time:** 3 days
   - **Success Metric:** User can explain why AAPL scored 82/100

3. **Capital Allocation Framework** ⚠️ CRITICAL
   - [ ] Define max position sizes:
     - Single stock: 10% of portfolio
     - Single crypto: 5% of portfolio
     - Total equities: 70%
     - Total crypto: 20%
     - Cash reserve: 10%
   - [ ] Display recommended allocation in UI
   - [ ] Add portfolio exposure tracker (pie chart)
   - **Estimated Time:** 2 days
   - **Success Metric:** User knows exactly how much to invest in each asset

**Phase 1 Total:** 7 days (1 week)  
**Deliverable:** System becomes **decision-focused**, not just informational

---

### **Phase 2: Enhanced Explainability (Week 4)**
**Goal:** Make system transparent and trustworthy

**Tasks:**
1. **Signal Breakdown UI**
   - [ ] Add "Explain Score" modal per asset
   - [ ] Show top 3 contributing factors with values
   - [ ] Display regime status and impact
   - [ ] Add confidence intervals (±X% uncertainty)
   - **Estimated Time:** 3 days

2. **LLM Redesign** (Fix Philosophy Violation)
   - [ ] Change LLM from "decision maker" to "context provider"
   - [ ] Integrate NewsAPI for asset-specific news (last 7 days)
   - [ ] LLM task: Summarize news in 3 sentences max
   - [ ] **Strict rule**: LLM adjustment limited to ±5% of score
   - [ ] Remove "AI recommendations" - replace with "Contextual Notes"
   - **Estimated Time:** 2 days

3. **Feature Importance Analysis**
   - [ ] Run SHAP or permutation importance
   - [ ] Identify top 10 features (remove bottom 10)
   - [ ] Simplify model for explainability
   - **Estimated Time:** 2 days

**Phase 2 Total:** 7 days (1 week)  
**Deliverable:** System is fully transparent (no black box)

---

### **Phase 3: Historical Validation (Week 5-6)**
**Goal:** Prove system improves decision quality vs benchmarks

**Tasks:**
1. **Backtest Framework**
   - [ ] Run 1-year historical simulation (Jan 2025 - Jan 2026)
   - [ ] Compare 3 strategies:
     1. System recommendations (composite score)
     2. ML-only recommendations (current)
     3. S&P 500 buy-and-hold (benchmark)
   - [ ] Measure:
     - Total return
     - Max drawdown
     - Sharpe ratio
     - Win rate (% profitable trades)
   - **Estimated Time:** 3 days
   - **Success Metric:** System beats S&P 500 on risk-adjusted return

2. **Performance Tracking Dashboard**
   - [ ] Track actual vs recommended allocations
   - [ ] Measure user adherence rate ("Did user follow recommendations?")
   - [ ] Calculate realized returns vs system predictions
   - [ ] Display "Following system recommendations: +X% YTD"
   - **Estimated Time:** 4 days

**Phase 3 Total:** 7 days (1 week)  
**Deliverable:** Proven track record, user trust established

---

### **Phase 4: Risk Management Enhancement (Week 7)**
**Goal:** Protect capital in adverse conditions

**Tasks:**
1. **Regime-Based Risk Controls**
   - [ ] **Risk-Off Mode:**
     - Reduce max position size to 5% (stocks), 2% (crypto)
     - Increase cash reserve to 30%
     - Show "DEFENSIVE MODE ACTIVE" banner
   - [ ] **High Volatility Mode (VIX > 25):**
     - Show "⚠️ CAUTION" badges on all BUY signals
     - Suggest 50% of normal allocation
   - **Estimated Time:** 2 days

2. **Individual Asset Risk Scoring**
   - [ ] Compute risk score per asset (0-100):
     - Volatility (ATR percentile)
     - Drawdown risk (max 3-month drop)
     - Correlation to S&P 500
   - [ ] Display risk score in UI
   - [ ] **Rule**: Flag assets with risk >80 as "High Risk"
   - **Estimated Time:** 2 days

3. **Portfolio Exposure Limits**
   - [ ] Block new BUY signals when:
     - Total equity exposure > 70%
     - Total crypto exposure > 20%
     - Single sector > 30% (e.g., tech stocks)
   - [ ] Show "Portfolio Limit Reached" message
   - **Estimated Time:** 2 days

**Phase 4 Total:** 6 days  
**Deliverable:** Comprehensive risk protection

---

## 📅 Timeline Summary

| Phase | Duration | Weeks | Deliverable |
|-------|----------|-------|-------------|
| Phase 1: Critical Gaps | 7 days | Week 2-3 | Decision-focused system |
| Phase 2: Explainability | 7 days | Week 4 | Transparent system |
| Phase 3: Validation | 7 days | Week 5-6 | Proven track record |
| Phase 4: Risk Management | 6 days | Week 7 | Risk-protected system |
| **Total** | **27 days** | **7 weeks** | **Complete DSS** |

**Target Completion:** End of February 2026

---

## 📋 Integration with Existing Backlog

This document supersedes and consolidates:
- ✅ `BACKLOG.md` - Operational weekly tasks (continue using)
- ⚠️ `PRODUCT_REQUIREMENTS.md` - Old requirements (archive)
- ⚠️ `PRODUCT_ROADMAP_2026.md` - Strategic features (archive)
- ⚠️ `TECHNICAL_ASSESSMENT_2026.md` - Technical evaluation (move to assessments/)

**Master Planning Hierarchy:**
1. **DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md** (this document) - What & Why
2. **BACKLOG.md** - When & How (weekly execution)
3. Architecture Decision Records (ADRs) - Implementation decisions

**Action Required:**
- [ ] Update BACKLOG.md to reference this document
- [ ] Archive old PRODUCT_REQUIREMENTS.md
- [ ] Move TECHNICAL_ASSESSMENT_2026.md to assessments/
- [ ] Update README.md to point to new requirements

---

## 🔄 Review Schedule

This document shall be reviewed:
- **Weekly:** During sprint planning (Monday)
- **Monthly:** Strategic alignment check (1st of month)
- **Quarterly:** Philosophy and scope validation (Apr, Jul, Oct, Jan)

**Next Review:** 2026-01-13 (Week 2 planning)

---

## 📞 Decision Authority

**Philosophy Changes:** Require review with Kevin Garcia  
**Scope Changes:** Require review with Kevin Garcia  
**Implementation Details:** Engineering team autonomy within this framework  

---

**Last Updated:** 2026-01-06  
**Version:** 1.0  
**Status:** Active - Master Requirements  
**Author:** Kevin Garcia

---

## Appendix A: Current System vs Requirements Matrix

| Requirement | Status | Gap | Priority | Phase |
|-------------|--------|-----|----------|-------|
| Market Data | ✅ Done | None | - | - |
| Technical Signals | ✅ Done | Benchmark missing | Low | 3 |
| ML Ranking | ✅ Done | None | - | - |
| **Market Regime** | ❌ Missing | **Complete** | **CRITICAL** | **1** |
| **Composite Score** | ❌ Missing | **Complete** | **CRITICAL** | **1** |
| **Allocation Limits** | ❌ Missing | **Complete** | **CRITICAL** | **1** |
| LLM Context | ⚠️ Violates | Redesign needed | High | 2 |
| Explainability | ⚠️ Partial | UI missing | High | 2 |
| Risk Management | ⚠️ Partial | Core integration | High | 4 |
| Decision Interface | ⚠️ Partial | Actionable view | Medium | 2 |
| Backtesting | ❌ Missing | Framework | Medium | 3 |
| Performance Track | ❌ Missing | Dashboard | Medium | 3 |

**Legend:**
- ✅ Done: Fully implemented
- ⚠️ Partial: Exists but needs improvement
- ❌ Missing: Not implemented

---

**END OF DOCUMENT**
