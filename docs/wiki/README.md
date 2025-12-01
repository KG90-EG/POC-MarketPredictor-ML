# POC-MarketPredictor-ML Wiki

Welcome to the comprehensive documentation for POC-MarketPredictor-ML!

---

## 📚 Quick Navigation

### Getting Started
- **[Home](Home.md)** - Wiki homepage with overview and quick links
- **[What is POC-MarketPredictor-ML?](What-is-POC-MarketPredictor-ML.md)** - Detailed introduction to the application
- **[Quick Start Guide](Quick-Start-Guide.md)** - Get up and running in 5 minutes

### User Documentation
- **[Using the Application](Using-the-Application.md)** - Complete user guide
- **[Understanding Trading Signals](Understanding-Trading-Signals.md)** - How to interpret buy/sell recommendations
- **[FAQ](FAQ.md)** - Frequently asked questions

### Reference
- **[Main README](../../README.md)** - Project overview in repository root
- **[OVERVIEW.md](../../OVERVIEW.md)** - Comprehensive overview document
- **[BACKLOG.md](../../BACKLOG.md)** - Product backlog with prioritized tasks
- **[SPEC.md](../../SPEC.md)** - Technical specifications

---

## 🎯 What You'll Find Here

### For Users
Learn how to use the application effectively:
- Selecting markets and viewing rankings
- Understanding ML-powered trading signals
- Searching for specific stocks
- Using AI-powered analysis
- Interpreting probabilities and recommendations

### For Developers
Technical documentation:
- Architecture overview
- API reference
- Development setup
- Contributing guidelines
- Testing procedures

### For Operators
Deployment and operations:
- Production deployment guides
- Docker and Kubernetes
- Monitoring and observability
- Troubleshooting
- Performance optimization

---

## 📖 Documentation Structure

```
docs/wiki/
├── README.md                           (This file)
├── Home.md                            (Wiki homepage)
├── What-is-POC-MarketPredictor-ML.md (Introduction)
├── Quick-Start-Guide.md               (5-minute setup)
├── Using-the-Application.md           (User guide)
├── Understanding-Trading-Signals.md    (Signal interpretation)
└── FAQ.md                             (Frequently asked questions)
```

---

## 🚀 Quick Links

### Essential Reading
1. **[Home](Home.md)** - Start here!
2. **[Quick Start Guide](Quick-Start-Guide.md)** - Get running fast
3. **[Using the Application](Using-the-Application.md)** - Learn the features
4. **[Understanding Trading Signals](Understanding-Trading-Signals.md)** - Interpret recommendations

### Common Tasks
- **First time setup** → [Quick Start Guide](Quick-Start-Guide.md)
- **Using the UI** → [Using the Application](Using-the-Application.md)
- **Understanding signals** → [Understanding Trading Signals](Understanding-Trading-Signals.md)
- **Have a question?** → [FAQ](FAQ.md)
- **Found a bug?** → [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

---

## 🎓 Learning Path

### Beginner
1. Read [What is POC-MarketPredictor-ML?](What-is-POC-MarketPredictor-ML.md)
2. Follow [Quick Start Guide](Quick-Start-Guide.md)
3. Explore the UI
4. Try different market views
5. Search for stocks you know

### Intermediate
1. Read [Understanding Trading Signals](Understanding-Trading-Signals.md)
2. Review [Using the Application](Using-the-Application.md)
3. Set up OpenAI API for AI analysis
4. Enable Redis for better performance
5. Try multi-market selection

### Advanced
1. Read [SPEC.md](../../SPEC.md) for technical details
2. Review [ARCHITECTURE_REVIEW.md](../../ARCHITECTURE_REVIEW.md)
3. Study ML model architecture
4. Deploy to production
5. Contribute to the project

---

## 💡 Key Concepts

### Trading Signals
The application uses a **5-tier signal system**:
- 🟢 **STRONG BUY** (≥65%) - High confidence buy
- 🟢 **BUY** (55-64%) - Good buying opportunity
- 🟡 **HOLD** (45-54%) - Maintain position
- 🟠 **CONSIDER SELLING** (35-44%) - Weak position
- 🔴 **SELL** (<35%) - Exit recommended

See [Understanding Trading Signals](Understanding-Trading-Signals.md) for details.

### Machine Learning
- Models: RandomForest and XGBoost
- Features: RSI, MACD, Bollinger Bands, SMA, Momentum, Volatility
- Training: Daily retraining via CI/CD
- Output: Probability score (0-100%)

### Multi-Market Support
Access **8 global markets**:
- 🌐 Global (US large-caps)
- 🇺🇸 United States
- 🇨🇭 Switzerland
- 🇩🇪 Germany
- 🇬🇧 United Kingdom
- 🇫🇷 France
- 🇯🇵 Japan
- 🇨🇦 Canada

---

## 🤝 Contributing

Want to help improve the documentation?

1. **Found an error?** Open an issue
2. **Have suggestions?** Start a discussion
3. **Want to contribute?** Submit a pull request

See [Contributing Guide](../../CONTRIBUTING.md) (if available) or check the main README.

---

## 🆘 Getting Help

### Documentation
- Start with [FAQ](FAQ.md)
- Check relevant wiki pages
- Review main [README](../../README.md)

### Community
- [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/KG90-EG/POC-MarketPredictor-ML/discussions) - Questions and ideas

### Support
- Search existing issues first
- Provide detailed information
- Include error messages and logs
- Describe steps to reproduce

---

## 📮 Contact

- **GitHub**: [@KG90-EG](https://github.com/KG90-EG)
- **Repository**: [POC-MarketPredictor-ML](https://github.com/KG90-EG/POC-MarketPredictor-ML)
- **Issues**: [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)

---

## 🗺️ Roadmap

See what's coming next:
- [BACKLOG.md](../../BACKLOG.md) - Detailed product backlog
- [GitHub Projects](https://github.com/KG90-EG/POC-MarketPredictor-ML/projects) - Current sprint

### Upcoming Features
- User authentication and portfolios
- Historical backtesting visualization
- Email/SMS alerts
- More international markets
- Model ensemble
- Mobile app

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](../../LICENSE) for details.

---

*Last updated: December 1, 2025*
