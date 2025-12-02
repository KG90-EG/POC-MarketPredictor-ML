# Alert System Documentation

**Version**: 1.0.0  
**Date**: December 2, 2025  
**Status**: ✅ Production Ready

---

## Overview

The Alert System provides real-time notifications for important trading events, helping users stay informed about market changes, signal shifts, and trading opportunities.

## Features

### Alert Types

1. **Signal Change** 🔄
   - Triggers when BUY/SELL/HOLD signal changes
   - Priority: HIGH (for BUY), MEDIUM (for SELL)
   - Example: "Signal changed from HOLD to BUY"

2. **High Confidence** 🎯
   - Triggers when prediction confidence ≥ 75%
   - Priority: HIGH (for BUY), MEDIUM (for SELL)
   - Example: "High confidence BUY signal (85%)"

3. **Price Spike** 📈
   - Triggers on ≥5% price change
   - Priority: HIGH (≥10%), MEDIUM (≥5%)
   - Example: "Price spike up 7.5%"

4. **Momentum Shift** 🌊
   - Crypto only: Momentum crosses thresholds
   - Priority: HIGH (>5), MEDIUM (≤0)
   - Example: "Momentum shifted from -2.0 to 6.5"

### Priority Levels

- 🚨 **CRITICAL**: Urgent action required
- 🔴 **HIGH**: Important, review soon
- 🟡 **MEDIUM**: Noteworthy, check when convenient
- 🟢 **LOW**: Informational only

---

## Architecture

### Backend (`market_predictor/alerts.py`)

```python
class AlertManager:
    def __init__(self, max_alerts: int = 100):
        self.alerts: List[Alert] = []
        self.last_signals: Dict[str, str] = {}
        self.last_prices: Dict[str, float] = {}
        self.last_momentum: Dict[str, float] = {}

    def check_and_create_alerts(
        self, symbol, name, asset_type, prediction, current_price
    ) -> List[Alert]:
        # Returns new alerts created
```

**Key Methods**:

- `check_and_create_alerts()` - Main alert detection logic
- `get_alerts()` - Fetch alerts with filters
- `mark_as_read()` - Mark alerts as read
- `clear_alerts()` - Remove old alerts
- `get_unread_count()` - Count unread alerts

### Frontend (`AlertPanel.jsx`)

**Components**:

- `AlertPanel` - Main alert UI component
- Alert bell icon with badge
- Filterable alert list
- Real-time auto-refresh (30s)

**Features**:

- Unread/Priority/Type filters
- Mark all as read
- Clear old alerts (>7 days)
- Time formatting ("5m ago", "2h ago")
- Click to mark as read

---

## API Endpoints

### GET `/alerts`

Fetch alerts with optional filters.

**Query Parameters**:

```
unread_only: bool = False     # Only unread alerts
priority: str = None          # Filter by priority (low, medium, high, critical)
asset_type: str = None        # Filter by type (stock, crypto)
limit: int = 50               # Max alerts to return
```

**Response**:

```json
{
  "alerts": [
    {
      "alert_id": "AAPL_signal_change_1701234567.89",
      "alert_type": "signal_change",
      "priority": "high",
      "asset_type": "stock",
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "message": "Signal changed from HOLD to BUY",
      "timestamp": "2025-12-02T10:30:00Z",
      "data": {
        "old_signal": "HOLD",
        "new_signal": "BUY",
        "confidence": 82.5,
        "reasoning": "Strong bullish signal from ML model"
      },
      "read": false
    }
  ],
  "unread_count": 5,
  "total_count": 23
}
```

### POST `/alerts/mark-read`

Mark alerts as read.

**Body**:

```json
["alert_id_1", "alert_id_2", "alert_id_3"]
```

**Response**:

```json
{
  "message": "Marked 3 alerts as read",
  "marked_count": 3
}
```

### DELETE `/alerts/clear`

Clear old alerts.

**Query Parameters**:

```
older_than_days: int = 7      # Remove alerts older than N days
```

**Response**:

```json
{
  "message": "Cleared 12 old alerts",
  "removed_count": 12
}
```

---

## Integration Points

### Prediction Functions

Alerts are automatically checked after every prediction:

**Stock Predictions** (`get_watchlist_prediction`):

```python
result = {
    "signal": signal,
    "confidence": confidence,
    "reasoning": reasoning,
    "metrics": {"probability": prob, "rsi": rsi, "momentum": momentum}
}

# Check for alerts
current_price = float(df["Adj Close"].iloc[-1])
alert_manager.check_and_create_alerts(
    symbol=ticker,
    name=ticker,
    asset_type="stock",
    prediction=result,
    current_price=current_price
)
```

**Crypto Predictions**:

```python
result = {
    "signal": signal,
    "confidence": confidence,
    "reasoning": reasoning,
    "metrics": {"price_change_24h": ..., "momentum": momentum}
}

# Check for alerts
alert_manager.check_and_create_alerts(
    symbol=ticker,
    name=crypto_name,
    asset_type="crypto",
    prediction=result,
    current_price=current_price
)
```

---

## Alert Detection Logic

### Signal Change Detection

```python
if last_signal and signal != last_signal and signal in ['BUY', 'SELL']:
    priority = AlertPriority.HIGH if signal == 'BUY' else AlertPriority.MEDIUM
    # Create alert...
```

### High Confidence Detection

```python
if signal in ['BUY', 'SELL'] and confidence >= 75:
    priority = AlertPriority.HIGH if signal == 'BUY' else AlertPriority.MEDIUM
    # Create alert...
```

### Price Spike Detection

```python
if current_price and symbol in self.last_prices:
    price_change_pct = ((current_price - last_price) / last_price) * 100
    if abs(price_change_pct) >= 5:  # 5% threshold
        priority = AlertPriority.HIGH if abs(price_change_pct) >= 10 else AlertPriority.MEDIUM
        # Create alert...
```

### Momentum Shift Detection (Crypto)

```python
if momentum is not None and symbol in self.last_momentum:
    # Alert on crossing thresholds
    if (last_mom <= 0 and momentum > 5) or (last_mom > 5 and momentum <= 0):
        priority = AlertPriority.HIGH if momentum > 5 else AlertPriority.MEDIUM
        # Create alert...
```

---

## Frontend Usage

### Import and Use

```jsx
import AlertPanel from './components/AlertPanel';

function App() {
  return (
    <header>
      <AlertPanel />
      {/* Other header elements */}
    </header>
  );
}
```

### Customization

**Auto-refresh interval**:

```jsx
// In AlertPanel.jsx
useEffect(() => {
  loadAlerts();
  const interval = setInterval(loadAlerts, 30000); // 30 seconds
  return () => clearInterval(interval);
}, [filter]);
```

**Max alerts to show**:

```jsx
const params = new URLSearchParams();
params.append('limit', '50'); // Adjust as needed
```

---

## Configuration

### Alert Manager Settings

```python
# In server.py initialization
from .alerts import AlertManager

alert_manager = AlertManager(max_alerts=100)  # Max alerts to keep in memory
```

### Thresholds

**Confidence Threshold** (for high confidence alerts):

```python
if confidence >= 75:  # 75% threshold
```

**Price Spike Threshold**:

```python
if abs(price_change_pct) >= 5:  # 5% change
    priority = HIGH if >= 10 else MEDIUM  # 10% for HIGH priority
```

**Momentum Thresholds** (crypto):

```python
if (last_mom <= 0 and momentum > 5) or (last_mom > 5 and momentum <= 0):
    # Crossing 0 or 5 triggers alert
```

---

## Performance Considerations

### Memory Management

- **Max Alerts**: 100 alerts kept in memory
- **Auto-cleanup**: Oldest alerts removed when limit exceeded
- **Manual cleanup**: Clear alerts older than 7 days via API

### State Tracking

Alert manager tracks last known state for each symbol:

- `last_signals`: Dict[symbol, signal]
- `last_prices`: Dict[symbol, price]
- `last_momentum`: Dict[symbol, momentum]

This allows detection of changes without database queries.

---

## Testing

### Unit Tests

```python
# test_alerts.py (to be created)
def test_signal_change_alert():
    manager = AlertManager()

    # First prediction: HOLD
    manager.check_and_create_alerts(
        "AAPL", "Apple", "stock",
        {"signal": "HOLD", "confidence": 50},
        150.0
    )
    assert len(manager.alerts) == 0

    # Second prediction: BUY (should create alert)
    alerts = manager.check_and_create_alerts(
        "AAPL", "Apple", "stock",
        {"signal": "BUY", "confidence": 80},
        155.0
    )
    assert len(alerts) == 2  # Signal change + high confidence
```

### Integration Tests

```python
def test_alert_api():
    response = client.get("/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()
    assert "unread_count" in response.json()
```

---

## Future Enhancements

### Phase 2 (Planned)

1. **Email Notifications**
   - Send email alerts via SendGrid/AWS SES
   - Digest mode (daily/weekly summary)
   - Unsubscribe link

2. **Push Notifications**
   - Browser push (Web Push API)
   - Mobile push (Firebase Cloud Messaging)

3. **Custom Alert Rules**
   - User-defined thresholds
   - Specific symbols to watch
   - Time-based rules (only during market hours)

4. **Alert Analytics**
   - Alert history dashboard
   - Accuracy metrics (how often alerts led to profitable trades)
   - Performance tracking

5. **Webhooks**
   - Send alerts to Slack/Discord/Telegram
   - Custom webhook URLs
   - Zapier integration

### Phase 3 (Future)

- Machine learning for alert prioritization
- Alert suppression (avoid spam)
- Smart batching (combine related alerts)
- Voice alerts (text-to-speech)

---

## Troubleshooting

### Alerts Not Appearing

1. **Check prediction calls**: Alerts are only created during prediction
2. **Verify thresholds**: Ensure changes meet threshold criteria
3. **Check filters**: Unread filter may hide read alerts
4. **Check limit**: Default limit is 50 alerts

### Too Many Alerts

1. **Increase thresholds**: Raise confidence/price spike thresholds
2. **Filter by priority**: Show only HIGH/CRITICAL
3. **Clear old alerts**: Delete alerts older than 7 days
4. **Adjust auto-refresh**: Reduce refresh frequency

### Missing State

If alerts aren't detecting changes, restart backend to reset state tracking dictionaries.

---

## Support

**Documentation**:

- [BACKLOG.md](../BACKLOG.md) - Future enhancements
- [API Docs](http://localhost:8000/docs) - Interactive API reference

**Issues**:

- [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

---

**Last Updated**: December 2, 2025  
**Version**: 1.0.0  
**Author**: Kevin Garcia (@KG90-EG)
