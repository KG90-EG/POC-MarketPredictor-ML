# NFR-011: Backend Multi-Asset & JSON Architecture - Implementation Plan

> **Status:** Draft  
> **Created:** 2026-02-06  
> **Spec:** [spec.md](./spec.md)

---

## 🏗️ Architecture Decisions

### AD-1: Asset Type Naming Convention
**Decision:** Use business terminology internally.

| Internal Name | API Name | Legacy Name | Description |
|---------------|----------|-------------|-------------|
| `share` | `shares` | `stock` | Equities (AAPL, MSFT) |
| `digital_asset` | `digital_assets` | `crypto` | Cryptocurrencies (BTC, ETH) |
| `commodity` | `commodities` | - | Raw materials (Gold, Oil) |

**Rationale:**
- Business-aligned naming
- Clear differentiation
- Future-proof (can add more asset classes)

**Migration:**
```python
# Backward compatibility mapper
ASSET_TYPE_MAP = {
    "stock": "share",
    "crypto": "digital_asset",
    "share": "share",
    "digital_asset": "digital_asset",
    "commodity": "commodity"
}
```

---

### AD-2: JSON Configuration Structure
**Decision:** Three main config files with JSON Schema validation.

```
config/
├── assets.json           # Asset class definitions
├── risk_limits.json      # Portfolio limits
├── ml_config.json        # ML hyperparameters
└── schemas/
    ├── assets.schema.json
    ├── risk_limits.schema.json
    └── ml_config.schema.json
```

**Rationale:**
- Single source of truth per domain
- Schema validation catches errors early
- Easy to version control
- Environment overrides for deployment flexibility

---

### AD-3: Commodities Data Strategy
**Decision:** Use yfinance with aggressive caching.

**Tickers (Top 8):**
| Commodity | Ticker | Category |
|-----------|--------|----------|
| Gold | GC=F | Precious Metals |
| Silver | SI=F | Precious Metals |
| Crude Oil | CL=F | Energy |
| Natural Gas | NG=F | Energy |
| Copper | HG=F | Industrial Metals |
| Platinum | PL=F | Precious Metals |
| Wheat | ZW=F | Agriculture |
| Corn | ZC=F | Agriculture |

**Caching:**
- TTL: 5 minutes (commodity markets less volatile)
- Fallback: Return cached data if API fails
- Pre-warm cache on startup

---

### AD-4: Unified Ranking API Design
**Decision:** Parameterized endpoint with consistent schema.

**Endpoint:**
```
GET /api/ranking/{asset_type}
    ?limit=50
    &min_score=0
    &sort=composite_score
    &country=US (shares only)
```

**Response Schema:**
```json
{
  "asset_type": "string",
  "count": "integer",
  "timestamp": "ISO8601",
  "regime": "RISK_ON|RISK_OFF|NEUTRAL",
  "ranking": [
    {
      "ticker": "string",
      "name": "string",
      "composite_score": "float (0-100)",
      "signal": "BUY|SELL|HOLD",
      "risk_score": "float (0-100)",
      "price": "float",
      "change_24h": "float (%)",
      "change_7d": "float (%)",
      "market_cap": "float",
      "volume_24h": "float",
      "asset_metadata": {}
    }
  ]
}
```

---

### AD-5: Storage Layer Architecture
**Decision:** Hybrid storage based on access patterns.

| Data Type | Storage | Reason |
|-----------|---------|--------|
| Configurations | JSON files | Versionable, human-readable |
| Rankings (live) | In-memory cache | Fast access, TTL expiry |
| Rankings (snapshot) | JSON files | Historical analysis |
| Backtest results | JSON files | Export/import, archival |
| User feedback | SQLite | Transactional, queryable |
| LLM logs | SQLite | Transactional, analytics |
| Analytics events | SQLite | Time-series queries |

**File Structure:**
```
data/
├── rankings/
│   ├── shares/
│   │   └── 2026-02-06_10-00.json
│   ├── digital_assets/
│   └── commodities/
├── backtests/
│   └── {uuid}.json
└── analytics/
    └── events.jsonl
```

---

## 📅 Implementation Phases

### Phase 1: Foundation (Week 1) 
**Effort:** ~16 hours

- [ ] Create JSON config files (assets, limits, ml)
- [ ] Add JSON Schema validation
- [ ] Create config loader with env override
- [ ] Add asset type mapper (backward compat)
- [ ] Update existing endpoints to use configs
- [ ] Unit tests for config loading

**Deliverables:**
- `config/assets.json`
- `config/risk_limits.json`
- `config/ml_config.json`
- `src/trading_engine/config_loader.py`
- Tests

---

### Phase 2: Commodities Integration (Week 2)
**Effort:** ~20 hours

- [ ] Create commodity data fetcher
- [ ] Add commodity risk scoring (adjusted volatility)
- [ ] Create `/api/commodity/ranking` endpoint
- [ ] Add commodity tickers to popular list
- [ ] Update portfolio validation for commodities
- [ ] Cache warm-up on startup
- [ ] Integration tests

**Deliverables:**
- `src/trading_engine/commodity_service.py`
- Commodity endpoints in `server.py`
- Tests

---

### Phase 3: Unified Ranking API (Week 3)
**Effort:** ~16 hours

- [ ] Create unified `/api/ranking/{asset_type}` endpoint
- [ ] Standardize response format across all asset types
- [ ] Add deprecation warnings to legacy endpoints
- [ ] Update OpenAPI documentation
- [ ] Add query parameters (limit, min_score, sort)
- [ ] Performance optimization (parallel fetching)
- [ ] Integration tests

**Deliverables:**
- Unified ranking endpoint
- Updated OpenAPI spec
- Tests

---

### Phase 4: JSON Storage & Export (Week 4)
**Effort:** ~12 hours

- [ ] Implement ranking snapshot storage
- [ ] Implement backtest JSON export
- [ ] Add import endpoint for backtests
- [ ] Create retention policy (90 days)
- [ ] Add export endpoint for rankings
- [ ] Documentation

**Deliverables:**
- JSON storage layer
- Export/import endpoints
- Documentation

---

## ⚠️ Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| yfinance rate limits | Medium | Data gaps | Aggressive caching, fallback to last known |
| Breaking API changes | High | Frontend breaks | Version header, backward compat layer |
| Config file corruption | Low | System crash | Validate on load, keep backup |
| Performance regression | Medium | Slow API | Benchmark before/after, optimize queries |

---

## 📊 Key Metrics

```python
# Success Metrics
- Config files: 3 (assets, limits, ml)
- Asset types supported: 3 (shares, digital_assets, commodities)
- Commodity tickers: 8
- API consistency: 100% (unified schema)
- Backward compatibility: 100%
- Test coverage: >80%
```

---

## 🔗 Dependencies

**Required:**
- yfinance (already installed) ✅
- jsonschema (to add)
- Existing caching layer ✅

**Optional:**
- boto3 (for S3 archival, later)

---

## 📝 Open Questions (Resolved)

1. ✅ **Which commodities?** Top 8: Gold, Silver, Oil, Gas, Copper, Platinum, Wheat, Corn
2. ✅ **Backward compatibility?** Yes, legacy endpoints remain with deprecation warning
3. ✅ **SQLite vs JSON?** Hybrid: SQLite for transactional, JSON for configs/exports
4. ✅ **Config validation?** JSON Schema on startup
