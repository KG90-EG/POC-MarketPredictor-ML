# Repository Structure Guidelines

This document defines the organization structure for the POC-MarketPredictor-ML repository.

## 📁 Directory Structure

```
POC-MarketPredictor-ML/
├── config/              # Configuration files
│   ├── ml/             # ML-specific configs (hyperparameters, etc.)
│   ├── deployment/     # Deployment configs (docker-compose, etc.)
│   └── monitoring/     # Monitoring configs (prometheus, grafana)
├── data/               # Data storage
│   └── analytics/      # Analytics and tracking data
├── docs/               # Documentation
│   ├── api/           # API documentation
│   ├── architecture/  # Architecture Decision Records (ADRs)
│   ├── deployment/    # Deployment guides
│   ├── development/   # Development docs
│   ├── features/      # Feature documentation
│   └── getting-started/  # Quickstart guides
├── examples/          # Example code and usage
├── frontend/          # React/Vite frontend application
├── logs/              # Application logs and temporary files
├── models/            # Trained ML models (*.bin files)
├── monitoring/        # Monitoring infrastructure
├── scripts/           # Utility scripts
│   ├── analysis/     # Analysis scripts
│   ├── cleanup_repo.sh
│   └── validate_structure.sh
├── src/               # Source code
│   ├── backtest/     # Backtesting module
│   ├── data/         # Data processing
│   ├── trading_engine/  # Core trading engine
│   └── training/     # Model training module
└── tests/             # Test files
```

## 📋 File Placement Rules

### ✅ Root Directory (Essential Files Only)

**Allowed files in root:**

- `Dockerfile` - Docker build configuration
- `LICENSE` - Project license
- `Makefile` - Build and development commands
- `README.md` - Project overview
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - Docker orchestration
- `docker-compose.monitoring.yml` - Monitoring stack

**Hidden config files (with dot prefix):**

- `.gitignore`, `.dockerignore`
- `.env.example`
- `.pre-commit-config.yaml`
- `.readthedocs.yaml`
- `.secrets.baseline`

### 📄 Documentation Files

**All `.md` files except `README.md` belong in `docs/`:**

```bash
# ✅ Correct
docs/getting-started/QUICKSTART.md
docs/deployment/README_SERVERS.md
docs/features/TRADING_SIGNALS.md
docs/development/MODEL_RETRAINING.md

# ❌ Wrong
QUICKSTART.md  # Should be in docs/getting-started/
DEPLOYMENT.md  # Should be in docs/deployment/
```

### ⚙️ Configuration Files

```bash
# ✅ Correct
config/ml/best_hyperparameters.json
config/deployment/docker-compose.yml
config/pyproject.toml

# ❌ Wrong
best_hyperparameters.json  # Should be in config/ml/
settings.json  # Should be in config/
```

### 🔧 Scripts

```bash
# ✅ Correct
scripts/train_production.py
scripts/deploy_production.sh
scripts/cleanup_repo.sh

# ❌ Wrong
deploy.sh  # Should be in scripts/
train.py   # Should be in scripts/ or src/
```

### 📊 Logs & Temporary Files

```bash
# ✅ Correct
logs/training_output.log
logs/backend.log
logs/.backend.pid

# ❌ Wrong
training_output.log  # Should be in logs/
.backend.pid  # Should be in logs/
debug.log  # Should be in logs/
```

### 💻 Source Code

```bash
# ✅ Correct
src/trading_engine/server.py
src/backtest/backtester.py
src/training/trainer.py

# ❌ Wrong
server.py  # Should be in src/trading_engine/
backtester.py  # Should be in src/backtest/
```

## 🔒 Automated Enforcement

### Pre-Commit Hook

The repository includes a pre-commit hook that automatically validates structure:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

When you try to commit a file to the wrong location:

```
❌ File not allowed in root: training_output.log
   → Move to: logs/

❌ Structure validation failed: 1 violations

📁 Correct structure:
   • Documentation → docs/
   • Config files → config/
   • Scripts → scripts/
   • Logs → logs/
   • Source code → src/
```

### Cleanup Script

If files end up in the wrong place:

```bash
# Automatically reorganize files
./scripts/cleanup_repo.sh
```

### GitHub Actions

The CI pipeline checks structure on every push/PR:

```yaml
# .github/workflows/structure-check.yml
- Check for loose files in root
- Verify documentation placement
- Validate config file locations
```

## 🛠️ Common Scenarios

### Creating New Documentation

```bash
# ❌ Don't do this
touch NEW_FEATURE.md

# ✅ Do this
touch docs/features/NEW_FEATURE.md
```

### Adding ML Hyperparameters

```bash
# ❌ Don't do this
echo '{"lr": 0.01}' > hyperparameters.json

# ✅ Do this
echo '{"lr": 0.01}' > config/ml/hyperparameters.json
```

### Creating Training Scripts

```bash
# ❌ Don't do this
touch train_new_model.py

# ✅ Do this
touch scripts/train_new_model.py
# or
touch src/training/new_trainer.py
```

### Logging Output

```python
# ❌ Don't do this
with open("output.log", "w") as f:
    f.write(log_data)

# ✅ Do this
with open("logs/output.log", "w") as f:
    f.write(log_data)
```

## 🔍 Quick Reference

| File Type | Location | Example |
|-----------|----------|---------|
| Documentation | `docs/` | `docs/features/ALERTS.md` |
| Python source | `src/` | `src/trading_engine/ml/` |
| Scripts | `scripts/` | `scripts/deploy.sh` |
| Config (ML) | `config/ml/` | `config/ml/hyperparameters.json` |
| Config (Deploy) | `config/deployment/` | `config/deployment/docker-compose.yml` |
| Logs | `logs/` | `logs/training.log` |
| Tests | `tests/` | `tests/test_trading.py` |
| Frontend | `frontend/` | `frontend/src/` |
| Data | `data/` | `data/analytics/` |

## 💡 Benefits

1. **Consistency**: Everyone knows where to find files
2. **Scalability**: Easy to add new features without clutter
3. **Automation**: Pre-commit hooks prevent mistakes
4. **Maintenance**: Clean root directory is easier to navigate
5. **Collaboration**: New contributors understand structure immediately

## 🚨 Bypassing Checks (Not Recommended)

Only use in emergencies:

```bash
# Skip pre-commit hooks (dangerous!)
git commit --no-verify -m "Emergency fix"
```

**Note**: CI checks will still catch violations!

## 📞 Questions?

If you're unsure where a file should go:

1. Check this guide
2. Look at similar existing files
3. Run `./scripts/cleanup_repo.sh` to see suggestions
4. Ask in PR comments
