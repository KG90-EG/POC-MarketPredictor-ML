# 🚀 Quick Start Guide

Get Market Predictor running in **5 minutes**!

---

## ⚡ Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** installed
- **Git** installed
- **15 minutes** of your time

---

## 📥 Step 1: Clone Repository

```bash
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML
```

---

## 🔧 Step 2: Backend Setup (2 minutes)

### Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Initialize Database

```bash
# Create data directory
mkdir -p data

# Initialize database
python -c "
from trading_fun.simulation_db import SimulationDB
db = SimulationDB()
db.initialize_db()
print('✓ Database initialized')
"
```

---

## 🎨 Step 3: Frontend Setup (2 minutes)

```bash
cd frontend

# Install dependencies
npm install

# Build frontend
npm run build

# Return to root
cd ..
```

---

## ▶️ Step 4: Start the Application (1 minute)

### Option A: Automated Start (Recommended)

```bash
# Start both servers with health checks
./scripts/start_servers.sh
```

**Features:**
- ✅ Automatic port cleanup
- ✅ Health check verification  
- ✅ Process management
- ✅ Detailed logging
- ✅ Status monitoring

**Expected output:**

```
ℹ Starting backend server on port 8000...
✓ Backend started successfully (PID: 12345)
ℹ Starting frontend server on port 5173...
✓ Frontend started successfully (PID: 12346)
✓ All servers started successfully!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Backend:  http://localhost:8000
✓ Frontend: http://localhost:5173
ℹ API Docs: http://localhost:8000/docs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Useful commands:**

```bash
./scripts/start_servers.sh --status    # Check server status
./scripts/start_servers.sh --stop      # Stop all servers
./scripts/start_servers.sh --help      # Show all options
```

### Option B: Manual Start

<details>
<summary>Click to expand manual start instructions</summary>

#### Terminal 1 - Backend Server

```bash
# Make sure you're in the project root with .venv activated
source .venv/bin/activate

# Start backend
python -m trading_fun.server
```

**Expected output:**

```
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://127.0.0.1:8000
```

✅ Backend is running on **<http://localhost:8000>**

#### Terminal 2 - Frontend Dev Server

```bash
cd frontend

# Start dev server
npm run dev
```

**Expected output:**

```
VITE v5.0.0  ready in 500 ms
➜  Local:   http://localhost:5173/
```

✅ Frontend is running on **<http://localhost:5173>**

</details>

---

## 🎯 Step 5: Access the Application

Open your browser and navigate to:

```
http://localhost:5173
```

You should see:

- ✅ Market Predictor Dashboard
- ✅ Health check showing "Backend Connected"
- ✅ Simulation controls
- ✅ Real-time crypto data

---

## 🧪 Quick Test

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-09T12:00:00",
  "version": "1.0.0"
}
```

### Test 2: Start a Simulation

1. Open **<http://localhost:5173>**
2. Select a crypto pair (e.g., BTC/USD)
3. Click **"Start Simulation"**
4. Watch real-time trades appear! 🎉

---

## 🐛 Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'trading_fun'`

**Fix:**

```bash
# Make sure you're in the project root
pwd  # Should show .../POC-MarketPredictor-ML

# Activate virtual environment
source .venv/bin/activate

# Verify Python path
python -c "import sys; print('\n'.join(sys.path))"
# Should include your project directory

# Try again
python -m trading_fun.server
```

---

### Frontend won't build

**Error:** `npm ERR! Missing script: "build"`

**Fix:**

```bash
cd frontend

# Verify package.json exists
cat package.json | grep '"build"'

# Clean install
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

### Port already in use

**Error:** `OSError: [Errno 48] Address already in use`

**Fix:**

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python -m trading_fun.server --port 8001
```

---

### Database errors

**Error:** `sqlite3.OperationalError: unable to open database file`

**Fix:**

```bash
# Create data directory
mkdir -p data
chmod 777 data

# Reinitialize database
python -c "
from trading_fun.simulation_db import SimulationDB
db = SimulationDB()
db.initialize_db()
"
```

---

### CORS errors in browser

**Error:** `Access to fetch at 'http://localhost:8000' blocked by CORS`

**Fix:**

1. Check backend is running on port 8000
2. Check `trading_fun/server.py` has CORS middleware:

   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Restart backend server

---

## 📚 Next Steps

### Explore Features

1. **Trading Simulation**
   - Navigate to Simulation Dashboard
   - Start automated trading
   - View real-time performance

2. **Watchlist**
   - Add crypto pairs to watchlist
   - Set price alerts
   - Monitor live prices

3. **Analytics**
   - View trading history
   - Check win/loss ratios
   - Analyze performance metrics

### Customize Settings

Edit `trading_fun/server.py`:

```python
# Change initial balance
INITIAL_BALANCE = 100000  # $100k

# Change trading fee
TRADING_FEE = 0.001  # 0.1%

# Change update interval
UPDATE_INTERVAL = 5  # 5 seconds
```

### Add API Keys (Optional)

For production use with real data:

1. Get API keys from [CoinGecko](https://www.coingecko.com/en/api)
2. Create `.env` file:

   ```bash
   COINGECKO_API_KEY=your_api_key_here
   RATE_LIMIT_REQUESTS=50
   ```

---

## 🔐 Security Notes

**For Development Only:**

- ⚠️ Default SQLite database (not for production)
- ⚠️ No authentication required
- ⚠️ CORS allows localhost only
- ⚠️ Debug mode enabled

**Before Production:**

- ✅ Set up PostgreSQL
- ✅ Add user authentication
- ✅ Configure proper CORS
- ✅ Disable debug mode
- ✅ Set up HTTPS

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup.

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Browser (Client)                    │
│                  http://localhost:5173                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         │ WebSocket
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI Server)                   │
│                  http://localhost:8000                  │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  trading.py  │  │  server.py   │  │ websocket.py │ │
│  │  (Trading    │  │  (API        │  │ (Real-time   │ │
│  │   Logic)     │  │  Endpoints)  │  │  Updates)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ SQL
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Database (SQLite)                          │
│               data/market_predictor.db                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🆘 Still Having Issues?

1. **Check logs:**

   ```bash
   # Backend logs
   tail -f logs/market_predictor.log

   # Frontend logs (in browser)
   F12 → Console tab
   ```

2. **Consult detailed guides:**
   - [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
   - [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System details
   - [CI_CD_FIX_GUIDE.md](docs/CI_CD_FIX_GUIDE.md) - Pipeline fixes

3. **Open an issue:**

   ```
   https://github.com/KG90-EG/POC-MarketPredictor-ML/issues/new
   ```

   Include:
   - Error message
   - What you've tried
   - Your OS and Python version

---

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized
- [ ] Frontend built (`npm run build`)
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Health check passes
- [ ] Can access dashboard at <http://localhost:5173>
- [ ] Can start a simulation

---

**🎉 Congratulations!** Your Market Predictor is now running!

For advanced features and production deployment, see the [full documentation](docs/).
