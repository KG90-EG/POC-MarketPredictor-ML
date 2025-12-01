# GitHub Secrets Configuration Guide

This guide explains all the GitHub secrets needed for the POC-MarketPredictor-ML CI/CD pipelines.

## Required vs Optional Secrets

### ✅ **Required for Basic CI** (None)
The basic CI pipeline will work without any secrets configured. Tests and linting will run automatically.

### 🔧 **Optional - Docker Registry**
Enable Docker image publishing to GitHub Container Registry.

**Secret:** `CR_PAT`
- **What:** GitHub Personal Access Token with `write:packages` permission
- **Where:** GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
- **Permissions needed:** `write:packages`, `read:packages`
- **How to add:**
  1. Create token at https://github.com/settings/tokens
  2. Go to repository → Settings → Secrets and variables → Actions
  3. Click "New repository secret"
  4. Name: `CR_PAT`
  5. Value: Your token

**What happens without it:** Docker image won't be pushed to registry, but build will succeed locally.

---

### 🚀 **Optional - Netlify Deployment**
Enable automatic frontend deployment to Netlify.

**Secrets:** `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`

**How to get these:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Link your site or create new one
cd frontend
netlify init

# Get your credentials
netlify status
```

**From Netlify Dashboard:**
- `NETLIFY_AUTH_TOKEN`: User settings → Applications → Personal access tokens
- `NETLIFY_SITE_ID`: Site settings → General → Site information → API ID

**What happens without it:** Frontend won't auto-deploy, but you can deploy manually with `netlify deploy`.

---

### 📊 **Optional - MLflow Tracking**
Enable ML experiment tracking with remote MLflow server.

**Secret:** `MLFLOW_TRACKING_URI`
- **What:** URL of your MLflow tracking server
- **Example:** `https://your-mlflow-server.com`
- **Default:** Uses local file-based tracking if not set

**What happens without it:** MLflow will use local file-based tracking in `./mlruns` directory.

---

### ☁️ **Optional - AWS S3 Model Storage**
Enable automatic model upload to S3 for production deployment.

**Secrets:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`

**How to get these:**
1. Create IAM user in AWS Console with S3 permissions
2. Create access key for the user
3. Create or identify your S3 bucket name

**Permissions needed (IAM Policy):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name/*",
        "arn:aws:s3:::your-bucket-name"
      ]
    }
  ]
}
```

**What happens without it:** Models will only be stored locally in `./models` directory.

---

### 📄 **Optional - GitHub Pages**
Enable automatic documentation deployment.

**Setup (no secrets needed):**
1. Go to repository Settings → Pages
2. Under "Source", select "GitHub Actions"
3. Save

**Requirements:**
- Repository must be public OR
- You must have GitHub Pro/Team/Enterprise

**What happens without it:** Documentation won't be published online, but you can view it locally.

---

## Quick Setup Summary

### Minimal Setup (Everything works locally)
```bash
# No secrets needed!
# Just push code and CI will run tests and build
```

### Production Setup (All features enabled)
```bash
# 1. Add to GitHub repository secrets:
CR_PAT=ghp_your_github_token
NETLIFY_AUTH_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_netlify_site_id
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET=your-bucket-name
MLFLOW_TRACKING_URI=https://your-mlflow-server.com

# 2. Enable GitHub Pages in repository settings
```

---

## Troubleshooting

### "Resource not accessible by integration"
- Go to Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"

### "CR_PAT secret not found"
- This is optional! The workflow will skip Docker push if not configured
- Add the secret only if you want to publish Docker images

### "NETLIFY_AUTH_TOKEN not set"
- This is optional! Frontend can be deployed manually
- Add the secret only if you want automatic deployments

### Workflow fails on "Run training script"
- Check that your model training script works locally first
- Training failures won't fail the entire CI pipeline (warning only)

---

## Checking Workflow Status

After configuring secrets, verify they work:

1. **View workflow runs:** Repository → Actions tab
2. **Check specific job:** Click on workflow run → View job details
3. **Look for notices:** Blue info boxes indicate skipped optional steps
4. **Look for warnings:** Yellow boxes indicate non-critical failures

**Healthy output looks like:**
- ✅ Tests pass
- ✅ Linting succeeds
- ✅ Docker build completes
- 🔵 Notice: Skipping optional deployments (if secrets not configured)

---

## Security Best Practices

1. **Never commit secrets to code** - Always use GitHub Secrets
2. **Use minimal permissions** - Give tokens only the permissions they need
3. **Rotate tokens regularly** - Update tokens every 90 days
4. **Use environment-specific tokens** - Different tokens for dev/staging/prod
5. **Monitor token usage** - Check GitHub token usage in settings

---

## Need Help?

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Netlify Docs:** https://docs.netlify.com/
- **AWS IAM Docs:** https://docs.aws.amazon.com/IAM/
- **MLflow Docs:** https://mlflow.org/docs/latest/index.html
