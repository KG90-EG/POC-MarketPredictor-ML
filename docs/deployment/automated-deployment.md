# Automated Deployment

**📍 Location**: This guide is located at the repository root.

**➡️ See**: [`AUTOMATED_DEPLOYMENT.md`](../../AUTOMATED_DEPLOYMENT.md)

---

## Overview

The Automated Deployment guide covers:
- GitHub Actions CI/CD pipeline (300+ lines)
- CLI deployment script (400+ lines)
- Manual deployment commands
- Environment variable configuration
- Troubleshooting guide

## Three Deployment Methods

### 1. GitHub Actions (Fully Automated)
- Add secrets to GitHub repository settings
- Push to main branch
- Automatic deployment to Railway + Vercel
- Auto-updates CORS configuration
- Runs production tests

### 2. CLI Script (One Command)
```bash
./scripts/deploy_production.sh
```

Features:
- Checks dependencies
- Deploys backend to Railway
- Deploys frontend to Vercel
- Updates CORS automatically
- Generates deployment summary

### 3. Manual Commands
Step-by-step Railway and Vercel CLI commands for manual control.

## Quick Start

```bash
# Install deployment tools
brew install railway vercel

# Deploy with CLI script
./scripts/deploy_production.sh

# Or follow GitHub Actions setup
# See full guide for secrets configuration
```

---

**Full Documentation**: [`../../AUTOMATED_DEPLOYMENT.md`](../../AUTOMATED_DEPLOYMENT.md)
