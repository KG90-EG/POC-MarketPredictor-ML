# Production Deployment Guide

Complete guide for deploying POC-MarketPredictor-ML to production environments.

## Overview

This project supports multiple deployment methods:

| Method | Backend | Frontend | Complexity | Time |
|--------|---------|----------|------------|------|
| **Automated (GitHub Actions)** | Railway | Vercel | Low | 10-15 min |
| **CLI Script** | Railway | Vercel | Medium | 15-20 min |
| **Manual** | Any platform | Any platform | High | 30+ min |

**Recommended**: Automated deployment via GitHub Actions for CI/CD pipeline.

---

## Prerequisites

Before deploying, ensure you have:

### Required
- ✅ GitHub account with repository access
- ✅ Railway account (free tier available)
- ✅ Vercel account (free tier available)
- ✅ All secrets configured (see `GITHUB_SECRETS.md`)

### Optional
- ✅ AWS S3 bucket for model storage
- ✅ OpenAI API key for AI features
- ✅ Custom domain names

### Local Setup
- ✅ GitHub CLI: `brew install gh`
- ✅ Railway CLI: `npm install -g @railway/cli`
- ✅ Vercel CLI: `npm install -g vercel`

---

## Quick Start: Automated Deployment

### Step 1: Configure Secrets

Follow `GITHUB_SECRETS.md` to add all required secrets to GitHub repository:

```bash
# Required secrets
RAILWAY_TOKEN
VERCEL_TOKEN
VERCEL_ORG_ID
VERCEL_PROJECT_ID
```

### Step 2: Trigger Deployment

```bash
# Push to main branch
git push origin main

# Or manually trigger via GitHub Actions
gh workflow run deploy-production.yml
```

### Step 3: Monitor Deployment

```bash
# Watch deployment progress
gh run watch

# Or view in GitHub web UI
# https://github.com/KG90-EG/POC-MarketPredictor-ML/actions
```

### Step 4: Verify Deployment

```bash
# Check backend health
curl https://your-railway-app.railway.app/health

# Check frontend
curl https://your-project.vercel.app

# Test full integration
./scripts/verify_deployment.sh
```

**Deployment complete!** Backend and frontend are live with automatic SSL certificates.

---

## CLI Deployment Script

For more control or CI/CD troubleshooting:

### Installation

```bash
# Ensure CLIs are installed
npm install -g @railway/cli vercel

# Authenticate
railway login
vercel login
```

### Deploy Backend (Railway)

```bash
# Run automated deployment script
./scripts/deploy_production.sh --backend-only

# Or manually:
railway link ${RAILWAY_PROJECT_ID}
railway up
railway open
```

### Deploy Frontend (Vercel)

```bash
# Run automated deployment script
./scripts/deploy_production.sh --frontend-only

# Or manually:
cd frontend
vercel --prod
```

### Full Deployment

```bash
# Deploy both backend and frontend
./scripts/deploy_production.sh --all

# With environment validation
./scripts/deploy_production.sh --all --validate

# With health checks
./scripts/deploy_production.sh --all --verify
```

---

## Deployment Script Reference

### scripts/deploy_production.sh

Comprehensive deployment automation with:
- ✅ Pre-deployment validation
- ✅ Environment variable verification
- ✅ Health checks after deployment
- ✅ Rollback on failure
- ✅ Deployment notifications

### Usage

```bash
./scripts/deploy_production.sh [OPTIONS]

Options:
  --all              Deploy backend and frontend
  --backend-only     Deploy backend only (Railway)
  --frontend-only    Deploy frontend only (Vercel)
  --validate         Validate environment before deploying
  --verify           Run health checks after deployment
  --rollback         Rollback to previous deployment
  --dry-run          Simulate deployment without changes
  -h, --help         Show help message

Examples:
  # Full production deployment with verification
  ./scripts/deploy_production.sh --all --validate --verify

  # Backend only (for API changes)
  ./scripts/deploy_production.sh --backend-only --verify

  # Rollback to previous version
  ./scripts/deploy_production.sh --rollback
```

### Environment Validation

Script checks for:
- Required secrets configured
- Valid API keys and tokens
- Database connectivity (if applicable)
- S3 bucket access (if configured)
- Model files present

### Health Checks

Post-deployment verification:
- Backend `/health` endpoint responds
- Frontend loads successfully
- WebSocket connection works
- API endpoints return expected responses
- Metrics endpoint accessible

---

## Manual Deployment

### Backend: Railway

#### 1. Create Railway Project

```bash
# Login to Railway
railway login

# Create new project
railway init

# Link to existing project (if already created)
railway link
```

#### 2. Configure Environment Variables

Set in Railway dashboard or via CLI:

```bash
# Core settings
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=info

# Optional: OpenAI API
railway variables set OPENAI_API_KEY=sk-...

# Optional: AWS S3
railway variables set AWS_ACCESS_KEY_ID=AKIA...
railway variables set AWS_SECRET_ACCESS_KEY=...
railway variables set AWS_S3_BUCKET=your-bucket

# Optional: MLflow
railway variables set MLFLOW_TRACKING_URI=https://...
railway variables set MLFLOW_EXPERIMENT_NAME=production
```

#### 3. Deploy Backend

```bash
# Deploy from current directory
railway up

# Or deploy specific service
railway up --service backend

# Check deployment status
railway status

# View logs
railway logs

# Open deployed app
railway open
```

#### 4. Custom Domain (Optional)

```bash
# Add custom domain via CLI
railway domain

# Or in Railway dashboard:
# Settings → Domains → Add Domain → your-api.com
```

### Frontend: Vercel

#### 1. Create Vercel Project

```bash
# Login to Vercel
vercel login

# Link project
cd frontend
vercel link

# Or create new project
vercel
```

#### 2. Configure Environment Variables

Set in Vercel dashboard or via CLI:

```bash
# Backend API URL
vercel env add VITE_API_URL production
# Enter: https://your-railway-app.railway.app

# Optional: Analytics
vercel env add VITE_ANALYTICS_ID production
# Enter: G-XXXXXXXXXX
```

#### 3. Deploy Frontend

```bash
# Deploy to production
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs

# Open deployed app
vercel open
```

#### 4. Custom Domain (Optional)

```bash
# Add domain via CLI
vercel domains add your-app.com

# Or in Vercel dashboard:
# Settings → Domains → Add → your-app.com
```

---

## Alternative Platforms

### Backend Alternatives

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 poc-marketpredictor

# Create environment
eb create production-env

# Deploy
eb deploy

# Open
eb open
```

#### Google Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/market-predictor

# Deploy
gcloud run deploy market-predictor \
  --image gcr.io/PROJECT_ID/market-predictor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Get URL
gcloud run services describe market-predictor --format 'value(status.url)'
```

#### Heroku

```bash
# Create app
heroku create poc-marketpredictor

# Add buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main

# Open
heroku open
```

### Frontend Alternatives

#### Netlify

```bash
# Install CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod --dir dist
```

#### AWS Amplify

```bash
# Install CLI
npm install -g @aws-amplify/cli

# Initialize
amplify init

# Add hosting
amplify add hosting

# Deploy
amplify publish
```

#### Cloudflare Pages

```bash
# Install CLI
npm install -g wrangler

# Login
wrangler login

# Deploy
cd frontend
npm run build
wrangler pages publish dist
```

---

## Rollback Procedures

### Railway Rollback

```bash
# View deployments
railway deployments

# Rollback to specific deployment
railway rollback DEPLOYMENT_ID

# Or via script
./scripts/deploy_production.sh --rollback
```

### Vercel Rollback

```bash
# List deployments
vercel ls

# Promote previous deployment
vercel promote DEPLOYMENT_URL

# Or via dashboard:
# Deployments → Previous deployment → Promote to Production
```

### GitHub Actions Rollback

```bash
# Revert last commit
git revert HEAD
git push origin main

# Or redeploy specific commit
gh workflow run deploy-production.yml --ref COMMIT_SHA
```

---

## Monitoring and Health Checks

### Backend Health Check

```bash
# Basic health
curl https://your-railway-app.railway.app/health

# Detailed metrics
curl https://your-railway-app.railway.app/metrics

# Expected response:
# {"status": "healthy", "version": "1.0.0", "uptime": 3600}
```

### Frontend Health Check

```bash
# Check frontend loads
curl -I https://your-project.vercel.app

# Expected: HTTP 200 OK
```

### WebSocket Connection Test

```bash
# Test WebSocket
python examples/websocket_client.py --url wss://your-railway-app.railway.app/ws

# Expected: Connection successful, receiving real-time updates
```

### Automated Health Checks

```bash
# Run comprehensive verification
./scripts/verify_deployment.sh

# Or specific checks
./scripts/verify_deployment.sh --backend-only
./scripts/verify_deployment.sh --frontend-only
```

---

## Troubleshooting

### Deployment Fails: Missing Dependencies

**Issue**: Build fails with `ModuleNotFoundError`

**Solution**:
```bash
# Ensure requirements.txt is up to date
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Railway Deployment Timeout

**Issue**: Deployment times out during build

**Solution**:
1. Check Railway build logs for specific error
2. Optimize Dockerfile (use multi-stage builds)
3. Reduce dependencies in `requirements.txt`
4. Contact Railway support for increased timeout

### Vercel Build Fails

**Issue**: Frontend build fails with `VITE_API_URL is not defined`

**Solution**:
```bash
# Set environment variable in Vercel
vercel env add VITE_API_URL production
# Enter: https://your-railway-app.railway.app

# Redeploy
vercel --prod
```

### Backend Crashes on Startup

**Issue**: Railway app starts but crashes immediately

**Solution**:
```bash
# Check logs
railway logs --tail

# Common issues:
# 1. Missing environment variables
railway variables

# 2. Port binding issue - ensure using Railway's PORT
# Check server.py uses: int(os.environ.get("PORT", 8000))

# 3. Database connection failure
# Verify database credentials
```

### CORS Errors in Production

**Issue**: Frontend can't connect to backend due to CORS

**Solution**:
```python
# In trading_fun/server.py, ensure correct origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### SSL Certificate Issues

**Issue**: `SSL certificate verification failed`

**Solution**:
- Railway and Vercel provide automatic SSL
- Ensure custom domains have DNS configured correctly
- Wait 24-48 hours for SSL propagation
- Check domain DNS settings: `dig your-domain.com`

---

## Security Checklist

Before deploying to production:

- [ ] All secrets in environment variables (not hardcoded)
- [ ] CORS origins restricted to production domains
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Authentication implemented (if required)
- [ ] HTTPS enforced (automatic with Railway/Vercel)
- [ ] Security headers configured
- [ ] Pre-commit hooks active
- [ ] Dependencies scanned for vulnerabilities
- [ ] Logs don't expose sensitive data

---

## Performance Optimization

### Backend Optimizations

```python
# Enable response caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

# Use async database queries
# Enable connection pooling
# Implement request batching
```

### Frontend Optimizations

```bash
# Enable build optimizations in vite.config.js
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },
}
```

### CDN Configuration

Both Railway and Vercel provide automatic CDN:
- Static assets cached globally
- Auto-invalidation on new deployments
- Edge caching for improved latency

---

## Scaling Considerations

### Railway Scaling

```bash
# Upgrade plan for higher resources
railway plan

# Configure auto-scaling (Pro plan)
# Settings → Resources → Enable Auto-scaling

# Horizontal scaling (multiple instances)
railway scale --replicas 3
```

### Vercel Scaling

Vercel automatically scales based on traffic:
- Serverless functions handle bursts
- CDN caches static assets globally
- No manual configuration needed

For high traffic:
- Upgrade to Pro plan for higher limits
- Implement edge middleware for optimization
- Use ISR (Incremental Static Regeneration)

---

## Cost Estimation

### Free Tier Limits

**Railway** (Free):
- $5/month credit
- 500 hours/month runtime
- 1GB RAM, 1 vCPU
- 1GB storage

**Vercel** (Free):
- 100GB bandwidth/month
- Unlimited websites
- Serverless functions: 100GB-hours

### Production Costs

**Railway** (Hobby - $5/month):
- $5 credit/month
- Shared resources
- Sufficient for small apps

**Railway** (Pro - $20/month):
- $20 credit/month
- Priority support
- Team collaboration

**Vercel** (Pro - $20/month):
- 1TB bandwidth
- Team collaboration
- Analytics included

**Estimated monthly cost**: $10-40 depending on traffic.

---

## CI/CD Pipeline

### GitHub Actions Workflow

Already configured in `.github/workflows/deploy-production.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        uses: bervProject/railway-deploy@main
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: backend

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### Continuous Integration

Before deployment, CI runs:
1. ✅ Pre-commit hooks (linting, formatting)
2. ✅ Unit tests
3. ✅ Integration tests
4. ✅ Security scans
5. ✅ Build verification

Deployment only proceeds if all checks pass.

---

## Post-Deployment

### Verify Deployment

```bash
# Run comprehensive checks
./scripts/verify_deployment.sh --all

# Test specific functionality
curl https://your-api.com/health
curl https://your-api.com/docs
curl https://your-api.com/metrics
```

### Update Documentation

```bash
# Update PRODUCTION_READY.md with URLs
# Add deployment date and version
# Document any issues encountered
```

### Monitor Performance

- Check Railway/Vercel dashboards for metrics
- Set up alerts for downtime
- Monitor error rates in logs
- Track API response times

### Announce Deployment

```bash
# Tag release
git tag -a v1.0.0 -m "Production release 1.0.0"
git push origin v1.0.0

# Create GitHub release
gh release create v1.0.0 --title "Production Release 1.0.0" --notes "Initial production deployment"
```

---

## Support and Resources

- **Railway Documentation**: https://docs.railway.app/
- **Vercel Documentation**: https://vercel.com/docs
- **GitHub Actions**: https://docs.github.com/en/actions
- **Project Documentation**: `docs/`
- **Deployment Issues**: Open issue on GitHub

---

## Quick Reference

| Task | Command |
|------|---------|
| **Deploy via GitHub Actions** | `git push origin main` |
| **Deploy backend (CLI)** | `./scripts/deploy_production.sh --backend-only` |
| **Deploy frontend (CLI)** | `./scripts/deploy_production.sh --frontend-only` |
| **Full deployment** | `./scripts/deploy_production.sh --all` |
| **Rollback** | `./scripts/deploy_production.sh --rollback` |
| **Health check** | `./scripts/verify_deployment.sh` |
| **View logs (Railway)** | `railway logs` |
| **View logs (Vercel)** | `vercel logs` |

---

## Next Steps

1. ✅ Configure all secrets (see `GITHUB_SECRETS.md`)
2. ✅ Run deployment script with `--validate` flag
3. ✅ Monitor first deployment closely
4. ✅ Set up custom domains (optional)
5. ✅ Configure monitoring alerts
6. ✅ Document production URLs in README.md

**You're ready to deploy! Choose your preferred method above and follow the steps.** 🚀
