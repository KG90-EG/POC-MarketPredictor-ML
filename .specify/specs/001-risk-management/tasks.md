# Phase 4: Task Breakdown

## Tag 1: Risk Scoring Backend (Core)

### Task 1.1: RiskScorer Klasse erstellen
**Datei:** `src/trading_engine/risk_scoring.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Keine  

- [ ] Erstelle `RiskScorer` Klasse
- [ ] Implementiere `calculate_volatility_score(ticker)`:
  - ATR (Average True Range) berechnen
  - Normalisieren auf 0-100 Skala
  - Höhere ATR = höherer Risk Score
- [ ] Implementiere `calculate_drawdown_score(ticker)`:
  - Max Drawdown der letzten 3 Monate
  - Normalisieren auf 0-100 Skala
- [ ] Implementiere `calculate_correlation_score(ticker, benchmark="SPY")`:
  - Korrelation zu S&P 500
  - Hohe Korrelation = höheres systemisches Risiko

### Task 1.2: Composite Risk Score
**Datei:** `src/trading_engine/risk_scoring.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 1.1  

- [ ] Implementiere `get_composite_risk_score(ticker)`:
  - Volatilität: 40% Gewicht
  - Drawdown: 35% Gewicht
  - Korrelation: 25% Gewicht
- [ ] Füge Risk Level Klassifikation hinzu:
  - LOW: 0-40
  - MEDIUM: 41-70
  - HIGH: 71-100
- [ ] Error Handling: Fallback auf 50 bei fehlenden Daten

### Task 1.3: Unit Tests für Risk Scoring
**Datei:** `tests/test_risk_scoring.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 1.2  

- [ ] Test: `test_volatility_score_range` (0-100)
- [ ] Test: `test_drawdown_score_calculation`
- [ ] Test: `test_correlation_score_with_spy`
- [ ] Test: `test_composite_risk_score_weights`
- [ ] Test: `test_fallback_on_missing_data`

---

## Tag 2: Market Regime Erweiterung

### Task 2.1: Defensive Mode Logic
**Datei:** `src/trading_engine/market_regime.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Keine  

- [ ] Füge `defensive_mode` Property zu `RegimeState` hinzu
- [ ] Implementiere `get_defensive_mode_limits()`:
  ```python
  def get_defensive_mode_limits(self) -> dict:
      if self.regime_status == "RISK_OFF":
          return {
              "single_stock_max": 5,  # von 10%
              "single_crypto_max": 2.5,  # von 5%
              "total_equity_max": 35,  # von 70%
              "min_cash": 30  # von 10%
          }
      return default_limits
  ```
- [ ] Implementiere `should_show_caution_badge()`:
  - True wenn VIX > 25 ODER Regime = NEUTRAL

### Task 2.2: Position Limits Enforcement
**Datei:** `src/trading_engine/market_regime.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 2.1  

- [ ] Füge `check_position_limit(current_allocation, asset_type)` hinzu
- [ ] Rückgabe: `{"allowed": bool, "warning": str}`
- [ ] Logge Limit-Verletzungen

---

## Tag 3: API Endpoints

### Task 3.1: Portfolio Exposure Endpoint
**Datei:** `src/trading_engine/server.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 2.1  

- [ ] Erstelle `GET /api/portfolio/exposure`:
  ```python
  @app.get("/api/portfolio/exposure")
  async def get_portfolio_exposure():
      # Berechne aktuelle Allokation
      # Hole defensive mode limits
      # Prüfe auf Warnungen
      return ExposureResponse(...)
  ```
- [ ] Response Model `ExposureResponse` erstellen

### Task 3.2: Predict Endpoint erweitern
**Datei:** `src/trading_engine/server.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 1.2  

- [ ] Erweitere `/api/predict/{ticker}` Response:
  - `risk_score`: int (0-100)
  - `risk_level`: str (LOW/MEDIUM/HIGH)
  - `risk_breakdown`: dict
  - `caution_badge`: bool
- [ ] Integriere `RiskScorer`

### Task 3.3: Ranking Endpoint erweitern
**Datei:** `src/trading_engine/server.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 3.2 [P]  

- [ ] Erweitere `/ranking` Response:
  - Füge `risk_score` zu jedem Asset hinzu
  - Füge `risk_level` hinzu
- [ ] Sortiere nach Composite Score (wie bisher)

### Task 3.4: Regime Endpoint erweitern
**Datei:** `src/trading_engine/server.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 2.1 [P]  

- [ ] Erweitere `/regime` Response:
  - `defensive_mode`: bool
  - `position_limits`: dict (aktuelle Limits)

### Task 3.5: API Integration Tests
**Datei:** `tests/test_api_endpoints.py`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Tasks 3.1-3.4  

- [ ] Test: `test_portfolio_exposure_endpoint`
- [ ] Test: `test_predict_includes_risk_score`
- [ ] Test: `test_ranking_includes_risk_score`
- [ ] Test: `test_regime_includes_defensive_mode`

---

## Tag 4: Frontend Components

### Task 4.1: DefensiveModeBar Component
**Datei:** `frontend/src/components/DefensiveModeBar.jsx`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 3.4  

- [ ] Erstelle Component mit rotem Banner
- [ ] Sticky am oberen Rand
- [ ] Text: "🔴 DEFENSIVE MODE ACTIVE - Position limits reduced by 50%"
- [ ] Conditional Rendering basierend auf `defensive_mode`

### Task 4.2: DefensiveModeBar CSS
**Datei:** `frontend/src/components/DefensiveModeBar.css`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 4.1 [P]  

- [ ] Roter Hintergrund (#dc2626)
- [ ] Weißer Text
- [ ] Animation: Pulse
- [ ] Responsive

### Task 4.3: RiskBadge Component
**Datei:** `frontend/src/components/RiskBadge.jsx`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 3.2  

- [ ] Badge mit Risk Score (0-100)
- [ ] Farbkodierung:
  - Grün (#22c55e): 0-40
  - Gelb (#eab308): 41-70
  - Rot (#ef4444): 71-100
- [ ] Tooltip mit Breakdown (Volatilität, Drawdown, Korrelation)

### Task 4.4: RiskBadge CSS
**Datei:** `frontend/src/components/RiskBadge.css`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 4.3 [P]  

- [ ] Badge Styling (rounded, compact)
- [ ] Hover-State für Tooltip
- [ ] Dark Mode Support

---

## Tag 5: Frontend Integration

### Task 5.1: ExposureChart Component
**Datei:** `frontend/src/components/ExposureChart.jsx`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 3.1  

- [ ] Pie Chart mit Recharts
- [ ] Segmente: Equity (blau), Crypto (orange), Cash (grau)
- [ ] Limit-Linien anzeigen
- [ ] Warnung wenn Limit überschritten

### Task 5.2: StockRanking Integration
**Datei:** `frontend/src/components/StockRanking.jsx`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Tasks 4.3, 3.3  

- [ ] RiskBadge in Tabelle einbinden
- [ ] Neue Spalte: "Risk"
- [ ] "High Risk" Badge für Score > 70

### Task 5.3: App.jsx Integration
**Datei:** `frontend/src/App.jsx`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Tasks 4.1, 5.1  

- [ ] DefensiveModeBar importieren
- [ ] Conditional Rendering am Top
- [ ] ExposureChart in Dashboard einbinden

---

## Tag 6: Testing & Deployment

### Task 6.1: Frontend Tests
**Datei:** `frontend/src/__tests__/RiskManagement.test.jsx`  
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Tasks 4.1-5.3  

- [ ] Test: DefensiveModeBar zeigt bei RISK_OFF
- [ ] Test: RiskBadge Farbkodierung korrekt
- [ ] Test: ExposureChart zeigt Warnungen

### Task 6.2: End-to-End Test
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 6.1  

- [ ] Server starten
- [ ] Frontend laden
- [ ] Prüfen: Risk Scores in Ranking sichtbar
- [ ] Prüfen: Defensive Mode bei RISK_OFF

### Task 6.3: Git Commit & Push
**Status:** ⬜ Not Started  
**Abhängigkeiten:** Task 6.2  

- [ ] `git add -A`
- [ ] `git commit -m "feat: Phase 4 Risk Management complete"`
- [ ] `git push origin main`
- [ ] Requirements-Dokument updaten

---

## Zusammenfassung

| Tag | Tasks | Fokus |
|-----|-------|-------|
| 1 | 1.1, 1.2, 1.3 | Risk Scoring Backend |
| 2 | 2.1, 2.2 | Market Regime Erweiterung |
| 3 | 3.1, 3.2, 3.3, 3.4, 3.5 | API Endpoints |
| 4 | 4.1, 4.2, 4.3, 4.4 | Frontend Components |
| 5 | 5.1, 5.2, 5.3 | Frontend Integration |
| 6 | 6.1, 6.2, 6.3 | Testing & Deployment |

**Total Tasks:** 19  
**Parallel-fähig:** 4 (markiert mit [P])
