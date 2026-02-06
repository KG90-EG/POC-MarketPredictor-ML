# Market Predictor Frontend

**Minimal React app for ML-powered asset predictions**

## Quick Start

```bash
npm install
npm run dev
```

Open http://localhost:5173

## Features

- 📈 **Stock Rankings** - Top stocks by ML score
- 🪙 **Crypto Rankings** - Top cryptocurrencies
- 🛢️ **Commodities** - Raw materials
- 🔍 **Search** - Filter by ticker or company name
- 🌙 **Dark Mode** - Toggle theme
- 📊 **Market Regime** - Risk-On/Off indicator

## Architecture

Single-file React app (~350 lines):

```
src/
├── App.jsx      # Complete application
├── main.jsx     # Entry point
└── styles.css   # All styling
```

## API Integration

Uses Vite proxy to backend (port 8000):

| Frontend Path | Backend Path |
|---------------|--------------|
| `/ranking` | `http://localhost:8000/ranking` |
| `/api/*` | `http://localhost:8000/api/*` |
| `/regime` | `http://localhost:8000/regime` |

## Company Name Mapping

70+ tickers have human-readable names:

```javascript
TICKER_NAMES = {
  AAPL: 'Apple Inc.',
  TSLA: 'Tesla',
  'NESN.SW': 'Nestlé',
  BTC: 'Bitcoin',
  // ...
}
```

## Build

```bash
npm run build    # Production build
npm run preview  # Preview production build
```

Output in `dist/` folder.
