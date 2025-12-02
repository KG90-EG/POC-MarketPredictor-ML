# Market Predictor ML - Technical Specification

**Version**: 2.0  
**Last Updated**: December 2, 2024

## Overview

Market Predictor ML is a full-stack machine learning application for stock and cryptocurrency analysis, providing real-time predictions, portfolio management, and watchlist capabilities with integrated AI insights.

---

## Core Features

### 1. Stock Analysis & Predictions

**Backend API**: `/predict/{ticker}`, `/ticker_info/{ticker}`, `/search_stocks`

- Machine Learning predictions using Random Forest classifier
- Technical indicators: RSI, MACD, Bollinger Bands, Momentum Score
- Real-time stock data via yfinance API
- **Enhanced Stock Search**: Dynamic ticker lookup with yfinance fallback for stocks not in popular list
  - Searches popular stocks first (100+ companies)
  - Falls back to live yfinance lookup if not found
  - Auto-tries common suffixes (.SW, .DE, .L, .PA) for European stocks
  - Supports Swiss (e.g., HOLN.SW), German, UK, and French exchanges
- Confidence scores and probability distributions
- 52-week high/low tracking

**Frontend**:

- Interactive stock search with autocomplete
- Real-time price updates
- Visual prediction confidence indicators
- BUY/SELL/HOLD recommendations based on ML confidence

### 2. Cryptocurrency Rankings

**Backend API**: `/crypto/ranking`, `/crypto/details/{crypto_id}`, `/crypto/search`

- CoinGecko API integration for crypto data
- Momentum-based scoring algorithm
- Support for 200+ cryptocurrencies
- NFT tokens included by default
- Market cap, volume, and 24h price change tracking
- **Fixed**: Proper nested market_data parsing for watchlist crypto display

**Frontend**:

- Dynamic crypto rankings table
- Sortable columns (rank, name, price, change %, market cap)
- **Simplified UI**: Removed "Show Top" dropdown (use pagination instead)
- Pagination with 20 cryptos per page
- Subtle refresh button (minimalist design)
- No NFT toggle (always enabled)

### 3. Watchlists/Portfolios (Phase 1)

**Backend API**:

- `GET /watchlists` - Get all user watchlists
- `POST /watchlists` - Create new watchlist
- `GET /watchlists/{id}` - Get watchlist details
- `PUT /watchlists/{id}` - Update watchlist
- `DELETE /watchlists/{id}` - Delete watchlist
- `POST /watchlists/{id}/stocks` - Add stock or crypto to watchlist
- `DELETE /watchlists/{id}/stocks/{ticker}` - Remove from watchlist

**Database Schema**:

```sql
CREATE TABLE watchlists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE watchlist_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  watchlist_id INTEGER NOT NULL,
  ticker TEXT NOT NULL,
  asset_type TEXT DEFAULT 'stock',  -- 'stock' or 'crypto'
  added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
  UNIQUE(watchlist_id, ticker)
);
```

**Features**:

- **Mixed Asset Support**: Single watchlist can contain both stocks and cryptocurrencies
- **Fixed Crypto Data Display**: Properly parses CoinGecko API nested structure (`market_data.current_price.usd`)
- **Client-Side Momentum Calculation**: Computes momentum score for crypto assets based on:
  - Market cap rank (top 10/50 weighted)
  - 24h, 7d, 30d price changes
  - Displays accurate price, change %, and volume
- **Smart Ticker Validation**: Auto-corrects common mistakes (e.g., APPLE → AAPL)
- **Live Data Fetching**: Real-time prices, predictions, and confidence scores
- **Asset Type Toggle**: Switch between stock and crypto search modes
- **Dynamic Dropdowns**:
  - Stock search: `/popular_stocks` + yfinance fallback (50+ companies)
  - Crypto search: `/popular_cryptos` (30+ cryptocurrencies)
- **Investment Insights**:
  - Current price and 24h change percentage
  - BUY/SELL/HOLD recommendation with confidence
  - Momentum score
  - Distance from 52-week high (stocks only)

**Frontend Components**:

- `WatchlistManager.jsx`: Main component with CRUD operations
- Asset type toggle buttons (📈 Stocks / ₿ Crypto)
- Searchable dropdown with live API filtering
- Responsive grid layout for watchlist items

### 4. Market/Country Selector

**Backend API**: `GET /countries`

Returns:

```json
{
  "countries": [
    {
      "id": "Global",
      "label": "🌐 Global",
      "description": "Top global stocks",
      "flag": "🌐"
    },
    {
      "id": "Switzerland",
      "label": "🇨🇭 Switzerland",
      "description": "Swiss companies",
      "flag": "🇨🇭"
    }
    // ... more countries
  ]
}
```

**Features**:

- **Dynamic Market List**: Backend-driven country configuration
- **Visual Card Design**: Nice boxes with hover effects
- **Flag Emojis**: Clear visual identification
- **Responsive Grid**: Auto-adjusting layout for mobile
- **Single Selection Mode**: Only one market active at a time

**Frontend**:

- `MarketSelector.jsx` component with CSS module
- Grid layout with 180px minimum card width
- Hover animations and shadow effects
- Selected state with green gradient background

### 5. AI-Powered Analysis

**Backend API**: `/analyze`

- OpenAI GPT-4 integration for company insights
- Context-aware recommendations based on portfolio
- Customizable analysis prompts

**Frontend**:

- AI analysis modal with streaming responses
- Company-specific insights on demand

---

## Technical Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **ML Model**: Random Forest Classifier (scikit-learn)
- **Database**: SQLite with WAL mode
- **Data Sources**:
  - yfinance (stock data)
  - CoinGecko API (crypto data)
  - OpenAI API (AI analysis)
- **Caching**: In-memory cache with TTL
- **Monitoring**: Prometheus metrics, health checks

### Frontend

- **Framework**: React 18 with Vite
- **Styling**: CSS modules with responsive design
- **HTTP Client**: Axios
- **State Management**: React hooks (useState, useEffect)

### Deployment

- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose
- **Web Server**: Gunicorn with Uvicorn workers
- **Storage**: Persistent volumes for data and models

---

## API Endpoints

### Stock Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/predict/{ticker}` | Get ML prediction for stock |
| GET | `/ticker_info/{ticker}` | Get comprehensive stock info |
| POST | `/ticker_info_batch` | Batch ticker info fetch |
| GET | `/ranking` | Get ranked stock predictions |
| GET | `/popular_stocks` | Get popular stocks list |
| GET | `/search_stocks` | Search stocks by query |
| GET | `/countries` | Get available market countries |

### Crypto Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/crypto/ranking` | Get crypto rankings |
| GET | `/crypto/details/{id}` | Get crypto details |
| GET | `/crypto/search` | Search cryptocurrencies |
| GET | `/popular_cryptos` | Get popular crypto list |
| GET | `/search_cryptos` | Search cryptos by query |

### Watchlist Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/watchlists` | List user watchlists |
| POST | `/watchlists` | Create watchlist |
| GET | `/watchlists/{id}` | Get watchlist details |
| PUT | `/watchlists/{id}` | Update watchlist |
| DELETE | `/watchlists/{id}` | Delete watchlist |
| POST | `/watchlists/{id}/stocks` | Add asset to watchlist |
| DELETE | `/watchlists/{id}/stocks/{ticker}` | Remove from watchlist |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check status |
| GET | `/metrics` | Prometheus metrics |
| WS | `/ws` | WebSocket connection |

---

## Data Models

### Stock Prediction Response

```json
{
  "ticker": "AAPL",
  "prediction": 1,
  "probability": 0.75,
  "confidence": "High",
  "indicators": {
    "rsi": 65.2,
    "macd": 1.5,
    "momentum_score": 0.8
  }
}
```

### Watchlist Item

```json
{
  "id": 1,
  "watchlist_id": 1,
  "ticker": "AAPL",
  "asset_type": "stock",
  "notes": "Apple Inc.",
  "added_at": "2024-12-02T10:00:00Z"
}
```

### Market/Country

```json
{
  "id": "Switzerland",
  "label": "🇨🇭 Switzerland",
  "description": "Swiss companies",
  "flag": "🇨🇭"
}
```

---

## Machine Learning Model

### Training Pipeline

- **Script**: `training/trainer.py`
- **Features**: Technical indicators (20+ features)
- **Algorithm**: Random Forest with 100 estimators
- **Validation**: Accuracy threshold > 0.55 for auto-promotion
- **Retraining**: Scheduled or on-demand via `train_watchlist.py`

### Feature Engineering

- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume analysis
- Price momentum
- 52-week high/low distance

---

## UX Improvements (Version 2.0)

### Watchlists

✅ Mixed asset support (stocks + crypto in one list)  
✅ Live price and prediction updates  
✅ Asset type toggle with visual indicators  
✅ Smart ticker validation and auto-correction  

### Market Selector

✅ Dynamic country list from backend  
✅ Visual card design with hover effects  
✅ Responsive grid layout  
✅ Flag emojis for quick identification  

### Crypto Section

✅ Subtle refresh button (minimalist design)  
✅ NFT tokens always included  
✅ Removed unnecessary toggle  
✅ Improved empty state messaging  

---

## Security & Performance

- **Rate Limiting**: Implemented via rate_limiter.py
- **Caching**: TTL-based cache for expensive API calls
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error messages and logging
- **CORS**: Configured for frontend origin

---

## Future Enhancements

- [ ] Phase 2: Price Alerts with WebSocket notifications
- [ ] Phase 3: Portfolio Analytics with performance tracking
- [ ] Multi-user authentication with JWT
- [ ] Historical prediction accuracy tracking
- [ ] Advanced charting with TradingView integration
- [ ] Mobile app (React Native)

---

## Development

### Setup

```bash
# Backend
pip install -r requirements.txt
python -m market_predictor.server

# Frontend
cd frontend
npm install
npm run dev
```

### Testing

```bash
# Backend tests
pytest

# Frontend tests
npm test
```

### Training Model

```bash
python training/trainer.py
# or for watchlist-based training
python scripts/train_watchlist.py
```

---

## Documentation

- **API Docs**: <http://localhost:8080/docs> (Swagger UI)
- **Training Guide**: `docs/TRAINING_GUIDE.md`
- **Phase 1 Summary**: `docs/features/PHASE1_WATCHLISTS_SUMMARY.md`
- **Deployment**: `DEPLOYMENT.md`
- **README**: `README.md`

---

## Support

For issues, feature requests, or contributions, please use the GitHub repository issue tracker.

**Repository**: KG90-EG/POC-MarketPredictor-ML
