# Deployment Guide

## GitHub Pages Setup

The documentation site deploys automatically to GitHub Pages when you push to `main`.

### First-time Setup

1. **Enable GitHub Pages**:
   - Go to your repository: https://github.com/KG90-EG/Trading-Fun
   - Click **Settings** → **Pages**
   - Under "Source", select **GitHub Actions**
   - Click **Save**

2. **Verify Deployment**:
   - After enabling, push a commit or manually trigger the "Deploy Docs" workflow
   - Your docs will be available at: `https://KG90-EG.github.io/Trading-Fun/`

### Troubleshooting

#### Error: "Failed to create deployment (status: 404)"

This means GitHub Pages isn't enabled yet. Follow the setup steps above.

#### Error: "Resource not accessible by integration"

Ensure the workflow has the required permissions:
- Repository Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"
- Check "Allow GitHub Actions to create and approve pull requests"

## Netlify Deployment (Frontend)

The React frontend can be deployed to Netlify.

### Setup Netlify Deployment

1. **Create Netlify Account**:
   - Sign up at https://netlify.com

2. **Add Repository Secrets**:
   - Go to GitHub repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `NETLIFY_AUTH_TOKEN`: Your Netlify personal access token
     - `NETLIFY_SITE_ID`: Your Netlify site ID

3. **Get Netlify Credentials**:
   ```bash
   # Install Netlify CLI
   npm install -g netlify-cli
   
   # Login
   netlify login
   
   # Create site
   cd frontend
   netlify init
   
   # Get your Site ID and Auth Token
   netlify status
   ```

4. **Configure Build Settings** (if deploying manually):
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
   - Node version: 20

### Manual Deployment

```bash
# Build frontend
cd frontend
npm install
npm run build

# Deploy to Netlify
netlify deploy --prod --dir=dist
```

## Local Development

### Backend (Port 8000)

```bash
# Activate virtual environment
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Start backend
uvicorn trading_fun.server:app --reload --port 8000
```

### Frontend (Port 5173)

```bash
cd frontend
npm install
npm run dev
```

Access the application at: http://localhost:5173

## CI/CD Workflows

### Available Workflows

1. **CI** (`.github/workflows/ci.yml`)
   - Runs on: Push to any branch, Pull requests
   - Tests backend code, linting, type checking

2. **Deploy Docs** (`.github/workflows/pages.yml`)
   - Runs on: Push to main, Manual trigger
   - Deploys documentation to GitHub Pages

3. **Deploy Frontend** (`.github/workflows/deploy-frontend.yml`)
   - Runs on: Push to main, Manual trigger
   - Deploys React app to Netlify
   - Requires: Netlify secrets configured

4. **Model Promotion** (`.github/workflows/promotion.yml`)
   - Runs on: Daily at 4:00 UTC, Manual trigger
   - Trains new model, evaluates, and promotes if better

### Manual Workflow Triggers

```bash
# Using GitHub CLI
gh workflow run "Deploy Docs"
gh workflow run "Deploy Frontend (Netlify)"
gh workflow run "Model Promotion"

# Or use GitHub UI:
# Actions tab → Select workflow → Run workflow
```

## Environment Variables

### Backend (.env)

```bash
OPENAI_API_KEY=your_openai_key_here
REDIS_URL=redis://localhost:6379  # Optional
MLFLOW_TRACKING_URI=file:./mlruns  # Optional
```

### Frontend (.env.local)

```bash
VITE_API_URL=http://localhost:8000
```

## Production Checklist

- [ ] GitHub Pages enabled in repository settings
- [ ] Netlify site created and secrets configured (if using)
- [ ] OpenAI API key added to `.env` file
- [ ] All tests passing: `pytest`
- [ ] Frontend builds successfully: `npm run build`
- [ ] Backend starts without errors
- [ ] Model file exists: `models/prod_model.bin`

## Support

For issues or questions:
- Check GitHub Actions logs for deployment failures
- Review `DEPLOYMENT.md` for setup instructions
- Ensure all secrets and configurations are correct
