# Phase 4: Implementation Plan

## Übersicht

**Tech Stack:** FastAPI + React + Vite (bestehend)  
**Neue Module:** 2 Backend + 2 Frontend  
**Geschätzte Zeit:** 6 Tage  

## Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
├─────────────────────────────────────────────────────────────────┤
│  DefensiveModeBar.jsx    │  RiskBadge.jsx    │  ExposureChart.jsx│
│  (Banner bei RISK_OFF)   │  (Risk Score UI)  │  (Portfolio Pie)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND API                              │
├─────────────────────────────────────────────────────────────────┤
│  /api/portfolio/exposure  │  /api/predict/{ticker} (erweitert)  │
│  /regime (erweitert)      │  /ranking (erweitert)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       CORE MODULES                               │
├─────────────────────────────────────────────────────────────────┤
│  risk_scoring.py          │  market_regime.py (erweitert)       │
│  (ATR, Drawdown, Korr.)   │  (Defensive Mode Logic)             │
└─────────────────────────────────────────────────────────────────┘
```

## Neue Dateien

### Backend

1. **`src/trading_engine/risk_scoring.py`** (NEU)
   - `RiskScorer` Klasse
   - `calculate_volatility_score(ticker)` - ATR-basiert
   - `calculate_drawdown_score(ticker)` - Max Drawdown 3 Monate
   - `calculate_correlation_score(ticker)` - vs S&P 500
   - `get_composite_risk_score(ticker)` - Gewichteter Score 0-100

2. **`src/trading_engine/market_regime.py`** (ERWEITERN)
   - `get_defensive_mode_limits()` - Reduzierte Limits bei RISK_OFF
   - `should_show_caution_badge()` - True wenn High Volatility

### Frontend

3. **`frontend/src/components/DefensiveModeBar.jsx`** (NEU)
   - Roter Banner bei RISK_OFF
   - Text: "🔴 DEFENSIVE MODE - Reduced position limits active"
   - Sticky am oberen Rand

4. **`frontend/src/components/RiskBadge.jsx`** (NEU)
   - Farbiger Badge (grün/gelb/rot) mit Risk Score
   - Tooltip mit Breakdown (Volatilität, Drawdown, Korrelation)

5. **`frontend/src/components/ExposureChart.jsx`** (NEU)
   - Pie Chart mit Portfolio-Allokation
   - Warnung wenn Limit überschritten

## Bestehende Dateien (zu erweitern)

### Backend

- **`src/trading_engine/server.py`**
  - Neuer Endpoint: `/api/portfolio/exposure`
  - Erweitern: `/api/predict/{ticker}` mit `risk_score`
  - Erweitern: `/ranking` mit `risk_score` pro Asset
  - Erweitern: `/regime` mit `defensive_mode` Flag

### Frontend

- **`frontend/src/App.jsx`**
  - DefensiveModeBar einbinden (conditional)

- **`frontend/src/components/StockRanking.jsx`**
  - RiskBadge neben Score anzeigen
  - "High Risk" Flag für Score > 70

## API Contracts

### GET /api/portfolio/exposure

```json
{
  "exposure": {
    "equity_percent": 45.5,
    "crypto_percent": 12.0,
    "cash_percent": 42.5
  },
  "limits": {
    "max_equity": 70,
    "max_crypto": 20,
    "min_cash": 10
  },
  "defensive_mode": false,
  "warnings": []
}
```

### GET /api/predict/{ticker} (erweitert)

```json
{
  "ticker": "AAPL",
  "composite_score": 75,
  "signal": "BUY",
  "risk_score": 42,
  "risk_level": "MEDIUM",
  "risk_breakdown": {
    "volatility": 35,
    "drawdown": 48,
    "correlation": 45
  },
  "caution_badge": false
}
```

### GET /regime (erweitert)

```json
{
  "regime_status": "RISK_ON",
  "regime_score": 72,
  "defensive_mode": false,
  "position_limits": {
    "single_stock_max": 10,
    "single_crypto_max": 5,
    "total_equity_max": 70,
    "total_crypto_max": 20
  }
}
```

## Teststrategie

### Unit Tests

- `tests/test_risk_scoring.py`
  - Test: ATR Berechnung
  - Test: Drawdown Berechnung
  - Test: Korrelation Berechnung
  - Test: Composite Risk Score

### Integration Tests

- `tests/test_integration.py` (erweitern)
  - Test: /api/portfolio/exposure Endpoint
  - Test: Risk Score in /ranking Response
  - Test: Defensive Mode bei RISK_OFF

### Frontend Tests

- `frontend/src/__tests__/RiskManagement.test.jsx`
  - Test: DefensiveModeBar Rendering
  - Test: RiskBadge Farbkodierung
  - Test: ExposureChart Warnungen

## Rollout Plan

1. **Tag 1-2:** Backend risk_scoring.py implementieren + Tests
2. **Tag 3:** Backend API Endpoints erweitern + Tests
3. **Tag 4:** Frontend DefensiveModeBar + RiskBadge
4. **Tag 5:** Frontend ExposureChart + StockRanking Integration
5. **Tag 6:** End-to-End Tests + Bugfixes + Deployment

## Risiko-Mitigation

| Risiko | Mitigation |
|--------|------------|
| Fehlende historische Daten | Fallback: Risk Score = 50 (neutral) |
| yfinance Rate Limits | Caching mit 5 Minuten TTL |
| S&P 500 Daten nicht verfügbar | Fallback: Korrelation = 0.5 |
