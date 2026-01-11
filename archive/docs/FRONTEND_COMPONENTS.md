# Frontend Components Documentation

## Overview

This document describes the React components in the Trading-Fun frontend application, including the health monitoring system with modal overlay design.

---

## Core Components

### 1. App Component (`frontend/src/App.jsx`)

**Purpose:** Main application component that manages state and renders all UI elements.

**Key Features:**
- Market view selection (8 markets: Global, Switzerland, Germany, UK, France, Japan, Canada)
- Stock rankings display with pagination
- Company detail sidebar
- Theme toggle (light/dark mode)
- Simulation dashboard language dropdown (EN/DE/IT/ES) with persisted preference
- Health status indicator integration
- Error handling with user-friendly messages

**State Management:**
- `selectedMarket`: Currently selected market view
- `rankings`: Stock rankings data from API
- `currentPage`: Pagination state
- `selectedStock`: Currently selected stock for detail view
- `darkMode`: Theme preference (persisted to localStorage)
- `showHealthPanel`: Controls health modal visibility
- `healthStatus`: Current system health status

**Localization:**
- Strings are organized by language in `frontend/src/translations.js`.
- The simulation dashboard stores the chosen language in `localStorage` (`app_language`) so subsequent visits reuse the same locale.

**Health Indicator Implementation:**
```jsx
// Health status icon in header
<button
  className={`health-indicator ${healthStatus.status}`}
  onClick={() => setShowHealthPanel(!showHealthPanel)}
  title="System Health"
>
  <span className="status-dot"></span>
</button>

// Health modal (conditional render)
<HealthCheck
  isOpen={showHealthPanel}
  onClose={() => setShowHealthPanel(false)}
/>
```

**Auto-refresh:**
- Health status refreshes every 30 seconds
- Uses `setInterval` with cleanup on unmount

---

### 2. ErrorBoundary Component (`frontend/src/components/ErrorBoundary.jsx`)

**Purpose:** Catches JavaScript errors anywhere in the component tree and displays a fallback UI.

**Key Features:**
- Prevents entire app crash from component errors
- User-friendly error display with emoji
- One-click retry functionality
- Preserves app state when possible

**Props:**
- `children`: React nodes to wrap and protect

**State:**
- `hasError`: Boolean indicating if error was caught
- `error`: Error object with details

**Implementation:**
```jsx
<ErrorBoundary>
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
</ErrorBoundary>
```

**Error Display:**
- 😵 Emoji for visual feedback
- Error message display
- "Try Again" button to reset error state
- Maintains clean, minimal design

---

### 3. HealthCheck Component (`frontend/src/components/HealthCheck.jsx`)

**Purpose:** Real-time system health monitoring displayed as a modal overlay.

**Key Features:**
- Modal overlay design with backdrop
- Comprehensive system diagnostics
- Performance metrics display
- Auto-refresh capability (30s intervals)
- Manual refresh button
- Click-outside-to-close
- Close button (X) in top-right

**Props:**
- `isOpen`: Boolean to control modal visibility
- `onClose`: Callback function to close modal

**State:**
- `health`: Health check data from `/health` endpoint
- `metrics`: Metrics data from `/metrics` endpoint
- `loading`: Loading state indicator
- `error`: Error state for failed requests
- `lastChecked`: Timestamp of last health check

**API Endpoints:**
```javascript
// Health endpoint
const health = await api.health();
// Returns: { status, model_loaded, openai_available, cache_backend, redis_status }

// Metrics endpoint
const metrics = await api.metrics();
// Returns: { cache_stats, rate_limiter_stats, websocket_stats, model_info }
```

**Status Colors:**
- 🟢 Green: Operational (`status === 'ok'`)
- 🟡 Yellow: Degraded (some services down)
- 🔴 Red: Error (critical failure)
- ⚫ Gray: Loading/Unknown

**Modal Structure:**
```jsx
<div className="health-overlay" onClick={onClose}>
  <div className="health-modal" onClick={(e) => e.stopPropagation()}>
    <button className="health-close" onClick={onClose}>×</button>
    {/* Health content */}
    <div className="health-footer">
      <span>Last Updated: {timestamp}</span>
      <button onClick={refresh}>↻</button>
    </div>
  </div>
</div>
```

**Sections:**

1. **Header:**
   - Component title with pulsing status indicator
   - Close button (×) in top-right corner

2. **System Status:**
   - Backend API (with response time)
   - ML Model (loaded/not loaded)
   - OpenAI API (available/unavailable)
   - Cache Backend (Redis/in-memory)

3. **Performance Metrics:**
   - Cache statistics (hit rate, key count)
   - Rate limiter stats (tracked IPs)
   - WebSocket stats (connections, subscribed tickers)

4. **Footer:**
   - Last Updated timestamp
   - Refresh button (↻) for manual updates

**Styling:** See `frontend/src/components/HealthCheck.css`

---

## Component Styling

### HealthCheck.css

**Design Philosophy:**
- Explicit color definitions (no CSS variables)
- Full light/dark mode support using `body.dark-mode` selector
- Modal overlay pattern
- Smooth animations and transitions

**Key Styles:**

1. **Overlay:**
```css
.health-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 9999;
  animation: fadeIn 0.2s ease-out;
}
```

2. **Modal:**
```css
.health-modal {
  background: #ffffff;  /* Dark: #1a1a2e */
  max-width: 800px;
  max-height: 85vh;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

body.dark-mode .health-modal {
  background: #1a1a2e;
}
```

3. **Status Colors:**
```css
.status.ok { color: #10b981; }      /* Green */
.status.degraded { color: #f59e0b; } /* Yellow */
.status.error { color: #ef4444; }    /* Red */
.status.loading { color: #6b7280; }  /* Gray */
```

4. **Animations:**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```

**Light Mode Colors:**
- Background: `#ffffff`
- Text: `#2c3e50`
- Secondary text: `#666`
- Borders: `#e0e0e0`
- Card backgrounds: `#f9f9f9`

**Dark Mode Colors:**
- Background: `#1a1a2e`
- Text: `#e6e8ec`
- Secondary text: `#9aa0aa`
- Borders: `#3a3a4a`
- Card backgrounds: `#252535`

---

### styles.css (App-level styles)

**Health Indicator Icon:**
```css
.health-indicator {
  position: relative;
  right: 120px;  /* Between theme toggle and help button */
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* Status-based colors */
.health-indicator.ok .status-dot {
  background: #10b981;
  animation: pulse-green 2s infinite;
}

.health-indicator.degraded .status-dot {
  background: #f59e0b;
  animation: pulse-yellow 2s infinite;
}

.health-indicator.error .status-dot {
  background: #ef4444;
  animation: pulse-red 2s infinite;
}

.health-indicator.loading .status-dot {
  background: #6b7280;
  animation: spin 1s linear infinite;
}
```

**Animations:**
- Pulse animations for error/degraded states
- Spin animation for loading state
- Smooth hover effects

---

## State Management

### React Query Configuration

**Setup:** (`frontend/src/App.jsx`)
```javascript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,      // 5 minutes
      cacheTime: 10 * 60 * 1000,     // 10 minutes
      retry: 2,                       // Retry failed requests twice
      refetchOnWindowFocus: false     // Don't refetch on window focus
    }
  }
});
```

**Benefits:**
- Automatic background refetching
- Intelligent caching
- Request deduplication
- Built-in retry logic
- Loading and error states

**Usage Example:**
```javascript
const { data, isLoading, error } = useQuery({
  queryKey: ['rankings', selectedMarket],
  queryFn: () => api.getRankings(selectedMarket)
});
```

---

## API Integration

### API Service (`frontend/src/api.js`)

**Health Endpoints:**
```javascript
// Get system health status
const health = async () => {
  const response = await fetch(`${API_URL}/health`);
  return response.json();
};

// Get performance metrics
const metrics = async () => {
  const response = await fetch(`${API_URL}/metrics`);
  return response.json();
};
```

**Error Handling:**
- Network error detection
- Rate limit detection (429 status)
- 404 handling for invalid tickers
- Detailed error messages with context

---

## Usage Examples

### Opening Health Modal

**From App.jsx:**
```javascript
const [showHealthPanel, setShowHealthPanel] = useState(false);

// Toggle via health indicator icon
<button
  className={`health-indicator ${healthStatus.status}`}
  onClick={() => setShowHealthPanel(!showHealthPanel)}
>
  <span className="status-dot"></span>
</button>

// Render modal
<HealthCheck
  isOpen={showHealthPanel}
  onClose={() => setShowHealthPanel(false)}
/>
```

### Auto-refresh Health Status

**Implementation:**
```javascript
useEffect(() => {
  const checkHealth = async () => {
    try {
      const health = await api.health();
      setHealthStatus(health);
    } catch (error) {
      setHealthStatus({ status: 'error' });
    }
  };

  checkHealth(); // Initial check
  const interval = setInterval(checkHealth, 30000); // Every 30s

  return () => clearInterval(interval); // Cleanup
}, []);
```

### Manual Refresh

**HealthCheck component:**
```javascript
const handleRefresh = async () => {
  setLoading(true);
  try {
    const [healthData, metricsData] = await Promise.all([
      api.health(),
      api.metrics()
    ]);
    setHealth(healthData);
    setMetrics(metricsData);
    setLastChecked(new Date());
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

---

## Best Practices

### Component Architecture

1. **Separation of Concerns:**
   - App.jsx: Main state and routing
   - ErrorBoundary: Error handling
   - HealthCheck: System diagnostics

2. **Props Flow:**
   - Pass control props (`isOpen`, `onClose`)
   - Keep state in parent component when possible
   - Use callbacks for actions

3. **Error Handling:**
   - ErrorBoundary for component errors
   - Try-catch in async functions
   - User-friendly error messages

### Styling

1. **Theme Support:**
   - Use `body.dark-mode` selector
   - Define explicit colors for both themes
   - Avoid CSS variables for critical UI

2. **Animations:**
   - Use `@keyframes` for reusable animations
   - Keep animations subtle and performant
   - Provide smooth transitions

3. **Responsive Design:**
   - Use `max-width` for modals
   - Set `max-height` with overflow
   - Test on different screen sizes

### Performance

1. **Auto-refresh:**
   - Use reasonable intervals (30s)
   - Always cleanup intervals
   - Debounce user actions

2. **API Calls:**
   - Use `Promise.all` for parallel requests
   - Implement proper loading states
   - Cache results when appropriate

3. **React Query:**
   - Set appropriate `staleTime`
   - Configure `cacheTime` for data freshness
   - Use `retry` for resilience

---

## Troubleshooting

### Health Modal Not Opening

**Check:**
1. `isOpen` prop is being passed correctly
2. `onClose` callback is defined
3. Modal overlay has correct z-index
4. No CSS conflicts with parent elements

### Status Colors Not Showing

**Check:**
1. CSS classes match status values
2. Dark mode selector is working
3. Color definitions are present
4. Browser supports the CSS features used

### Auto-refresh Not Working

**Check:**
1. `setInterval` is being called
2. Cleanup function returns `clearInterval`
3. Component hasn't unmounted
4. API endpoints are reachable

---

## Future Enhancements

### Planned Features

1. **WebSocket Integration:**
   - Real-time price updates in UI
   - Live health status updates
   - Reduced polling overhead

2. **Component Refactoring:**
   - Split App.jsx into smaller components
   - Create MarketView component
   - Extract SearchBar and CompanyDetail

3. **Advanced Health Metrics:**
   - Historical health data
   - Performance trends
   - Alert thresholds

4. **Accessibility:**
   - ARIA labels for modal
   - Keyboard navigation
   - Screen reader support

---

**Last Updated:** November 30, 2025  
**Status:** ✅ All components implemented and documented
