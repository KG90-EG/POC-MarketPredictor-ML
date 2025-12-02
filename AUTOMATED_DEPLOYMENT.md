# 🤖 Automated Deployment Guide

This guide covers automated deployment using GitHub Actions and CLI scripts.

---

## Option 1: GitHub Actions (Recommended)

### Setup (One-time)

1. **Get Railway Token**
   ```bash
   # Visit https://railway.app/account/tokens
   # Create new token with full access
   ```

2. **Get Vercel Token**
   ```bash
   # Visit https://vercel.com/account/tokens
   # Create new token
   ```

3. **Add GitHub Secrets**
   
   Go to: `https://github.com/KG90-EG/POC-MarketPredictor-ML/settings/secrets/actions`
   
   Add these secrets:
   ```
   RAILWAY_TOKEN=your-railway-token
   RAILWAY_PROJECT_ID=your-railway-project-id
   VERCEL_TOKEN=your-vercel-token
   VERCEL_ORG_ID=your-vercel-org-id
   VERCEL_PROJECT_ID=your-vercel-project-id
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   ```

4. **Get Railway Project ID**
   ```bash
   railway login
   railway link
   # Copy project ID from railway.json
   ```

5. **Get Vercel IDs**
   ```bash
   cd frontend
   vercel link
   # Copy org ID and project ID from .vercel/project.json
   ```

### Deploy

**Automatic** (on every push to main):
```bash
git push origin main
# GitHub Actions will automatically deploy
```

**Manual** (via GitHub UI):
1. Go to: `https://github.com/KG90-EG/POC-MarketPredictor-ML/actions`
2. Click "Deploy to Production"
3. Click "Run workflow"
4. Select branch and click "Run workflow"

**Monitor**:
```bash
# Watch deployment progress at:
https://github.com/KG90-EG/POC-MarketPredictor-ML/actions
```

---

## Option 2: CLI Script (Local)

### Prerequisites

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Install Vercel CLI
npm install -g vercel

# Install jq (macOS)
brew install jq

# Login to services
railway login
vercel login
```

### Setup Tokens

```bash
# Export Railway token (get from https://railway.app/account/tokens)
export RAILWAY_TOKEN=your-railway-token

# Vercel uses interactive login (already done with `vercel login`)
```

### Deploy Everything

```bash
cd /path/to/POC-MarketPredictor-ML

# Run automated deployment
./scripts/deploy_production.sh
```

This script will:
1. ✅ Run security checks
2. ✅ Deploy backend to Railway
3. ✅ Deploy frontend to Vercel
4. ✅ Update CORS configuration
5. ✅ Run production tests
6. ✅ Generate deployment summary

### Deploy Individual Services

**Backend only**:
```bash
./scripts/deploy_production.sh --backend-only
```

**Frontend only**:
```bash
./scripts/deploy_production.sh --frontend-only
```

---

## Option 3: Manual Commands

### Backend (Railway)

```bash
# Login
railway login

# Link project (first time only)
railway link

# Deploy
railway up

# Check status
railway status

# View logs
railway logs

# Get URL
railway open
```

### Frontend (Vercel)

```bash
# Login
vercel login

# Link project (first time only)
cd frontend
vercel link

# Deploy to production
vercel --prod --build-env VITE_API_URL=https://your-backend.railway.app

# View deployments
vercel ls

# View logs
vercel logs
```

---

## Deployment Workflow Comparison

| Method | Setup Time | Deploy Time | Auto-Deploy | Rollback | Best For |
|--------|-----------|-------------|-------------|----------|----------|
| **GitHub Actions** | 15 min (one-time) | 5-8 min | ✅ Yes | ✅ Easy | Teams, CI/CD |
| **CLI Script** | 5 min | 3-5 min | ❌ No | ⚠️ Manual | Quick deploys |
| **Manual** | 2 min | 2-3 min | ❌ No | ⚠️ Manual | Testing, debugging |

---

## Environment Variables Reference

### Railway (Backend)

Required in Railway dashboard → Variables:
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

Optional:
```bash
SENTRY_DSN=https://xxxxxxxxxxxxx@sentry.io/xxxxxxxxxxxxx
REDIS_URL=redis://default:password@host:6379
```

### Vercel (Frontend)

Required in Vercel dashboard → Settings → Environment Variables:
```bash
VITE_API_URL=https://your-backend.railway.app
```

Optional:
```bash
NODE_VERSION=18
VITE_APP_VERSION=1.0.0
SENTRY_DSN=https://xxxxxxxxxxxxx@sentry.io/xxxxxxxxxxxxx
```

---

## Post-Deployment

### Verify Deployment

```bash
# Test backend
./scripts/test_deployment.sh https://your-backend.railway.app

# Test frontend
open https://your-frontend.vercel.app

# Check logs
railway logs --tail
vercel logs --follow
```

### Monitor

- **Railway**: https://railway.app/project/[your-project]/deployments
- **Vercel**: https://vercel.com/[username]/[project]/deployments
- **Sentry** (if configured): https://sentry.io

### Rollback

**Railway**:
```bash
railway rollback
```

**Vercel**:
```bash
vercel rollback
# or via dashboard: Deployments → Previous deployment → Promote
```

---

## Troubleshooting

### GitHub Actions Fails

1. **Check secrets**: Verify all required secrets are set
2. **Check token permissions**: Tokens need write access
3. **View logs**: Actions tab → Failed workflow → Detailed logs
4. **Re-run**: Actions tab → Failed workflow → Re-run jobs

### CLI Script Fails

1. **Check tokens**:
   ```bash
   echo $RAILWAY_TOKEN  # Should show your token
   railway whoami       # Should show your account
   vercel whoami        # Should show your account
   ```

2. **Check connectivity**:
   ```bash
   railway status  # Should connect
   vercel ls       # Should list projects
   ```

3. **View detailed logs**:
   ```bash
   bash -x ./scripts/deploy_production.sh  # Debug mode
   ```

### Deployment Successful But App Not Working

1. **Check CORS**: Verify frontend URL in backend CORS origins
2. **Check environment variables**: Railway and Vercel dashboards
3. **Check logs**:
   ```bash
   railway logs --tail 100
   vercel logs --follow
   ```
4. **Test endpoints**:
   ```bash
   curl https://your-backend.railway.app/health
   curl https://your-backend.railway.app/docs
   ```

---

## Advanced Configuration

### Custom Domains

**Railway**:
```bash
railway domain add your-api-domain.com
```

**Vercel**:
```bash
vercel domains add your-app-domain.com
```

### Preview Deployments

**Automatic preview** on pull requests:
- Vercel: Automatic preview URLs
- Railway: PR environments (configure in settings)

### Environment-Specific Deployments

**Staging environment**:
```yaml
# In GitHub Actions, use:
on:
  push:
    branches:
      - staging

# Or manually trigger with staging environment
```

### Deployment Notifications

Add to `.github/workflows/deploy.yml`:
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Deployment completed: ${{ steps.deploy.outputs.url }}"
      }
```

---

## Cost Optimization

### Railway
- **Starter Plan**: $5/month (500 hours)
- **Pro Plan**: $20/month (no limits)
- Tip: Use sleep/wake for dev environments

### Vercel
- **Hobby**: Free (non-commercial)
- **Pro**: $20/month per user
- Tip: Optimize build times (<10 min for free tier)

---

## Security Best Practices

1. ✅ **Never commit** `.env` files
2. ✅ **Use GitHub secrets** for sensitive data
3. ✅ **Rotate tokens** every 90 days
4. ✅ **Enable 2FA** on Railway and Vercel
5. ✅ **Monitor logs** for unusual activity
6. ✅ **Use environment-specific** API keys

---

## Quick Reference

**Check deployment status**:
```bash
railway status
vercel ls --prod
```

**View logs**:
```bash
railway logs --tail
vercel logs
```

**Redeploy**:
```bash
railway up
vercel --prod
```

**Environment variables**:
```bash
railway variables
vercel env ls
```

---

**Last Updated**: December 2, 2025  
**For Support**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for manual deployment
