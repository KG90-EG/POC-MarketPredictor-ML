# Using the Application - Complete User Guide

A comprehensive guide to using POC-MarketPredictor-ML effectively.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Market Selection](#market-selection)
4. [Viewing Stock Rankings](#viewing-stock-rankings)
5. [Understanding Company Details](#understanding-company-details)
6. [Searching for Stocks](#searching-for-stocks)
7. [AI-Powered Analysis](#ai-powered-analysis)
8. [Customizing Your Experience](#customizing-your-experience)
9. [Monitoring System Health](#monitoring-system-health)
10. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

### Accessing the Application

After installation (see [Quick Start Guide](Quick-Start-Guide.md)):

1. **Start Backend**: `uvicorn trading_fun.server:app --reload`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Open Browser**: Navigate to `http://localhost:5173`

### First Time Experience

When you first open the application:
- Default market view is **Global** (US large-caps)
- Rankings load automatically (top 30 stocks)
- Data fetches in ~4 seconds (with cache) or ~30 seconds (first time)
- Progress indicators show loading status

---

## Interface Overview

### Header Section

```
┌─────────────────────────────────────────────────────────┐
│  📊 POC-MarketPredictor-ML     [☀️]  [❤️]  [?]  [↻]  │
└─────────────────────────────────────────────────────────┘
```

**Components**:
- **Title**: Application name
- **Theme Toggle** (☀️/🌙): Switch between light and dark mode
- **Health Status** (❤️): System health indicator
  - 🟢 Green: All systems operational
  - 🟡 Yellow: Some services degraded
  - 🔴 Red: Critical issues
  - ⚪ Gray: Checking...
- **Help** (?): Opens help modal with usage instructions
- **Refresh** (↻): Reload current rankings

### Market View Selector

```
┌─────────────────────────────────────────────────────────┐
│  [🌐 Global] [🇺🇸 United States] [🇨🇭 Switzerland]     │
│  [🇩🇪 Germany] [🇬🇧 UK] [🇫🇷 France] [🇯🇵 Japan] [🇨🇦 CA] │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Click to toggle market selection
- Multiple markets can be selected simultaneously
- Checkmark (✓) shows selected markets
- Disabled during loading

### Rankings Table

```
┌──────────────────────────────────────────────────────────────────┐
│ Rank  Ticker  Company        Country  Signal     Prob  Price ... │
├──────────────────────────────────────────────────────────────────┤
│  1    AAPL    Apple Inc.     🇺🇸 US   🟢 BUY     72%   $278.45   │
│  2    MSFT    Microsoft       🇺🇸 US   🟢 BUY     68%   $425.30   │
│  ...                                                              │
└──────────────────────────────────────────────────────────────────┘
```

**Columns**:
- **Rank**: Position (1-30)
- **Ticker**: Stock symbol (clickable)
- **Company**: Full company name
- **Country**: Country of domicile with flag
- **Signal**: Trading recommendation with color
- **Probability**: ML confidence percentage
- **Price**: Current stock price
- **Change %**: Daily price change
- **Volume**: Trading volume
- **Market Cap**: Company valuation

### Pagination

```
┌────────────────────────────────────────────┐
│  [← Previous]  Page 1 of 3  [Next →]      │
│  Showing 1-10 of 30 stocks                │
└────────────────────────────────────────────┘
```

**Features**:
- 10 stocks per page
- Previous/Next buttons
- Page dropdown selector
- Item count display
- Auto-hides if only one page

### Search Section

```
┌────────────────────────────────────────────┐
│  Search Individual Stocks                  │
│  ┌──────────────────────┬─────────┬──────┐ │
│  │ Enter ticker (AAPL) │ [Search]│ [Clear]│
│  └──────────────────────┴─────────┴──────┘ │
└────────────────────────────────────────────┘
```

---

## Market Selection

### Single Market Selection

**How to**:
1. Click a market button (e.g., 🇨🇭 Switzerland)
2. Wait for rankings to load (4-30 seconds)
3. View top 30 stocks from that market

**Example**: Switzerland
- Loads Swiss companies (Nestle, Novartis, Roche, etc.)
- Sorted by market capitalization
- Ranked by ML probability

### Multiple Market Selection

**How to**:
1. Click multiple market buttons
2. Selected markets show checkmark (✓)
3. System merges and deduplicates stocks
4. Ranks combined list by probability

**Example**: Switzerland + Germany
- Loads Swiss and German companies
- Combines into single list
- Removes duplicates
- Ranks by ML score

**Benefits**:
- Build diversified portfolios
- Compare across markets
- Identify best opportunities globally

### Market Characteristics

**🌐 Global (US Large-Caps)**:
- Focus: Technology companies
- Count: Top 50
- Examples: Apple, Microsoft, Nvidia, Tesla
- Best for: Growth investors

**🇺🇸 United States**:
- Focus: All sectors
- Count: Top 30
- Examples: Broad market leaders
- Best for: Diversification

**🇨🇭 Switzerland**:
- Focus: Healthcare, Finance
- Count: Top 30
- Examples: Nestle, Novartis, Roche, UBS
- Best for: Stability, dividends

**🇩🇪 Germany**:
- Focus: Industrials, Automotive
- Count: Top 20
- Examples: SAP, Siemens, BMW, Volkswagen
- Best for: Industrial exposure

**🇬🇧 United Kingdom**:
- Focus: Energy, Finance
- Count: Top 20
- Examples: Shell, AstraZeneca, HSBC, BP
- Best for: Energy exposure

**🇫🇷 France**:
- Focus: Luxury, Energy
- Count: Top 20
- Examples: LVMH, L'Oreal, TotalEnergies, Airbus
- Best for: Luxury goods, aerospace

**🇯🇵 Japan**:
- Focus: Automotive, Technology
- Count: Top 20
- Examples: Toyota, Sony, Nintendo, SoftBank
- Best for: Asia exposure

**🇨🇦 Canada**:
- Focus: Tech, Finance
- Count: Top 20
- Examples: Shopify, Royal Bank, Enbridge
- Best for: North America diversification

---

## Viewing Stock Rankings

### Understanding the Ranking Table

Each row shows comprehensive stock information:

**Rank Column**:
- Position in ranked list
- Top 3 get special badges:
  - 🥇 Gold (#1)
  - 🥈 Silver (#2)
  - 🥉 Bronze (#3)

**Ticker Column**:
- Stock symbol (e.g., AAPL)
- Clickable to view details
- Links to company detail sidebar

**Company Column**:
- Full legal name
- Truncated if too long
- Full name in detail view

**Country Column**:
- Flag emoji + country code
- Filterable dropdown
- Shows country of domicile

**Signal Column**:
- Color-coded badge
- 🟢 Green: BUY signals
- 🟡 Yellow: HOLD
- 🟠 Orange: CONSIDER SELLING
- 🔴 Red: SELL
- Clear visual indicator

**Probability Column**:
- Percentage (0-100%)
- Higher = more confident
- Based on ML model output

**Price Column**:
- Current stock price
- Currency matches market
- Updates on refresh

**Change % Column**:
- Daily price change
- Color-coded:
  - 🟢 Green: Positive
  - 🔴 Red: Negative
  - ⚪ Gray: Unchanged

**Volume Column**:
- Trading volume
- Formatted (K, M, B)
- Indicates liquidity

**Market Cap Column**:
- Company valuation
- Formatted (M, B, T)
- Indicates company size

### Sorting and Filtering

**Current Sorting**:
- Ranked by ML probability (highest first)
- Top-ranked stocks appear first
- Consistent across pages

**Country Filter** (Dropdown):
- Shows countries present in current data
- Select to filter by country
- "All Countries" shows everything

**Future Enhancements** (see [BACKLOG.md](../../BACKLOG.md)):
- Sort by any column
- Filter by market cap range
- Filter by sector
- Custom sorting preferences

---

## Understanding Company Details

### Opening the Detail Sidebar

**How to**:
- Click any row in the rankings table
- Stock row highlights
- Detail sidebar slides in from right
- Overlay dims background

### Sidebar Sections

**1. Trading Signal Badge**
```
┌─────────────────────────────┐
│   🟢 STRONG BUY (72%)       │
└─────────────────────────────┘
```
- Large, prominent display
- Color-coded
- Shows probability

**2. Company Header**
```
Company: Apple Inc.
Country: 🇺🇸 United States
```
- Full company name
- Country with flag

**3. Price Information Grid**
```
┌─────────────┬──────────────┐
│ Current     │ $278.45      │
│ Change      │ +$2.30 (+1.8%)│
│ 52W High    │ $299.50      │
│ 52W Low     │ $164.08      │
└─────────────┴──────────────┘
```
- Current price
- Daily change ($ and %)
- 52-week range

**4. Market Data Grid**
```
┌─────────────┬──────────────┐
│ Market Cap  │ $4.32T       │
│ Volume      │ 45.8M        │
│ P/E Ratio   │ 28.5         │
└─────────────┴──────────────┘
```
- Market capitalization
- Trading volume
- Price-to-earnings ratio

**5. ML Probability**
```
ML Probability: 72%
```
- Raw probability score
- Basis for signal

**6. Recommendation Text**
```
Based on technical indicators, this stock shows
strong bullish momentum. Consider for portfolio
addition or position increase.
```
- Detailed recommendation
- Explains signal reasoning
- Actionable guidance

### Closing the Sidebar

**How to**:
- Click outside the sidebar (on overlay)
- Click "X" button (if present)
- Press Escape key (future feature)

---

## Searching for Stocks

### Using the Search Function

**Step-by-step**:
1. Locate search section below rankings
2. Enter ticker symbol (e.g., "AAPL", "TSLA")
3. Click "Search" button or press Enter
4. Wait for results (1-3 seconds)
5. View results in table format

### Search Results

**Result Table** (similar to rankings):
- Shows single stock
- All information displayed
- Clickable for details
- Same columns as rankings table

**What You Get**:
- Current price and market data
- ML probability
- Trading signal
- Company information
- Country domicile

### Search Tips

**Valid Tickers**:
- US stocks: AAPL, MSFT, GOOGL, TSLA
- Swiss stocks: NESN.SW, NOVN.SW, ROG.SW
- German stocks: SAP.DE, SIE.DE, BMW.DE
- UK stocks: SHEL.L, AZN.L, HSBA.L
- French stocks: MC.PA, OR.PA, FP.PA
- Japanese stocks: 7203.T, 6758.T, 7974.T
- Canadian stocks: SHOP.TO, RY.TO, ENB.TO

**Common Mistakes**:
- ❌ Company name (use ticker symbol)
- ❌ Incorrect ticker format
- ❌ Delisted stocks
- ❌ Stocks without data

**If Search Fails**:
- Check ticker format
- Try adding country suffix (.SW, .DE, .L, etc.)
- Verify stock is publicly traded
- Check for typos

### Clearing Search Results

**How to**:
- Click "Clear" button
- Results disappear
- Can search again

---

## AI-Powered Analysis

### Prerequisites

**Required**:
- OpenAI API key
- Set in environment variable or `.env` file

**Setup**:
```bash
# .env file
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### Requesting AI Analysis

**How to**:
1. Load stock rankings (any market)
2. Click "Get AI Recommendations" button
3. Wait for analysis (5-15 seconds)
4. View detailed recommendations

### Analysis Content

**What You Get**:

**1. TOP 3 BUY RECOMMENDATIONS**
```
1. AAPL - Strong buy at $278
   Reasoning: Excellent momentum, strong fundamentals,
   positive technical setup. Industry leader with
   consistent growth.

2. MSFT - Attractive entry point
   Reasoning: Cloud growth driving revenue, AI
   positioning strong, solid dividend history.

3. NVDA - High growth potential
   Reasoning: AI chip demand surging, market leader,
   exceptional margins and growth.
```

**2. SELL/AVOID**
```
Stocks to consider selling or avoiding:
- XYZ: Weak fundamentals, declining margins
- ABC: Negative momentum, industry headwinds
```

**3. KEY RISKS**
```
Key risks to monitor:
- Interest rate changes
- Economic slowdown concerns
- Sector-specific challenges
```

**4. ACTION PLAN**
```
Recommended actions:
1. Allocate 30% to top 3 STRONG BUY stocks
2. Exit positions with SELL signals
3. Monitor HOLD positions for signal changes
4. Diversify across sectors
```

### AI Analysis Tips

**Best Practices**:
- ✅ Request for full rankings (10-30 stocks)
- ✅ Provide context in user input (if feature available)
- ✅ Review regularly (weekly/monthly)
- ✅ Combine with your own research

**Limitations**:
- Based on current data snapshot
- General advice, not personalized
- Doesn't know your risk tolerance
- Should be one input among many

**Cost Considerations**:
- Costs ~$0.01-0.05 per request
- Cached for 5 minutes
- Monitor OpenAI usage

---

## Customizing Your Experience

### Theme Toggle

**Dark Mode / Light Mode**:

**How to Switch**:
- Click sun (☀️) or moon (🌙) icon in header
- Theme changes immediately
- Preference saved to browser

**Dark Mode** (default):
- Dark background (#1a1a1a)
- Light text (#ffffff)
- Reduced eye strain
- Better for low-light environments

**Light Mode**:
- Light background (#ffffff)
- Dark text (#333333)
- Better for bright environments
- Familiar traditional look

### Refresh Frequency

**Options**:
1. **Manual Refresh**: Click refresh button (↻)
2. **Auto-Refresh**: WebSocket updates (future feature)
3. **Page Reload**: Browser refresh (F5)

**Recommendations**:
- Day traders: Refresh every 15-30 minutes
- Swing traders: Refresh once or twice daily
- Long-term investors: Refresh weekly

---

## Monitoring System Health

### Health Status Indicator

**Location**: Header, near theme toggle

**Status Colors**:
- 🟢 **Green**: All systems operational
- 🟡 **Yellow**: Some services degraded
- 🔴 **Red**: Critical issues
- ⚪ **Gray**: Checking status

**What It Monitors**:
- Backend API availability
- ML model loading status
- OpenAI API connectivity
- Redis cache status
- WebSocket manager

**Auto-Refresh**: Every 30 seconds

### Health Check Modal

**Opening**:
- Click the health status indicator
- Modal overlay appears

**Information Displayed**:

**1. Backend API**
- Status: ✅ Operational / ❌ Error
- Response time: ~50ms

**2. ML Model**
- Status: ✅ Loaded / ❌ Missing
- Path: models/prod_model.bin

**3. OpenAI API**
- Status: ✅ Available / ❌ Not configured
- Model: gpt-4o-mini

**4. Cache Backend**
- Type: Redis / In-memory
- Status: ✅ Connected / ❌ Disconnected

**5. Performance Metrics**
- Cache hit rate: 78%
- Rate limiter: 23 tracked IPs
- WebSocket: 5 active connections

**Refresh Button**: Manual refresh of health data

**Closing**: Click outside modal

---

## Tips and Best Practices

### For New Users

**Start Simple**:
1. Explore one market (e.g., Global)
2. Review top 10 stocks
3. Click a few stocks to see details
4. Try the search feature
5. Toggle dark/light mode

**Learn Gradually**:
- Understand [trading signals](Understanding-Trading-Signals.md)
- Read about each market
- Try multi-market selection
- Request AI analysis

### For Active Investors

**Daily Routine**:
1. Check health status (ensure system is working)
2. Refresh rankings
3. Review signal changes
4. Check any stocks you own
5. Look for new STRONG BUY opportunities

**Weekly Routine**:
1. Review all positions
2. Check for signal downgrades
3. Request AI analysis
4. Rebalance if needed
5. Update watchlist

### For Developers

**API Access**:
- Use REST endpoints directly
- Implement custom frontends
- Build integrations
- Automate trading strategies

**Customization**:
- Modify market configurations
- Adjust ML model parameters
- Add custom indicators
- Create new visualizations

### General Best Practices

**Do's** ✅:
- Diversify across markets
- Follow signal changes
- Combine with fundamental analysis
- Use stop losses
- Review regularly
- Keep learning

**Don'ts** ❌:
- Don't invest blindly
- Don't ignore SELL signals
- Don't over-trade
- Don't risk too much on one stock
- Don't use for day trading
- Don't skip your own research

---

## Keyboard Shortcuts (Future Feature)

**Planned Shortcuts**:
- `r` - Refresh rankings
- `s` - Focus search
- `/` - Open help
- `?` - Show shortcuts modal
- `n` - Next page
- `p` - Previous page
- `1-8` - Select market view
- `Esc` - Close modals

See [BACKLOG.md](../../BACKLOG.md) for status.

---

## Mobile Usage

**Responsive Design**:
- ✅ Works on phones and tablets
- ✅ Touch-friendly buttons
- ✅ Optimized layouts
- ✅ Readable text sizes

**Limitations**:
- Table may require horizontal scrolling
- Some columns hidden on small screens
- Better experience on tablet or desktop

**Future**: Native mobile app (see [BACKLOG.md](../../BACKLOG.md))

---

## Troubleshooting

### Data Not Loading

**Check**:
1. Backend is running: `curl http://localhost:8000/health`
2. Network connection
3. Browser console for errors (F12)
4. Rate limit not exceeded

### Slow Performance

**Solutions**:
1. Enable Redis caching
2. Check network speed
3. Reduce number of selected markets
4. Clear browser cache

### Search Not Working

**Check**:
1. Valid ticker symbol
2. Correct format (e.g., .SW for Swiss stocks)
3. Stock is publicly traded
4. Not rate limited

---

## Next Steps

**Learn More**:
- [Understanding Trading Signals](Understanding-Trading-Signals.md)
- [Multi-Market Analysis](Multi-Market-Analysis.md)
- [API Reference](API-Reference.md)

**Get Help**:
- [FAQ](FAQ.md)
- [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- [Community Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)

---

*Last updated: December 1, 2025*
