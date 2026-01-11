# 🔌 API Integration Guide

**Market Predictor ML - External Integration Documentation**

Version: 1.0 | Last Updated: 2026-01-11

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Core Endpoints](#core-endpoints)
5. [Webhooks](#webhooks)
6. [Real-Time Data (WebSocket)](#real-time-data-websocket)
7. [Error Handling](#error-handling)
8. [Code Examples](#code-examples)
9. [Best Practices](#best-practices)
10. [Changelog](#changelog)

---

## 🚀 Quick Start

### Base URL

```
Development:  http://localhost:8000
Production:   https://your-domain.com
```

### API Documentation

Interactive API docs available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Spec:** `http://localhost:8000/api/openapi.json`

### Simple Request Example

```bash
# Get stock ranking
curl http://localhost:8000/ranking

# Get specific stock prediction
curl http://localhost:8000/api/predict/AAPL

# Check market regime
curl http://localhost:8000/regime
```

---

## 🔐 Authentication

### Current Status

**⚠️ Authentication is OPTIONAL in current version**

The API currently operates in **development mode** with no authentication required. For production deployments, implement one of the following:

### Option 1: API Key (Recommended for Production)

**Setup (Coming Soon):**
```bash
# Generate API key
POST /api/auth/keys
{
  "name": "My Integration",
  "permissions": ["read", "write"]
}

# Response
{
  "api_key": "sk_live_1234567890abcdef",
  "created_at": "2026-01-11T10:00:00Z"
}
```

**Usage:**
```bash
curl -H "X-API-Key: sk_live_1234567890abcdef" \
  http://localhost:8000/ranking
```

### Option 2: JWT Tokens (For User-Based Apps)

**Login Flow:**
```bash
# 1. Get access token
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "secure_password"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}

# 2. Use token in requests
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  http://localhost:8000/ranking
```

### Option 3: OAuth 2.0 (For Third-Party Apps)

**Coming Soon** - For apps that need user consent flow.

---

## ⏱️ Rate Limiting

### Current Limits

| Endpoint Category | Rate Limit | Window |
|------------------|------------|--------|
| **Market Data** (`/ranking`, `/regime`) | 60 requests | 1 minute |
| **Predictions** (`/api/predict/{ticker}`) | 30 requests | 1 minute |
| **Simulations** (`/api/simulations/*`) | 20 requests | 1 minute |
| **Backtesting** (`/api/backtest/run`) | 5 requests | 1 hour |
| **MLOps** (`/api/ml/*`) | 10 requests | 1 minute |
| **WebSocket** (connections) | 5 connections | per IP |

### Rate Limit Headers

Every response includes rate limit information:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1673456789
```

### Handling Rate Limits

**Response when limit exceeded:**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after": 30
}
```

**Best Practice:**
```python
import requests
import time

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url)
        
        if response.status_code == 429:  # Too Many Requests
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue
            
        return response.json()
    
    raise Exception("Max retries exceeded")
```

---

## 📡 Core Endpoints

### 1. Stock Ranking

**Endpoint:** `GET /ranking`

**Description:** Get ranked list of stocks with composite scores.

**Parameters:**
```python
{
  "limit": 50,          # Number of stocks (default: 50)
  "region": "US",       # US, CH, DE, UK, FR (default: all)
  "min_score": 0,       # Minimum composite score (0-100)
  "sort": "desc"        # Sort order: desc or asc
}
```

**Response:**
```json
{
  "regime": {
    "status": "Risk-On",
    "vix": 18.5,
    "sp500_trend": "uptrend"
  },
  "timestamp": "2026-01-11T10:30:00Z",
  "ranking": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "composite_score": 78.5,
      "signal": "BUY",
      "components": {
        "technical_score": 75.0,
        "ml_score": 80.0,
        "momentum_score": 82.0,
        "regime_adjustment": 5.0
      },
      "price": 175.50,
      "change_pct": 2.3
    }
  ]
}
```

**Example:**
```python
import requests

response = requests.get(
    "http://localhost:8000/ranking",
    params={"limit": 10, "min_score": 70}
)

top_stocks = response.json()["ranking"]
for stock in top_stocks:
    print(f"{stock['ticker']}: {stock['composite_score']}")
```

---

### 2. Stock Prediction

**Endpoint:** `GET /api/predict/{ticker}`

**Description:** Get ML prediction for specific stock.

**Response:**
```json
{
  "ticker": "AAPL",
  "prediction": {
    "probability": 0.78,
    "signal": "BUY",
    "confidence": "high"
  },
  "features": {
    "rsi": 65.2,
    "macd": 1.5,
    "bb_position": 0.75
  },
  "last_updated": "2026-01-11T10:30:00Z"
}
```

---

### 3. Market Regime

**Endpoint:** `GET /regime`

**Description:** Get current market regime status.

**Response:**
```json
{
  "regime": "Risk-On",
  "vix": 18.5,
  "sp500_trend": "uptrend",
  "confidence": 0.85,
  "interpretation": {
    "risk_level": "low",
    "recommendation": "Safe to take new positions",
    "position_sizing": "full"
  },
  "last_updated": "2026-01-11T10:30:00Z"
}
```

---

### 4. Portfolio Validation

**Endpoint:** `POST /api/portfolio/validate`

**Description:** Validate proposed allocation before execution.

**Request:**
```json
{
  "allocations": [
    {"ticker": "AAPL", "allocation_pct": 10},
    {"ticker": "MSFT", "allocation_pct": 8},
    {"ticker": "GOOGL", "allocation_pct": 12}
  ],
  "total_portfolio_value": 100000
}
```

**Response:**
```json
{
  "valid": false,
  "violations": [
    {
      "type": "position_size_exceeded",
      "ticker": "GOOGL",
      "limit": 10,
      "proposed": 12,
      "message": "Position size exceeds 10% limit"
    }
  ],
  "suggested_allocation": [
    {"ticker": "AAPL", "allocation_pct": 10},
    {"ticker": "MSFT", "allocation_pct": 8},
    {"ticker": "GOOGL", "allocation_pct": 10}
  ]
}
```

---

### 5. Backtesting

**Endpoint:** `POST /api/backtest/run`

**Description:** Run historical backtest comparison.

**Request:**
```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "start_date": "2025-01-01",
  "end_date": "2026-01-11",
  "initial_capital": 100000
}
```

**Response:**
```json
{
  "backtest_period": {
    "start_date": "2025-01-01",
    "end_date": "2026-01-11",
    "duration_days": 376
  },
  "strategies": {
    "composite": {
      "metrics": {
        "total_return": 15.2,
        "max_drawdown": 8.5,
        "sharpe_ratio": 1.45,
        "win_rate": 68.0
      }
    },
    "ml_only": {
      "metrics": {
        "total_return": 12.1,
        "max_drawdown": 10.2,
        "sharpe_ratio": 1.15,
        "win_rate": 62.0
      }
    },
    "sp500": {
      "metrics": {
        "total_return": 10.5,
        "max_drawdown": 7.8,
        "sharpe_ratio": 1.20,
        "win_rate": 100.0
      }
    }
  },
  "comparison": {
    "winner_by_return": {
      "strategy": "Composite Score System",
      "return": 15.2
    },
    "alpha_vs_benchmark": {
      "alpha": 4.7,
      "interpretation": "Outperformed"
    }
  }
}
```

---

## 🪝 Webhooks

### Setup

**1. Register Webhook:**
```bash
POST /api/webhooks
{
  "url": "https://your-app.com/webhook/market-predictor",
  "events": ["regime_change", "signal_change", "alert_triggered"],
  "secret": "your_webhook_secret"
}

# Response
{
  "webhook_id": "wh_1234567890",
  "status": "active",
  "created_at": "2026-01-11T10:00:00Z"
}
```

### Webhook Events

#### 1. Regime Change
**Triggered when:** Market regime changes (Risk-On ↔ Neutral ↔ Risk-Off)

**Payload:**
```json
{
  "event": "regime_change",
  "timestamp": "2026-01-11T10:30:00Z",
  "data": {
    "old_regime": "Neutral",
    "new_regime": "Risk-Off",
    "vix": 31.2,
    "sp500_trend": "downtrend"
  }
}
```

#### 2. Signal Change
**Triggered when:** Stock signal changes significantly (BUY → SELL or vice versa)

**Payload:**
```json
{
  "event": "signal_change",
  "timestamp": "2026-01-11T10:30:00Z",
  "data": {
    "ticker": "AAPL",
    "old_signal": "BUY",
    "new_signal": "SELL",
    "old_score": 75,
    "new_score": 38
  }
}
```

#### 3. Alert Triggered
**Triggered when:** User-defined alert conditions met

**Payload:**
```json
{
  "event": "alert_triggered",
  "timestamp": "2026-01-11T10:30:00Z",
  "data": {
    "alert_id": "alert_123",
    "ticker": "AAPL",
    "condition": "price_above",
    "threshold": 180,
    "current_value": 181.50
  }
}
```

### Webhook Security

**Verify Webhook Signature:**
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify webhook signature"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

# Usage
payload = request.body
signature = request.headers.get('X-Webhook-Signature')
secret = "your_webhook_secret"

if verify_webhook(payload, signature, secret):
    # Process webhook
    pass
else:
    # Reject
    return {"error": "Invalid signature"}, 403
```

---

## 🔌 Real-Time Data (WebSocket)

### Connection

```javascript
// JavaScript
const ws = new WebSocket('ws://localhost:8000/ws/your-client-id');

ws.onopen = () => {
  console.log('Connected to Market Predictor');
  
  // Subscribe to stock updates
  ws.send(JSON.stringify({
    action: 'subscribe',
    ticker: 'AAPL'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

### Subscription Types

**1. Price Updates:**
```json
{
  "action": "subscribe",
  "ticker": "AAPL",
  "frequency": "1m"  // 1m, 5m, 15m, 1h
}
```

**2. Signal Updates:**
```json
{
  "action": "subscribe",
  "event": "signal_change",
  "tickers": ["AAPL", "MSFT", "GOOGL"]
}
```

**3. Regime Updates:**
```json
{
  "action": "subscribe",
  "event": "regime_change"
}
```

### Message Format

**Price Update:**
```json
{
  "type": "price_update",
  "ticker": "AAPL",
  "price": 175.50,
  "change_pct": 2.3,
  "volume": 45000000,
  "timestamp": "2026-01-11T10:30:00Z"
}
```

**Signal Update:**
```json
{
  "type": "signal_update",
  "ticker": "AAPL",
  "composite_score": 78.5,
  "signal": "BUY",
  "timestamp": "2026-01-11T10:30:00Z"
}
```

---

## ❗ Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Check API key/token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Check endpoint URL |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Retry with exponential backoff |
| 503 | Service Unavailable | System maintenance, retry later |

### Error Response Format

```json
{
  "detail": "Stock ticker not found",
  "error_code": "TICKER_NOT_FOUND",
  "timestamp": "2026-01-11T10:30:00Z",
  "request_id": "req_1234567890"
}
```

### Retry Strategy

```python
import requests
import time

def api_call_with_retry(url, max_retries=3, backoff_factor=2):
    """Make API call with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limited
                wait_time = backoff_factor ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            elif e.response.status_code >= 500:
                # Server error
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    print(f"Server error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            else:
                # Client error (4xx) - don't retry
                raise
                
        except requests.exceptions.Timeout:
            print("Request timeout. Retrying...")
            if attempt < max_retries - 1:
                time.sleep(backoff_factor ** attempt)
                continue
            else:
                raise
    
    raise Exception("Max retries exceeded")
```

---

## 💻 Code Examples

### Python

```python
import requests
from typing import List, Dict

class MarketPredictorClient:
    """Python client for Market Predictor API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
    
    def get_ranking(self, limit: int = 50, min_score: float = 0) -> List[Dict]:
        """Get stock ranking"""
        response = self.session.get(
            f"{self.base_url}/ranking",
            params={"limit": limit, "min_score": min_score}
        )
        response.raise_for_status()
        return response.json()["ranking"]
    
    def get_prediction(self, ticker: str) -> Dict:
        """Get prediction for ticker"""
        response = self.session.get(f"{self.base_url}/api/predict/{ticker}")
        response.raise_for_status()
        return response.json()
    
    def get_regime(self) -> Dict:
        """Get market regime"""
        response = self.session.get(f"{self.base_url}/regime")
        response.raise_for_status()
        return response.json()
    
    def validate_portfolio(self, allocations: List[Dict], total_value: float) -> Dict:
        """Validate portfolio allocations"""
        response = self.session.post(
            f"{self.base_url}/api/portfolio/validate",
            json={
                "allocations": allocations,
                "total_portfolio_value": total_value
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = MarketPredictorClient()

# Get top 10 stocks
top_stocks = client.get_ranking(limit=10, min_score=70)
for stock in top_stocks:
    print(f"{stock['ticker']}: {stock['composite_score']}")

# Check regime
regime = client.get_regime()
print(f"Market Regime: {regime['regime']}")

# Validate allocation
allocations = [
    {"ticker": "AAPL", "allocation_pct": 10},
    {"ticker": "MSFT", "allocation_pct": 8}
]
validation = client.validate_portfolio(allocations, 100000)
print(f"Valid: {validation['valid']}")
```

---

### JavaScript/TypeScript

```typescript
// TypeScript
interface StockRanking {
  ticker: string;
  composite_score: number;
  signal: string;
  price: number;
}

class MarketPredictorAPI {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = 'http://localhost:8000', apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.apiKey && { 'X-API-Key': this.apiKey }),
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: { ...headers, ...options?.headers },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async getRanking(limit: number = 50, minScore: number = 0): Promise<StockRanking[]> {
    const data = await this.request<{ ranking: StockRanking[] }>(
      `/ranking?limit=${limit}&min_score=${minScore}`
    );
    return data.ranking;
  }

  async getPrediction(ticker: string) {
    return this.request(`/api/predict/${ticker}`);
  }

  async getRegime() {
    return this.request('/regime');
  }
}

// Usage
const api = new MarketPredictorAPI();

// Get rankings
const topStocks = await api.getRanking(10, 70);
topStocks.forEach(stock => {
  console.log(`${stock.ticker}: ${stock.composite_score}`);
});

// Check regime
const regime = await api.getRegime();
console.log(`Market Regime: ${regime.regime}`);
```

---

### cURL Examples

```bash
# Get ranking
curl "http://localhost:8000/ranking?limit=10&min_score=70"

# Get prediction
curl "http://localhost:8000/api/predict/AAPL"

# Get regime
curl "http://localhost:8000/regime"

# Validate portfolio
curl -X POST "http://localhost:8000/api/portfolio/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "allocations": [
      {"ticker": "AAPL", "allocation_pct": 10},
      {"ticker": "MSFT", "allocation_pct": 8}
    ],
    "total_portfolio_value": 100000
  }'

# Run backtest
curl -X POST "http://localhost:8000/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-01-01",
    "end_date": "2026-01-11",
    "initial_capital": 100000
  }'
```

---

## ✅ Best Practices

### 1. Caching

**Cache frequently accessed data:**
```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_regime(cache_time: int):
    """Cache regime for 5 minutes"""
    return client.get_regime()

# Use current 5-minute window as cache key
regime = get_cached_regime(time.time() // 300)
```

### 2. Batch Requests

**Instead of:**
```python
# ❌ Bad: 10 separate requests
for ticker in tickers:
    prediction = client.get_prediction(ticker)
```

**Do this:**
```python
# ✅ Good: Single ranking request
ranking = client.get_ranking(limit=50)
predictions = {stock['ticker']: stock for stock in ranking}
```

### 3. Error Handling

```python
try:
    ranking = client.get_ranking()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Rate limited
        print("Rate limited. Implement backoff.")
    elif e.response.status_code >= 500:
        # Server error
        print("Server error. Retry later.")
    else:
        # Client error
        print(f"Client error: {e.response.json()}")
except requests.exceptions.Timeout:
    print("Request timeout. Check network.")
```

### 4. WebSocket Reconnection

```javascript
class ReconnectingWebSocket {
  constructor(url) {
    this.url = url;
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('Connected');
      this.reconnectDelay = 1000;
    };

    this.ws.onclose = () => {
      console.log('Disconnected. Reconnecting...');
      setTimeout(() => {
        this.reconnectDelay = Math.min(
          this.reconnectDelay * 2,
          this.maxReconnectDelay
        );
        this.connect();
      }, this.reconnectDelay);
    };
  }
}
```

---

## 📅 Changelog

### Version 1.0 (2026-01-11)

**Added:**
- Initial API documentation
- 45 REST endpoints
- WebSocket support
- Rate limiting (60 req/min)
- Webhook events
- Backtest API
- LLM context endpoints

**Security:**
- API key authentication (coming soon)
- Webhook signature verification
- CORS configuration

---

## 📞 Support

**Issues:** [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

**API Status:** Check `/health` endpoint

**Documentation:** `http://localhost:8000/docs`

---

**Happy Integrating! 🚀**

*Last Updated: 2026-01-11*
