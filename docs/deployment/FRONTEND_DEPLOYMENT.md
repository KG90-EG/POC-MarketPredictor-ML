# Frontend Deployment Guide

This guide covers deploying the Trading Fun frontend to various platforms.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Netlify Deployment](#netlify-deployment)
3. [Vercel Deployment](#vercel-deployment)
4. [Environment Variables](#environment-variables)
5. [Build Configuration](#build-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Node.js 18+ installed
- Git repository access
- Backend API deployed and accessible
- Account on deployment platform (Netlify/Vercel)

---

## Netlify Deployment

### Quick Deploy (Recommended)

**Option 1: Deploy via Netlify Dashboard**

1. **Sign in to Netlify**: https://app.netlify.com
2. **Import from Git**:
   - Click "Add new site" → "Import an existing project"
   - Connect to GitHub and select your repository
3. **Configure Build Settings**:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
   - Node version: `18`
4. **Add Environment Variables**:
   - Go to Site settings → Environment variables
   - Add `VITE_API_URL` with your backend API URL
   - Example: `https://your-backend-api.com` or `https://poc-marketpredictor-ml.onrender.com`
5. **Deploy**: Click "Deploy site"

**Option 2: Deploy via Netlify CLI**

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Login to Netlify
netlify login

# Navigate to frontend directory
cd frontend

# Build the project
npm run build

# Deploy
netlify deploy --prod --dir=dist

# Follow prompts to create new site or link existing
```

### Configuration Files

The repository includes:

1. **netlify.toml** (root directory):
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "frontend/dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **frontend/public/_redirects**:
```
/*    /index.html   200
```

This ensures SPA routing works correctly (all routes redirect to index.html).

### Custom Domain (Optional)

1. Go to Site settings → Domain management
2. Add custom domain
3. Configure DNS:
   - Add CNAME record pointing to your Netlify subdomain
   - Or use Netlify DNS (recommended)

---

## Vercel Deployment

### Quick Deploy

**Option 1: Deploy via Vercel Dashboard**

1. **Sign in to Vercel**: https://vercel.com
2. **Import Project**:
   - Click "Add New" → "Project"
   - Import from GitHub
   - Select your repository
3. **Configure Project**:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. **Environment Variables**:
   - Add `VITE_API_URL` with your backend URL
5. **Deploy**: Click "Deploy"

**Option 2: Deploy via Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Navigate to frontend
cd frontend

# Deploy
vercel --prod
```

### vercel.json (Optional)

Create `frontend/vercel.json` for additional configuration:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://api.example.com` |

### Setting Environment Variables

**Netlify**:
1. Site settings → Environment variables
2. Add variable key and value
3. Redeploy site

**Vercel**:
1. Project Settings → Environment Variables
2. Add variable key and value
3. Select environments (Production/Preview/Development)
4. Redeploy

**Local Development**:
Create `frontend/.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

---

## Build Configuration

### Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### Vite Configuration

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    outDir: 'dist',
    sourcemap: false, // Set to true for debugging production
  },
})
```

### Build Optimization

**Enable production optimizations**:

1. **Code Splitting**: Vite automatically splits code
2. **Minification**: Enabled by default in production
3. **Tree Shaking**: Dead code elimination
4. **Asset Optimization**: Images and CSS minified

**Optional: Add to vite.config.js**:
```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'axios'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
})
```

---

## Troubleshooting

### Build Fails

**Error: "Cannot find module"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Error: "Out of memory"**
```bash
# Increase Node memory
NODE_OPTIONS="--max-old-space-size=4096" npm run build
```

### API Connection Issues

**CORS Errors**

Backend must allow frontend origin:
```python
# In backend (server.py)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Mixed Content (HTTP/HTTPS)**

- Ensure backend is HTTPS if frontend is HTTPS
- Or use relative URLs for same-origin deployment

### Routing Issues

**404 on page refresh**

Ensure redirects are configured:
- Netlify: `_redirects` file in `frontend/public/`
- Vercel: Rewrites in `vercel.json`

### Environment Variables Not Working

**Check**:
1. Variable name starts with `VITE_` prefix
2. Variables set in deployment platform
3. Site redeployed after adding variables
4. Using `import.meta.env.VITE_API_URL` (not `process.env`)

**Debug**:
```javascript
// In src/api.js
console.log('API URL:', import.meta.env.VITE_API_URL)
```

---

## Deployment Checklist

- [ ] Backend API deployed and accessible
- [ ] `VITE_API_URL` environment variable configured
- [ ] Backend CORS configured for frontend domain
- [ ] Build command tested locally (`npm run build`)
- [ ] `_redirects` file in `frontend/public/` (Netlify)
- [ ] SSL certificate active (HTTPS)
- [ ] Custom domain configured (optional)
- [ ] Error pages customized (optional)
- [ ] Analytics configured (optional)
- [ ] Performance monitoring setup (optional)

---

## Performance Optimization

### Recommended Settings

**Netlify**:
- Enable Asset Optimization (CSS/JS/Images)
- Enable Prerendering for static content
- Configure CDN caching

**Vercel**:
- Edge Network automatically enabled
- Automatic image optimization
- Serverless functions for API routes (if needed)

### Monitoring

**Tools**:
- Lighthouse (Chrome DevTools)
- WebPageTest
- GTmetrix
- Netlify Analytics / Vercel Analytics

**Targets**:
- Performance Score: 90+
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Cumulative Layout Shift: < 0.1

---

## CI/CD Integration

### Automatic Deployments

Both Netlify and Vercel support automatic deployments:

1. **Production**: Deploys on push to `main` branch
2. **Preview**: Deploys on pull requests
3. **Branch Deploys**: Deploys on specific branches

### GitHub Actions (Alternative)

```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      - name: Build
        working-directory: ./frontend
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
      - name: Deploy to Netlify
        uses: netlify/actions/cli@master
        with:
          args: deploy --prod --dir=frontend/dist
        env:
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
```

---

## Cost Estimates

### Free Tier Limits

**Netlify**:
- 100GB bandwidth/month
- 300 build minutes/month
- 1 concurrent build
- Free SSL

**Vercel**:
- Unlimited bandwidth
- 100GB-hours compute/month
- Serverless functions
- Free SSL

### When to Upgrade

- High traffic (>100k visitors/month)
- Need more build minutes
- Custom build concurrency
- Advanced analytics

---

## Support & Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [Vite Documentation](https://vitejs.dev/guide/)
- [React Documentation](https://react.dev/)

---

**Last Updated**: December 1, 2025  
**Deployment Status**: ✅ Ready for Production
