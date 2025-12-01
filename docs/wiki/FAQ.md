# Frequently Asked Questions (FAQ)

Quick answers to common questions about POC-MarketPredictor-ML.

---

## General Questions

### What is POC-MarketPredictor-ML?

POC-MarketPredictor-ML is a production-grade machine learning application that provides intelligent stock ranking, prediction, and AI-powered trading recommendations. It analyzes global markets using ML models and provides clear buy/sell/hold signals.

**Key Features**:
- ML-powered stock predictions
- 8 global market coverage
- Real-time market data
- AI-powered analysis (optional)
- Modern web interface

### Is this financial advice?

**No.** POC-MarketPredictor-ML is a tool to help you make informed decisions. It is **not** financial advice. Always:
- Do your own research
- Understand what you're investing in
- Consider consulting a financial advisor
- Only invest money you can afford to lose

### Is it free to use?

**Yes!** The application is open-source (MIT license) and free to use. However:
- **OpenAI API** (optional) requires an API key and has costs
- **Deploying to cloud** may incur hosting costs
- **yfinance data** is free but has informal rate limits

### Who should use this?

**Ideal for**:
- Individual investors seeking data-driven insights
- Portfolio managers analyzing multiple markets
- Developers building trading tools
- Data scientists studying ML in finance
- Students learning about financial ML

**Not ideal for**:
- Day traders (signals are for medium-term)
- Those seeking guaranteed returns
- Complete beginners without basic investment knowledge

---

## Technical Questions

### What programming languages are used?

**Backend**:
- Python 3.10+ (FastAPI, scikit-learn, XGBoost)

**Frontend**:
- JavaScript (React 18, Vite)

**Infrastructure**:
- Docker for containerization
- YAML for CI/CD (GitHub Actions)

### What are the system requirements?

**Minimum**:
- Python 3.10 or higher
- Node.js 18 or higher
- 4GB RAM
- 2GB free disk space

**Recommended**:
- Python 3.12
- Node.js 20
- 8GB RAM
- 5GB free disk space
- Redis for caching

**Operating Systems**:
- ✅ macOS (Intel & Apple Silicon)
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ Windows 10/11

### Can I run this on my laptop?

**Yes!** The application runs fine on a modern laptop. No GPU required. However:
- Initial load may take 10-30 seconds
- Fetching 30 stocks takes ~4 seconds (with cache)
- RAM usage: ~500MB backend + ~200MB frontend

### Do I need an OpenAI API key?

**No, it's optional.** The core ML predictions work without it. OpenAI is only needed for:
- AI-powered detailed analysis
- Contextual market insights
- Specific buy/sell recommendations

Without OpenAI, you still get:
- ML probability scores
- Trading signals (STRONG BUY, BUY, etc.)
- Real-time market data
- Technical indicators

### Do I need Redis?

**No, it's optional.** The application has an in-memory cache fallback. Redis is recommended for:
- Production deployments
- Multiple server instances
- Better performance
- Persistent caching across restarts

Without Redis:
- Cache resets on server restart
- Can't share cache across instances
- Slightly slower on first load

---

## Usage Questions

### How do I get started?

1. Clone the repository
2. Install dependencies (Python + Node.js)
3. Start backend: `uvicorn trading_fun.server:app --reload`
4. Start frontend: `cd frontend && npm run dev`
5. Open browser: `http://localhost:5173`

See [Quick Start Guide](Quick-Start-Guide.md) for detailed instructions.

### How do I select stocks?

**Option 1: Market Views**
- Click market buttons at the top (Global, Switzerland, etc.)
- System automatically loads top stocks by market cap
- View ranked list with buy/sell signals

**Option 2: Search**
- Enter ticker symbol in search box
- Click Search or press Enter
- View detailed information and signal

### What do the signals mean?

- 🟢 **STRONG BUY** (≥65%): High confidence buy
- 🟢 **BUY** (55-64%): Good buying opportunity
- 🟡 **HOLD** (45-54%): Maintain position
- 🟠 **CONSIDER SELLING** (35-44%): Weak position
- 🔴 **SELL** (<35%): Exit recommended

See [Understanding Trading Signals](Understanding-Trading-Signals.md) for details.

### How often should I check signals?

**Recommended frequency**:
- **Weekly**: For long-term investors
- **Bi-weekly**: For moderate traders
- **Monthly**: For passive investors

Signals are updated daily, but significant changes are less frequent.

### Can I use this for day trading?

**No, not recommended.** POC-MarketPredictor-ML is designed for:
- Medium-term analysis (weeks to months)
- Position/swing trading
- Portfolio construction

For day trading, you need:
- Intraday data and signals
- Much faster updates (seconds, not minutes)
- Different trading strategies

### How accurate are the predictions?

**Model accuracy**: ~65-70% on historical data

**Important notes**:
- Past performance doesn't guarantee future results
- Accuracy varies by market conditions
- Higher probability signals tend to be more accurate
- Always combine with other analysis

### What markets are supported?

**Currently supported (8 markets)**:
1. 🌐 Global (US large-caps)
2. 🇺🇸 United States
3. 🇨🇭 Switzerland
4. 🇩🇪 Germany
5. 🇬🇧 United Kingdom
6. 🇫🇷 France
7. 🇯🇵 Japan
8. 🇨🇦 Canada

**Planned** (see [BACKLOG.md](../../BACKLOG.md)):
- China, India, Brazil, Australia, South Korea

### Can I analyze custom stock lists?

**Yes!** Use the `/ranking` API with custom tickers:

```bash
curl "http://localhost:8000/ranking?tickers=AAPL,MSFT,GOOGL,AMZN,TSLA"
```

Or add tickers to the market configuration in `trading_fun/config.py`.

---

## Data & API Questions

### Where does the data come from?

**Stock Data**: yfinance (Yahoo Finance)
- Prices, volume, market cap
- Historical data for ML models
- Company fundamentals

**AI Analysis**: OpenAI API (optional)
- GPT-4o-mini model
- Contextual insights
- Trading recommendations

### How often is data updated?

**Real-time data**:
- Prices: On demand (when you refresh)
- WebSocket: Every 30 seconds (if connected)

**ML predictions**:
- Updated daily via CI/CD
- New model trained each day
- Best model promoted to production

**Cache TTLs**:
- Country rankings: 1 hour
- Ticker info: 30 minutes (configurable)
- AI analysis: 5 minutes

### Is the data real-time?

**Mostly yes**, with caveats:
- **During market hours**: Near real-time (15-30 second delay)
- **After market close**: Last close price
- **Weekends**: Previous Friday's close
- **Holidays**: Last trading day

### What if yfinance is down?

The app handles failures gracefully:
- Shows cached data if available
- Returns error message for new requests
- Retries with exponential backoff
- Falls back to last known data

### Are there API rate limits?

**Yes, two types**:

1. **Internal rate limit**: 60 requests/minute per IP (default)
   - Configurable via `RATE_LIMIT_RPM`
   - Prevents abuse
   - Returns 429 status when exceeded

2. **yfinance informal limits**: Not documented
   - Too many requests may get throttled
   - Use caching to minimize calls
   - Spread requests over time

---

## ML Model Questions

### What ML models are used?

**Current**:
- RandomForest classifier (default)
- XGBoost alternative

**Planned**:
- Model ensemble (combine multiple models)
- LSTM for time series
- Transformer models

### How are models trained?

**Training process**:
1. Fetch historical price data (1+ years)
2. Calculate technical indicators (RSI, MACD, etc.)
3. Generate labels (outperform vs. underperform)
4. Train model with cross-validation
5. Evaluate on test set
6. Log metrics to MLflow
7. Save model artifact

**Frequency**: Daily via GitHub Actions

### What features does the model use?

**Technical indicators**:
- RSI (14-period)
- SMA50, SMA200
- MACD, MACD Signal
- Bollinger Bands (upper, lower)
- Momentum (10-day)
- Volatility (30-day)

See [ML Model Guide](ML-Model-Guide.md) for details.

### Can I train my own model?

**Yes!** Use the training scripts:

```bash
python training/trainer.py
```

Customize:
- Features in `trading_fun/features.py`
- Model parameters in `training/trainer.py`
- Training data timeframe

### How do I update the production model?

**Automatic** (recommended):
- CI/CD workflow trains daily
- Best model promoted automatically
- Updates `models/prod_model.bin`

**Manual**:
```bash
# Train new model
python training/trainer.py

# Promote to production
cp models/model_YYYYMMDD_HHMMSS.bin models/prod_model.bin

# Restart server
```

---

## Deployment Questions

### Can I deploy this to production?

**Yes!** The application is production-ready with:
- Docker support
- Health checks
- Metrics endpoints
- Structured logging
- Rate limiting
- Caching

See [Deployment Guide](Deployment-Guide.md).

### What are the deployment options?

**Cloud Platforms**:
- AWS (EC2, ECS, EKS)
- Google Cloud (Compute Engine, GKE)
- Azure (VM, AKS)
- DigitalOcean (Droplets, Kubernetes)
- Heroku, Render, Railway

**Containerization**:
- Docker
- Docker Compose
- Kubernetes

**Frontend**:
- Netlify (automated via CI/CD)
- Vercel
- GitHub Pages (docs only)
- Cloudflare Pages

### How much does deployment cost?

**Minimum** (small scale):
- **Backend**: $5-20/month
  - DigitalOcean Droplet ($6/month)
  - AWS t2.micro (free tier or ~$10/month)
  - Heroku Hobby ($7/month)

- **Frontend**: Free
  - Netlify free tier
  - Vercel free tier
  - GitHub Pages (free)

- **Redis**: $5-15/month
  - Redis Cloud free tier (30MB)
  - AWS ElastiCache ($15/month)

**Total**: $10-35/month

**Production** (high availability):
- Load balancer: $10-20/month
- Multiple backend instances: $50-100/month
- Redis: $15-50/month
- Monitoring: $0-50/month

**Total**: $75-220/month

### Do I need Kubernetes?

**No, not initially.** Kubernetes is optional and recommended for:
- Large scale (1000+ users)
- High availability requirements
- Multiple regions
- Complex microservices

For most use cases, Docker or simple VMs are sufficient.

---

## Troubleshooting

### Backend won't start

**Check**:
1. Python version: `python --version` (need 3.10+)
2. Dependencies installed: `pip install -r requirements.txt`
3. Port 8000 available: `lsof -i :8000` (macOS/Linux)
4. Model file exists: `ls models/prod_model.bin`

### Frontend won't start

**Check**:
1. Node.js version: `node --version` (need 18+)
2. Dependencies installed: `cd frontend && npm install`
3. Backend running: visit `http://localhost:8000/health`

### No data loading

**Check**:
1. Backend status: `curl http://localhost:8000/health`
2. Network: Browser console for errors (F12)
3. API URL: `frontend/.env` should have correct `VITE_API_URL`
4. Rate limit: Wait a minute if you see 429 errors

### Slow performance

**Solutions**:
1. Enable Redis caching
2. Increase cache TTLs
3. Use batch API endpoints
4. Check network latency
5. Optimize database queries (if using DB)

### "Model not found" error

**Solutions**:
1. Train a model: `python training/trainer.py`
2. Download pre-trained model (if available)
3. Check `PROD_MODEL_PATH` environment variable
4. Verify file permissions

---

## Feature Requests

### Can I request a feature?

**Yes!** Please:
1. Check [BACKLOG.md](../../BACKLOG.md) first
2. Open a GitHub issue
3. Describe the feature and use case
4. Label as "enhancement"

### How can I contribute?

See [Contributing Guide](Contributing-Guide.md). We welcome:
- Bug fixes
- New features
- Documentation improvements
- Test coverage
- UI/UX enhancements

### What's on the roadmap?

**Q1 2026**:
- User authentication & portfolios
- Historical backtesting visualization
- Email/SMS alerts

**Q2 2026**:
- Model ensemble
- Kubernetes deployment
- More international markets

See [BACKLOG.md](../../BACKLOG.md) for full roadmap.

---

## Security Questions

### Is my data secure?

**Yes**:
- No user data is stored (currently)
- No personal information collected
- API keys stored in environment variables
- HTTPS recommended for production
- Rate limiting prevents abuse

### Should I use HTTPS?

**In production, yes!** Use HTTPS for:
- Protecting API keys
- Encrypting data in transit
- Preventing man-in-the-middle attacks

**In development, no.** HTTP on localhost is fine.

### How do I secure my API keys?

**Best practices**:
- Never commit keys to git
- Use `.env` files (gitignored)
- Use environment variables
- Rotate keys regularly
- Use GitHub secrets for CI/CD

### Is the OpenAI API key exposed?

**No.** The key is:
- Stored on backend only
- Never sent to frontend
- Never logged
- Only used for API calls to OpenAI

---

## Performance Questions

### Why is the first load slow?

**Reasons**:
- Fetching data from yfinance (external API)
- Calculating ML features
- No cached data yet

**Solutions**:
- Enable Redis caching
- Use batch API endpoints
- Pre-warm cache
- Increase cache TTLs

### How can I make it faster?

**Backend**:
1. Enable Redis caching
2. Increase cache TTLs
3. Use batch endpoints
4. Optimize ML model size
5. Add more worker processes

**Frontend**:
1. Enable production build
2. Use code splitting
3. Implement lazy loading
4. Add service worker caching
5. Optimize images

### What's the maximum throughput?

**Single instance**:
- 250 requests/second (simple endpoints)
- 50 requests/second (complex endpoints)
- Depends on CPU, network, caching

**With scaling**:
- Horizontal scaling (multiple instances)
- Load balancer distribution
- Shared Redis cache
- Can handle 1000+ RPS

---

## Legal & Licensing

### What license is this under?

**MIT License** - permissive open-source license

**You can**:
- Use commercially
- Modify
- Distribute
- Private use

**You must**:
- Include license and copyright notice

**You cannot**:
- Hold liable

### Can I use this commercially?

**Yes!** The MIT license allows commercial use. However:
- This is not financial advice
- Consult a lawyer for compliance
- Consider disclaimer for users
- Ensure compliance with securities regulations

### Do I need to credit the project?

**Not required**, but appreciated! If you:
- Fork or modify: Please link back
- Write about it: Mention the project
- Use in production: Consider sponsoring

---

## Community & Support

### Where can I get help?

1. **Documentation**: Check the [wiki](Home.md)
2. **Search Issues**: Someone may have had the same problem
3. **GitHub Issues**: Create a new issue
4. **GitHub Discussions**: Ask questions

### How do I report a bug?

1. Check if it's already reported
2. Create a GitHub issue
3. Include:
   - Description of the bug
   - Steps to reproduce
   - Expected vs. actual behavior
   - Environment (OS, versions, etc.)
   - Error messages and logs

### How do I stay updated?

- ⭐ **Star** the repository on GitHub
- 👁️ **Watch** for releases and updates
- 📰 Follow changelog in releases
- 💬 Join GitHub Discussions

---

## Still Have Questions?

If your question isn't answered here:

1. **Check the wiki**: [Home](Home.md)
2. **Read the docs**: [README.md](../../README.md)
3. **Ask on GitHub**: [Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)
4. **Open an issue**: [Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

---

*Last updated: December 1, 2025*
