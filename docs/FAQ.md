# ❓ FAQ - Häufig gestellte Fragen

**Letzte Aktualisierung:** 2. Januar 2026

---

## 🚀 Getting Started

### Q: Wie starte ich die App?

**A:** Zwei Möglichkeiten:

**Option 1: Automatisch (Empfohlen)**

```bash
./scripts/start_servers.sh
```

**Option 2: Manuell**

```bash
# Terminal 1: Backend
python -m uvicorn src.trading_engine.api.server:app --reload

# Terminal 2: Frontend  
cd frontend && npm run dev
```

Dann öffne: <http://localhost:5173>

---

### Q: Installation schlägt fehl - was tun?

**A:** Checke Prerequisites:

```bash
# Python Version (braucht 3.10+)
python3 --version

# Node Version (braucht 18+)
node --version

# Installiere Dependencies
pip install -r requirements.txt
cd frontend && npm install
```

**Häufige Probleme:**

- `ModuleNotFoundError`: `pip install -r requirements.txt`
- `npm ERR!`: Lösche `node_modules/` und `npm install` nochmal
- Port 8000 belegt: `lsof -ti:8000 | xargs kill -9`

---

## 💰 Trading Questions

### Q: Wie finde ich die besten Stocks zum Kaufen?

**A:** 3-Schritt Prozess:

1. **Buy Opportunities Tab** öffnen
2. Sortiere nach **Confidence** (höchste zuerst)
3. Kaufe Top 3-5 mit:
   - Confidence > 75%
   - Strong/Moderate Momentum
   - Bekannte Companies

**Beispiel:**

```
✅ AAPL - BUY - 87% - Strong Momentum  ← KAUFEN
✅ MSFT - BUY - 82% - Moderate Momentum ← KAUFEN
⚠️ XYZ  - BUY - 65% - Weak Momentum    ← SKIP (zu riskant)
```

---

### Q: Was bedeutet "Confidence"?

**A:** Die Wahrscheinlichkeit dass die Prediction stimmt.

- **80%+**: Hohe Sicherheit - Trade wahrscheinlich
- **60-79%**: Moderate Sicherheit - vorsichtig sein
- **<60%**: Niedrige Sicherheit - besser skippen

**ML Model Accuracy:** 75% historisch  
→ Von 100 BUY Signals sind ~75 richtig

---

### Q: Wann soll ich verkaufen?

**A:** Sell wenn:

1. **Profit Target erreicht**: +10-15% Gewinn
2. **Signal wechselt zu SELL**: App zeigt jetzt "SELL"
3. **Stop Loss getroffen**: -5% Verlust
4. **Zeit abgelaufen**: Nach 7-14 Tagen, nimm Profit/Verlust

**Never:**

- Halten während Verlust und hoffen
- Verkaufen bei kleinem Dip (-1-2%)
- FOMO kaufen wenn schon +20%

---

### Q: Wie viel Geld soll ich pro Trade investieren?

**A:** **Max 5% deines Kapitals pro Trade.**

**Beispiel:**

```
Portfolio: $10,000

Per Trade Max: $500 (5%)
Number of Stocks: 10-20
Per Stock: $500-1,000

→ Diversification schützt dich
→ Ein Verlust = nur -5% Portfolio
```

**Conservative:** 3-4% per trade  
**Aggressive:** 5-7% per trade (höheres Risiko)

---

### Q: Kann ich mit dieser App echtes Geld traden?

**A:** **NEIN - nur Simulation aktuell.**

Die App ist für:

- ✅ Paper Trading (Fake Money)
- ✅ Strategy Testing
- ✅ Learning

**Für Real Trading:**

1. Nutze Simulation um Strategy zu testen
2. Wenn profitabel nach 2-3 Monaten
3. Öffne Account bei Broker (Robinhood, IBKR, etc.)
4. Copy Trades manuell von App zu Broker

**Future:** Direct Broker Integration geplant (Q2 2026)

---

## 📊 Technical Questions

### Q: Wie funktioniert die ML Prediction?

**A:** 3-stufiger Prozess:

```
1. Data Collection
   - Download historical prices (Yahoo Finance)
   - 2 Jahre Daten für jeden Stock

2. Feature Engineering
   - Berechne 40+ technische Indikatoren
   - RSI, MACD, Bollinger Bands, etc.

3. ML Model (XGBoost)
   - Trained auf 1000+ Stocks
   - Predicts: BUY (1) oder SELL (0)
   - Output: Confidence Score
```

**Model Performance:**

- Accuracy: 75%
- Precision: 78%
- Recall: 72%
- F1 Score: 0.75

---

### Q: Warum ist /ranking so langsam?

**A:** Yahoo Finance API ist langsam.

**Current:** 20 Stocks × 2 Sekunden = 40 Sekunden  
**Fix in Progress:** Caching → 3 Sekunden

**Workaround:**

- Nutze Watchlists (nur deine Stocks)
- Check Crypto Rankings (schneller)
- Refresh nur 1× täglich

---

### Q: Wie aktuell sind die Daten?

**A:** Kommt drauf an:

| Data Type | Update Frequency | Freshness |
|-----------|------------------|-----------|
| Stock Prices | 5 min Cache | 5 min old |
| Crypto Prices | Real-time | <1 min old |
| ML Predictions | 15 min Cache | 15 min old |
| Rankings | On demand | Fresh |

**Für Day Trading:** Zu langsam (5 min delay)  
**Für Swing Trading:** Perfect (7-14 Tage holds)

---

## 🔧 Features & Functionality

### Q: Was ist der Unterschied zwischen Rankings und Opportunities?

**A:**

**Rankings:**

- Alle Stocks ranked nach Prediction
- Sortierbar nach verschiedenen Metriken
- Für Research & Exploration

**Opportunities:**

- Nur BUY Signals
- Nur Confidence >70%
- Für schnelle Entscheidungen

**Empfehlung:** Nutze Opportunities für Daily Checks

---

### Q: Wie erstelle ich eine Watchlist?

**A:**

```
1. Gehe zu "Watchlists" Tab
2. Click "New Watchlist"
3. Name: "My Picks"
4. Add Stocks:
   - Suche Ticker (z.B. AAPL)
   - Click "Add"
5. Save Watchlist

→ Jetzt siehst du nur deine Stocks
→ Schnellere Updates
→ Personalisiertes Tracking
```

---

### Q: Kann ich eigene Strategies backtesten?

**A:** **Ja, via Simulation.**

**Example:**

```
Strategy: "Buy Top 5 Monthly"

1. Create Simulation: $10,000
2. Check Buy Opportunities
3. Buy Top 5 with Confidence >80%
4. Hold 30 days
5. Sell all
6. Repeat

Track Results:
- Month 1: +8%
- Month 2: -2%
- Month 3: +12%
- Average: +6%/month

→ Strategy works? Use real money (small)
```

---

### Q: Gibt es Alerts für Price Changes?

**A:** **Aktuell NEIN, aber geplant.**

**Coming Soon (Q1 2026):**

- Price Alerts: "AAPL hit $200"
- Signal Alerts: "MSFT changed to SELL"
- Portfolio Alerts: "Your portfolio -5% today"

**Current Workaround:**

- Check App 1-2× täglich
- Set Google Finance alerts
- Use TradingView alerts

---

## 🐛 Troubleshooting

### Q: "Unable to connect to server" Error

**A:** Backend ist nicht gestartet.

**Fix:**

```bash
# Check ob Backend läuft
curl http://localhost:8000/health

# Wenn nicht:
python -m uvicorn src.trading_engine.api.server:app --reload

# Oder automatic:
./scripts/start_servers.sh
```

---

### Q: Buy Opportunities zeigt keine Results

**A:** Zwei mögliche Gründe:

**1. Yahoo Finance Rate Limit**

```bash
# Check Backend Logs
tail -f logs/backend.log | grep "Yahoo"

# Wenn Rate Limit:
→ Warte 5 Minuten
→ Nutze Crypto Rankings instead
```

**2. Alle Stocks sind SELL**

```bash
# Markt ist bearish
→ Normal bei Market Crash
→ Check Crypto stattdessen
→ Warte auf bullish Market
```

---

### Q: Simulation Portfolio stimmt nicht

**A:** Check:

1. **Trades ausgeführt?**
   - Gehe zu "Trade History"
   - Check ob Buy/Sell Orders da sind

2. **Genug Cash?**
   - Initial: $10,000
   - Nach Buys: Cash reduziert
   - Can't buy wenn nicht genug Cash

3. **Prices updated?**
   - Click "Refresh Portfolio"
   - Prices update nur bei Page Load

---

### Q: Crypto Rankings laden nicht

**A:** CoinGecko API Issue.

**Check:**

```bash
# Test API direkt
curl http://localhost:8000/crypto/ranking

# Wenn Error:
→ CoinGecko Rate Limit (30 requests/min)
→ Warte 1-2 Minuten
→ Refresh Page
```

---

## 💻 Development Questions

### Q: Wie kann ich zur Development beitragen?

**A:** See [CONTRIBUTING.md](../CONTRIBUTING.md)

**Quick Start:**

```bash
1. Fork Repository
2. Create Branch: git checkout -b feature/my-feature
3. Make Changes
4. Run Tests: pytest tests/ -v
5. Commit: git commit -m "feat: Add feature"
6. Push: git push origin feature/my-feature
7. Create Pull Request
```

---

### Q: Wo sind die Tests?

**A:**

```
tests/
├── test_trading.py          # ML predictions
├── test_api_endpoints.py    # API contracts
├── test_simulation.py       # Trading logic
├── test_crypto.py          # Crypto features
└── test_server.py          # Server basics

Run: pytest tests/ -v
```

**Current Coverage:** ~65% (need improvement)

---

### Q: Wie deploye ich in Production?

**A:** See [DEPLOYMENT.md](deployment/DEPLOYMENT_GUIDE.md)

**Quick Deploy:**

```bash
# Backend: Railway
railway up

# Frontend: Vercel  
vercel --prod

# Oder automatic:
./scripts/deploy_production.sh
```

---

## 🔐 Security & Privacy

### Q: Sind meine Daten sicher?

**A:** **Aktuell: Alle Daten lokal.**

- ✅ Keine Cloud Upload
- ✅ SQLite Database lokal
- ✅ Keine User Accounts
- ✅ Keine Personal Data gespeichert

**In Production:** Nutze HTTPS, encrypted Database

---

### Q: Brauche ich einen API Key?

**A:** **NEIN für basic Features.**

**Optional API Keys:**

```
OpenAI (für AI Analysis):
  - Get: https://platform.openai.com
  - Set: OPENAI_API_KEY in .env
  - Cost: ~$5-10/month

CoinGecko Pro (für mehr Crypto Data):
  - Get: https://coingecko.com/api
  - Set: COINGECKO_API_KEY in .env
  - Cost: $0 (Free tier) oder $129/month (Pro)
```

---

### Q: Kann jemand meine Trades sehen?

**A:** **NEIN - alles ist privat.**

- Simulations: Nur lokal
- Watchlists: Nur lokal
- Kein Social Features aktuell

**Future:** Optional Public Leaderboards (Opt-in)

---

## 📱 Mobile & Access

### Q: Gibt es eine Mobile App?

**A:** **Nicht yet, aber geplant.**

**Current:**

- ✅ Web App ist mobile-responsive
- ✅ Funktioniert im Browser (Chrome, Safari)
- ⚠️ Nicht optimiert für Mobile

**Future (Q2 2026):**

- React Native App (iOS + Android)
- Push Notifications
- Offline Mode

---

### Q: Kann ich von überall zugreifen?

**A:** **Kommt drauf an:**

**Development (localhost):**

- ❌ Nur auf deinem Computer
- ❌ Nicht von Phone/Tablet

**Production (deployed):**

- ✅ Vercel URL: <https://your-app.vercel.app>
- ✅ Von überall mit Internet
- ✅ Mobile Browser funktioniert

---

## 💡 Best Practices

### Q: Wie oft soll ich die App checken?

**A:** **Kommt auf Strategy an:**

**Day Trading:**

- ❌ APP IST NICHT DAFÜR GEBAUT
- Data ist 5-15 min alt
- Zu langsam für intraday

**Swing Trading (7-14 Tage):**

- ✅ 1-2× täglich checken
- Morning: Check Opportunities
- Evening: Update Portfolio

**Long-term (Monate):**

- ✅ 1× pro Woche
- Check Rankings
- Rebalance monatlich

---

### Q: Soll ich allen Signals folgen?

**A:** **NEIN - nur High Confidence.**

**Filter:**

```
✅ Follow:
- Confidence >80%
- Strong Momentum
- Bekannte Companies
- Multiple Indicators align

❌ Skip:
- Confidence <70%
- Weak Momentum
- Unknown Companies
- Conflicting Signals
```

---

### Q: Wie lerne ich mehr über Trading?

**A:** **Resources:**

**Books:**

- "A Random Walk Down Wall Street" (Malkiel)
- "The Intelligent Investor" (Graham)
- "Trading for a Living" (Elder)

**Courses:**

- Udemy: "Stock Trading" Courses
- Coursera: "Financial Markets" (Yale)
- YouTube: "Rayner Teo", "The Chart Guys"

**Practice:**

- Use THIS App für Simulation
- Paper Trade 3-6 Monate
- Join Trading Communities

---

## 🆘 Still Need Help?

**Not finding your answer?**

1. **Search Documentation:**
   - [Trader Guide](TRADER_GUIDE.md)
   - [Technical Docs](technical/)
   - [Architecture](technical/ARCHITECTURE.md)

2. **Check GitHub Issues:**
   - Existing Issues: Maybe already answered
   - Create New Issue: We'll help

3. **Contact:**
   - Email: <support@marketpredictor.com> (planned)
   - Discord: Join Community (planned)

---

**Last Updated:** 2. Januar 2026  
**Version:** 1.0.0
