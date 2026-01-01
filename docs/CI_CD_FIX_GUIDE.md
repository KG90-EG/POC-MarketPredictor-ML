# CI/CD Pipeline Fix Guide

Last Updated: January 2026

---

## 🎯 Overview

This guide provides step-by-step instructions to fix all CI/CD pipeline issues identified in the project.

---

## 🔧 Issue 1: GitHub Secrets Configuration

### Current State

GitHub Actions workflows warn about missing secrets:

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`
- `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`
- `RAILWAY_TOKEN`, `RAILWAY_PROJECT_ID`
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
- `CR_PAT` (GitHub Container Registry)
- `MLFLOW_TRACKING_URI`

### Impact

**Non-blocking** - CI passes but shows warnings. Some deployment features are disabled.

### Solution

#### Option 1: Add All Secrets (Recommended for Production)

1. **Go to GitHub Repository Settings**

   ```
   https://github.com/KG90-EG/POC-MarketPredictor-ML/settings/secrets/actions
   ```

2. **Click "New repository secret"**

3. **Add each secret:**

   **AWS Secrets** (for S3 model storage):

   ```
   Name: AWS_ACCESS_KEY_ID
   Value: <your-aws-access-key>

   Name: AWS_SECRET_ACCESS_KEY
   Value: <your-aws-secret-key>

   Name: S3_BUCKET
   Value: <your-s3-bucket-name>
   ```

   **Netlify Secrets** (for frontend deployment):

   ```
   Name: NETLIFY_AUTH_TOKEN
   Value: <your-netlify-token>

   Name: NETLIFY_SITE_ID
   Value: <your-site-id>
   ```

   **Railway Secrets** (for backend deployment):

   ```
   Name: RAILWAY_TOKEN
   Value: <your-railway-token>

   Name: RAILWAY_PROJECT_ID
   Value: <your-project-id>
   ```

   **Vercel Secrets** (alternative frontend):

   ```
   Name: VERCEL_TOKEN
   Value: <your-vercel-token>

   Name: VERCEL_ORG_ID
   Value: <your-org-id>

   Name: VERCEL_PROJECT_ID
   Value: <your-project-id>
   ```

   **GitHub Container Registry**:

   ```
   Name: CR_PAT
   Value: <your-github-personal-access-token>
   ```

   **MLflow**:

   ```
   Name: MLFLOW_TRACKING_URI
   Value: <your-mlflow-server-url>
   ```

#### Option 2: Make Secrets Optional (Development)

Update workflows to gracefully handle missing secrets:

```yaml
# Example: .github/workflows/ci.yml
- name: Push Docker image (optional)
  env:
    CR_PAT: ${{ secrets.CR_PAT }}
  run: |
    if [ -n "$CR_PAT" ]; then
      echo "Pushing Docker image..."
      # Docker push commands
    else
      echo "::notice::CR_PAT not set, skipping Docker push"
    fi
```

**Status:** ✅ Already implemented in current workflows

---

## 🔧 Issue 2: Pre-commit Hook Failures

### Current State

```
detect-secrets...........Failed
- hook id: detect-secrets
- exit code: 1
error: Invalid baseline
```

### Root Cause

- Outdated `.secrets.baseline` file
- Version mismatch between pre-commit hook and installed detect-secrets

### Solution

#### Step 1: Update Pre-commit Hooks

```bash
cd /path/to/POC-MarketPredictor-ML

# Install/update pre-commit
pip install pre-commit

# Update all hooks to latest versions
pre-commit autoupdate
```

**Expected Output:**

```
[https://github.com/psf/black] updating 24.3.0 -> 25.11.0
[https://github.com/Yelp/detect-secrets] updating v1.4.0 -> v1.5.0
...
```

#### Step 2: Install detect-secrets

```bash
pip install detect-secrets
```

#### Step 3: Regenerate Secrets Baseline

```bash
detect-secrets scan > .secrets.baseline
```

#### Step 4: Commit Changes

```bash
git add .pre-commit-config.yaml .secrets.baseline
git commit -m "chore: update pre-commit hooks and secrets baseline"
git push
```

#### Step 5: Verify

```bash
pre-commit run --all-files
```

All hooks should pass ✅

---

## 🔧 Issue 3: Module Import Test Failures

### Current State

Tests fail due to mixed imports:

```python
# Some tests import from market_predictor
from market_predictor.trading import build_dataset

# Server uses trading_fun
from trading_fun.server import app
```

### Solution

#### Step 1: Identify All Import Issues

```bash
# Find all imports from market_predictor
grep -r "from market_predictor" tests/ training/ scripts/
grep -r "import market_predictor" tests/ training/ scripts/
```

#### Step 2: Update Test Files

**Before:**

```python
from market_predictor.trading import build_dataset, train_model
from market_predictor.server import app
```

**After:**

```python
from trading_fun.trading import build_dataset, train_model
from trading_fun.server import app
```

#### Step 3: Update All Files

Create a migration script:

```bash
# scripts/fix_imports.sh
#!/bin/bash

# Replace market_predictor with trading_fun in all Python files
find tests/ training/ scripts/ -name "*.py" -type f -exec sed -i '' 's/from market_predictor\./from trading_fun./g' {} +
find tests/ training/ scripts/ -name "*.py" -type f -exec sed -i '' 's/import market_predictor/import trading_fun/g' {} +

echo "✓ Import statements updated"
```

Run it:

```bash
chmod +x scripts/fix_imports.sh
./scripts/fix_imports.sh
```

#### Step 4: Verify Tests Pass

```bash
pytest -v
```

---

## 🔧 Issue 4: Database Permissions in CI

### Current State

CI tests fail with:

```
sqlite3.OperationalError: unable to open database file
```

### Root Cause

CI environment doesn't have write permissions or data directory doesn't exist.

### Solution

Update `.github/workflows/ci.yml`:

```yaml
- name: Setup test environment
  run: |
    # Create data directory
    mkdir -p data

    # Set permissions
    chmod 777 data

    # Initialize database
    python -c "
    from trading_fun.simulation_db import SimulationDB
    db = SimulationDB()
    db.initialize_db()
    "

- name: Run tests
  run: |
    pytest -v --tb=short
```

---

## 🔧 Issue 5: Frontend Build in CI

### Current State

Frontend build sometimes fails in CI:

```
npm ERR! code ELIFECYCLE
npm ERR! errno 1
```

### Root Cause

- Node version mismatch
- Missing dependencies
- Out of memory

### Solution

Update `.github/workflows/ci.yml`:

```yaml
- name: Set up Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json

- name: Install frontend dependencies
  run: |
    cd frontend
    npm ci --prefer-offline --no-audit

- name: Build frontend
  run: |
    cd frontend
    NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

---

## 🔧 Issue 6: Docker Build Failures

### Current State

```
ERROR: failed to solve: process "/bin/sh -c pip install -r requirements.txt" did not complete successfully
```

### Root Cause

- Network timeouts
- Missing system dependencies
- Python version issues

### Solution

Update `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies with retries
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --timeout=60 --retries=5

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data && chmod 777 data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "trading_fun.server"]
```

---

## 🔧 Issue 7: Flake8 and Black Warnings

### Current State

```
flake8 warnings found
black formatting issues found
```

### Solution

#### Auto-fix Black Issues

```bash
black trading_fun/ backtest/ scripts/ tests/
```

#### Auto-fix Flake8 (where possible)

```bash
# Install autoflake
pip install autoflake

# Remove unused imports and variables
autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r trading_fun/ tests/
```

#### Update `.flake8` Configuration

```ini
[flake8]
max-line-length = 120
extend-ignore = E203, W503, F401, C901
exclude =
    .git,
    __pycache__,
    .venv,
    .venv-1,
    market_predictor,
    migrations
```

#### Add Pre-commit Auto-formatting

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 25.11.0
    hooks:
      - id: black
        args: [--line-length=120]

  - repo: https://github.com/pycqa/flake8
    rev: 7.3.0
    hooks:
      - id: flake8
        args: [--max-line-length=120, --extend-ignore=E203,W503]
```

---

## ✅ Verification Checklist

After applying all fixes:

### Local Verification

```bash
# 1. Pre-commit hooks pass
pre-commit run --all-files

# 2. Tests pass
pytest -v

# 3. Linting passes
flake8 trading_fun/
black --check trading_fun/

# 4. Build succeeds
docker build -t market_predictor:test .

# 5. Frontend builds
cd frontend && npm run build
```

### CI Verification

```bash
# Push changes and verify CI passes
git add .
git commit -m "fix: resolve all CI/CD pipeline issues"
git push

# Check GitHub Actions
# https://github.com/KG90-EG/POC-MarketPredictor-ML/actions
```

---

## 📋 Summary of Changes

### Files Modified

- `.github/workflows/ci.yml` - Updated test setup and build steps
- `.pre-commit-config.yaml` - Updated hook versions
- `.secrets.baseline` - Regenerated with latest detect-secrets
- `Dockerfile` - Improved build reliability
- `.flake8` - Updated linting rules
- `tests/**/*.py` - Fixed import statements
- `training/**/*.py` - Fixed import statements
- `scripts/**/*.py` - Fixed import statements

### Secrets Added (Optional)

- AWS credentials
- Deployment platform tokens
- Container registry PAT
- MLflow URI

---

## 🆘 If Issues Persist

1. **Check CI logs:**

   ```
   https://github.com/KG90-EG/POC-MarketPredictor-ML/actions
   ```

2. **Run locally in Docker:**

   ```bash
   docker build -t test .
   docker run test pytest -v
   ```

3. **Clear CI cache:**
   - Go to Actions tab
   - Click on workflow
   - Click "..." → "Delete workflow cache"

4. **Ask for help:**
   - Open GitHub Issue with:
     - Error message
     - CI log snippet
     - What you've tried

---

**Next Steps:** After fixing CI/CD, proceed with [module consolidation](../ARCHITECTURE.md#migration-plan).
