# Troubleshooting Guide

Common issues and solutions for Market Predictor ML.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Backend Problems](#backend-problems)
- [Frontend Issues](#frontend-issues)
- [API Connection Problems](#api-connection-problems)
- [Docker Issues](#docker-issues)
- [Performance Problems](#performance-problems)
- [Data & API Issues](#data--api-issues)

---

## Installation Issues

### Python Dependencies Won't Install

**Problem:** `pip install -r requirements.txt` fails

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

3. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

4. **Install system dependencies (macOS):**
   ```bash
   brew install python@3.9
   ```

### Node Modules Installation Fails

**Problem:** `npm install` fails in frontend directory

**Solutions:**

1. **Check Node version:**
   ```bash
   node --version  # Should be 18 or higher
   ```

2. **Clear npm cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Use correct Node version:**
   ```bash
   nvm install 18
   nvm use 18
   npm install
   ```

### Missing Environment Variables

**Problem:** Application crashes with "Environment variable not set"

**Solution:**

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Add required variables:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ALPHA_VANTAGE_API_KEY=your-key-here  # Optional
   ```

3. **Verify environment loading:**
   ```bash
   python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

---

## Backend Problems

### Backend Won't Start

**Problem:** `python -m market_predictor.server` fails

**Solutions:**

1. **Check if port 8000 is in use:**
   ```bash
   lsof -i :8000
   kill -9 <PID>  # Kill process using port
   ```

2. **Check for import errors:**
   ```bash
   python -c "import market_predictor"
   ```

3. **Verify OpenAI API key:**
   ```bash
   python -c "import os; from openai import OpenAI; print('OpenAI configured')"
   ```

4. **Check logs:**
   ```bash
   tail -f logs/app.log  # If logging to file
   ```

### Model Loading Fails

**Problem:** "Model failed to load" error

**Solutions:**

1. **Check model file exists:**
   ```bash
   ls -la models/
   ```

2. **Retrain model:**
   ```bash
   python training/trainer.py
   ```

3. **Check model permissions:**
   ```bash
   chmod 644 models/*.pkl
   ```

### Health Check Fails

**Problem:** `/health` endpoint returns 500 error

**Diagnostic:**
```bash
curl http://localhost:8000/health
```

**Solutions:**

1. **Check OpenAI configuration:**
   - Verify API key is set
   - Test OpenAI connection:
     ```bash
     python -c "from openai import OpenAI; client = OpenAI(); print('OK')"
     ```

2. **Check model status:**
   - Ensure model file exists
   - Verify model is not corrupted

3. **Review server logs:**
   ```bash
   # Check for detailed error messages
   python -m market_predictor.server 2>&1 | tee server.log
   ```

---

## Frontend Issues

### Frontend Won't Start

**Problem:** `npm run dev` fails

**Solutions:**

1. **Check if port 5173 is in use:**
   ```bash
   lsof -i :5173
   kill -9 <PID>
   ```

2. **Clear Vite cache:**
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```

3. **Reinstall dependencies:**
   ```bash
   rm -rf node_modules
   npm install
   ```

### Blank Page or React Errors

**Problem:** Frontend loads but shows blank page

**Solutions:**

1. **Check browser console:**
   - Open DevTools (F12)
   - Look for JavaScript errors
   - Check Network tab for failed requests

2. **Verify API connection:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (macOS)

4. **Check for compilation errors:**
   ```bash
   npm run build
   ```

### Styles Not Loading

**Problem:** Application appears unstyled

**Solutions:**

1. **Check CSS file:**
   ```bash
   ls -la frontend/src/styles.css
   ```

2. **Verify import in main files:**
   - Check `main.jsx` imports `styles.css`

3. **Clear Vite cache:**
   ```bash
   rm -rf node_modules/.vite
   npm run dev
   ```

---

## API Connection Problems

### CORS Errors

**Problem:** "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solutions:**

1. **Check backend CORS settings in `server.py`:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Verify frontend is running on correct port:**
   ```bash
   # Frontend should be on 5173
   curl http://localhost:5173
   ```

3. **Restart backend after CORS changes**

### Connection Refused

**Problem:** "Failed to fetch" or "Connection refused"

**Diagnostic:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check if frontend can reach backend
curl -H "Origin: http://localhost:5173" http://localhost:8000/health
```

**Solutions:**

1. **Ensure backend is running:**
   ```bash
   python -m market_predictor.server
   ```

2. **Check firewall settings:**
   - Allow connections on ports 8000 and 5173

3. **Verify API URL in frontend:**
   - Check `frontend/src/api.js`
   - Should point to `http://localhost:8000`

### WebSocket Connection Fails

**Problem:** WebSocket connection drops or won't connect

**Solutions:**

1. **Check WebSocket endpoint:**
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/test');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (err) => console.error('Error:', err);
   ```

2. **Verify backend supports WebSocket:**
   - Check `server.py` has WebSocket routes
   - Ensure no proxy is blocking WebSocket upgrade

3. **Check browser WebSocket support:**
   ```javascript
   console.log('WebSocket' in window);
   ```

---

## Docker Issues

### Docker Build Fails

**Problem:** `docker-compose build` fails

**Solutions:**

1. **Check Dockerfile syntax:**
   ```bash
   docker build -t test .
   ```

2. **Clear Docker cache:**
   ```bash
   docker system prune -a
   docker-compose build --no-cache
   ```

3. **Check Docker daemon:**
   ```bash
   docker info
   ```

### Container Won't Start

**Problem:** Container exits immediately

**Solutions:**

1. **Check container logs:**
   ```bash
   docker-compose logs
   ```

2. **Run container interactively:**
   ```bash
   docker-compose run --rm web bash
   ```

3. **Verify environment variables:**
   ```bash
   docker-compose config
   ```

### Port Already in Use

**Problem:** "Port is already allocated"

**Solutions:**

1. **Check what's using the port:**
   ```bash
   lsof -i :8000
   ```

2. **Change port in docker-compose.yml:**
   ```yaml
   ports:
     - "8001:8000"  # Map to different host port
   ```

3. **Stop conflicting containers:**
   ```bash
   docker-compose down
   docker ps -a  # Check for other containers
   ```

---

## Performance Problems

### Slow API Response

**Problem:** API requests take too long

**Diagnostic:**
```bash
time curl http://localhost:8000/stocks?market=nasdaq
```

**Solutions:**

1. **Check cache configuration:**
   - Ensure caching is enabled in `pyproject.toml`
   - Verify cache TTL settings

2. **Monitor API rate limits:**
   - Alpha Vantage: 5 calls/minute (free tier)
   - CoinGecko: 10-50 calls/minute
   - OpenAI: Check your tier limits

3. **Optimize database queries:**
   - Review query patterns in `trading.py`

4. **Check system resources:**
   ```bash
   top  # Check CPU/memory usage
   ```

### High Memory Usage

**Problem:** Application uses excessive memory

**Solutions:**

1. **Check memory usage:**
   ```bash
   ps aux | grep python
   ```

2. **Limit cache size:**
   - Reduce TTL values in config
   - Implement cache size limits

3. **Profile memory usage:**
   ```bash
   pip install memory_profiler
   python -m memory_profiler market_predictor/server.py
   ```

### Frontend Lag

**Problem:** UI feels slow or unresponsive

**Solutions:**

1. **Check React DevTools Profiler:**
   - Install React DevTools browser extension
   - Profile component renders

2. **Optimize re-renders:**
   - Use `React.memo()` for expensive components
   - Implement proper key props in lists

3. **Reduce API polling frequency:**
   - Check `api.js` for polling intervals
   - Use WebSocket for real-time updates instead

---

## Data & API Issues

### No Stock Data Returned

**Problem:** API returns empty array or null

**Solutions:**

1. **Check API keys:**
   ```bash
   echo $ALPHA_VANTAGE_API_KEY
   ```

2. **Test external API directly:**
   ```bash
   curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=YOUR_KEY"
   ```

3. **Check rate limits:**
   - Alpha Vantage free tier: 5 calls/min, 500/day
   - Wait and retry

4. **Verify market parameter:**
   - Valid values: `ftse100`, `sp500`, `nasdaq`

### Cryptocurrency Data Not Loading

**Problem:** `/crypto` endpoint fails

**Solutions:**

1. **Test CoinGecko API:**
   ```bash
   curl "https://api.coingecko.com/api/v3/ping"
   ```

2. **Check CoinGecko rate limits:**
   - Free tier: 10-50 calls/minute
   - Consider implementing request queue

3. **Verify NFT filtering:**
   ```bash
   curl "http://localhost:8000/crypto?include_nft=false"
   ```

### AI Analysis Returns Errors

**Problem:** `/analyze` endpoint fails

**Solutions:**

1. **Verify OpenAI API key:**
   ```bash
   python -c "import os; print(len(os.getenv('OPENAI_API_KEY', '')))"
   ```

2. **Check OpenAI service status:**
   - Visit https://status.openai.com

3. **Review request context:**
   - Ensure context is not too long (< 4000 characters)
   - Check for special characters causing issues

4. **Check OpenAI rate limits:**
   - Depends on your API tier
   - Implement exponential backoff

---

## Common Error Messages

### "Model not found"

**Cause:** Model file doesn't exist or path is wrong

**Solution:**
```bash
python training/trainer.py  # Train new model
# Or check model path in config
```

### "OpenAI API key not configured"

**Cause:** Missing or invalid OPENAI_API_KEY

**Solution:**
```bash
export OPENAI_API_KEY=sk-your-key-here
# Or add to .env file
```

### "Cache initialization failed"

**Cause:** Cache configuration issue

**Solution:**
- Check `cache.py` configuration
- Verify cache directory permissions
- Disable caching temporarily to test: `CACHE_ENABLED=false`

### "Rate limit exceeded"

**Cause:** Too many API requests

**Solution:**
- Wait for rate limit window to reset
- Implement request queuing
- Upgrade API tier if needed

---

## Debug Mode

Enable debug mode for detailed logging:

**Backend:**
```bash
LOG_LEVEL=DEBUG python -m market_predictor.server
```

**Frontend:**
```javascript
// In api.js
const DEBUG = true;
```

---

## Getting Help

If you can't resolve your issue:

1. **Check existing issues:**
   - [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

2. **Create detailed bug report:**
   - Include error messages
   - Provide steps to reproduce
   - Share relevant logs
   - Specify OS and versions

3. **Include system information:**
   ```bash
   python --version
   node --version
   npm --version
   docker --version
   ```

4. **Share configuration (redact secrets):**
   ```bash
   cat pyproject.toml
   cat frontend/package.json
   ```

---

**Last Updated**: December 1, 2025
