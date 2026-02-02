# NFR-010: ML Training Pipeline - Tasks

> **Status:** Draft  
> **Created:** 2026-02-02  
> **Spec:** [spec.md](./spec.md)  
> **Plan:** [plan.md](./plan.md)

---

## 📊 Estimation Summary

| Phase | Tasks | Manual Effort | With Agent |
|-------|-------|---------------|------------|
| Phase 1 | 4 | ~3h | ~45min |
| Phase 2 | 4 | ~2h | ~30min |
| Phase 3 | 4 | ~3h | ~45min |
| Phase 4 | 4 | ~4h | ~1h |
| Phase 5 | 4 | ~6h | ~1.5h |
| **Total** | **20** | **~18h** | **~4.5h** |

---

## Phase 1: Scheduled Training

### Task 1.1: Create Training Workflow
**File:** `.github/workflows/train-model.yml`

**Requirements:**
- [ ] Scheduled cron trigger (Sunday 2 AM UTC)
- [ ] Manual workflow_dispatch trigger
- [ ] Python setup and dependency install
- [ ] Run training script
- [ ] Upload model artifact

**Template:**
```yaml
name: Model Training
on:
  schedule:
    - cron: '0 2 * * 0'
  workflow_dispatch:
jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python scripts/train_production.py
      - uses: actions/upload-artifact@v4
        with:
          name: model-${{ github.run_number }}
          path: models/
```

---

### Task 1.2: Refactor Training Script
**File:** `scripts/train_production.py`

**Requirements:**
- [ ] Accept command-line arguments
- [ ] Output structured logs (JSON)
- [ ] Exit codes for success/failure
- [ ] Save model with timestamp
- [ ] Update `best_hyperparameters.json` if improved

---

### Task 1.3: Add Training Notifications
**File:** `.github/workflows/train-model.yml`

**Requirements:**
- [ ] Send notification on success/failure
- [ ] Include training metrics in message
- [ ] Support GitHub notifications (default)
- [ ] Optional: Slack webhook integration

---

### Task 1.4: Create Training README
**File:** `src/training/README.md`

**Requirements:**
- [ ] Document training pipeline
- [ ] How to trigger manual training
- [ ] How to check training status
- [ ] Troubleshooting common issues

---

## Phase 2: Model Versioning

### Task 2.1: Implement Versioning Script
**File:** `scripts/version_model.py`

**Requirements:**
- [ ] Generate semantic version (v1.0.0, v1.1.0, ...)
- [ ] Auto-increment based on last version
- [ ] Support major/minor/patch increments
- [ ] Update VERSION file

---

### Task 2.2: Create Archive Structure
**Files:** `models/README.md`, folder structure

**Requirements:**
- [ ] Create `models/production/` folder
- [ ] Create `models/staging/` folder
- [ ] Create `models/archive/` folder
- [ ] Document structure in README

---

### Task 2.3: Model Metadata
**File:** `scripts/train_production.py`

**Requirements:**
- [ ] Save metadata JSON with each model
- [ ] Include: version, date, metrics, training config
- [ ] Save alongside model file
- [ ] Example: `model_v1.2.0_metadata.json`

---

### Task 2.4: Rollback Script
**File:** `scripts/rollback_model.py`

**Requirements:**
- [ ] List available versions
- [ ] Rollback to specific version
- [ ] Copy archived model to production
- [ ] Update symlinks/references
- [ ] Log rollback action

---

## Phase 3: Automated Validation

### Task 3.1: Auto-Backtest New Model
**File:** `scripts/validate_model.py`

**Requirements:**
- [ ] Load staging model
- [ ] Run backtest on last 3 months data
- [ ] Calculate key metrics (accuracy, Sharpe, etc.)
- [ ] Output comparison report

---

### Task 3.2: Production Comparison
**File:** `scripts/validate_model.py`

**Requirements:**
- [ ] Load production model metrics
- [ ] Compare with staging model
- [ ] Calculate improvement/regression %
- [ ] Pass/Fail based on thresholds

---

### Task 3.3: Generate Comparison Report
**File:** `scripts/validate_model.py`

**Requirements:**
- [ ] Markdown report output
- [ ] Table with metric comparisons
- [ ] Recommendation: PROMOTE / REJECT
- [ ] Save to `reports/model_comparison.md`

---

### Task 3.4: Integrate Validation in Workflow
**File:** `.github/workflows/train-model.yml`

**Requirements:**
- [ ] Run validation after training
- [ ] Fail workflow if validation fails
- [ ] Upload comparison report as artifact
- [ ] Comment on PR if applicable

---

## Phase 4: Hyperparameter Optimization

### Task 4.1: Install and Configure Optuna
**Files:** `requirements.txt`, `config/optuna_config.py`

**Requirements:**
- [ ] Add `optuna` to requirements.txt
- [ ] Create configuration file
- [ ] Define default search space
- [ ] Set trial and timeout limits

---

### Task 4.2: Define Search Space
**File:** `src/training/hyperparams.py`

**Requirements:**
- [ ] Define parameter ranges for XGBoost
- [ ] Include: n_estimators, max_depth, learning_rate, etc.
- [ ] Use Optuna suggest_* methods
- [ ] Document each parameter

---

### Task 4.3: Create Optimization Script
**File:** `scripts/optimize_hyperparams.py`

**Requirements:**
- [ ] Create Optuna study
- [ ] Define objective function
- [ ] Run optimization with limits
- [ ] Save best params to JSON
- [ ] Log to MLflow

---

### Task 4.4: Integrate with Training Pipeline
**File:** `scripts/train_production.py`

**Requirements:**
- [ ] Option to use saved best params
- [ ] Option to run optimization first
- [ ] Flag: `--optimize` vs `--use-best`
- [ ] Update GitHub Actions workflow

---

## Phase 5: Drift Detection (Future)

### Task 5.1: Install Evidently AI
**File:** `requirements.txt`

**Requirements:**
- [ ] Add `evidently` to requirements.txt
- [ ] Verify compatibility with existing deps
- [ ] Test import in project

---

### Task 5.2: Create Drift Monitoring Script
**File:** `scripts/detect_drift.py`

**Requirements:**
- [ ] Load reference data (training data)
- [ ] Load current data (recent production)
- [ ] Calculate PSI for key features
- [ ] Generate drift report

---

### Task 5.3: Drift Alert Thresholds
**File:** `config/drift_config.py`

**Requirements:**
- [ ] Define PSI thresholds (e.g., 0.1 = warning, 0.25 = critical)
- [ ] Configure which features to monitor
- [ ] Define alert destinations

---

### Task 5.4: Auto-Trigger Retraining
**File:** `.github/workflows/drift-check.yml`

**Requirements:**
- [ ] Scheduled drift check (daily)
- [ ] If drift > threshold, trigger training
- [ ] Notification of drift detection
- [ ] Log drift metrics over time

---

## 📝 Notes

- Phase 1-3 are core MVP
- Phase 4 improves model quality
- Phase 5 is advanced automation
- Leverage existing `scripts/auto_retrain.py`
- Use MLflow for all experiment tracking
