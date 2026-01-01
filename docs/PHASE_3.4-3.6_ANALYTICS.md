# Phase 3.4-3.6: Usability Testing, A/B Testing & Analytics

## ✅ Phase 3.4: Usability Testing Setup

### Implementation Status: COMPLETE

### Components Created

#### 1. UsabilityTracker Component

**Location**: `frontend/src/components/UsabilityTracker.jsx`

**Features**:

- 🎯 **Session Tracking**: Automatic session ID generation and management
- 🖱️ **Click Tracking**: Captures all user clicks with coordinates and target info
- 📜 **Scroll Tracking**: Monitors scroll behavior (throttled to 2s intervals)
- 👁️ **Visibility Tracking**: Detects when user switches tabs/windows
- 🔍 **Navigation Tracking**: Records user journey through the app
- ⚠️ **Error Tracking**: Captures JavaScript errors and component failures
- 📊 **Custom Events**: Allows tracking of specific user actions
- 💾 **Local Storage**: Backs up sessions locally (last 50 sessions)
- 🌐 **Backend Sync**: Sends session data to `/api/usability/sessions`

**Usage**:

```jsx
// Integrated in App.jsx
<UsabilityTracker
  enabled={import.meta.env.DEV || import.meta.env.VITE_ENABLE_USABILITY_TRACKING === 'true'}
/>

// Access tracker globally
window.usabilityTracker.trackCustomEvent('feature_used', { feature: 'stock_search' })
window.usabilityTracker.exportSession() // Manual export
```

**Data Captured**:

- User agent, screen size, viewport dimensions
- Click heatmap data (x, y coordinates + target element)
- Scroll depth and patterns
- Page visibility changes
- Navigation paths
- Error occurrences
- Custom event data

**Analysis Helper**:

```javascript
import { analyzeUsabilityData } from './components/UsabilityTracker'

const sessions = JSON.parse(localStorage.getItem('usability_sessions') || '[]')
const analysis = analyzeUsabilityData(sessions)
// Returns: totalSessions, averageDuration, clickHeatmap, commonPaths, errorPatterns
```

#### 2. Backend Usability Endpoints

**Location**: `src/trading_engine/analytics_routes.py`

**Endpoints**:

**POST `/api/usability/sessions`**

- Store complete usability testing session
- Input: UsabilitySession (id, events, statistics, etc.)
- Output: Success confirmation + session ID

**GET `/api/usability/sessions?limit=50`**

- Retrieve recent usability sessions
- Returns: List of sessions sorted by start time (newest first)

**GET `/api/usability/analysis`**

- Get aggregated usability insights
- Returns:
  - Total sessions analyzed
  - Average session duration (seconds)
  - Total clicks and errors
  - Top 10 click targets
  - Top 10 error patterns

**Data Storage**:

- Format: JSONL (JSON Lines) in `data/analytics/usability_sessions.jsonl`
- Retention: Unlimited (manually managed)
- Backup: Also stored in browser localStorage

---

## ✅ Phase 3.5: A/B Testing Infrastructure

### Implementation Status: COMPLETE

### Components Created

#### 1. A/B Test Framework

**Location**: `frontend/src/components/ABTest.jsx`

**Core Features**:

- 🧪 **Multi-Variant Testing**: Supports A/B/n tests (not just A/B)
- ⚖️ **Weighted Distribution**: Custom variant weights (e.g., 50/50 or 70/30)
- 💾 **Persistent Assignment**: Users keep same variant across sessions
- 📊 **Conversion Tracking**: Track goals, conversions, and custom events
- 📈 **Statistical Significance**: Built-in Chi-square test calculator
- 🎯 **Targeted Events**: Track specific actions per experiment

**Usage Example**:

```jsx
import { ABTest, Variant, useABTest } from './components/ABTest'

// In App.jsx - define experiments
const abTestExperiments = {
  'stock_card_layout': {
    variants: ['A', 'B'],
    weights: [0.5, 0.5]
  },
  'cta_button_text': {
    variants: ['A', 'B', 'C'],
    weights: [0.33, 0.33, 0.34]
  }
}

// In component - use test
const { getVariant, trackConversion } = useABTest()

const variant = getVariant('stock_card_layout')

// Track conversion
trackConversion('stock_card_layout', 'purchase', 99.99)

// Render variants
<ABTest name="cta_button_text">
  <Variant variant="A">
    <button>Buy Now</button>
  </Variant>
  <Variant variant="B">
    <button>Get Started</button>
  </Variant>
  <Variant variant="C">
    <button>Try It Free</button>
  </Variant>
</ABTest>
```

**ABTestProvider Context**:

```jsx
<ABTestProvider experiments={abTestExperiments}>
  <AppContent />
</ABTestProvider>
```

**Statistical Analysis**:

```javascript
import { calculateSignificance, analyzeABTestResults } from './components/ABTest'

// Calculate significance between two variants
const result = calculateSignificance(
  { conversions: 120, impressions: 1000 }, // Variant A
  { conversions: 150, impressions: 1000 }  // Variant B
)
// Returns: variantA/B rates, difference, confidence interval, p-value, z-score

// Analyze all stored results
const results = analyzeABTestResults()
// Returns: experiment results with conversion rates and significance
```

#### 2. Backend A/B Test Endpoints

**Location**: `src/trading_engine/analytics_routes.py`

**Endpoints**:

**POST `/api/ab-test/assignment`**

- Track when user is assigned to variant
- Input: userId, experiment, variant, timestamp, userAgent, screenSize
- Output: Success confirmation

**POST `/api/ab-test/conversion`**

- Track conversion event
- Input: userId, experiment, variant, conversionType, value
- Output: Success confirmation

**POST `/api/ab-test/event`**

- Track custom event within experiment
- Input: userId, experiment, variant, eventName, data
- Output: Success confirmation

**GET `/api/ab-test/results`**

- Get aggregated A/B test results
- Returns:
  - Per-experiment, per-variant statistics
  - Impressions (assignments)
  - Conversions
  - Conversion rates (%)
  - Total assignments and conversions

**Data Storage**:

- `data/analytics/ab_assignments.jsonl` - Variant assignments
- `data/analytics/ab_conversions.jsonl` - Conversion events
- `data/analytics/ab_events.jsonl` - Custom events

**Example Experiments Configured**:

1. **stock_card_layout**: A vs B layout comparison
2. **cta_button_text**: A vs B vs C button text
3. **price_chart_default**: Candlestick vs Line chart default

---

## ✅ Phase 3.6: Analytics Integration

### Implementation Status: COMPLETE

### Components Created

#### 1. Analytics System

**Location**: `frontend/src/components/Analytics.jsx`

**Core Features**:

- 📊 **Event Tracking**: Track any custom event with properties
- 📄 **Page View Tracking**: Automatic and manual page view tracking
- 🖱️ **Click Tracking**: Track specific button/link clicks
- 🔍 **Search Tracking**: Monitor search queries and results
- 📝 **Form Tracking**: Track form submissions and success rates
- ⚡ **Feature Usage**: Track which features users engage with
- ⚠️ **Error Tracking**: Automatic error capture and reporting
- 🏎️ **Performance Metrics**: Track loading times and performance
- 🎯 **Conversion Tracking**: Monitor goal completions
- 📦 **Batch Processing**: Events queued and sent in batches (10 events or 5s)
- 💾 **Offline Support**: Uses `navigator.sendBeacon` for page unload
- 🔒 **User Privacy**: Anonymous user IDs stored in localStorage

**Singleton Instance**:

```javascript
import analytics, { trackWebVitals } from './components/Analytics'

// Initialize (done in App.jsx via AnalyticsProvider)
analytics.init({
  endpoint: '/api/analytics/events',
  batchSize: 10,
  flushInterval: 5000,
  debug: true
})

// Track events
analytics.track('button_click', { button: 'buy_stock', ticker: 'AAPL' })
analytics.trackPageView('Stock Details')
analytics.trackSearch('TSLA', 1)
analytics.trackFeature('price_alerts', 'create', { threshold: 500 })
analytics.trackError(new Error('API failed'), { endpoint: '/api/ranking' })
analytics.trackPerformance('api_response', 234, 'ms')
analytics.trackConversion('stock_purchase', 1000, 'USD')
```

**React Hook**:

```jsx
import { useAnalytics } from './components/Analytics'

function MyComponent() {
  const { trackEvent, trackClick, trackSearch, trackError } = useAnalytics()

  // Automatically tracks page view on mount

  const handleClick = (e) => {
    trackClick(e.currentTarget, 'Purchase Button')
  }

  const handleSearch = (query, results) => {
    trackSearch(query, results.length)
  }

  return <button onClick={handleClick}>Buy Stock</button>
}
```

**Web Vitals Tracking**:

```javascript
import { trackWebVitals } from './components/Analytics'

// Track Core Web Vitals automatically
trackWebVitals()
// Tracks: FCP, LCP, FID, CLS, PageLoad time
```

**AnalyticsProvider**:

```jsx
import { AnalyticsProvider } from './components/Analytics'

<AnalyticsProvider config={{ debug: import.meta.env.DEV }}>
  <App />
</AnalyticsProvider>
```

#### 2. Backend Analytics Endpoints

**Location**: `src/trading_engine/analytics_routes.py`

**Endpoints**:

**POST `/api/analytics/events`**

- Track batch of analytics events
- Input: AnalyticsBatch { events: [...], meta: {...} }
- Output: Success + events received count

**GET `/api/analytics/summary`**

- Get analytics summary statistics
- Returns:
  - Total events tracked
  - Unique users and sessions
  - Top 10 events by frequency
  - Event type breakdown

**Event Data Captured**:

- Event name and custom properties
- User ID and session ID
- Timestamp (client + server received time)
- URL, pathname, referrer
- User agent, screen size, language
- Batch ID for tracking

**Data Storage**:

- Format: JSONL in `data/analytics/events.jsonl`
- Retention: Unlimited (can implement rotation)
- Backup: Also stored in browser localStorage (last 1000 events)

#### 3. Integration in App.jsx

**Analytics Tracking Added**:

```jsx
// Track web vitals on mount
useEffect(() => {
  trackWebVitals()
  analytics.trackPageView('Market Predictor Dashboard')
}, [])

// Track ranking loads
async function fetchRanking(market) {
  analytics.trackFeature('stock_ranking', 'load', { market })
  const startTime = Date.now()
  // ... fetch logic ...
  analytics.trackPerformance('ranking_load', Date.now() - startTime)
}

// Track searches
async function performSearch(ticker) {
  analytics.trackSearch(ticker)
  // ... search logic ...
}
```

---

## 📊 Combined System Architecture

### Frontend Flow

```
User Action
    ↓
UsabilityTracker (captures all interactions)
    ↓
Analytics (tracks specific events)
    ↓
ABTest (tracks experiment assignments/conversions)
    ↓
Backend APIs (stores data)
    ↓
Analysis Tools (generate insights)
```

### Data Storage Structure

```
data/analytics/
├── events.jsonl              # All analytics events
├── ab_assignments.jsonl      # A/B test variant assignments
├── ab_conversions.jsonl      # A/B test conversions
├── ab_events.jsonl           # A/B test custom events
└── usability_sessions.jsonl  # Usability testing sessions
```

### Provider Hierarchy in App

```jsx
<ErrorBoundary>
  <AnalyticsProvider>
    <ABTestProvider experiments={...}>
      <QueryClientProvider>
        <AppContent />
        <UsabilityTracker />
      </QueryClientProvider>
    </ABTestProvider>
  </AnalyticsProvider>
</ErrorBoundary>
```

---

## 🎯 Usage Examples

### Example 1: Track Feature Usage

```jsx
// When user opens price chart
analytics.trackFeature('price_chart', 'open', {
  ticker: 'AAPL',
  chartType: 'candlestick',
  timeframe: '1D'
})
```

### Example 2: A/B Test Button Color

```jsx
<ABTest name="buy_button_color">
  <Variant variant="green">
    <button className="btn-green" onClick={handleBuy}>Buy Stock</button>
  </Variant>
  <Variant variant="blue">
    <button className="btn-blue" onClick={handleBuy}>Buy Stock</button>
  </Variant>
</ABTest>

// Track conversion when user completes purchase
const { trackConversion } = useABTest()
trackConversion('buy_button_color', 'purchase', stockPrice)
```

### Example 3: Usability Analysis

```jsx
// Get all stored sessions
const sessions = JSON.parse(localStorage.getItem('usability_sessions') || '[]')

// Analyze
import { analyzeUsabilityData } from './components/UsabilityTracker'
const insights = analyzeUsabilityData(sessions)

console.log('Total Sessions:', insights.totalSessions)
console.log('Average Duration:', insights.averageDuration, 'seconds')
console.log('Click Heatmap Points:', insights.clickHeatmap.length)
console.log('Most Common Path:', insights.commonPaths[0])
console.log('Top Error:', insights.errorPatterns[0])
```

---

## 📈 Benefits Achieved

### Usability Testing (3.4)

- ✅ **User Behavior Insights**: See exactly how users interact with the app
- ✅ **Error Detection**: Identify problematic UI elements causing errors
- ✅ **Navigation Analysis**: Understand common user paths
- ✅ **Performance Issues**: Spot slow interactions or bottlenecks
- ✅ **Heat Map Data**: Visual representation of click patterns

### A/B Testing (3.5)

- ✅ **Data-Driven Decisions**: Make UI changes based on actual user data
- ✅ **Risk Mitigation**: Test changes with subset before full rollout
- ✅ **Conversion Optimization**: Identify which variants drive better results
- ✅ **Statistical Validation**: Know when results are significant
- ✅ **Multi-Variant Testing**: Compare more than 2 options simultaneously

### Analytics (3.6)

- ✅ **Product Insights**: Understand which features users love/ignore
- ✅ **Performance Monitoring**: Track load times and bottlenecks
- ✅ **Error Tracking**: Proactive error detection and resolution
- ✅ **User Journey Mapping**: See complete user flow through app
- ✅ **Conversion Funnels**: Identify drop-off points in user flows
- ✅ **Web Vitals**: Monitor Core Web Vitals (FCP, LCP, FID, CLS)

---

## 🔧 Configuration

### Enable Usability Tracking in Production

```bash
# In .env file
VITE_ENABLE_USABILITY_TRACKING=true
```

### Configure Analytics

```javascript
// In App.jsx or main entry point
analytics.init({
  endpoint: '/api/analytics/events',
  batchSize: 10,           // Send after 10 events
  flushInterval: 5000,     // Or every 5 seconds
  debug: false             // Enable console logs
})
```

### Define A/B Tests

```javascript
const abTestExperiments = {
  'experiment_name': {
    variants: ['A', 'B', 'C'],
    weights: [0.5, 0.25, 0.25]  // 50% A, 25% B, 25% C
  }
}
```

---

## 🚀 Next Steps

### Recommended Enhancements

1. **Dashboard**: Build admin dashboard to view all analytics data
2. **Alerts**: Set up alerts for high error rates or low conversions
3. **Automation**: Automatically end A/B tests when significance reached
4. **Export**: Add CSV/JSON export for analytics data
5. **Visualization**: Create heatmap overlay for usability data
6. **Retention**: Implement data retention policies (e.g., 90 days)
7. **Privacy**: Add GDPR consent banner and data deletion
8. **Real-time**: WebSocket integration for live analytics dashboard

### Integration with External Tools

- **Google Analytics**: Send events to GA4 for wider team access
- **Mixpanel**: Deep funnel and cohort analysis
- **Hotjar**: Visual heatmaps and session recordings
- **Sentry**: Advanced error tracking and monitoring
- **Amplitude**: Product analytics and user behavior

---

## 📝 Files Created/Modified

### New Files

1. `frontend/src/components/UsabilityTracker.jsx` - Usability tracking component
2. `frontend/src/components/ABTest.jsx` - A/B testing framework
3. `frontend/src/components/Analytics.jsx` - Analytics tracking system
4. `src/trading_engine/analytics_routes.py` - Backend analytics endpoints
5. `docs/PHASE_3.4-3.6_ANALYTICS.md` - This documentation

### Modified Files

1. `frontend/src/App.jsx`:
   - Added imports for all 3 systems
   - Wrapped app with AnalyticsProvider and ABTestProvider
   - Added UsabilityTracker component
   - Integrated analytics tracking in fetchRanking and performSearch
   - Added trackWebVitals call
   - Defined A/B test experiments

2. `src/trading_engine/server.py`:
   - Imported analytics_router
   - Included analytics_router in app

### Data Files Created (Runtime)

1. `data/analytics/events.jsonl`
2. `data/analytics/ab_assignments.jsonl`
3. `data/analytics/ab_conversions.jsonl`
4. `data/analytics/ab_events.jsonl`
5. `data/analytics/usability_sessions.jsonl`

---

## ✅ Phase 3 Complete Summary

**Phase 3.1**: ✅ Onboarding Flow  
**Phase 3.2**: ✅ Accessibility (WCAG 2.1 AA)  
**Phase 3.3**: ✅ Performance Optimization  
**Phase 3.4**: ✅ Usability Testing Setup  
**Phase 3.5**: ✅ A/B Testing Infrastructure  
**Phase 3.6**: ✅ Analytics Integration

🎉 **All Phase 3 objectives completed!**

The Market Predictor ML application now has enterprise-grade UX infrastructure with comprehensive tracking, testing, and analytics capabilities.
