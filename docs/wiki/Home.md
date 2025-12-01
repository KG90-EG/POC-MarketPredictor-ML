# POC-MarketPredictor-ML Wiki

Welcome to the POC-MarketPredictor-ML wiki! This comprehensive guide will help you understand, use, and contribute to the project.

---

## 📚 Wiki Contents

### Getting Started
- [Home](Home.md) - Project overview and quick links
- [What is POC-MarketPredictor-ML?](What-is-POC-MarketPredictor-ML.md) - Detailed introduction
- [Quick Start Guide](Quick-Start-Guide.md) - Get up and running in 5 minutes
- [Installation](Installation.md) - Detailed installation instructions
- [Configuration](Configuration.md) - Environment variables and settings

### User Guide
- [Using the Application](Using-the-Application.md) - Complete user guide
- [Understanding Trading Signals](Understanding-Trading-Signals.md) - How to interpret recommendations
- [Multi-Market Analysis](Multi-Market-Analysis.md) - Working with global markets
- [AI Analysis](AI-Analysis.md) - Using OpenAI-powered recommendations
- [FAQ](FAQ.md) - Frequently asked questions

### Technical Documentation
- [Architecture Overview](Architecture-Overview.md) - System design and components
- [API Reference](API-Reference.md) - Complete API documentation
- [ML Model Guide](ML-Model-Guide.md) - Understanding the machine learning models
- [Database Schema](Database-Schema.md) - Data models and relationships
- [WebSocket API](WebSocket-API.md) - Real-time updates

### Development
- [Development Setup](Development-Setup.md) - Setting up your dev environment
- [Contributing Guide](Contributing-Guide.md) - How to contribute
- [Code Structure](Code-Structure.md) - Project organization
- [Testing Guide](Testing-Guide.md) - Writing and running tests
- [Frontend Development](Frontend-Development.md) - React app development

### Deployment
- [Deployment Guide](Deployment-Guide.md) - Production deployment
- [Docker Deployment](Docker-Deployment.md) - Container deployment
- [Kubernetes](Kubernetes.md) - K8s deployment guide
- [CI/CD Pipelines](CICD-Pipelines.md) - GitHub Actions workflows
- [Monitoring](Monitoring.md) - Observability and alerting

### Advanced Topics
- [Performance Optimization](Performance-Optimization.md) - Optimization techniques
- [Security Best Practices](Security-Best-Practices.md) - Security guidelines
- [Scaling Guide](Scaling-Guide.md) - Horizontal and vertical scaling
- [Troubleshooting](Troubleshooting.md) - Common issues and solutions
- [Production Checklist](Production-Checklist.md) - Pre-deployment checklist

---

## 🎯 What is POC-MarketPredictor-ML?

**POC-MarketPredictor-ML** is a production-grade machine learning application that provides intelligent stock ranking, prediction, and AI-powered trading recommendations.

### Key Features

🤖 **ML-Powered Predictions**
- RandomForest and XGBoost models
- Technical indicator analysis (RSI, MACD, Bollinger Bands)
- Probability-based recommendations

🌍 **Global Market Coverage**
- 8 international markets (US, Switzerland, Germany, UK, France, Japan, Canada)
- Real-time data from yfinance
- Dynamic stock discovery and validation

🎯 **Automated Trading Signals**
- 5-tier system: STRONG BUY → SELL
- Clear visual indicators
- Actionable recommendations

🧠 **AI Analysis**
- OpenAI GPT-4o-mini integration
- Contextual market insights
- Risk assessment and action plans

⚛️ **Modern UI**
- React 18 with Vite
- Dark/light theme
- Real-time updates
- Mobile responsive

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ 
- Node.js 18+
- Git

### 2. Installation
```bash
# Clone repository
git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
cd POC-MarketPredictor-ML

# Install backend
pip install -r requirements.txt

# Install frontend
cd frontend
npm install
cd ..
```

### 3. Run Application
```bash
# Terminal 1: Start backend
uvicorn trading_fun.server:app --reload

# Terminal 2: Start frontend
cd frontend && npm run dev
```

### 4. Open Browser
Navigate to `http://localhost:5173` and start exploring!

---

## 🎓 Key Benefits

### For Investors
✅ **Data-Driven Decisions** - Remove emotion from investing  
✅ **Global Diversification** - Access international markets  
✅ **Real-Time Insights** - Live market data and updates  
✅ **AI-Powered Analysis** - Contextual recommendations  
✅ **Clear Signals** - Simple buy/sell/hold guidance  

### For Developers
✅ **Production-Ready** - Enterprise features included  
✅ **Well-Documented** - Comprehensive guides  
✅ **Modern Stack** - FastAPI, React, Docker  
✅ **Tested** - High test coverage  
✅ **Extensible** - Modular architecture  

### For Operations
✅ **Scalable** - Redis caching, horizontal scaling  
✅ **Observable** - Health checks, metrics, logs  
✅ **Secure** - Rate limiting, API protection  
✅ **Reliable** - Error handling, fallbacks  
✅ **Configurable** - Environment-based config  

---

## 📊 How It Works

### 1. Data Collection
- Fetch real-time stock data from yfinance
- Validate company information and market data
- Sort by market capitalization
- Cache results for performance

### 2. Feature Engineering
- Calculate technical indicators (RSI, MACD, SMA, Bollinger Bands)
- Compute momentum and volatility metrics
- Normalize features for ML model

### 3. ML Prediction
- Feed features to trained model (RandomForest/XGBoost)
- Get probability score (0-100%)
- Rank stocks by confidence

### 4. Signal Generation
- Map probability to 5-tier system
- Generate buy/sell/hold recommendations
- Display with visual indicators

### 5. AI Analysis (Optional)
- Enrich with market context
- Send to OpenAI for analysis
- Get detailed recommendations
- Cache results

### 6. Display Results
- Show rankings in UI
- Real-time updates via WebSocket
- Interactive company details
- Actionable insights

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                Frontend (React)                  │
│  - Market selector                               │
│  - Stock rankings table                          │
│  - Company detail sidebar                        │
│  - AI analysis panel                             │
│  - Real-time updates                             │
└──────────────┬──────────────────────────────────┘
               │ HTTP REST / WebSocket
┌──────────────▼──────────────────────────────────┐
│           Backend (FastAPI)                      │
│  - Rate limiter middleware                       │
│  - Request logging                               │
│  - Cache layer (Redis/in-memory)                 │
│  - API endpoints                                 │
└──────┬────────┬──────────┬──────────┬───────────┘
       │        │          │          │
   ┌───▼───┐ ┌─▼──┐ ┌─────▼─────┐ ┌─▼─────┐
   │  ML   │ │Redis│ │ yfinance  │ │OpenAI │
   │ Model │ │     │ │    API    │ │  API  │
   └───────┘ └────┘ └───────────┘ └───────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **ML**: scikit-learn, XGBoost
- **Tracking**: MLflow
- **Data**: yfinance
- **AI**: OpenAI API
- **Cache**: Redis (optional)

### Frontend
- **Framework**: React 18
- **Build**: Vite
- **State**: @tanstack/react-query
- **HTTP**: Axios
- **Styling**: Custom CSS

### Infrastructure
- **CI/CD**: GitHub Actions
- **Container**: Docker
- **Orchestration**: Kubernetes (optional)
- **Monitoring**: Prometheus + Grafana

---

## 📖 Documentation

### Essential Reading
1. [README.md](../../README.md) - Project overview
2. [OVERVIEW.md](../../OVERVIEW.md) - Comprehensive overview
3. [SPEC.md](../../SPEC.md) - Technical specifications
4. [Quick Start Guide](Quick-Start-Guide.md) - Get started fast

### For Users
- [Using the Application](Using-the-Application.md)
- [Understanding Trading Signals](Understanding-Trading-Signals.md)
- [Multi-Market Analysis](Multi-Market-Analysis.md)
- [FAQ](FAQ.md)

### For Developers
- [Development Setup](Development-Setup.md)
- [Contributing Guide](Contributing-Guide.md)
- [Testing Guide](Testing-Guide.md)
- [API Reference](API-Reference.md)

### For Operators
- [Deployment Guide](Deployment-Guide.md)
- [Monitoring](Monitoring.md)
- [Troubleshooting](Troubleshooting.md)
- [Production Checklist](Production-Checklist.md)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Read the [Contributing Guide](Contributing-Guide.md)**
2. **Check the [BACKLOG.md](../../BACKLOG.md)** for open tasks
3. **Fork the repository**
4. **Create a feature branch**
5. **Make your changes**
6. **Write tests**
7. **Submit a pull request**

### Areas Where We Need Help
- 🐛 Bug fixes
- ✨ New features from backlog
- 📝 Documentation improvements
- 🧪 Test coverage
- 🎨 UI/UX enhancements
- 🌍 Internationalization

---

## 📞 Support

### Getting Help
- **Documentation**: Start here!
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions in GitHub Discussions

### Reporting Issues
When reporting an issue, please include:
1. Description of the problem
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment (OS, Python version, etc.)
6. Error messages and logs

---

## 🗺️ Roadmap

### Q1 2026
- User authentication and portfolios
- Historical backtesting visualization
- Email/SMS alerts
- Increased test coverage

### Q2 2026
- Model ensemble
- Feature engineering improvements
- Kubernetes deployment
- Monitoring & alerting

### Q3 2026
- Database layer (PostgreSQL)
- More international markets
- Advanced portfolio optimization
- CI/CD improvements

### Q4 2026
- Sentiment analysis integration
- Model explainability (SHAP)
- GraphQL API
- Mobile app (React Native)

See [BACKLOG.md](../../BACKLOG.md) for detailed roadmap.

---

## 📈 Performance

### Benchmarks
| Metric | Value |
|--------|-------|
| Load 30 stocks | 4s (was 45s) |
| Validate stocks | 10s (was 60s) |
| API response time | <1s (p95) |
| Cache hit rate | 78% |
| Throughput | 250 RPS |

### Optimizations
- ✅ Batch API endpoints
- ✅ Parallel processing (ThreadPoolExecutor)
- ✅ Redis caching
- ✅ Smart TTL strategies
- ✅ WebSocket for real-time updates

---

## 🔒 Security

### Security Features
- 🔐 Rate limiting (60 RPM default)
- 🔑 API key management
- 🛡️ CORS configuration
- 📝 Structured logging
- ⚠️ Input validation
- 🚫 Error handling

### Best Practices
- Store secrets in environment variables
- Use `.env` files (gitignored)
- Enable HTTPS in production
- Regular dependency updates
- Security audits
- Monitor for vulnerabilities

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](../../LICENSE) for details.

---

## 🌟 Star Us!

If you find this project useful, please give it a star on [GitHub](https://github.com/KG90-EG/POC-MarketPredictor-ML)!

---

## 📮 Contact

- **GitHub**: [@KG90-EG](https://github.com/KG90-EG)
- **Repository**: [POC-MarketPredictor-ML](https://github.com/KG90-EG/POC-MarketPredictor-ML)
- **Issues**: [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

---

*Last updated: December 1, 2025*
