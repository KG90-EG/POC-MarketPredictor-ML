# Buy/Sell Trading Opportunities

**Version**: 2.0.0  
**Date**: December 2, 2025  
**Status**: ✅ Production Ready

---

## Overview

The Buy/Sell Trading Opportunities feature provides curated lists of top trading opportunities based on ML predictions and momentum analysis. It helps users quickly identify the best stocks and cryptocurrencies to buy or sell.

## Features

### 📊 Opportunity Lists

- **Stock Buy Opportunities**: Top 6 stocks with BUY signals
- **Stock Sell Opportunities**: Top 6 stocks with SELL signals
- **Crypto Buy Opportunities**: Top 6 cryptocurrencies with positive momentum
- **Crypto Sell Opportunities**: Top 6 cryptocurrencies with negative momentum

### 🎯 Selection Criteria

**Stocks**:

- Analyzes top 30 stocks by probability
- Gets ML predictions for each
- Filters for BUY (probability ≥ 40%) or SELL (probability ≤ 35%)
- Sorts by confidence score
- Shows top 6 of each

**Crypto**:

- Analyzes top 30 cryptocurrencies
- Calculates momentum score (24h/7d/30d weighted)
- Filters for BUY (momentum > -2) or SELL (momentum < -2)
- Sorts by confidence
- Shows top 6 of each

---

## UI Components

### Tabs

- **Stocks** - Stock buy/sell opportunities
- **Crypto** - Cryptocurrency buy/sell opportunities

### Opportunity Cards

Each card displays:

- **Symbol & Name** (e.g., AAPL - Apple Inc.)
- **Signal Badge** 🟢 BUY or 🔴 SELL
- **Confidence Score** (0-100%)
- **ML Probability** (stocks only, 0-100%)
- **Current Price** ($XXX.XX or N/A)
- **Reasoning** - Why this signal was generated
- **Action Links**:
  - View Chart (Yahoo Finance / CoinGecko)
  - Market Info (Google Finance / CoinMarketCap)

### AI Analysis Section

- **Optional Context Input** - Provide additional context (risk tolerance, timeframe, etc.)
- **Analyze Button** - Generate AI-powered analysis using OpenAI
- **Analysis Results** - Comprehensive trading recommendations

---

## Prediction Logic

### Stock Predictions

**ML Model**: Random Forest Classifier (75%+ accuracy)

**Features**:

- SMA50, SMA200 (Moving averages)
- RSI (Relative Strength Index)
- Volatility (30-day rolling std)
- Momentum_10d (10-day momentum)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands (upper, lower)

**Signal Thresholds** (Ultra-Aggressive):

```python
if prob >= 0.60:
    signal = "BUY"
    confidence = prob * 100
    reasoning = "Strong bullish signal"
elif prob >= 0.40:
    signal = "BUY"
    confidence = prob * 100
    reasoning = "Moderate bullish signal"
elif prob <= 0.20:
    signal = "SELL"
    confidence = (1 - prob) * 100
    reasoning = "Strong bearish signal"
elif prob <= 0.35:
    signal = "SELL"
    confidence = (1 - prob) * 100
    reasoning = "Weak bearish signal"
else:
    signal = "HOLD"
    confidence = 50 + abs(prob - 0.5) * 20
    reasoning = "Neutral"
```

### Crypto Predictions

**Momentum Score**: Weighted average of price changes

```python
momentum = (
    price_change_24h * 0.5 +
    price_change_7d * 0.3 +
    price_change_30d * 0.2
)
```

**Signal Thresholds**:

```python
if momentum > 5 or price_change_24h > 2:
    signal = "BUY"
    confidence = min(95, 70 + momentum)
    reasoning = "Strong positive momentum"
elif momentum > 0 or price_change_24h > 0:
    signal = "BUY"
    confidence = 60 + momentum * 2
    reasoning = "Moderate positive momentum"
elif momentum > -2 and price_change_24h > -1:
    signal = "BUY"
    confidence = 50 + momentum
    reasoning = "Mild positive momentum"
elif momentum < -5 or price_change_24h < -3:
    signal = "SELL"
    confidence = min(80, 60 + abs(momentum))
    reasoning = "Negative momentum"
else:
    signal = "HOLD"
    confidence = 50 + abs(momentum) / 2
    reasoning = "Neutral trend"
```

---

## API Integration

### Backend Endpoints

**Stock Opportunities**:

```
GET /ranking?country=Global         # Get top stocks
GET /watchlist/prediction/{ticker}?asset_type=stock  # Get prediction
```

**Crypto Opportunities**:

```
GET /crypto/ranking?limit=50        # Get top cryptos
GET /watchlist/prediction/{crypto_id}?asset_type=crypto  # Get prediction
```

**AI Analysis**:

```
POST /analyze_opportunities
Body: {
  "opportunities": [...],  # List of opportunities
  "user_context": "..."    # Optional context
}
```

### Response Format

**Prediction Response**:

```json
{
  "signal": "BUY",
  "confidence": 82.5,
  "reasoning": "Strong bullish signal from ML model (prob: 0.65)",
  "metrics": {
    "probability": 0.652,
    "rsi": 45.3,
    "momentum": 0.0234
  }
}
```

---

## Frontend Implementation

### Data Flow

1. **Load Opportunities** (on mount + every 5 minutes)

   ```jsx
   useEffect(() => {
     loadOpportunities();
     const interval = setInterval(loadOpportunities, 5 * 60 * 1000);
     return () => clearInterval(interval);
   }, []);
   ```

2. **Fetch Stock Rankings**

   ```jsx
   const stockResponse = await apiClient.get('/ranking?country=Global');
   const stocks = stockResponse.data.ranking || [];
   ```

3. **Get Predictions** (parallel)

   ```jsx
   const stockPredictions = await Promise.all(
     stocks.slice(0, 30).map(async (stock) => {
       const predRes = await apiClient.get(
         `/watchlist/prediction/${stock.ticker}?asset_type=stock`
       );
       return { ...stock, prediction: predRes.data };
     })
   );
   ```

4. **Filter & Sort**

   ```jsx
   const buyStocks = stockPredictions
     .filter(s => s.prediction.signal === 'BUY')
     .sort((a, b) => b.prediction.confidence - a.prediction.confidence)
     .slice(0, 6);
   ```

5. **Render Cards**

   ```jsx
   {buyStocks.map(stock => (
     <div className="opportunity-card">
       <div className="signal-badge buy">🟢 BUY</div>
       <div className="confidence-score">{stock.prediction.confidence}%</div>
       {/* More card content */}
     </div>
   ))}
   ```

### State Management

```jsx
const [stockBuyOpportunities, setStockBuyOpportunities] = useState([]);
const [stockSellOpportunities, setStockSellOpportunities] = useState([]);
const [cryptoBuyOpportunities, setCryptoBuyOpportunities] = useState([]);
const [cryptoSellOpportunities, setCryptoSellOpportunities] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
const [activeTab, setActiveTab] = useState('stocks');
const [userContext, setUserContext] = useState('');
const [analyzing, setAnalyzing] = useState(false);
const [analysis, setAnalysis] = useState(null);
```

---

## AI Analysis Feature

### How It Works

1. User provides optional context (risk tolerance, investment timeframe, etc.)
2. System sends top opportunities + context to OpenAI
3. AI generates comprehensive analysis with recommendations
4. Analysis displayed in formatted card

### Prompt Template

```
You are a financial advisor. Analyze these trading opportunities and provide recommendations.

Opportunities:
[List of stocks/cryptos with signals, confidence, reasoning]

User Context:
[User's provided context]

Provide:
1. Top 3 recommendations
2. Risk assessment
3. Suggested entry/exit points
4. Overall market sentiment
```

### OpenAI Configuration

```python
response = OPENAI_CLIENT.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=500,
    temperature=0.7
)
```

---

## Configuration

### Opportunity Limits

```jsx
// In BuyOpportunities.jsx
.slice(0, 6)  // Show max 6 opportunities per section
```

To adjust:

```jsx
const MAX_OPPORTUNITIES = 10;  // Change to desired number
.slice(0, MAX_OPPORTUNITIES)
```

### Prediction Thresholds

**Stock Thresholds** (`market_predictor/server.py`):

```python
BUY_THRESHOLD = 0.40   # 40% probability
SELL_THRESHOLD = 0.35  # 35% probability
```

**Crypto Thresholds**:

```python
BUY_MOMENTUM_THRESHOLD = -2   # Momentum > -2
SELL_MOMENTUM_THRESHOLD = -5  # Momentum < -5
```

### Analysis Sample Size

```jsx
// Number of stocks/cryptos to analyze for opportunities
stocks.slice(0, 30)  // Analyze top 30 stocks
cryptos.slice(0, 30)  // Analyze top 30 cryptos
```

### Auto-Refresh Interval

```jsx
const interval = setInterval(loadOpportunities, 5 * 60 * 1000); // 5 minutes
```

---

## Performance Optimization

### Parallel Predictions

Predictions are fetched in parallel using `Promise.all`:

```jsx
const stockPredictions = await Promise.all(
  stocks.slice(0, 30).map(async (stock) => {
    // Fetch prediction
  })
);
```

**Benefits**:

- 30 stocks: ~2-3 seconds (parallel) vs ~30 seconds (sequential)
- 30 cryptos: ~2-3 seconds (parallel) vs ~30 seconds (sequential)

### Caching

Backend uses Redis caching:

```python
@cache.cached(timeout=300, key_prefix="prediction")  # 5 minutes
def get_watchlist_prediction(ticker, asset_type):
    # ...
```

### Error Handling

Failed predictions don't block others:

```jsx
const stockPredictions = await Promise.all(
  stocks.map(async (stock) => {
    try {
      const predRes = await apiClient.get(...);
      return { ...stock, prediction: predRes.data };
    } catch (err) {
      console.error(`Failed for ${stock.ticker}:`, err);
      return {
        ...stock,
        prediction: { signal: 'HOLD', confidence: 50, reasoning: 'Unavailable' }
      };
    }
  })
);
```

---

## Chart & Market Info Links

### Stock Links

**Yahoo Finance Chart**:

```
https://finance.yahoo.com/quote/{ticker}/chart
```

**Google Finance**:

```
https://www.google.com/finance/quote/{ticker}:NASDAQ
```

### Crypto Links

**CoinGecko Chart**:

```
https://www.coingecko.com/en/coins/{crypto_id}
```

**CoinMarketCap**:

```
https://coinmarketcap.com/currencies/{crypto_id}
```

---

## Styling

### CSS Classes

```css
.opportunity-card          /* Main card container */
.opportunity-symbol        /* Symbol (ticker/name) */
.signal-badge             /* BUY/SELL badge */
  .buy                    /* Green BUY badge */
  .sell                   /* Red SELL badge */
.confidence-score         /* Confidence percentage */
.opportunity-details      /* Price, probability */
.opportunity-reasoning    /* Signal reasoning */
.opportunity-actions      /* Chart/market links */
```

### Responsive Design

```css
@media (max-width: 1200px) {
  .opportunities-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 columns on tablets */
  }
}

@media (max-width: 768px) {
  .opportunities-grid {
    grid-template-columns: 1fr; /* 1 column on mobile */
  }
}
```

---

## Testing

### Manual Testing Checklist

- [ ] Load page → See loading state
- [ ] Wait → See opportunities (Buy & Sell sections)
- [ ] Switch tabs → See Stock and Crypto opportunities
- [ ] Click chart link → Opens Yahoo Finance/CoinGecko
- [ ] Click market info → Opens Google Finance/CoinMarketCap
- [ ] Enter AI context → Click Analyze → See analysis
- [ ] Refresh button → Reloads opportunities
- [ ] Wait 5 minutes → Auto-refreshes

### Edge Cases

- [ ] No buy opportunities (all HOLD/SELL)
- [ ] No sell opportunities (all BUY/HOLD)
- [ ] API errors (graceful fallback)
- [ ] Missing prices (shows "N/A")
- [ ] OpenAI API failure (show error message)

### Unit Tests (To Be Created)

```jsx
// test/components/BuyOpportunities.test.jsx
describe('BuyOpportunities', () => {
  it('renders loading state', () => {
    // Test loading spinner
  });

  it('renders stock opportunities', () => {
    // Test stock cards display
  });

  it('renders crypto opportunities', () => {
    // Test crypto cards display
  });

  it('switches tabs', () => {
    // Test tab switching
  });

  it('analyzes opportunities', () => {
    // Test AI analysis
  });
});
```

---

## Known Limitations

1. **Static Limit**: Only top 6 opportunities shown (by design)
2. **No Pagination**: Can't view more than 6 without changing code
3. **Auto-Refresh Only**: No manual trigger for individual items
4. **No Sorting Options**: Always sorted by confidence
5. **No Filtering**: Can't filter by sector, market cap, etc.

---

## Future Enhancements

### Phase 2 (Q1 2026)

- [ ] **Customizable Limits**: User-adjustable number of opportunities
- [ ] **Sorting Options**: Sort by price, confidence, momentum
- [ ] **Filtering**: By sector, market cap, country
- [ ] **Favorites**: Pin specific opportunities
- [ ] **Comparison Tool**: Side-by-side comparison
- [ ] **Export**: CSV/PDF export of opportunities

### Phase 3 (Q2 2026)

- [ ] **Historical Performance**: Track accuracy of past signals
- [ ] **Alerts Integration**: Alert when new opportunities appear
- [ ] **Portfolio Integration**: Link to watchlists
- [ ] **Backtesting**: Simulate strategy performance
- [ ] **Social Sharing**: Share opportunities with others
- [ ] **News Integration**: Show relevant news for each opportunity

---

## Troubleshooting

### No Opportunities Appearing

**Cause**: Too strict thresholds or no stocks meet criteria

**Solutions**:

1. Check threshold values (40% BUY, 35% SELL)
2. Verify ML model is loaded
3. Check if stocks have recent data
4. Review server logs for errors

### Wrong Price Display

**Issue**: Shows "$N/A" instead of "N/A"

**Fix**: Ensure template literal syntax is correct:

```jsx
// Correct
{stock.current_price != null ? `$${stock.current_price.toFixed(2)}` : 'N/A'}

// Wrong (produces "$N/A")
${stock.current_price ? stock.current_price.toFixed(2) : 'N/A'}
```

### Slow Loading

**Causes**:

- Fetching predictions for many stocks/cryptos
- No caching
- Slow API responses

**Solutions**:

1. Reduce analysis sample size (30 → 20 stocks)
2. Increase cache TTL (5 min → 10 min)
3. Implement server-side batching
4. Add loading progress indicator

---

## Support

**Documentation**:

- [API Documentation](http://localhost:8000/docs)
- [BACKLOG.md](../BACKLOG.md)
- [ALERTS.md](./ALERTS.md)

**Issues**:

- [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

---

**Last Updated**: December 2, 2025  
**Version**: 2.0.0  
**Author**: Kevin Garcia (@KG90-EG)
