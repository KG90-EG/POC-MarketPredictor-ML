# Simulation API (Paper Trading)

The paper-trading engine exposes a set of REST endpoints under `/api/simulations` for creating simulations, requesting AI recommendations, executing trades, and reviewing portfolio history. Each endpoint is backed by the `TradingSimulation` engine and `SimulationDB` persistence layer.

## Endpoints

### 1. Create Simulation
- **Method/Path:** `POST /api/simulations`
- **Body:**
  - `user_id` (string, optional, default: `"default_user"`)
  - `initial_capital` (number, optional, default: `10000.0`)
  - `mode` (string, optional, `"auto"` or `"manual"`, default: `"auto"`)
- **Response:** Simulation metadata with `simulation_id`, initial cash, mode, and timestamps.

### 2. Get Simulation
- **Method/Path:** `GET /api/simulations/{simulation_id}`
- **Response:** Full simulation snapshot including cash, open positions, executed trades, and derived performance metrics.

### 3. Get AI Recommendations
- **Method/Path:** `POST /api/simulations/{simulation_id}/recommendations`
- **Response:** List of ML-driven recommendations with `ticker`, `action`, `quantity`, `price`, `confidence`, and `reason` values generated from the ranking model and risk rules.
- **Errors:** `503` when the ML model has not been loaded; `404` if the simulation ID is unknown.

### 4. Execute Trade
- **Method/Path:** `POST /api/simulations/{simulation_id}/trades`
- **Body:**
  - `ticker` (string, required)
  - `action` (string, required, `"BUY"` or `"SELL"`)
  - `quantity` (integer, required)
  - `price` (number, required, execution price per share)
  - `reason` (string, required, rationale for the trade)
  - `ml_confidence` (number, optional, confidence score from the model)
- **Response:** Trade confirmation with timestamp, updated cash, and position balances.
- **Errors:** `400` when the trade violates balance or position rules; `404` if the simulation ID is unknown.

### 5. Auto-Trade
- **Method/Path:** `POST /api/simulations/{simulation_id}/auto-trade`
- **Query:** `max_trades` (integer, optional, default: `3`)
- **Response:** List of executed trades derived from the top AI recommendations plus updated cash balance.

### 6. Portfolio Snapshot
- **Method/Path:** `GET /api/simulations/{simulation_id}/portfolio`
- **Response:** Current positions enriched with live prices, total portfolio value, P&L totals, and initial capital reference.

### 7. Trade History
- **Method/Path:** `GET /api/simulations/{simulation_id}/history`
- **Response:** Chronological list of executed trades, each with ISO-formatted timestamps.

### 8. Reset Simulation
- **Method/Path:** `POST /api/simulations/{simulation_id}/reset`
- **Response:** Confirmation that trades and positions were cleared and cash was restored to the initial capital.

### 9. Delete Simulation
- **Method/Path:** `DELETE /api/simulations/{simulation_id}`
- **Response:** Confirmation that the simulation and associated data were removed from storage.

## Notes
- All responses are JSON.
- The service uses Yahoo Finance data (`yfinance`) to hydrate prices for portfolio and recommendation flows.
- Simulation IDs are integer primary keys persisted by the `SimulationDB` layer in SQLite.
