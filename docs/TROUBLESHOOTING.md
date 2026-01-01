# Troubleshooting Guide - POC-MarketPredictor-ML

Last Updated: January 2026

---

## 🔧 Common Issues & Solutions

### Backend Issues

#### 1. Server Won't Start - ModuleNotFoundError

**Error:**

```
ModuleNotFoundError: No module named 'trading_fun'
```

**Solution:**

```bash
# Run from project root, not from trading_fun directory
cd /path/to/POC-MarketPredictor-ML
python -m trading_fun.server
```

**Alternative:** Add project root to PYTHONPATH

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python trading_fun/server.py
```

---

#### 2. Import Error - market_predictor vs trading_fun

**Error:**

```
ImportError: attempted relative import with no known parent package
```

**Cause:** Mixed imports between `market_predictor/` and `trading_fun/`

**Solution:**
Run server as module:

```bash
python -m trading_fun.server
```

**Long-term Fix:** Consolidate to single module (in backlog)

---

#### 3. Database Locked Error

**Error:**

```
sqlite3.OperationalError: database is locked
```

**Solutions:**

1. **Close other connections:**

   ```bash
   # Find processes using the database
   lsof data/market_predictor.db

   # Kill if necessary
   kill -9 <PID>
   ```

2. **Increase timeout:**

   ```python
   # In simulation_db.py or database.py
   conn = sqlite3.connect('database.db', timeout=30.0)
   ```

3. **Use PostgreSQL** (recommended for production)

---

#### 4. Missing joblib Module

**Error:**

```
ModuleNotFoundError: No module named 'joblib'
```

**Solution:**

```bash
pip install joblib
# Or reinstall all requirements
pip install -r requirements.txt
```

---

#### 5. Port 8000 Already in Use

**Error:**

```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```

**Solutions:**

1. **Find and kill process:**

   ```bash
   # macOS/Linux
   lsof -i :8000
   kill -9 <PID>

   # Or use different port
   uvicorn trading_fun.server:app --port 8001
   ```

2. **Start on different port:**

   ```bash
   python -m trading_fun.server --port 8001
   ```

---

### Frontend Issues

#### 6. Frontend Won't Start - Port 5173 in Use

**Error:**

```
Port 5173 is in use, trying another one...
```

**Solution:**

```bash
# Kill process on port 5173
lsof -i :5173
kill -9 <PID>

# Or let Vite auto-assign port (it will tell you which port it uses)
```

---

#### 7. API Connection Refused

**Error in Browser Console:**

```
Error: Network Error
AxiosError: Request failed with status code 0
```

**Checklist:**

1. ✅ Backend running on port 8000?

   ```bash
   curl http://localhost:8000/health
   ```

2. ✅ Correct API URL in frontend?

   ```javascript
   // frontend/src/api.js
   const API_BASE_URL = 'http://localhost:8000'
   ```

3. ✅ CORS enabled in backend?

   ```python
   # trading_fun/server.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       ...
   )
   ```

---

#### 8. SimulationDashboard Errors

**Error:**

```
Unexpected token (142:6)
Promise.all async/await error
```

**Solution:**
Already fixed in latest version. Update code:

```javascript
// WRONG:
await Promise.all([
  loadTradeHistory(currentSim.simulation_id),
  loadSimulation(currentSim.simulation_id)
]);

// CORRECT:
await loadTradeHistory(currentSim.simulation_id);
await loadSimulation(currentSim.simulation_id);
```

---

### CI/CD Issues

#### 9. GitHub Actions - Missing Secrets Warning

**Warning:**

```
Context access might be invalid: AWS_ACCESS_KEY_ID
```

**Not an Error!** This is a warning, CI still passes.

**To Fix (Optional):**

1. Go to GitHub repo → Settings → Secrets → Actions
2. Add required secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `S3_BUCKET`
   - `NETLIFY_AUTH_TOKEN`
   - `NETLIFY_SITE_ID`
   - etc.

See `.github/workflows/ci.yml` for full list.

---

#### 10. Pre-commit Hooks Failing

**Error:**

```
detect-secrets...........Failed
- hook id: detect-secrets
- exit code: 1
```

**Solution:**

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Regenerate secrets baseline
detect-secrets scan > .secrets.baseline

# Try commit again
git add .
git commit -m "Your message"
```

---

### Database & Data Issues

#### 11. Simulation Not Found

**Error:**

```
404: Simulation not found
```

**Debugging:**

```python
# Check if simulation exists
import sqlite3
conn = sqlite3.connect('data/market_predictor.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM simulations")
print(cursor.fetchall())
```

**Common Causes:**

- Database was reset
- Wrong simulation_id
- User isolation not implemented yet

---

#### 12. Trade History Empty

**Issue:** No trades showing despite executing trades

**Debugging:**

```python
# Check trades table
cursor.execute("SELECT * FROM trades WHERE simulation_id = ?", (sim_id,))
print(cursor.fetchall())
```

**Common Causes:**

- Trades not committed to database
- Frontend fetching wrong simulation_id
- Database transaction not committed

---

### Performance Issues

#### 13. Slow API Responses

**Symptoms:** Requests taking > 5 seconds

**Solutions:**

1. **Enable caching:**

   ```bash
   # Set REDIS_URL in .env
   export REDIS_URL="redis://localhost:6379"
   ```

2. **Check external API calls:**

   ```python
   # Add logging to see what's slow
   with RequestLogger("/ranking") as logger:
       # Your code
       logger.log_metric("external_api_time", duration)
   ```

3. **Reduce data fetching:**
   - Limit number of tickers in ranking
   - Use cached predictions
   - Implement pagination

---

#### 14. Memory Issues

**Error:**

```
MemoryError: Unable to allocate array
```

**Solutions:**

1. **Limit concurrent simulations:**

   ```python
   # In server.py
   MAX_SIMULATIONS_PER_USER = 5
   ```

2. **Clear old simulations:**

   ```sql
   DELETE FROM simulations
   WHERE created_at < datetime('now', '-30 days');
   ```

3. **Use generator for large datasets:**

   ```python
   # Instead of loading all at once
   for chunk in pd.read_csv('data.csv', chunksize=1000):
       process(chunk)
   ```

---

### Deployment Issues

#### 15. Docker Build Fails

**Error:**

```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

**Solutions:**

1. **Check Dockerfile syntax:**

   ```dockerfile
   # Make sure requirements.txt exists
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   ```

2. **Build with no cache:**

   ```bash
   docker build --no-cache -t market_predictor:latest .
   ```

---

#### 16. Railway/Render Deployment Fails

**Common Issues:**

1. **Wrong start command:**

   ```bash
   # Correct for Railway/Render:
   python -m trading_fun.server

   # NOT:
   uvicorn market_predictor.server:app
   ```

2. **Missing environment variables:**
   - Add all required vars in platform settings
   - Check `.env.example` for required vars

3. **Health check failing:**
   - Verify `/health` endpoint works locally
   - Check health check URL in platform settings

---

## 🔍 Debugging Tools

### Backend Debugging

#### Enable Debug Logging

```python
# In trading_fun/logging_config.py
setup_logging(log_level="DEBUG")
```

#### Check Database State

```bash
# Install sqlite3 CLI
brew install sqlite3  # macOS
apt-get install sqlite3  # Ubuntu

# Inspect database
sqlite3 data/market_predictor.db
.tables
.schema simulations
SELECT * FROM simulations LIMIT 5;
```

#### Monitor API Calls

```bash
# Use httpie for testing
http GET http://localhost:8000/health
http POST http://localhost:8000/api/simulations user_id=test initial_capital=10000
```

### Frontend Debugging

#### React DevTools

Install browser extension:

- Chrome: [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/)
- Firefox: [React Developer Tools](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

#### Network Tab

Check API calls in browser DevTools:

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "XHR" or "Fetch"
4. Check request/response details

#### Console Logging

```javascript
// Add to components for debugging
console.log('Current simulation:', currentSim);
console.log('Portfolio data:', portfolio);
console.log('API response:', response.data);
```

---

## 📞 Getting Help

If your issue isn't listed here:

1. **Check Logs:**
   - Backend: Console output or log files
   - Frontend: Browser console (F12)

2. **Search GitHub Issues:**
   [Existing Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

3. **Create New Issue:**
   Include:
   - Error message (full stack trace)
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)
   - What you've already tried

4. **Community Discussion:**
   [GitHub Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)

---

## 🛠️ Quick Fixes Checklist

Before reporting an issue, try these:

- [ ] Restart backend and frontend
- [ ] Clear browser cache
- [ ] Delete `node_modules` and `npm install` again
- [ ] Check all required environment variables are set
- [ ] Verify database file exists and is not corrupted
- [ ] Check no processes are using the ports
- [ ] Try running with fresh database (backup first!)
- [ ] Update all dependencies (`pip install -U -r requirements.txt`)
- [ ] Check disk space
- [ ] Review recent code changes

---

**Last Resort:** Try starting from scratch with fresh install:

```bash
# Backup your data first!
mv data data.backup
git pull
rm -rf .venv node_modules frontend/node_modules
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
python -m trading_fun.server
```
