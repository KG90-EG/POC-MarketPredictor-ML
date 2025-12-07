# API Reference

Complete API documentation for the Market Predictor ML backend.

---

## Base URL

```
http://localhost:8000
```

For production deployments, replace with your deployed URL.

---

## Authentication

Currently, the API does not require authentication for local development. For production deployments, implement API key authentication or OAuth2.

---

## Endpoints

### Health Check

Check the health status of the backend service.

**Endpoint:** `GET /health`

**Description:** Returns the operational status of the backend, including model load state and OpenAI configuration.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "openai_configured": true
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `500 Internal Server Error`: Service is unhealthy

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Get Stocks

Retrieve ranked stocks for a specific market.

**Endpoint:** `GET /stocks`

**Query Parameters:**
- `market` (string, required): Market identifier
  - `ftse100` - FTSE 100 Index
  - `sp500` - S&P 500 Index
  - `nasdaq` - NASDAQ Composite

**Response:**
```json
[
  {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "price": 178.23,
    "momentum_score": 0.85,
    "change_percent": 2.34,
    "volume": 52000000,
    "market_cap": 2800000000000
  }
]
```

**Status Codes:**
- `200 OK`: Successfully retrieved stocks
- `400 Bad Request`: Invalid market parameter
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl "http://localhost:8000/stocks?market=nasdaq"
```

**Caching:** Results are cached for 5 minutes by default.

---

### Search Stock

Search for a specific stock by ticker symbol.

**Endpoint:** `POST /search`

**Request Body:**
```json
{
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "price": 178.23,
  "change_percent": 2.34,
  "volume": 52000000,
  "market_cap": 2800000000000,
  "pe_ratio": 28.5,
  "dividend_yield": 0.52,
  "52_week_high": 198.23,
  "52_week_low": 124.17
}
```

**Status Codes:**
- `200 OK`: Stock found
- `404 Not Found`: Stock ticker not found
- `400 Bad Request`: Invalid request body
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

---

### AI Analysis

Get AI-powered stock analysis and recommendations.

**Endpoint:** `POST /analyze`

**Request Body:**
```json
{
  "context": "What are the best tech stocks for long-term growth?",
  "market": "nasdaq"
}
```

**Parameters:**
- `context` (string, required): Question or analysis request
- `market` (string, optional): Market to analyze (ftse100, sp500, nasdaq)

**Response:**
```json
{
  "analysis": "Based on current market conditions and momentum indicators, the following tech stocks show strong potential...",
  "ranked_stocks": [
    {
      "ticker": "AAPL",
      "score": 0.92,
      "reasoning": "Strong momentum with consistent growth and solid fundamentals",
      "confidence": 0.88
    },
    {
      "ticker": "MSFT",
      "score": 0.89,
      "reasoning": "Cloud computing leadership and AI integration driving growth",
      "confidence": 0.85
    }
  ],
  "timestamp": "2025-12-01T21:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Analysis completed
- `400 Bad Request`: Invalid request
- `503 Service Unavailable`: OpenAI API unavailable
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "context": "What are the best tech stocks?",
    "market": "nasdaq"
  }'
```

**Rate Limiting:** Limited to 10 requests per minute per IP.

**Caching:** Results cached for 1 hour based on context hash.

---

### Get Cryptocurrency Rankings

Retrieve ranked cryptocurrencies by market cap.

**Endpoint:** `GET /crypto`

**Query Parameters:**
- `limit` (integer, optional): Number of results (20, 50, 100, 250). Default: 20
- `include_nft` (boolean, optional): Include NFT tokens. Default: false
- `page` (integer, optional): Page number for pagination. Default: 1

**Response:**
```json
{
  "data": [
    {
      "id": "bitcoin",
      "symbol": "BTC",
      "name": "Bitcoin",
      "current_price": 42350.50,
      "market_cap": 828000000000,
      "market_cap_rank": 1,
      "price_change_percentage_24h": 2.45,
      "momentum_score": 0.78,
      "is_nft": false
    }
  ],
  "total": 250,
  "page": 1,
  "limit": 20
}
```

**Status Codes:**
- `200 OK`: Successfully retrieved cryptocurrencies
- `400 Bad Request`: Invalid parameters
- `503 Service Unavailable`: CoinGecko API unavailable
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl "http://localhost:8000/crypto?limit=50&include_nft=false"
```

**Caching:** Results cached for 2 minutes.

---

### WebSocket Connection

Real-time data streaming for live market updates.

**Endpoint:** `WS /ws/{client_id}`

**Path Parameters:**
- `client_id` (string, required): Unique client identifier

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onopen = () => {
  console.log('Connected to market data stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Market update:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from market data stream');
};
```

**Message Format:**
```json
{
  "type": "market_update",
  "market": "nasdaq",
  "timestamp": "2025-12-01T21:30:00Z",
  "data": {
    "ticker": "AAPL",
    "price": 178.45,
    "change_percent": 2.56
  }
}
```

**Message Types:**
- `market_update`: Real-time price update
- `crypto_update`: Cryptocurrency price update
- `system_notification`: System messages
- `error`: Error notifications

---

## Rate Limiting

The API implements rate limiting to ensure fair usage:

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/stocks` | 60 requests | 1 minute |
| `/search` | 30 requests | 1 minute |
| `/analyze` | 10 requests | 1 minute |
| `/crypto` | 60 requests | 1 minute |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1701462000
```

**Rate Limit Response:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 30
}
```

**Status Code:** `429 Too Many Requests`

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "timestamp": "2025-12-01T21:30:00Z",
  "path": "/stocks"
}
```

### Common Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 | Bad Request | Invalid parameters, malformed JSON |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error, check logs |
| 503 | Service Unavailable | External API unavailable |

---

## Data Models

### Stock Object

```typescript
{
  ticker: string;           // Stock symbol (e.g., "AAPL")
  name: string;             // Company name
  price: number;            // Current price
  momentum_score: number;   // 0.0 to 1.0
  change_percent: number;   // 24h change percentage
  volume: number;           // Trading volume
  market_cap: number;       // Market capitalization
}
```

### Cryptocurrency Object

```typescript
{
  id: string;               // CoinGecko ID
  symbol: string;           // Crypto symbol (e.g., "BTC")
  name: string;             // Full name
  current_price: number;    // Current price in USD
  market_cap: number;       // Market capitalization
  market_cap_rank: number;  // Ranking by market cap
  price_change_percentage_24h: number;  // 24h change
  momentum_score: number;   // 0.0 to 1.0
  is_nft: boolean;          // NFT token flag
}
```

### AI Analysis Object

```typescript
{
  analysis: string;         // Detailed analysis text
  ranked_stocks: Array<{
    ticker: string;
    score: number;          // 0.0 to 1.0
    reasoning: string;
    confidence: number;     // 0.0 to 1.0
  }>;
  timestamp: string;        // ISO 8601 format
}
```

---

## SDK Examples

### Python

```python
import requests

class MarketPredictorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_stocks(self, market="nasdaq"):
        response = requests.get(f"{self.base_url}/stocks", params={"market": market})
        response.raise_for_status()
        return response.json()
    
    def search_stock(self, ticker):
        response = requests.post(
            f"{self.base_url}/search",
            json={"ticker": ticker}
        )
        response.raise_for_status()
        return response.json()
    
    def analyze(self, context, market=None):
        payload = {"context": context}
        if market:
            payload["market"] = market
        response = requests.post(f"{self.base_url}/analyze", json=payload)
        response.raise_for_status()
        return response.json()

# Usage
client = MarketPredictorClient()
stocks = client.get_stocks("nasdaq")
analysis = client.analyze("Best tech stocks?", "nasdaq")
```

### JavaScript/TypeScript

```javascript
class MarketPredictorClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async getStocks(market = 'nasdaq') {
    const response = await fetch(`${this.baseUrl}/stocks?market=${market}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  async searchStock(ticker) {
    const response = await fetch(`${this.baseUrl}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }

  async analyze(context, market = null) {
    const payload = { context };
    if (market) payload.market = market;
    
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return response.json();
  }
}

// Usage
const client = new MarketPredictorClient();
const stocks = await client.getStocks('nasdaq');
const analysis = await client.analyze('Best tech stocks?', 'nasdaq');
```

---

## CORS Configuration

The API supports CORS for frontend integration:

**Allowed Origins:**
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev server)
- Production domains (configure in `server.py`)

**Allowed Methods:** GET, POST, OPTIONS

**Allowed Headers:** Content-Type, Authorization

---

## Caching Strategy

| Endpoint | Cache TTL | Cache Key |
|----------|-----------|-----------|
| `/stocks` | 5 minutes | market parameter |
| `/crypto` | 2 minutes | limit + include_nft |
| `/analyze` | 1 hour | context hash |
| `/search` | 10 minutes | ticker symbol |

**Cache Headers:**
```
Cache-Control: public, max-age=300
X-Cache: HIT
```

---

## Best Practices

1. **Use Caching**: Respect cache headers and implement client-side caching
2. **Handle Rate Limits**: Implement exponential backoff for 429 responses
3. **Error Handling**: Always handle errors gracefully with user-friendly messages
4. **WebSocket Reconnection**: Implement automatic reconnection with exponential backoff
5. **Timeouts**: Set appropriate timeouts (30s for API calls, 60s for AI analysis)
6. **Retry Logic**: Retry failed requests with exponential backoff (max 3 attempts)

---

## Support

For API issues or questions:
- **GitHub Issues**: [Report API bugs](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- **Documentation**: [Full wiki](https://github.com/KG90-EG/POC-MarketPredictor-ML/wiki)

**Last Updated**: December 1, 2025
