# NFR-010: ML Training Pipeline - Implementation Plan

> **Status:** Draft  
> **Created:** 2026-02-02  
> **Spec:** [spec.md](./spec.md)

---

## 🏗️ Architecture Decisions

### AD-1: Training Scheduler
**Decision:** Use GitHub Actions for scheduled training (no external scheduler needed).

**Rationale:**
- GitHub Actions already set up for CI/CD
- Cron syntax supported natively
- Free for public repos, generous limits for private
- No additional infrastructure to manage

**Schedule:**
```yaml
on:
  schedule:
    - cron: '0 2 * * 0'  # Every Sunday at 2 AM UTC
  workflow_dispatch:  # Manual trigger
```

---

### AD-2: Model Versioning with MLflow
**Decision:** Continue using MLflow for experiment tracking and model registry.

**Rationale:**
- Already integrated (`mlruns/` exists)
- Industry standard for ML lifecycle
- Supports model comparison and rollback
- Free and self-hosted

**Versioning Scheme:**
```
models/
├── production/
│   └── model.pkl  (current production)
├── staging/
│   └── model.pkl  (candidate for promotion)
└── archive/
    ├── v1.0.0_2026-01-15.pkl
    └── v1.1.0_2026-02-01.pkl
```

---

### AD-3: Model Promotion Strategy
**Decision:** Manual promotion with automated validation.

**Workflow:**
1. Training produces new model in `staging/`
2. Automated backtest runs against staging model
3. If metrics >= production, notify for review
4. Manual approval triggers promotion
5. Old production moved to archive

**Rationale:**
- Full automation risky for financial predictions
- Human oversight for critical changes
- Automated validation reduces manual work

---

### AD-4: Hyperparameter Optimization
**Decision:** Use Optuna with Bayesian optimization.

**Rationale:**
- More efficient than Grid Search
- Early stopping for poor trials
- Built-in visualization
- Integrates with MLflow

**Configuration:**
```python
study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(),
    pruner=optuna.pruners.MedianPruner()
)
study.optimize(objective, n_trials=50, timeout=3600)
```

---

### AD-5: Drift Detection (Future)
**Decision:** Use Evidently AI for data drift monitoring.

**Rationale:**
- Open source, free
- Comprehensive drift reports
- Integrates with existing data pipeline
- Can trigger retraining automatically

**Metrics:**
- PSI (Population Stability Index) for features
- Prediction distribution shift
- Target label distribution (if available)

---

## 📅 Implementation Phases

### Phase 1: Scheduled Training (~3h)
- [ ] Create GitHub Actions workflow `train-model.yml`
- [ ] Refactor existing training scripts for automation
- [ ] Add model artifact storage
- [ ] Notification on completion (GitHub, Slack)

### Phase 2: Model Versioning (~2h)
- [ ] Implement semantic versioning for models
- [ ] Create archive structure for old models
- [ ] Add model metadata (metrics, training date)
- [ ] Rollback script

### Phase 3: Automated Validation (~3h)
- [ ] Auto-run backtest on new model
- [ ] Compare metrics with production
- [ ] Generate comparison report
- [ ] Promotion criteria check

### Phase 4: Hyperparameter Optimization (~4h)
- [ ] Install and configure Optuna
- [ ] Define search space
- [ ] Integrate with training pipeline
- [ ] Save best params automatically

### Phase 5: Drift Detection (Future - ~6h)
- [ ] Install Evidently AI
- [ ] Create drift monitoring dashboard
- [ ] Set up alert thresholds
- [ ] Auto-trigger retraining

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| New model worse | Bad predictions | Medium | A/B testing, rollback |
| Training fails | No new model | Low | Error handling, retries |
| Data quality issues | Model overfits | Medium | Data validation |
| Long training time | Pipeline blocks | Low | Timeout limits, parallel |

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Training Success Rate | > 95% | GitHub Actions logs |
| Training Duration | < 30 min | Workflow timing |
| Model Accuracy | > 65% | Backtest results |
| Drift Detection | < 24h lag | Monitoring dashboard |
| Rollback Time | < 5 min | Manual test |

---

## 🔗 Dependencies

- GitHub Actions (✅ exists)
- MLflow (✅ exists)
- Optuna (🔧 to install)
- Evidently AI (🔧 future)
- Sufficient training data (6+ months)

---

## 🗂️ Existing Assets to Leverage

| Asset | Location | Status |
|-------|----------|--------|
| Training scripts | `src/training/` | ✅ Exists |
| MLflow experiments | `mlruns/` | ✅ Exists |
| Best hyperparameters | `best_hyperparameters.json` | ✅ Exists |
| Model files | `models/` | ✅ Exists |
| Auto-retrain script | `scripts/auto_retrain.py` | ✅ Exists |

---

## 📝 Open Questions

1. How often should we retrain? (Weekly vs Monthly)
2. What's the minimum performance delta for promotion?
3. Should we keep N versions or time-based retention?
4. Do we need GPU for training or is CPU sufficient?
