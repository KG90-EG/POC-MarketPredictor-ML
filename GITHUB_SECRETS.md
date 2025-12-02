# GitHub Secrets Configuration Guide

**Last Updated**: December 2, 2025

This guide explains how to configure GitHub repository secrets for CI/CD workflows.

---

## 🔐 Overview

GitHub Secrets are encrypted environment variables used in GitHub Actions workflows. They keep sensitive data (API keys, tokens) secure while enabling automated deployments.

**Access**: Repository Settings → Secrets and variables → Actions → New repository secret

---

## 📋 Required Secrets (For Production Deployment)

### Deployment Secrets

#### `RAILWAY_TOKEN` ⚠️ **Required for Backend Deployment**

- **Purpose**: Authenticate with Railway API for backend deployment
- **Used in**: `.github/workflows/deploy.yml`
- **How to get**:
  1. Go to <https://railway.app/account/tokens>
  2. Click "Create Token"
  3. Copy the token (starts with `railway_`)
- **Example**: `railway_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### `VERCEL_TOKEN` ⚠️ **Required for Frontend Deployment**

- **Purpose**: Authenticate with Vercel API for frontend deployment
- **Used in**: `.github/workflows/deploy.yml`
- **How to get**:
  1. Go to <https://vercel.com/account/tokens>
  2. Click "Create Token"
  3. Copy the token
- **Example**: `xxxxxxxxxxxxxxxxxxxxxxxxxx`

#### `VERCEL_ORG_ID` ⚠️ **Required for Frontend Deployment**

- **Purpose**: Identify your Vercel organization
- **Used in**: `.github/workflows/deploy.yml`
- **How to get**:
  1. Run `vercel link` in your frontend directory
  2. Check `.vercel/project.json` for `orgId`
- **Example**: `team_xxxxxxxxxxxxxxxxxxxxxxxx`

#### `VERCEL_PROJECT_ID` ⚠️ **Required for Frontend Deployment**

- **Purpose**: Identify your Vercel project
- **Used in**: `.github/workflows/deploy.yml`
- **How to get**:
  1. Run `vercel link` in your frontend directory
  2. Check `.vercel/project.json` for `projectId`
- **Example**: `prj_xxxxxxxxxxxxxxxxxxxxxxxx`

#### `RAILWAY_PROJECT_ID` ⚠️ **Required for Backend Deployment**

- **Purpose**: Identify your Railway project
- **Used in**: `.github/workflows/deploy.yml`
- **How to get**:
  1. Go to your Railway project dashboard
  2. Settings → Project ID
- **Example**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## 🔧 Application Secrets

#### `OPENAI_API_KEY` ⚠️ **Required for AI Analysis**

- **Purpose**: Enable OpenAI-powered trading analysis
- **Used in**: Backend runtime, `.github/workflows/deploy.yml`
- **How to get**:
  1. Go to <https://platform.openai.com/api-keys>
  2. Click "Create new secret key"
  3. Copy the key (starts with `sk-proj-`)
- **Example**: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Note**: Set this as Railway environment variable after deployment

---

## 📦 Optional Secrets (For Advanced Features)

### Model Artifact Storage (Optional)

#### `AWS_ACCESS_KEY_ID` 🔵 **Optional**

- **Purpose**: Upload model artifacts to S3
- **Used in**: `.github/workflows/promotion.yml`
- **Required for**: S3 model artifact storage (not needed for basic deployment)
- **How to get**:
  1. AWS Console → IAM → Users → Security credentials
  2. Create access key
- **Example**: `AKIAIOSFODNN7EXAMPLE`

#### `AWS_SECRET_ACCESS_KEY` 🔵 **Optional**

- **Purpose**: S3 authentication
- **Used in**: `.github/workflows/promotion.yml`
- **Required for**: S3 model artifact storage
- **Example**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

#### `S3_BUCKET` 🔵 **Optional**

- **Purpose**: S3 bucket name for model storage
- **Used in**: `.github/workflows/promotion.yml`
- **Required for**: S3 model artifact storage
- **Example**: `my-ml-models-bucket`

---

### Alternative Deployment Platforms (Optional)

#### `NETLIFY_AUTH_TOKEN` 🔵 **Optional**

- **Purpose**: Deploy frontend to Netlify (alternative to Vercel)
- **Used in**: `.github/workflows/deploy-frontend.yml`
- **Required for**: Netlify deployment only
- **How to get**:
  1. Netlify → User settings → Applications → Personal access tokens
  2. Generate new token
- **Example**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### `NETLIFY_SITE_ID` 🔵 **Optional**

- **Purpose**: Identify Netlify site
- **Used in**: `.github/workflows/deploy-frontend.yml`
- **Required for**: Netlify deployment only
- **How to get**:
  1. Netlify site → Site settings → Site details → API ID
- **Example**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

### MLflow Tracking (Optional)

#### `MLFLOW_TRACKING_URI` 🔵 **Optional**

- **Purpose**: Remote MLflow tracking server
- **Used in**: `.github/workflows/ci.yml`
- **Required for**: Remote MLflow server (defaults to local file storage)
- **Example**: `https://mlflow.example.com` or `file:./mlruns`

---

### Container Registry (Optional)

#### `CR_PAT` 🔵 **Optional**

- **Purpose**: GitHub Container Registry authentication
- **Used in**: `.github/workflows/ci.yml`
- **Required for**: Docker image publishing (not needed for Railway/Vercel deployment)
- **How to get**:
  1. GitHub → Settings → Developer settings → Personal access tokens
  2. Generate token with `write:packages` scope
- **Example**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🚀 Quick Setup Guide

### Minimal Production Setup (5 minutes)

For a basic production deployment, you need:

1. **Railway Backend**:
   - `RAILWAY_TOKEN`
   - `RAILWAY_PROJECT_ID`

2. **Vercel Frontend**:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

3. **OpenAI API**:
   - `OPENAI_API_KEY`

**Steps**:

```bash
# 1. Get Railway token
# Visit: https://railway.app/account/tokens

# 2. Get Vercel credentials
cd frontend
vercel link
cat .vercel/project.json  # Get orgId and projectId

# 3. Get Vercel token
# Visit: https://vercel.com/account/tokens

# 4. Get OpenAI key
# Visit: https://platform.openai.com/api-keys

# 5. Add all secrets to GitHub
# Go to: https://github.com/KG90-EG/POC-MarketPredictor-ML/settings/secrets/actions
```

---

## 🔍 How to Add Secrets

### Via GitHub Web Interface

1. **Navigate to repository settings**:

   ```
   https://github.com/KG90-EG/POC-MarketPredictor-ML/settings/secrets/actions
   ```

2. **Click "New repository secret"**

3. **Enter secret details**:
   - Name: Exact name from table above (case-sensitive)
   - Value: Your secret value (will be encrypted)

4. **Click "Add secret"**

5. **Repeat for all required secrets**

### Via GitHub CLI (Alternative)

```bash
# Install GitHub CLI
brew install gh

# Authenticate
gh auth login

# Add secrets
gh secret set RAILWAY_TOKEN
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID
gh secret set RAILWAY_PROJECT_ID
gh secret set OPENAI_API_KEY

# Verify secrets
gh secret list
```

---

## ✅ Verification

After adding secrets, verify the setup:

1. **Check secrets are configured**:

   ```bash
   gh secret list
   ```

2. **Test deployment workflow**:

   ```bash
   git push origin main
   ```

3. **Monitor workflow**:
   - Go to: <https://github.com/KG90-EG/POC-MarketPredictor-ML/actions>
   - Check "Deploy to Production" workflow
   - Ensure all steps pass

---

## 🛡️ Security Best Practices

### DO ✅

- ✅ **Rotate secrets regularly** (every 90 days)
- ✅ **Use minimal permissions** (read-only when possible)
- ✅ **Delete unused secrets** immediately
- ✅ **Use separate tokens** for different environments
- ✅ **Enable secret scanning** in repository settings
- ✅ **Review audit logs** periodically

### DON'T ❌

- ❌ **Never commit secrets** to repository
- ❌ **Don't share secrets** via chat/email
- ❌ **Don't use same secret** across multiple projects
- ❌ **Don't log secrets** in workflow outputs
- ❌ **Don't hardcode secrets** in workflows
- ❌ **Don't skip secret rotation**

---

## 🐛 Troubleshooting

### "Secret not found" Error

**Problem**: Workflow fails with secret access error

**Solution**:

1. Verify secret name matches exactly (case-sensitive)
2. Check secret is added at repository level (not organization)
3. Re-add the secret if it was recently deleted

### "Invalid credentials" Error

**Problem**: Authentication fails with valid-looking token

**Solution**:

1. Regenerate the token from provider dashboard
2. Verify token has correct permissions/scopes
3. Check token hasn't expired
4. Ensure no extra spaces when copying token

### Workflow Skips Deployment Step

**Problem**: Workflow runs but skips deployment

**Solution**:

1. Check workflow conditions (branch, event type)
2. Verify all required secrets are set
3. Check workflow logs for "Skipped" messages
4. Ensure workflow is not disabled

---

## 📚 Related Documentation

- [Automated Deployment Guide](AUTOMATED_DEPLOYMENT.md)
- [Production Ready Guide](PRODUCTION_READY.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [GitHub Actions Workflows](.github/workflows/)

---

## 🆘 Support

**Issues**: <https://github.com/KG90-EG/POC-MarketPredictor-ML/issues>

**Quick Links**:

- Railway Dashboard: <https://railway.app/dashboard>
- Vercel Dashboard: <https://vercel.com/dashboard>
- OpenAI Platform: <https://platform.openai.com>
- GitHub Secrets: <https://github.com/KG90-EG/POC-MarketPredictor-ML/settings/secrets/actions>

---

**Last Updated**: December 2, 2025  
**Version**: 1.0.0
