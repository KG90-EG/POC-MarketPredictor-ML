# NFR-011: Backend Multi-Asset & JSON Architecture - Tasks

> **Status:** In Progress  
> **Created:** 2026-02-06  
> **Updated:** 2026-02-06
> **Plan:** [plan.md](./plan.md)

---

## 🎯 Phase 1: Foundation (Week 1) ✅ COMPLETED

### TASK-011-001: Create JSON Asset Configuration ✅
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create `config/assets.json` with asset class definitions.

**Acceptance Criteria:**
- [x] File created with all 3 asset types
- [x] Includes ticker lists per asset type
- [x] Includes risk multipliers
- [x] Includes data source configs

**Code Location:** `config/assets.json`

**Sample Structure:**
```json
{
  "schema_version": "1.0",
  "asset_types": {
    "shares": {
      "display_name": "Shares",
      "legacy_name": "stock",
      "enabled": true,
      "risk_multiplier": 1.0,
      "data_source": "yfinance",
      "cache_ttl_seconds": 300,
      "popular_tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"]
    },
    "digital_assets": {
      "display_name": "Digital Assets",
      "legacy_name": "crypto",
      "enabled": true,
      "risk_multiplier": 1.5,
      "data_source": "coingecko",
      "cache_ttl_seconds": 120
    },
    "commodities": {
      "display_name": "Raw Materials",
      "legacy_name": null,
      "enabled": true,
      "risk_multiplier": 0.8,
      "data_source": "yfinance",
      "cache_ttl_seconds": 300,
      "popular_tickers": ["GC=F", "CL=F", "SI=F"]
    }
  }
}
```

---

### TASK-011-002: Create JSON Risk Limits Configuration ✅
**Priority:** P0 | **Effort:** 1.5h | **Owner:** -

**Description:**
Create `config/risk_limits.json` with portfolio constraints.

**Acceptance Criteria:**
- [x] File created with asset exposure limits
- [x] Includes regime-specific multipliers
- [x] Includes diversification rules
- [x] Validated against JSON Schema

**Code Location:** `config/risk_limits.json`

---

### TASK-011-003: Create JSON ML Configuration
**Priority:** P1 | **Effort:** 1.5h | **Owner:** - | **Status:** Deferred (uses existing best_hyperparameters.json)

**Description:**
Create `config/ml_config.json` with ML hyperparameters.

**Acceptance Criteria:**
- [ ] File created with model settings
- [ ] Includes training schedule
- [ ] Includes feature weights per asset type
- [ ] References existing `best_hyperparameters.json`

**Code Location:** `config/ml_config.json`

---

### TASK-011-004: Create JSON Schema Files ✅
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Create JSON Schema files for validation.

**Acceptance Criteria:**
- [x] `config/schemas/assets.schema.json` created
- [x] `config/schemas/risk_limits.schema.json` created
- [ ] `config/schemas/ml_config.schema.json` created (deferred)
- [x] Schemas validate sample configs

**Code Location:** `config/schemas/`

---

### TASK-011-005: Create Config Loader Module ✅
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create centralized config loader with validation.

**Acceptance Criteria:**
- [x] Loads all JSON configs on startup
- [x] Validates against JSON Schemas
- [x] Supports environment variable overrides
- [x] Caches configs in memory
- [x] Logs validation errors clearly
- [x] Unit tests with 100% coverage

**Code Location:** `src/trading_engine/core/config_loader.py`

**Interface:**
```python
from trading_engine.core.config_loader import ConfigLoader

config = ConfigLoader()
assets = config.get_asset_types()
risk_limits = config.get_risk_limits("commodities")
```

---

### TASK-011-006: Add Asset Type Backward Compatibility ✅
**Priority:** P0 | **Effort:** 2h | **Owner:** -

**Description:**
Create mapper for legacy asset type names.

**Acceptance Criteria:**
- [x] `stock` → `shares` mapping works
- [x] `crypto` → `digital_assets` mapping works
- [x] New names work directly
- [x] All existing endpoints still accept legacy names
- [x] Unit tests for all mappings

**Code Location:** `src/trading_engine/utils/asset_mapper.py`

---

### TASK-011-007: Update Existing Endpoints for Config
**Priority:** P1 | **Effort:** 3h | **Owner:** - | **Status:** In Progress

**Description:**
Refactor existing endpoints to use new config loader.

**Acceptance Criteria:**
- [ ] `/api/stock/ranking` uses config for cache TTL
- [ ] `/api/crypto/ranking` uses config for cache TTL
- [ ] Risk calculations use config multipliers
- [ ] No hardcoded values remain
- [ ] All existing tests pass

**Code Location:** `src/trading_engine/server.py`

---

## 🌽 Phase 2: Commodities Integration (Week 2)

### TASK-011-008: Create Commodity Data Fetcher
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create service for fetching commodity data from yfinance.

**Acceptance Criteria:**
- [ ] Fetches all 8 commodity tickers
- [ ] Returns standardized data format
- [ ] Handles API errors gracefully
- [ ] Implements retry with backoff
- [ ] Caches results (5 min TTL)
- [ ] Unit tests with mocks

**Code Location:** `src/trading_engine/commodity_service.py`

**Tickers:**
```python
COMMODITY_TICKERS = {
    "GC=F": {"name": "Gold", "category": "precious_metals"},
    "SI=F": {"name": "Silver", "category": "precious_metals"},
    "CL=F": {"name": "Crude Oil", "category": "energy"},
    "NG=F": {"name": "Natural Gas", "category": "energy"},
    "HG=F": {"name": "Copper", "category": "industrial_metals"},
    "PL=F": {"name": "Platinum", "category": "precious_metals"},
    "ZW=F": {"name": "Wheat", "category": "agriculture"},
    "ZC=F": {"name": "Corn", "category": "agriculture"}
}
```

---

### TASK-011-009: Add Commodity Risk Scoring
**Priority:** P0 | **Effort:** 3h | **Owner:** -

**Description:**
Extend risk scoring model for commodities.

**Acceptance Criteria:**
- [ ] Volatility calculation for commodities
- [ ] Adjusted scoring for lower volatility
- [ ] Uses risk multiplier from config (0.8x)
- [ ] Seasonal factors for agriculture
- [ ] Unit tests

**Code Location:** `src/trading_engine/risk/commodity_scorer.py`

---

### TASK-011-010: Create Commodity Ranking Endpoint
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create `/api/commodity/ranking` endpoint.

**Acceptance Criteria:**
- [ ] Returns all commodities sorted by score
- [ ] Uses same response format as stocks/crypto
- [ ] Includes category field
- [ ] Cached for 5 minutes
- [ ] OpenAPI documented
- [ ] Integration tests

**Code Location:** `src/trading_engine/server.py`

---

### TASK-011-011: Update Portfolio Validation for Commodities
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Extend portfolio validation to accept commodities.

**Acceptance Criteria:**
- [ ] `/api/portfolio/validate` accepts commodity positions
- [ ] Validates commodity tickers
- [ ] Applies commodity risk limits
- [ ] Works with frontend payload
- [ ] Unit tests

**Code Location:** `src/trading_engine/server.py`

---

### TASK-011-012: Cache Warm-up on Startup
**Priority:** P2 | **Effort:** 2h | **Owner:** -

**Description:**
Pre-warm commodity cache on server startup.

**Acceptance Criteria:**
- [ ] Fetches all commodity data on startup
- [ ] Logs success/failure
- [ ] Non-blocking (background task)
- [ ] Retries on failure

**Code Location:** `src/trading_engine/server.py` (lifespan event)

---

## 🔄 Phase 3: Unified Ranking API (Week 3)

### TASK-011-013: Create Unified Ranking Endpoint
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create `/api/ranking/{asset_type}` unified endpoint.

**Acceptance Criteria:**
- [ ] Supports `shares`, `digital_assets`, `commodities`
- [ ] Also accepts legacy names (`stock`, `crypto`)
- [ ] Returns standardized response schema
- [ ] Supports query params: limit, min_score, sort
- [ ] Integration tests

**Code Location:** `src/trading_engine/server.py`

**Example:**
```bash
GET /api/ranking/shares?limit=10&min_score=50
GET /api/ranking/digital_assets?sort=volume_24h
GET /api/ranking/commodities?category=energy
```

---

### TASK-011-014: Add Deprecation Warnings to Legacy Endpoints
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Add deprecation headers to legacy endpoints.

**Acceptance Criteria:**
- [ ] `/api/stock/ranking` returns `Deprecation` header
- [ ] `/api/crypto/ranking` returns `Deprecation` header
- [ ] Header points to new unified endpoint
- [ ] Logs deprecation usage for metrics

**Headers:**
```
Deprecation: true
Sunset: 2026-06-01
Link: </api/ranking/shares>; rel="successor-version"
```

---

### TASK-011-015: Update OpenAPI Documentation
**Priority:** P1 | **Effort:** 3h | **Owner:** -

**Description:**
Update OpenAPI spec with new endpoints.

**Acceptance Criteria:**
- [ ] New unified endpoint documented
- [ ] Response schemas defined
- [ ] Examples provided
- [ ] Deprecation noted on legacy endpoints
- [ ] Generated from code annotations

**Code Location:** `docs/api/openapi.json`

---

### TASK-011-016: Parallel Data Fetching
**Priority:** P2 | **Effort:** 3h | **Owner:** -

**Description:**
Optimize unified endpoint with parallel fetching.

**Acceptance Criteria:**
- [ ] All asset types can be fetched in parallel
- [ ] Optional `?asset_type=all` returns all
- [ ] Uses asyncio.gather
- [ ] Benchmark: <500ms for all 3 asset types

**Code Location:** `src/trading_engine/ranking_service.py`

---

## 💾 Phase 4: JSON Storage & Export (Week 4)

### TASK-011-017: Implement Ranking Snapshot Storage
**Priority:** P1 | **Effort:** 3h | **Owner:** -

**Description:**
Store ranking snapshots in JSON files.

**Acceptance Criteria:**
- [ ] Snapshots saved every 15 minutes
- [ ] Stored in `data/rankings/{asset_type}/`
- [ ] Filename format: `YYYY-MM-DD_HH-MM.json`
- [ ] Compressed with gzip
- [ ] Background task, non-blocking

**Code Location:** `src/trading_engine/storage/ranking_storage.py`

---

### TASK-011-018: Implement Backtest JSON Export
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Export backtest results to JSON files.

**Acceptance Criteria:**
- [ ] `/api/backtest/{id}/export` endpoint
- [ ] Returns downloadable JSON file
- [ ] Includes all positions, trades, metrics
- [ ] Stored in `data/backtests/{uuid}.json`

**Code Location:** `src/trading_engine/server.py`

---

### TASK-011-019: Implement Backtest Import
**Priority:** P2 | **Effort:** 2h | **Owner:** -

**Description:**
Import backtests from JSON files.

**Acceptance Criteria:**
- [ ] `/api/backtest/import` endpoint (POST)
- [ ] Validates JSON structure
- [ ] Generates new UUID
- [ ] Returns backtest ID

**Code Location:** `src/trading_engine/server.py`

---

### TASK-011-020: Create Retention Policy
**Priority:** P2 | **Effort:** 2h | **Owner:** -

**Description:**
Implement 90-day retention for JSON files.

**Acceptance Criteria:**
- [ ] Daily cleanup job
- [ ] Deletes files older than 90 days
- [ ] Logs deletions
- [ ] Configurable in config

**Code Location:** `src/trading_engine/storage/retention.py`

---

### TASK-011-021: Add Export Endpoints
**Priority:** P2 | **Effort:** 2h | **Owner:** -

**Description:**
Add export endpoints for rankings.

**Acceptance Criteria:**
- [ ] `/api/ranking/{asset_type}/export?date=YYYY-MM-DD`
- [ ] Returns historical snapshot
- [ ] 404 if not found
- [ ] Supports date range

**Code Location:** `src/trading_engine/server.py`

---

## ✅ Verification Tasks

### TASK-011-022: Integration Test Suite
**Priority:** P0 | **Effort:** 4h | **Owner:** -

**Description:**
Create comprehensive integration tests.

**Acceptance Criteria:**
- [ ] Tests all new endpoints
- [ ] Tests backward compatibility
- [ ] Tests config loading
- [ ] Tests error handling
- [ ] CI/CD passing

**Code Location:** `tests/test_multi_asset_integration.py`

---

### TASK-011-023: Performance Benchmark
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Benchmark API performance.

**Acceptance Criteria:**
- [ ] Unified endpoint <200ms (cached)
- [ ] Commodity fetch <1s (uncached)
- [ ] Config load <50ms
- [ ] Results documented

**Code Location:** `tests/benchmarks/`

---

### TASK-011-024: Documentation Update
**Priority:** P1 | **Effort:** 2h | **Owner:** -

**Description:**
Update README and API docs.

**Acceptance Criteria:**
- [ ] README updated with new endpoints
- [ ] curl examples for all endpoints
- [ ] Configuration guide
- [ ] Migration guide from legacy endpoints

**Code Location:** `README.md`, `docs/`

---

## 📋 Summary

| Phase | Tasks | Effort | Priority |
|-------|-------|--------|----------|
| Foundation | 7 | 16h | P0-P1 |
| Commodities | 5 | 15h | P0-P2 |
| Unified API | 4 | 12h | P0-P2 |
| Storage | 5 | 11h | P1-P2 |
| Verification | 3 | 8h | P0-P1 |
| **Total** | **24** | **~62h** | - |

---

## 🔗 Cross-References

- **FR-006:** LLM Learning (feedback affects recommendations)
- **FR-007:** Frontend Multi-Asset Dashboard (consumes these APIs)
- **NFR-010:** ML Training Pipeline (uses ml_config.json)
- **005:** Config Consolidation (JSON-first approach alignment)
