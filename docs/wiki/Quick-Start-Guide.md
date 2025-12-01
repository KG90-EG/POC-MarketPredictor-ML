# Quick Start Guide

Get POC-MarketPredictor-ML up and running in **5 minutes**!

---

## Prerequisites

Before you begin, make sure you have:

- ✅ **Python 3.10 - 3.12** (recommended)
  - Check: `python --version`
  - Download: [python.org](https://www.python.org/downloads/)

- ✅ **Node.js 18+** (for frontend)
  - Check: `node --version`
  - Download: [nodejs.org](https://nodejs.org/)

- ✅ **Git** (for cloning)
  - Check: `git --version`
  - Download: [git-scm.com](https://git-scm.com/)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML
```

---

## Step 2: Install Backend Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- scikit-learn & XGBoost (ML models)
- yfinance (stock data)
- Redis (caching)
- And more...

**Note**: This may take 2-3 minutes.

---

## Step 3: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

This installs:
- React and React-DOM
- Vite (build tool)
- Axios (HTTP client)
- React Query (state management)
- And more...

**Note**: This may take 1-2 minutes.

---

## Step 4: Start the Backend

Open a terminal and run:

```bash
uvicorn trading_fun.server:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal open!**

---

## Step 5: Start the Frontend

Open a **new terminal** (keep the backend running) and run:

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.4.21  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## Step 6: Open Your Browser

Navigate to: **http://localhost:5173**

You should see the POC-MarketPredictor-ML interface! 🎉

---

## Step 7: Explore the Application

### Select a Market View
At the top of the page, you'll see market buttons:
- 🌐 **Global** (US large-caps)
- 🇺🇸 **United States**
- 🇨🇭 **Switzerland**
- 🇩🇪 **Germany**
- ... and more

Click any market to load stock rankings.

### View Stock Rankings
The table shows:
- **Rank** - Position (1-30)
- **Ticker** - Stock symbol
- **Company** - Full company name
- **Country** - Domicile
- **Signal** - Buy/Sell recommendation
- **Probability** - ML confidence (0-100%)
- **Price** - Current price
- **Change %** - Daily change
- **Volume** - Trading volume
- **Market Cap** - Company valuation

### Click on a Stock
Click any row to see detailed information:
- Trading signal with color coding
- Company name and country
- Price information (current, change, 52-week range)
- Market data (cap, volume, P/E ratio)
- ML probability
- Detailed recommendation

### Try the Search
Enter a stock symbol (e.g., "AAPL", "MSFT", "TSLA") and click Search or press Enter.

### Refresh Data
Click the "Refresh Rankings" button to get the latest data.

---

## Optional: Enable AI Analysis

Want AI-powered recommendations? Set up OpenAI integration:

### 1. Get an OpenAI API Key
- Visit [platform.openai.com](https://platform.openai.com/)
- Sign up or log in
- Go to API Keys section
- Create a new key

### 2. Set Environment Variable

**macOS/Linux**:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Windows (PowerShell)**:
```powershell
$env:OPENAI_API_KEY='your-api-key-here'
```

**Or create a `.env` file**:
```bash
# Copy example file
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor

# Add your key
OPENAI_API_KEY=sk-proj-your-key-here
```

### 3. Restart Backend
Stop the backend (CTRL+C) and start it again:
```bash
uvicorn trading_fun.server:app --reload
```

### 4. Use AI Analysis
In the UI, click "Get AI Recommendations" button to get detailed analysis!

---

## Optional: Enable Redis Caching

For better performance with Redis caching:

### 1. Install Redis

**macOS** (with Homebrew):
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Windows**:
Download from [redis.io](https://redis.io/download) or use Docker:
```bash
docker run -d -p 6379:6379 redis:latest
```

### 2. Configure Redis URL
Add to `.env` file:
```bash
REDIS_URL=redis://localhost:6379/0
```

### 3. Restart Backend
Redis will now be used for caching! Check the health endpoint to confirm:
```bash
curl http://localhost:8000/health
```

You should see `"cache_backend": "redis"`.

---

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

---

**Error**: `Address already in use`

**Solution**: Port 8000 is occupied. Either:
1. Stop the other process using port 8000
2. Or use a different port:
```bash
uvicorn trading_fun.server:app --reload --port 8001
```

And update frontend `.env` file:
```bash
VITE_API_URL=http://localhost:8001
```

---

### Frontend Won't Start

**Error**: `command not found: npm`

**Solution**: Install Node.js from [nodejs.org](https://nodejs.org/)

---

**Error**: `Port 5173 is already in use`

**Solution**: Vite will automatically try the next available port (5174, 5175, etc.). Check the terminal output for the actual URL.

---

### No Data Loading

**Error**: Rankings table shows "Loading..." forever

**Possible causes**:
1. **Backend not running** - Make sure backend terminal is open and running
2. **Wrong API URL** - Check `frontend/.env` (should be `http://localhost:8000`)
3. **Network error** - Check browser console for errors (F12)

**Solution**:
1. Verify backend is running: visit http://localhost:8000/health
2. Check frontend console for errors
3. Restart both backend and frontend

---

### API Rate Limit

**Error**: "Too many requests" or 429 status

**Solution**: Default rate limit is 60 requests per minute. Wait a bit or increase the limit:

Add to `.env`:
```bash
RATE_LIMIT_RPM=120
```

And restart backend.

---

### yfinance Data Issues

**Error**: Some stocks show "N/A" for data

**Cause**: yfinance API may not have complete data for all stocks

**Solution**: This is normal. The app handles missing data gracefully. Some tickers may be delisted or have incomplete information.

---

## Next Steps

Now that you're up and running:

1. **Explore Features**:
   - Try different market views
   - Search for specific stocks
   - Toggle dark/light theme
   - Check the health status indicator

2. **Read Documentation**:
   - [Using the Application](Using-the-Application.md) - Full user guide
   - [Understanding Trading Signals](Understanding-Trading-Signals.md) - How signals work
   - [API Reference](API-Reference.md) - API documentation

3. **Customize**:
   - Review [Configuration](Configuration.md) guide
   - Set up Redis for better performance
   - Enable OpenAI for AI analysis
   - Adjust rate limits and cache TTLs

4. **Deploy** (optional):
   - [Deployment Guide](Deployment-Guide.md) - Production deployment
   - [Docker Deployment](Docker-Deployment.md) - Container deployment

5. **Contribute**:
   - [Contributing Guide](Contributing-Guide.md) - Help improve the project
   - [BACKLOG.md](../../BACKLOG.md) - See open tasks

---

## Quick Command Reference

### Backend
```bash
# Start server
uvicorn trading_fun.server:app --reload

# Start with different port
uvicorn trading_fun.server:app --reload --port 8001

# Run tests
pytest

# Run with coverage
pytest --cov=trading_fun

# Lint code
flake8 .

# Format code
black .
```

### Frontend
```bash
# Start dev server
cd frontend && npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

### Docker
```bash
# Build image
docker build -t trading-fun:latest .

# Run container
docker run -p 8000:8000 trading-fun:latest

# Use docker-compose
docker-compose up
docker-compose down
```

---

## Common Configuration

### .env File Template
```bash
# Backend
PROD_MODEL_PATH=models/prod_model.bin
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
RATE_LIMIT_RPM=60
REDIS_URL=redis://localhost:6379/0

# MLflow (optional)
MLFLOW_TRACKING_URI=file:./mlruns
S3_BUCKET=your-bucket-name
```

### frontend/.env File
```bash
VITE_API_URL=http://localhost:8000
```

---

## Health Check

Verify everything is working:

### Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_path": "models/prod_model.bin",
  "openai_available": true,
  "cache_backend": "redis",
  "redis_status": "connected",
  "timestamp": 1701234567.89
}
```

### Frontend
Visit: http://localhost:5173

You should see the application interface.

### Test API
```bash
# Get rankings
curl http://localhost:8000/ranking?country=Global

# Get stock info
curl http://localhost:8000/ticker_info/AAPL

# Get metrics
curl http://localhost:8000/metrics
```

---

## Getting Help

If you're stuck:

1. **Check Documentation**: Most questions are answered in the [wiki](Home.md)
2. **Search Issues**: Someone may have had the same problem
3. **Ask for Help**: Create a [GitHub issue](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
4. **Check Logs**: Look at terminal output for error messages

---

## What's Next?

Congratulations! You now have POC-MarketPredictor-ML running locally. 🎉

### Recommended Reading
- **[What is POC-MarketPredictor-ML?](What-is-POC-MarketPredictor-ML.md)** - Understand what it does and how it works
- **[Using the Application](Using-the-Application.md)** - Full user guide
- **[Understanding Trading Signals](Understanding-Trading-Signals.md)** - How to interpret recommendations
- **[API Reference](API-Reference.md)** - Complete API documentation

### Try These Features
- ✅ Multi-market selection
- ✅ Real-time search
- ✅ Company detail sidebar
- ✅ Dark/light theme toggle
- ✅ Health status monitoring
- ✅ AI-powered analysis (with OpenAI key)

### Deploy to Production
Ready to deploy? Check out:
- **[Deployment Guide](Deployment-Guide.md)** - Production deployment
- **[Docker Deployment](Docker-Deployment.md)** - Container deployment
- **[Production Checklist](Production-Checklist.md)** - Pre-deployment checklist

---

*Happy trading! 📈*

---

*Last updated: December 1, 2025*
