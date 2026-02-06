# NFR-011: Backend Multi-Asset & JSON Architecture

> **Status:** Draft  
> **Created:** 2026-02-06  
> **Author:** Kevin Garcia  
> **Priority:** High  
> **Type:** Non-Functional Requirement (Architecture)

---

## 📋 Overview

Refactor backend architecture to support **three asset classes** with a **JSON-first approach** for configurations, rankings, and data storage. This enables cleaner APIs, easier debugging, and better extensibility.

### Asset Classes:
1. **Shares** (Stocks) - Existing, rename internally
2. **Digital Assets** (Crypto) - Existing, rename internally
3. **Commodities** (Raw Materials) - NEW: Gold, Oil, Silver, etc.

### JSON-First Approach:
- All configurations stored in JSON
- API responses consistently structured
- Ranking data cached as JSON
- Backtest results stored as JSON

---

## 🎯 User Stories

### NFR-11.1: Asset Type Standardization
**Als** Developer  
**möchte ich** konsistente Asset-Type Bezeichnungen  
**damit** API und UI konsistent sind

**Akzeptanzkriterien:**
- [ ] Internal asset types: `share`, `digital_asset`, `commodity`
- [ ] Mapping from legacy types: `stock` → `share`, `crypto` → `digital_asset`
- [ ] All API responses use new terminology
- [ ] Backward compatibility for existing clients (accept both)
- [ ] Documentation updated

---

### NFR-11.2: Commodities Integration
**Als** Trader  
**möchte ich** Rohstoffe analysieren können  
**damit** ich mein Portfolio diversifizieren kann

**Akzeptanzkriterien:**
- [ ] yfinance integration for commodities:
  - Gold (GC=F)
  - Silver (SI=F)
  - Crude Oil (CL=F)
  - Natural Gas (NG=F)
  - Copper (HG=F)
  - Platinum (PL=F)
  - Wheat (ZW=F)
  - Corn (ZC=F)
- [ ] New endpoint: `GET /api/commodity/ranking`
- [ ] Commodity-specific risk scoring (higher volatility baseline)
- [ ] Portfolio limits for commodities: max 15% total, max 5% single
- [ ] Commodity data cached for 5 minutes (markets slower)

---

### NFR-11.3: JSON Configuration Architecture
**Als** Developer  
**möchte ich** alle Configs als JSON  
**damit** sie versioniert und validiert werden können

**Akzeptanzkriterien:**
- [ ] Create `config/assets.json`:
  ```json
  {
    "shares": {
      "data_source": "yfinance",
      "cache_ttl_seconds": 300,
      "max_portfolio_exposure": 0.70,
      "max_single_position": 0.10,
      "popular_tickers": ["AAPL", "MSFT", "GOOGL", ...]
    },
    "digital_assets": {
      "data_source": "yfinance",
      "cache_ttl_seconds": 60,
      "max_portfolio_exposure": 0.20,
      "max_single_position": 0.05,
      "popular_tickers": ["BTC-USD", "ETH-USD", ...]
    },
    "commodities": {
      "data_source": "yfinance",
      "cache_ttl_seconds": 300,
      "max_portfolio_exposure": 0.15,
      "max_single_position": 0.05,
      "popular_tickers": ["GC=F", "CL=F", "SI=F", ...]
    }
  }
  ```
- [ ] Create `config/risk_limits.json` (from constitution)
- [ ] Create `config/ml_config.json` (hyperparams, thresholds)
- [ ] JSON Schema validation on startup
- [ ] Environment override capability (ENV vars take precedence)

---

### NFR-11.4: Unified Ranking API
**Als** Frontend  
**möchte ich** einen einheitlichen Ranking-Endpoint  
**damit** ich alle Asset-Klassen konsistent abrufen kann

**Akzeptanzkriterien:**
- [ ] Unified endpoint: `GET /api/ranking/{asset_type}`
  - `/api/ranking/shares`
  - `/api/ranking/digital_assets`
  - `/api/ranking/commodities`
- [ ] Consistent response format:
  ```json
  {
    "asset_type": "shares",
    "count": 50,
    "timestamp": "2026-02-06T10:00:00Z",
    "regime": "RISK_ON",
    "ranking": [
      {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "composite_score": 85.5,
        "signal": "BUY",
        "risk_score": 35,
        "price": 185.50,
        "change_24h": 2.3,
        "market_cap": 2800000000000
      }
    ]
  }
  ```
- [ ] Legacy endpoints remain (deprecated warning in response)
- [ ] OpenAPI documentation updated

---

### NFR-11.5: JSON-Based Backtest Results
**Als** Trader  
**möchte ich** Backtest-Resultate als JSON exportieren  
**damit** ich sie analysieren und archivieren kann

**Akzeptanzkriterien:**
- [ ] Backtest results stored in `data/backtests/{id}.json`
- [ ] Include full configuration and metrics
- [ ] Export endpoint: `GET /api/backtest/{id}/export`
- [ ] Import endpoint: `POST /api/backtest/import` (replay)
- [ ] JSON Schema for validation
- [ ] Retention policy: 90 days, then archive to S3 (optional)

---

### NFR-11.6: Storage Strategy (Hybrid)
**Als** System  
**möchte ich** optimale Storage für jeden Datentyp  
**damit** Performance und Wartbarkeit stimmen

**Akzeptanzkriterien:**
- [ ] **JSON Files** for:
  - Configurations (assets, limits, ML)
  - Backtest results
  - Ranking snapshots (hourly)
  - LLM prompt templates
- [ ] **SQLite** for:
  - User feedback (transactional)
  - LLM explanation logs
  - Analytics events
  - Alert history
- [ ] **In-Memory Cache** for:
  - Live rankings (Redis-like, TTL)
  - Feature computations
  - Session data
- [ ] Migration script from current structure

---

## 🔗 Cross-Reference: Existing Specs

| Spec | Overlap | Resolution |
|------|---------|------------|
| FR-001 (Risk Management) | Portfolio limits | NFR-011 provides JSON config, FR-001 uses it |
| FR-004 (ML Pipeline) | Model config | Move hyperparams to `ml_config.json` |
| FR-005 (Config Consolidation) | Config strategy | NFR-011 extends with JSON-first approach |
| FR-006 (LLM Learning) | Feedback storage | SQLite (as defined in FR-006) |

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking API changes | Frontend fails | Backward compatibility layer |
| yfinance commodity rate limits | Missing data | Cache aggressively, fallback tickers |
| JSON file corruption | Data loss | Validate on write, backup before save |
| Performance with large JSONs | Slow startup | Lazy loading, split files by domain |

---

## 📊 Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| API response consistency | 60% | 100% |
| Config locations | 5+ files | 3 JSON files |
| Commodity coverage | 0 | 8 major commodities |
| Startup config validation | None | 100% validated |
| Backtest export capability | None | Full JSON export |

---

## 📝 Notes

### Implementation Priority
1. **Phase 1**: Asset type standardization + JSON configs
2. **Phase 2**: Commodities integration
3. **Phase 3**: Unified ranking API
4. **Phase 4**: JSON backtest storage

### yfinance Commodity Tickers Reference
```
Gold:        GC=F
Silver:      SI=F
Crude Oil:   CL=F
Brent Oil:   BZ=F
Natural Gas: NG=F
Copper:      HG=F
Platinum:    PL=F
Palladium:   PA=F
Wheat:       ZW=F
Corn:        ZC=F
Soybeans:    ZS=F
Coffee:      KC=F
```

### Questions Resolved
- ✅ Use yfinance for commodities (simple, no new API)
- ✅ SQLite for transactional data (feedback, logs)
- ✅ JSON for configs and exports
- ✅ Backward compatibility required
