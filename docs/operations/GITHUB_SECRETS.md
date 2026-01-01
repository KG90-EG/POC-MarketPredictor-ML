# GitHub Secrets Setup Guide

This guide explains how to configure GitHub Secrets for CI/CD pipelines.

**TL;DR:** All secrets are **optional**. CI/CD works without them using defaults.

---

## 🔑 Optional Secrets

### Container Registry (Docker)

**Secret:** `CR_PAT`  
**Purpose:** Push Docker images to GitHub Container Registry  
**Required:** No - CI works without it  
**Impact:** Without this, Docker images won't be published (CI still passes)

**How to create:**

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Name: `GHCR_TOKEN` or similar
4. Scopes: Check `write:packages`, `read:packages`, `delete:packages`
5. Generate token
6. Copy token value
7. Go to your repository → Settings → Secrets and variables → Actions
8. Click "New repository secret"
9. Name: `CR_PAT`
10. Value: Paste token
11. Click "Add secret"

---

### MLflow Tracking (Optional)

**Secret:** `MLFLOW_TRACKING_URI`  
**Purpose:** Remote MLflow experiment tracking  
**Required:** No - Uses local tracking by default  
**Impact:** Without this, experiments are tracked locally only

**How to set:**

1. Deploy MLflow server (e.g., on Railway, Render)
2. Get the tracking URI (e.g., `https://mlflow.example.com`)
3. Go to repository → Settings → Secrets and variables → Actions
4. Click "New repository secret"
5. Name: `MLFLOW_TRACKING_URI`
6. Value: Your MLflow server URL
7. Click "Add secret"

---

### AWS S3 (Model Storage)

**Secrets:**

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET`

**Purpose:** Store trained models in S3  
**Required:** No - Models are stored locally by default  
**Impact:** Without these, models are stored in `models/` directory

**How to set:**

1. Create AWS account and S3 bucket
2. Create IAM user with S3 access
3. Get access key ID and secret access key
4. Add three secrets to GitHub:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `S3_BUCKET`: Your bucket name (e.g., `my-ml-models`)

---

### Deployment Platforms

#### Netlify (Frontend)

**Secrets:**

- `NETLIFY_AUTH_TOKEN`
- `NETLIFY_SITE_ID`

**Purpose:** Auto-deploy frontend to Netlify  
**Required:** Only if using automated Netlify deployment  
**Impact:** Without these, manual deployment is required

**How to get:**

1. Go to Netlify → User Settings → Applications
2. Create new personal access token
3. Get Site ID from Site Settings → General → Site details
4. Add both as GitHub secrets

#### Railway (Backend)

**Secrets:**

- `RAILWAY_TOKEN`
- `RAILWAY_PROJECT_ID`

**Purpose:** Auto-deploy backend to Railway  
**Required:** Only if using automated Railway deployment  
**Impact:** Without these, manual deployment is required

**How to get:**

1. Go to Railway dashboard
2. Account Settings → Tokens → Create token
3. Get Project ID from project settings
4. Add both as GitHub secrets

#### Vercel (Frontend Alternative)

**Secrets:**

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

**Purpose:** Auto-deploy frontend to Vercel  
**Required:** Only if using Vercel instead of Netlify  
**Impact:** Without these, manual deployment is required

**How to get:**

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel login`
3. Run `vercel link` in your project
4. Get token from Vercel dashboard → Settings → Tokens
5. Get org and project IDs from `.vercel/project.json`
6. Add all three as GitHub secrets

---

## ⚙️ Current CI/CD Behavior

### Without Any Secrets

✅ **What works:**

- Code linting (flake8, black)
- Unit tests (pytest)
- Docker image build
- Frontend build
- Local MLflow tracking
- Local model storage

❌ **What doesn't work:**

- Docker image publishing
- Remote MLflow tracking
- S3 model storage
- Automated deployments

### With CR_PAT Only

✅ **Additional features:**

- Docker images published to GHCR

### With All Secrets

✅ **Full automation:**

- Docker publishing
- Remote experiment tracking
- Cloud model storage
- Automated deployments to all platforms

---

## 🔍 Checking Secret Status

### In GitHub Actions Logs

Look for these messages:

```
::notice::No CR_PAT secret configured; skipping Docker push
::warning::MLFLOW_TRACKING_URI not set, using local tracking
::notice::AWS credentials not found, skipping S3 upload
```

### Locally

Check which secrets are set:

```bash
# List all secrets (doesn't show values)
gh secret list

# Check specific secret
gh secret list | grep CR_PAT
```

---

## 🛠️ Troubleshooting

### Secret not working

**Problem:** Secret is set but workflow doesn't use it

**Solutions:**

1. Check secret name matches workflow exactly (case-sensitive)
2. Re-save secret (sometimes helps)
3. Check workflow syntax: `${{ secrets.SECRET_NAME }}`
4. Check if secret is available in workflow context

### Expired tokens

**Problem:** `docker login` or API calls fail with 401

**Solutions:**

1. Regenerate token in provider dashboard
2. Update GitHub secret with new token
3. Re-run workflow

### Permission denied

**Problem:** Token has insufficient permissions

**Solutions:**

1. Check token scopes/permissions in provider settings
2. Regenerate with correct permissions
3. Update GitHub secret

---

## 📋 Quick Setup Checklist

For full CI/CD automation:

- [ ] Create GitHub Personal Access Token with `write:packages`
- [ ] Add `CR_PAT` secret to repository
- [ ] (Optional) Set up MLflow server and add `MLFLOW_TRACKING_URI`
- [ ] (Optional) Create AWS S3 bucket and add AWS secrets
- [ ] (Optional) Configure deployment platform and add tokens
- [ ] Test workflow by pushing to main branch
- [ ] Verify secrets work by checking Actions logs

---

## 🔒 Security Best Practices

1. **Never commit secrets to repository**
   - Use `.env` for local development
   - Add `.env` to `.gitignore`
   - Use GitHub Secrets for CI/CD

2. **Use minimal permissions**
   - Grant only necessary scopes
   - Use separate tokens for different services

3. **Rotate secrets regularly**
   - Regenerate tokens every 6 months
   - Update GitHub secrets immediately

4. **Monitor usage**
   - Check GitHub Actions logs for suspicious activity
   - Enable 2FA on all accounts

5. **Use organization secrets for teams**
   - Share secrets across multiple repos
   - Centralized management

---

## 📚 Further Reading

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

**Questions?** Open an issue or check the [CI/CD Fix Guide](docs/CI_CD_FIX_GUIDE.md).
