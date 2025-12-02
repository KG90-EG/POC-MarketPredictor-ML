# 🚀 Production Deployment Guide

**Date**: December 2, 2025  
**Status**: Ready for Production Deployment

This guide walks you through deploying the POC-MarketPredictor-ML application to production using Railway (Backend) and Vercel (Frontend).

---

## 📋 Pre-Deployment Checklist

### Required Accounts & Keys
- [x] GitHub account (for code access)
- [ ] Railway account (https://railway.app)
- [ ] Vercel account (https://vercel.com)
- [ ] OpenAI API Key (https://platform.openai.com/api-keys)

### Optional Services
- [ ] Sentry account for error tracking (https://sentry.io)
- [ ] Redis Cloud for distributed caching (https://redis.com)

---

## 🔧 Step 1: Backend Deployment (Railway)

### 1.1 Create Railway Project

1. **Sign up/Login** to Railway: https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account and select `KG90-EG/POC-MarketPredictor-ML`

### 1.2 Configure Environment Variables

In Railway dashboard, add these environment variables:

```bash
# Required
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Optional (for enhanced features)
SENTRY_DSN=https://xxxxxxxxxxxxx@sentry.io/xxxxxxxxxxxxx
REDIS_URL=redis://default:password@redis-xxxx.railway.internal:6379
```

### 1.3 Deploy Configuration

Railway will automatically detect:
- ✅ `railway.toml` (build & deploy settings)
- ✅ `Procfile` (start command with Gunicorn)
- ✅ `requirements.txt` (Python dependencies)

**Build Command** (auto-detected):
```bash
pip install -r requirements.txt
```

**Start Command** (from Procfile):
```bash
gunicorn trading_fun.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

### 1.4 Health Check Configuration

Railway will use the health check from `railway.toml`:
- **Path**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds

### 1.5 Get Backend URL

After deployment completes:
1. Click on your service in Railway dashboard
2. Go to **"Settings"** tab
3. Find **"Domains"** section
4. Copy the public URL (e.g., `https://your-app.railway.app`)

**Save this URL** - you'll need it for frontend deployment!

### 1.6 Test Backend Endpoints

```bash
# Health check
curl https://your-app.railway.app/health

# API documentation
open https://your-app.railway.app/docs

# Test ranking endpoint (may take 20-30s on first call)
curl https://your-app.railway.app/ranking?country=US&limit=20
```

---

## 🎨 Step 2: Frontend Deployment (Vercel)

### 2.1 Create Vercel Project

1. **Sign up/Login** to Vercel: https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import `KG90-EG/POC-MarketPredictor-ML` from GitHub
4. Select **"frontend"** directory as root

### 2.2 Configure Build Settings

Vercel will automatically detect Vite configuration:

**Framework Preset**: Vite  
**Root Directory**: `frontend`  
**Build Command**: `npm run build`  
**Output Directory**: `dist`  
**Install Command**: `npm install --legacy-peer-deps`

### 2.3 Configure Environment Variables

In Vercel dashboard, add:

```bash
# Required - Use your Railway backend URL from Step 1.5
VITE_API_URL=https://your-app.railway.app

# Optional
NODE_VERSION=18
VITE_APP_VERSION=1.0.0
```

**Important**: Replace `https://your-app.railway.app` with your actual Railway URL!

### 2.4 Deploy

Click **"Deploy"** and wait for build to complete (~2-3 minutes)

### 2.5 Get Frontend URL

After deployment:
- Vercel will provide a URL like `https://your-app.vercel.app`
- You can also set up a custom domain in Vercel settings

### 2.6 Test Frontend

1. Open `https://your-app.vercel.app`
2. Check console for errors (F12 → Console)
3. Test features:
   - Load Stock Rankings (US, EU, Asia)
   - Load Crypto Rankings
   - Search functionality
   - Click on stocks/crypto for detail sidebar
   - Refresh Rankings button

---

## 🔒 Step 3: Security Configuration

### 3.1 Update CORS Settings

Your frontend URL needs to be allowed in backend CORS settings.

**Edit `trading_fun/server.py`**:

```python
# Find the CORS middleware section (around line 80-90)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://your-app.vercel.app",  # Add your Vercel URL here
        # Add custom domain if you have one
        # "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push**:
```bash
git add trading_fun/server.py
git commit -m "feat: add production CORS origin"
git push origin main
```

Railway will auto-deploy the update!

### 3.2 Verify CORS

Test from browser console on your frontend:
```javascript
fetch('https://your-app.railway.app/health')
  .then(r => r.json())
  .then(console.log)
```

Should return `{"status": "healthy", ...}` without CORS errors.

---

## 🧪 Step 4: Production Testing

### 4.1 Backend API Tests

```bash
# Set your Railway URL
BACKEND_URL=https://your-app.railway.app

# Health check
curl $BACKEND_URL/health

# Stock rankings
curl "$BACKEND_URL/ranking?country=US&limit=10"

# Crypto rankings
curl "$BACKEND_URL/crypto/ranking?limit=10"

# Stock prediction
curl "$BACKEND_URL/predict_ticker?ticker=AAPL"

# Ticker info with AI analysis
curl "$BACKEND_URL/ticker_info?ticker=TSLA&include_ai=true"
```

### 4.2 Frontend UI Tests

Visit your Vercel URL and test:

**Stock Rankings**:
- [x] Load US stocks
- [x] Load EU stocks
- [x] Load Asia stocks
- [x] Pagination works
- [x] Search functionality
- [x] Click stock to open detail sidebar
- [x] AI analysis loads

**Crypto Rankings**:
- [x] Load top cryptocurrencies
- [x] Search crypto by name/symbol
- [x] Pagination works
- [x] Click crypto to open detail sidebar
- [x] Toggle NFT tokens
- [x] Change limit (20/50/100/200)

**General**:
- [x] Theme toggle works (light/dark)
- [x] Health check indicator works
- [x] Loading states display correctly
- [x] Error messages display correctly
- [x] Mobile responsive design works

### 4.3 Performance Tests

**Response Times** (should be < 3s after warmup):
- `/health`: < 100ms
- `/ranking`: 1-3s (first call may be 20-30s for model load)
- `/crypto/ranking`: 1-2s
- `/predict_ticker`: 500ms-2s

**Cache Verification**:
- Second call to same endpoint should be much faster (< 500ms)
- Check Railway logs for cache hits

**Monitoring**:
- Railway dashboard shows CPU/Memory usage
- Check `/prometheus` endpoint for metrics (if exposed)

---

## 📊 Step 5: Monitoring Setup (Optional)

### 5.1 Sentry Error Tracking

**Backend**:
1. Create Sentry project at https://sentry.io
2. Copy DSN from project settings
3. Add to Railway environment variables:
   ```
   SENTRY_DSN=https://xxxxxxxxxxxxx@sentry.io/xxxxxxxxxxxxx
   ```

**Frontend**:
1. Add Sentry SDK to frontend:
   ```bash
   cd frontend
   npm install @sentry/react @sentry/vite-plugin
   ```
2. Configure in `frontend/src/main.jsx` (already set up)
3. Add Sentry DSN to Vercel environment variables

### 5.2 Prometheus Metrics (Railway)

Railway doesn't expose custom ports, so Prometheus is best run locally or via Docker for development monitoring.

**For production monitoring**, consider:
- Railway's built-in metrics (CPU, Memory, Network)
- Sentry performance monitoring
- Custom application logs in Railway dashboard

---

## 🚨 Troubleshooting

### Backend Issues

**Problem**: Railway build fails with "Module not found"
- **Solution**: Check `requirements.txt` has all dependencies
- Run `pip freeze > requirements.txt` locally to capture all packages

**Problem**: Health check fails
- **Solution**: Check Railway logs for startup errors
- Verify `/health` endpoint works locally first
- Increase health check timeout in `railway.toml`

**Problem**: OpenAI API errors
- **Solution**: Verify `OPENAI_API_KEY` is set correctly in Railway
- Check OpenAI account has credits
- Check Railway logs for specific error messages

**Problem**: High response times (> 5s)
- **Solution**: First call loads model (expected 20-30s)
- Subsequent calls should use cache (< 2s)
- Check Railway logs for performance bottlenecks
- Consider upgrading Railway plan for more resources

### Frontend Issues

**Problem**: Vercel build fails
- **Solution**: Check `package.json` scripts are correct
- Ensure `npm install --legacy-peer-deps` is used
- Check build logs for specific error

**Problem**: API calls fail with CORS error
- **Solution**: Add Vercel domain to CORS origins in `server.py`
- Verify `VITE_API_URL` environment variable is set
- Check browser console for exact CORS error

**Problem**: Environment variables not loading
- **Solution**: Vercel requires variables to start with `VITE_`
- Redeploy after adding environment variables
- Check build logs to verify variables are present

**Problem**: 404 on page refresh
- **Solution**: Vercel should handle SPA routing automatically
- Verify `vercel.json` has correct redirects configuration

### General Issues

**Problem**: API key exposed in frontend
- **Solution**: Backend only! Never put API keys in frontend code
- Use `VITE_API_URL` to point to backend
- Backend handles all OpenAI API calls

**Problem**: Slow cold starts
- **Solution**: Railway free tier has cold starts (~30s)
- Consider upgrading to paid plan for always-on service
- First request after idle loads model (expected)

---

## 🎯 Post-Deployment Checklist

- [ ] Backend deployed to Railway ✅
- [ ] Frontend deployed to Vercel ✅
- [ ] Environment variables configured ✅
- [ ] CORS origins updated ✅
- [ ] All endpoints tested ✅
- [ ] Frontend UI tested ✅
- [ ] Error tracking (Sentry) set up
- [ ] Custom domain configured (optional)
- [ ] SSL/HTTPS verified ✅ (automatic on Railway/Vercel)
- [ ] API documentation accessible at `/docs`
- [ ] Performance metrics monitored

---

## 🔗 Important URLs

**Backend (Railway)**:
- Dashboard: https://railway.app/project/[your-project-id]
- API: https://your-app.railway.app
- Docs: https://your-app.railway.app/docs
- Health: https://your-app.railway.app/health

**Frontend (Vercel)**:
- Dashboard: https://vercel.com/[username]/[project]
- App: https://your-app.vercel.app
- Deployments: https://vercel.com/[username]/[project]/deployments

**Monitoring**:
- Sentry: https://sentry.io/organizations/[org]/projects/[project]
- Railway Logs: https://railway.app/project/[project-id]/service/[service-id]

---

## 📝 Next Steps

After successful deployment, consider:

1. **Custom Domain**: Set up custom domain in Vercel/Railway settings
2. **A/B Testing**: Implement model version testing (see BACKLOG.md)
3. **Enhanced AI**: Add sector analysis and risk scoring
4. **Cloud Storage**: Migrate models to S3/GCS
5. **Advanced Monitoring**: Set up Grafana Cloud or Datadog
6. **CI/CD**: Automate deployments via GitHub Actions
7. **Rate Limiting**: Monitor and adjust rate limits based on usage
8. **Scaling**: Upgrade Railway/Vercel plans as traffic grows

---

## 🆘 Support

**Documentation**:
- [Backend Deployment Guide](docs/BACKEND_DEPLOYMENT.md)
- [Frontend Deployment Guide](docs/FRONTEND_DEPLOYMENT.md)
- [BACKLOG.md](BACKLOG.md)
- [README.md](README.md)

**Logs & Debugging**:
- Railway logs: Real-time in dashboard
- Vercel logs: Build logs in deployment details
- Browser console: Frontend errors (F12)

**Issues**: Create issue on GitHub repository

---

**Last Updated**: December 2, 2025  
**Version**: 1.0.0  
**Deployment Status**: 🟢 Ready for Production
