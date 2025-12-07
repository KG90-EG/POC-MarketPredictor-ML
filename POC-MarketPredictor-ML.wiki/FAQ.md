# Frequently Asked Questions (FAQ)

Common questions about Market Predictor ML.

---

## General Questions

### What is Market Predictor ML?

Market Predictor ML is an AI-powered financial analysis platform that combines machine learning with real-time market data to provide intelligent stock and cryptocurrency insights. It features momentum-based ranking, GPT-4 analysis, and a modern React interface.

### Is this production-ready?

This is a proof-of-concept (POC) project demonstrating ML-powered financial analysis. While it includes production features like Docker deployment, CI/CD, and comprehensive testing, you should perform additional security audits and testing before using it in a production environment with real money.

### What markets are supported?

Currently supported markets:
- **Stocks**: FTSE 100, S&P 500, NASDAQ
- **Cryptocurrency**: Top 250 by market cap via CoinGecko

### Is this free to use?

The code is open-source under the MIT License. However, you'll need API keys for:
- **OpenAI** (required): Paid service, costs vary by usage
- **Alpha Vantage** (optional): Free tier available (500 calls/day)
- **CoinGecko** (free): No API key needed for basic usage

---

## Technical Questions

### What technologies are used?

**Backend:**
- FastAPI (Python web framework)
- Scikit-learn (Machine learning)
- OpenAI GPT-4 (AI analysis)
- Redis-compatible caching

**Frontend:**
- React 18
- Vite (Build tool)
- Vanilla CSS with dark mode

**Infrastructure:**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- pytest (Testing)

### What Python version is required?

Python 3.9 or higher. We recommend Python 3.11 for best performance.

### Can I use this with other programming languages?

Yes! The backend exposes a REST API that can be consumed by any language. Check the [API Reference](API-Reference) page for complete documentation.

### Does it support real-time data?

Yes, through WebSocket connections for live market updates. The system also uses caching with appropriate TTLs (Time-To-Live) to balance freshness with API rate limits.

---

## Features & Functionality

### How does the momentum scoring work?

The momentum score (0.0 to 1.0) combines multiple factors:
- Price change percentage (24h, 7d, 30d)
- Volume trends
- Volatility measures
- Market cap stability

Higher scores indicate stronger upward momentum.

### What makes the AI analysis different?

Our AI analysis uses GPT-4 with:
- Context-aware prompting based on current market data
- Momentum scores as input features
- Ranking algorithm that considers both AI reasoning and quantitative metrics
- Confidence scores for each recommendation

### Can I customize the analysis?

Yes! You can:
- Modify momentum calculation in `trading.py`
- Customize AI prompts in the analysis endpoint
- Adjust cache TTLs and rate limits in `pyproject.toml`
- Add new markets or data sources

### Does it support portfolio tracking?

Currently, the app shows market data and rankings but doesn't persist user portfolios. This feature is on the roadmap (see [BACKLOG.md](../BACKLOG.md)).

---

## Setup & Configuration

### Do I need all the API keys?

**Required:**
- OpenAI API key (for AI analysis features)

**Optional:**
- Alpha Vantage API key (for stock data; app has fallback mechanisms)

**Not required:**
- CoinGecko (free public API, no key needed)

### How do I get an OpenAI API key?

1. Visit https://platform.openai.com
2. Create an account or sign in
3. Navigate to API keys section
4. Create a new secret key
5. Add to your `.env` file: `OPENAI_API_KEY=sk-...`

### How do I configure caching?

Edit `pyproject.toml`:

```toml
[tool.market_predictor.cache]
market_data_ttl = 300        # 5 minutes
ai_analysis_ttl = 3600       # 1 hour
crypto_data_ttl = 120        # 2 minutes
enabled = true
```

### Can I deploy this to the cloud?

Yes! The project includes:
- Docker support for containerized deployment
- CI/CD with GitHub Actions
- Health check endpoint for monitoring

See [DEPLOYMENT.md](../DEPLOYMENT.md) for cloud deployment guides (AWS, GCP, Azure, Heroku).

---

## Development Questions

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure CI passes
5. Submit a pull request

See [Contributing Guidelines](Home#contributing) for details.

### Where are the tests?

Tests are in the `tests/` directory. Run with:

```bash
pytest                    # All tests
pytest tests/test_trading.py  # Specific file
pytest --cov             # With coverage
```

Current coverage: 20+ tests covering trading logic, API endpoints, caching, and rate limiting.

### How do I add a new market?

1. **Define market in configuration:**
   ```python
   # In trading.py or config
   MARKETS = {
       'my_market': {
           'name': 'My Market Index',
           'tickers': ['TICK1', 'TICK2', ...]
       }
   }
   ```

2. **Add data fetching logic:**
   ```python
   def fetch_my_market_data():
       # Implement data fetching
       pass
   ```

3. **Update API endpoint:**
   ```python
   @app.get("/stocks")
   def get_stocks(market: str):
       if market == 'my_market':
           return fetch_my_market_data()
   ```

4. **Add tests:**
   ```python
   def test_my_market():
       assert fetch_my_market_data() is not None
   ```

### Can I add new AI models?

Yes! The architecture supports pluggable models:

1. **For OpenAI:** Change model in the API call (e.g., `gpt-4o`, `gpt-4-turbo`)
2. **For custom models:** Modify `trading.py` to load your trained model
3. **For other providers:** Update the API client (e.g., Anthropic, Cohere)

---

## Performance & Scaling

### How many requests can it handle?

Performance depends on your deployment:
- **Local development:** 10-20 concurrent users
- **Docker (single container):** 50-100 concurrent users
- **Production (scaled):** 1000+ with proper infrastructure

Rate limiting is configured per endpoint (see [API Reference](API-Reference)).

### How do I improve performance?

1. **Enable caching:** Reduces API calls
2. **Increase cache TTLs:** For less volatile data
3. **Use WebSocket:** For real-time updates instead of polling
4. **Deploy with Gunicorn:** Production WSGI server
5. **Add Redis:** For distributed caching
6. **Scale horizontally:** Multiple backend instances behind load balancer

### What are the API rate limits?

**External APIs:**
- Alpha Vantage (free): 5 calls/min, 500/day
- CoinGecko (free): 10-50 calls/min
- OpenAI: Depends on your tier

**Internal API (configurable):**
- `/stocks`: 60/min
- `/analyze`: 10/min
- `/search`: 30/min

### Can it handle high-frequency trading?

No, this is not designed for HFT. Data refresh rates (5-minute cache for stocks, 2-minute for crypto) are too slow for high-frequency strategies. This tool is for analysis and medium-term investment insights.

---

## Data & Privacy

### What data is collected?

The application:
- Fetches public market data from external APIs
- Caches responses temporarily
- Does NOT store user portfolios or personal data
- Does NOT track individual users

Logging includes:
- API request patterns (anonymized)
- Error messages
- System health metrics

### Where is data stored?

- **Cache:** In-memory (Redis-compatible)
- **Models:** Local filesystem (`models/` directory)
- **Logs:** Local filesystem or stdout

No persistent database is used by default.

### Is my API key secure?

Best practices:
- Store in `.env` file (gitignored)
- Never commit API keys to version control
- Use environment variables in production
- Rotate keys periodically

For production, use secrets management services (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault).

### Can I use this with real money?

⚠️ **Disclaimer:** This is a POC for educational purposes. The predictions and analysis should NOT be used as the sole basis for financial decisions. Always:
- Consult with licensed financial advisors
- Do your own research
- Understand the risks
- Never invest more than you can afford to lose

---

## Troubleshooting

### Why am I getting "Rate limit exceeded"?

**Causes:**
- Too many API requests
- Free tier limits reached
- Cache disabled or TTL too low

**Solutions:**
- Wait for rate limit window to reset
- Enable caching
- Increase cache TTL
- Upgrade API tier

### Why is the AI analysis slow?

**Typical response times:**
- GPT-4: 5-15 seconds
- Cached response: < 1 second

**To improve:**
- Use caching (enabled by default)
- Switch to faster model (gpt-3.5-turbo)
- Reduce context length
- Implement request queuing

### Frontend shows blank page

**Common causes:**
1. Backend not running
2. CORS misconfiguration
3. JavaScript errors

**Check:**
```bash
# Backend health
curl http://localhost:8000/health

# Browser console (F12)
# Look for errors
```

See [Troubleshooting Guide](Troubleshooting) for detailed solutions.

---

## Roadmap & Future

### What features are planned?

See [BACKLOG.md](../BACKLOG.md) for the complete roadmap. Highlights:
- User authentication and saved portfolios
- More markets (international exchanges)
- Advanced technical indicators
- Backtesting interface
- Mobile app
- Email/SMS alerts

### Can I request a feature?

Yes! Please:
1. Check [existing issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
2. Create a new issue with the "feature request" label
3. Describe the use case and benefits

### Is commercial use allowed?

Yes, under the MIT License. You can:
- Use commercially
- Modify the code
- Distribute copies

Requirements:
- Include original license notice
- No warranty provided

---

## Support

### Where can I get help?

- **Wiki**: Comprehensive documentation
- **Issues**: [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- **Discussions**: [GitHub Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)
- **Troubleshooting**: [Troubleshooting Guide](Troubleshooting)

### How do I report a bug?

Create a [GitHub Issue](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues/new) with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs/error messages

### Can I hire you for custom development?

This is an open-source project. For custom development inquiries, please reach out through the repository contact information.

---

## More Questions?

Didn't find your answer? 

- Check the [full wiki](Home)
- Review the [API Reference](API-Reference)
- Browse [existing issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- Start a [discussion](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions)

---

**Last Updated**: December 1, 2025
