# Architecture Overview - POC-MarketPredictor-ML

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Status:** Production-Ready Beta

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │           React Frontend (Vite)                            │    │
│   │  • SimulationDashboard.jsx - Trading simulation UI         │    │
│   │  • Theme support (dark/light)                              │    │
│   │  • Multi-language (DE, EN, IT, ES, FR)                     │    │
│   │  • Real-time WebSocket updates                             │    │
│   └────────────┬──────────────────────────────────────────────┘    │
│                │ HTTP/WebSocket                                      │
│                ▼                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                        API GATEWAY LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌───────────────────────────────────────────────────────────┐    │
│   │         FastAPI Backend (trading_fun/)                     │    │
│   │  ┌─────────────────────────────────────────────────────┐  │    │
│   │  │  server.py - Main API Entry Point                   │  │    │
│   │  │  • /api/simulations/* - Trading simulation           │  │    │
│   │  │  • /ranking - Stock rankings                         │  │    │
│   │  │  • /crypto/* - Cryptocurrency data                   │  │    │
│   │  │  • /health - Health checks                           │  │    │
│   │  │  • /ws - WebSocket connections                       │  │    │
│   │  └─────────────────────────────────────────────────────┘  │    │
│   │                                                             │    │
│   │  ┌─────────────────────────────────────────────────────┐  │    │
│   │  │  Middleware & Services                              │  │    │
│   │  │  • CORS handling                                     │  │    │
│   │  │  • Rate limiting (rate_limiter.py)                   │  │    │
│   │  │  • Request validation (services.py)                  │  │    │
│   │  │  • Caching (cache.py - Redis/In-Memory)             │  │    │
│   │  │  • Logging (logging_config.py)                       │  │    │
│   │  │  • Metrics (metrics.py - Prometheus)                 │  │    │
│   │  └─────────────────────────────────────────────────────┘  │    │
│   └────────────┬──────────────────────────────────────────────┘    │
│                ▼                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                       BUSINESS LOGIC LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌───────────────────────┐  ┌───────────────────────┐             │
│   │  Trading Engine       │  │  ML/Analytics Engine  │             │
│   │  (trading.py)         │  │  (market_predictor/)  │             │
│   │  • Buy/Sell logic     │  │  • Feature extraction │             │
│   │  • Position sizing    │  │  • Model predictions  │             │
│   │  • Risk management    │  │  • Technical analysis │             │
│   └───────────┬───────────┘  └───────────┬───────────┘             │
│               │                            │                          │
│               ▼                            ▼                          │
│   ┌───────────────────────────────────────────────────────┐         │
│   │         Simulation Engine (simulation.py)              │         │
│   │  • Paper trading logic                                 │         │
│   │  • Portfolio management                                │         │
│   │  • Performance tracking                                │         │
│   │  • Trade history & metrics                             │         │
│   └────────────┬──────────────────────────────────────────┘         │
│                ▼                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│   │   SQLite DB  │  │  Redis Cache │  │  File System │            │
│   │  (simulation │  │  (optional)  │  │  (models/)   │            │
│   │   watchlist) │  │              │  │              │            │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│          │                  │                  │                     │
│          └──────────────────┴──────────────────┘                     │
│                             │                                         │
├─────────────────────────────┼─────────────────────────────────────────┤
│                   EXTERNAL DATA SOURCES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌────────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐      │
│   │  yfinance  │  │ CoinGecko│  │   MLflow   │  │  OpenAI  │      │
│   │  (stocks)  │  │  (crypto)│  │  (models)  │  │   (AI)   │      │
│   └────────────┘  └──────────┘  └────────────┘  └──────────┘      │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Structure

### Current Implementation (`trading_fun/`)

The active codebase is in `trading_fun/` directory:

```
trading_fun/
├── server.py           # FastAPI application entry point
├── trading.py          # Trading logic & feature extraction
├── simulation.py       # Paper trading simulation engine
├── simulation_db.py    # SQLite database for simulations
├── database.py         # Watchlist database
├── cache.py            # Caching layer (Redis/In-Memory)
├── rate_limiter.py     # API rate limiting
├── logging_config.py   # Structured logging
├── metrics.py          # Prometheus metrics
├── websocket.py        # WebSocket connection manager
├── crypto.py           # Cryptocurrency data integration
├── config.py           # Application configuration
└── services.py         # Business services
```

### Legacy Module (`market_predictor/`)

**⚠️ DEPRECATED** - Contains older implementation, still referenced in:

- simulation.py imports
- Documentation (needs update)
- Tests

**Action Required:** Consolidate to `trading_fun/` or update all references.

---

## 🔄 Data Flow

### 1. Trading Simulation Flow

```
User Request (Frontend)
    ↓
POST /api/simulations
    ↓
SimulationDashboard.jsx
    ↓
apiClient (axios)
    ↓
FastAPI Router (server.py)
    ↓
TradingSimulation (simulation.py)
    ↓
ML Model Prediction (trading.py)
    ↓
SQLite DB (simulation_db.py)
    ↓
Response to Frontend
    ↓
UI Update + WebSocket Broadcast
```

### 2. Stock Ranking Flow

```
GET /ranking
    ↓
Cache Check (cache.py)
    ↓
If Cache Miss:
    ├→ yfinance API
    ├→ Feature Extraction (trading.py)
    ├→ ML Model Prediction
    └→ Cache Result
    ↓
Response with Rankings
```

### 3. Real-time Updates Flow

```
WebSocket Connect
    ↓
WebSocket Manager (websocket.py)
    ↓
Subscribe to Channels:
    ├→ Portfolio Updates
    ├→ Trade Executions
    └→ Market Data
    ↓
Broadcast to Connected Clients
```

---

## 🔧 Key Components

### Backend Services

#### 1. **StockService** (`services.py`)

- Fetches stock data from yfinance
- Caches frequently accessed tickers
- Validates stock symbols

#### 2. **HealthService** (`services.py`)

- Monitors system health
- Checks database connections
- Validates external API availability

#### 3. **ValidationService** (`services.py`)

- Request validation
- Input sanitization
- Business rule enforcement

#### 4. **RateLimiter** (`rate_limiter.py`)

- 60 requests/minute per IP
- Sliding window algorithm
- Configurable limits

#### 5. **CacheManager** (`cache.py`)

- Redis (production) or in-memory (dev)
- TTL-based expiration
- Cache invalidation strategies

### Database Schema

#### Simulations Table

```sql
CREATE TABLE simulations (
    simulation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    initial_capital REAL NOT NULL,
    available_cash REAL NOT NULL,
    mode TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics TEXT  -- JSON encoded
);
```

#### Trades Table

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    action TEXT CHECK(action IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    reason TEXT,
    ml_confidence REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (simulation_id) REFERENCES simulations(simulation_id)
);
```

#### Positions Table

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id TEXT NOT NULL,
    ticker TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    avg_cost REAL NOT NULL,
    FOREIGN KEY (simulation_id) REFERENCES simulations(simulation_id),
    UNIQUE(simulation_id, ticker)
);
```

---

## 🚀 Deployment Architecture

### Development

```
Local Machine
├── Backend: uvicorn (port 8000)
├── Frontend: Vite dev server (port 5173)
├── Database: SQLite (./data/market_predictor.db)
└── Cache: In-memory
```

### Production (Railway/Render)

```
Cloud Platform
├── Backend Container (Dockerfile)
│   ├── Gunicorn + Uvicorn workers
│   ├── Environment variables from secrets
│   └── Health checks on /health
├── Frontend (Static Build)
│   ├── Deployed to Netlify/Vercel
│   ├── CDN distribution
│   └── Environment-specific API URLs
├── Database: PostgreSQL (planned)
└── Cache: Redis (optional)
```

---

## 🔐 Security Considerations

1. **API Rate Limiting**: 60 req/min per IP
2. **CORS Configuration**: Configured allowed origins
3. **Input Validation**: Pydantic models for all requests
4. **SQL Injection Prevention**: Parameterized queries
5. **Secret Management**: Environment variables, not hardcoded
6. **Error Handling**: No sensitive data in error responses

---

## 📊 Monitoring & Observability

### Metrics (Prometheus)

- Request count & latency
- Active simulations
- Trade executions
- Cache hit/miss rates
- Error rates by endpoint

### Logging

- Structured JSON logs
- Request ID tracking
- Performance metrics
- Error traces with context

### Health Checks

- `/health` endpoint
- Database connectivity
- External API availability
- Cache status

---

## 🔄 Migration Plan: `market_predictor/` → `trading_fun/`

### Issues

1. Duplicate code in two directories
2. Import inconsistencies
3. Documentation references wrong module
4. Tests import from `market_predictor`

### Solution

**Option 1: Consolidate to `trading_fun/`** (Recommended)

- Move simulation.py from market_predictor to trading_fun
- Update all imports
- Update documentation
- Archive market_predictor/

**Option 2: Rename `trading_fun/` to `market_predictor/`**

- Align with documentation
- More work to update configs
- Less intuitive name

**Recommendation:** Option 1 - Keep `trading_fun/` as the active module.

---

## Next Steps

1. ✅ Document architecture (this file)
2. 🔄 Create deployment diagrams
3. 🔄 Update README with correct module references
4. 🔄 Fix import inconsistencies
5. 🔄 Update CI/CD pipelines
6. 🔄 Add integration tests
