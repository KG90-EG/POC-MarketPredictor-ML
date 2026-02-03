# Market Predictor ML Constitution

## Core Principles

### I. Decision Support Only - NEVER Recommendations
The system is a **Decision Support System**, NOT an advisory system.
- NEVER provide direct buy/sell recommendations
- Always express as "Signal" or "Score", never as "Recommendation"
- User makes the final decision - system provides data only
- Disclaimer on every output: "This is not investment advice"

### II. Quantitative Signals Dominate
The scoring formula is immutable:
- **Technical Signals: 40%** (RSI, MACD, Bollinger, ADX)
- **ML Probability: 30%** (Random Forest Prediction)
- **Momentum: 20%** (Multi-Period: 10d, 30d, 60d)
- **Market Regime: 10%** (VIX + S&P 500 Trend)

These weights may ONLY be changed via a Constitution Amendment.

### III. LLM as Context Provider - Strict Boundaries
LLM (OpenAI) MAY:
- ✅ Summarize news (max 3 sentences)
- ✅ Identify risk events
- ✅ Adjust score by **±5% maximum**

LLM may NOT:
- ❌ Override or ignore scores
- ❌ Make direct buy/sell statements
- ❌ Contradict quantitative signals

### IV. Market Regime Has Veto Power
When Market Regime = "RISK_OFF":
- **All BUY signals are blocked**
- UI displays "DEFENSIVE MODE ACTIVE"
- Position limits are reduced by 50%

No exceptions. Capital protection > profit opportunities.

### V. Position Limits Are Inviolable
- **Single Stock**: Maximum 10% of portfolio
- **Single Crypto**: Maximum 5% of portfolio
- **Total Stocks**: Maximum 70% of portfolio
- **Total Crypto**: Maximum 20% of portfolio
- **Cash Reserve**: Minimum 10% of portfolio

During Risk-Off, all limits are reduced by 50%.

### VI. Explainability Is Mandatory
Every score must be explainable:
- Display top 3 positive factors
- Display top 3 risk factors
- User must understand WHY a score is high/low
- "Black Box" outputs are forbidden

### VII. Test-First Development
- Every new feature requires tests BEFORE merge
- Minimum 80% test coverage for new code paths
- Tests must pass before PR is merged
- Integration tests for all API endpoints

### VIII. Clean Codebase
- Unused code is archived daily (23:00 cron)
- No backup files in repository (.bak, .tmp, ~)
- Every new file is checked for duplicates
- Stale files (>90 days without changes) are reviewed

### IX. Pre-Commit Validation - No Broken Builds
**Before EVERY commit, the following checks must pass:**

1. **Backend Validation**
   - `python3 -m pytest tests/` - All tests green
   - `flake8 src/` - No linting errors
   - `black --check src/` - Code correctly formatted

2. **Frontend Validation**
   - `npx eslint src/` - No ESLint errors (Errors = Blocker)
   - `npm run build` - Build must succeed
   - JSX syntax correct (no unescaped `<` or `>`)

3. **Integration Check**
   - Backend starts without errors
   - Frontend starts without errors
   - Health endpoint reachable

**Why?**
- CI/CD pipelines must NEVER fail due to avoidable errors
- Broken UI is unacceptable for production
- Time for debugging = time lost for features

**Consequence of violation:**
- Commit is reverted
- Issue is created for Root Cause Analysis
- No blame, but process is improved

### X. Living Documentation
After every feature commit, relevant docs must be updated:

1. **README.md** - For new features, commands, or API changes
2. **TRADER_GUIDE.md** - For user-facing features
3. **openapi.json** - For API endpoint changes (auto-generated)
4. **Create ADR** - For architectural decisions

**Rule:** Code without current documentation is not finished.

**Exceptions:**
- Pure bugfixes (no new feature)
- Refactoring without functional changes
- Test-only commits

### XI. Clean Repository Structure
The repository must follow a clear, defined structure:

**Allowed Root-Level Files:**
- README.md, LICENSE, Makefile, Dockerfile
- requirements.txt, pyproject.toml, pytest.ini
- docker-compose.yml, .env.example
- Configuration files: .gitignore, .flake8, .pre-commit-config.yaml

**Folder Structure (mandatory):**
```
POC-MarketPredictor-ML/
├── src/                  # Python Source Code
│   ├── trading_engine/   # Backend API
│   ├── training/         # ML Training
│   ├── backtest/         # Backtesting
│   └── data/             # Data Processing
├── frontend/             # React Frontend
├── tests/                # Test Suite
├── docs/                 # Documentation
│   ├── architecture/     # ADRs, Specs
│   └── TRADER_GUIDE.md   # User Documentation
├── scripts/              # Shell Scripts
├── config/               # Deployment Configs
├── models/               # Trained ML Models
└── .specify/             # Spec-Kit Specs
```

**Forbidden in Root:**
- No temporary files (.bak, .tmp, ~)
- No changelog files (use Git History)
- No orphaned Markdown files
- No duplicates of config files

**Rule:** Every new file must be created in the correct folder.

**Verification:**
- Pre-commit hook validates structure
- CI/CD checks `structure-check.yml`
- Weekly cleanup script

## Technology Constraints

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ML**: scikit-learn Random Forest
- **Data**: yfinance for market data
- **Cache**: In-Memory (InMemoryCache)
- **LLM**: OpenAI GPT-4o-mini

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: CSS Modules
- **Charts**: Recharts
- **State**: React hooks (no Redux)

### Infrastructure
- **VCS**: Git + GitHub
- **CI/CD**: GitHub Actions
- **Deployment**: Docker / Railway
- **Monitoring**: Prometheus + Grafana

## Quality Gates

### Before Commit (MANDATORY)
1. ✅ Backend tests pass (`python3 -m pytest tests/`)
2. ✅ No Python linting errors (`flake8 src/`)
3. ✅ No ESLint errors in frontend (`npx eslint src/`)
4. ✅ Frontend builds successfully (`npm run build`)
5. ✅ Python formatted (`black src/`)
6. ✅ Frontend formatted (`npm run format`)

### Before Merge
1. ✅ All Quality Gates from "Before Commit" pass
2. ✅ No new unused files (daily cleanup)
3. ✅ Constitution compliance verified
4. ✅ Spec-Kit Checklist completed (if applicable)

### Before Production
1. ✅ Full test suite green
2. ✅ Health check passing
3. ✅ Market regime API responding
4. ✅ Model loaded and validated
5. ✅ All endpoints return valid responses

## Governance

- Constitution supersedes all other documentation
- Amendments require explicit approval and version bump
- All code reviews must verify Constitution compliance
- Violations are blockers - no exceptions

**Version**: 1.4.0 | **Updated**: 2026-02-03 | **Owner**: Kevin Garcia
