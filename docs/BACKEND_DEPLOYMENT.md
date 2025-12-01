# Backend Deployment Guide

This guide covers deploying the FastAPI backend to various cloud platforms.

---

## 📋 Pre-Deployment Checklist

### 1. **Environment Variables**
Required production environment variables:
```bash
# API Keys
OPENAI_API_KEY=your-openai-api-key

# Monitoring (Optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_ENABLED=true

# Application
PORT=8000
HOST=0.0.0.0
WORKERS=4
```

### 2. **Dependencies**
Ensure all dependencies are in `requirements.txt`:
```bash
pip freeze > requirements.txt
```

### 3. **Security Audit**
```bash
# Check for security vulnerabilities
pip install safety
safety check

# Scan for secrets
pip install detect-secrets
detect-secrets scan
```

### 4. **Test Production Build**
```bash
# Test with Gunicorn locally
gunicorn trading_fun.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 🚀 Deployment Options

### Option 1: Railway (Easiest, Recommended for MVP)

**Why Railway?**
- ✅ Zero-config Python deployments
- ✅ Free tier ($5 credit/month)
- ✅ Automatic HTTPS
- ✅ Built-in PostgreSQL/Redis if needed
- ✅ GitHub integration

**Steps**:

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create `railway.toml`** (in project root):
   ```toml
   [build]
   builder = "nixpacks"
   buildCommand = "pip install -r requirements.txt"
   
   [deploy]
   startCommand = "gunicorn trading_fun.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
   restartPolicyType = "on_failure"
   restartPolicyMaxRetries = 10
   ```

3. **Create `Procfile`** (optional, for clarity):
   ```
   web: gunicorn trading_fun.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

4. **Deploy**:
   ```bash
   railway init
   railway up
   ```

5. **Set Environment Variables**:
   ```bash
   railway variables set OPENAI_API_KEY=your-key
   railway variables set SENTRY_DSN=your-dsn
   ```

6. **Get URL**:
   ```bash
   railway open
   ```

---

### Option 2: Render

**Why Render?**
- ✅ Free tier (750 hours/month)
- ✅ Auto-deploy from Git
- ✅ Managed PostgreSQL/Redis
- ✅ Easy scaling

**Steps**:

1. **Create `render.yaml`** (in project root):
   ```yaml
   services:
     - type: web
       name: marketpredictor-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn trading_fun.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
       envVars:
         - key: OPENAI_API_KEY
           sync: false
         - key: PYTHON_VERSION
           value: 3.10.0
         - key: PORT
           value: 8000
       healthCheckPath: /api/health
       numInstances: 1
       plan: free
   ```

2. **Deploy via UI**:
   - Go to [https://dashboard.render.com](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Render auto-detects Python
   - Add environment variables
   - Click "Create Web Service"

3. **Deploy via CLI** (optional):
   ```bash
   # Install Render CLI
   brew tap render-oss/render
   brew install render
   
   # Deploy
   render deploy
   ```

---

### Option 3: AWS Elastic Beanstalk

**Why Elastic Beanstalk?**
- ✅ Auto-scaling and load balancing
- ✅ Integrates with AWS ecosystem
- ✅ Full control over infrastructure

**Steps**:

1. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

2. **Create `.ebextensions/python.config`**:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: trading_fun.server:app
       NumProcesses: 4
       NumThreads: 20
     aws:elasticbeanstalk:application:environment:
       PYTHONPATH: "/var/app/current:$PYTHONPATH"
   ```

3. **Create `Procfile`**:
   ```
   web: gunicorn trading_fun.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind :8000
   ```

4. **Initialize EB**:
   ```bash
   eb init -p python-3.10 marketpredictor-api
   ```

5. **Create Environment**:
   ```bash
   eb create marketpredictor-prod \
     --instance-type t3.small \
     --envvars OPENAI_API_KEY=your-key
   ```

6. **Deploy**:
   ```bash
   eb deploy
   ```

7. **Open**:
   ```bash
   eb open
   ```

---

### Option 4: Docker + Any Cloud Provider

**Why Docker?**
- ✅ Consistent across environments
- ✅ Works on any platform (AWS ECS, Google Cloud Run, Azure Container Instances)
- ✅ Full control

**Dockerfile** (already exists in project root):
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start with Gunicorn
CMD ["gunicorn", "trading_fun.server:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

**Deploy to AWS ECS**:

1. **Build and Push Image**:
   ```bash
   # Build
   docker build -t marketpredictor-api:latest .
   
   # Tag for ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
   
   docker tag marketpredictor-api:latest \
     your-account.dkr.ecr.us-east-1.amazonaws.com/marketpredictor-api:latest
   
   # Push
   docker push your-account.dkr.ecr.us-east-1.amazonaws.com/marketpredictor-api:latest
   ```

2. **Create ECS Task Definition** (`task-definition.json`):
   ```json
   {
     "family": "marketpredictor-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "api",
         "image": "your-account.dkr.ecr.us-east-1.amazonaws.com/marketpredictor-api:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "OPENAI_API_KEY",
             "value": "your-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/marketpredictor-api",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

3. **Create ECS Service**:
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name marketpredictor-api \
     --task-definition marketpredictor-api \
     --desired-count 2 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
   ```

**Deploy to Google Cloud Run**:
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/your-project/marketpredictor-api

# Deploy
gcloud run deploy marketpredictor-api \
  --image gcr.io/your-project/marketpredictor-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key
```

---

### Option 5: Heroku

**Why Heroku?**
- ✅ Very easy to deploy
- ✅ Free tier available
- ✅ Add-ons for Redis, PostgreSQL

**Steps**:

1. **Create `Procfile`**:
   ```
   web: gunicorn trading_fun.server:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

2. **Create `runtime.txt`**:
   ```
   python-3.10.13
   ```

3. **Deploy**:
   ```bash
   # Login
   heroku login
   
   # Create app
   heroku create marketpredictor-api
   
   # Set environment variables
   heroku config:set OPENAI_API_KEY=your-key
   
   # Deploy
   git push heroku main
   
   # Open
   heroku open
   ```

---

## 🔒 Security Best Practices

### 1. **Environment Variables**
```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use platform-specific secret managers
# Railway: railway variables set KEY=value
# Render: Add in dashboard
# AWS: Use Secrets Manager or Parameter Store
```

### 2. **CORS Configuration**
Update allowed origins in `trading_fun/server.py`:
```python
origins = [
    "https://your-frontend.netlify.app",
    "https://your-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. **Rate Limiting**
Already implemented in `trading_fun/rate_limiter.py`. Consider adding:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/stocks/{ticker}")
@limiter.limit("10/minute")
async def get_stock_data(request: Request, ticker: str):
    # ...
```

### 4. **API Key Security**
```python
# Rotate keys regularly
# Use different keys for dev/staging/prod
# Monitor API usage
```

---

## 📊 Monitoring & Observability

### 1. **Health Checks**
Endpoint: `GET /api/health`
```python
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 2. **Prometheus Metrics**
Already integrated. Metrics available at `/metrics`:
```
# Request count by endpoint
http_requests_total{method="GET",endpoint="/api/stocks"}

# Request latency
http_request_duration_seconds{endpoint="/api/stocks"}

# Active connections
http_active_connections
```

### 3. **Sentry Error Tracking**
Add to `trading_fun/server.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production",
)
```

### 4. **Logging**
Already configured in `trading_fun/logging_config.py`:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Server started", extra={"port": 8000})
```

---

## 🧪 Post-Deployment Testing

### 1. **Health Check**
```bash
curl https://your-backend.com/api/health
```

### 2. **Load Testing**
```bash
# Install k6
brew install k6

# Create test.js
echo '
import http from "k6/http";
export let options = {
  vus: 10,
  duration: "30s",
};
export default function() {
  http.get("https://your-backend.com/api/health");
}
' > test.js

# Run
k6 run test.js
```

### 3. **API Documentation**
Verify Swagger UI: `https://your-backend.com/docs`

---

## 🔄 CI/CD Pipeline

### GitHub Actions (`.github/workflows/backend-deploy.yml`):
```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'trading_fun/**'
      - 'requirements.txt'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Lint
        run: flake8 . --max-line-length=127

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 🐛 Troubleshooting

### Issue: Worker timeout errors
**Solution**: Increase timeout in Gunicorn:
```bash
gunicorn ... --timeout 120
```

### Issue: High memory usage
**Solution**: Reduce workers or add memory limits:
```bash
# Fewer workers
gunicorn ... --workers 2

# Docker memory limit
docker run --memory="1g" ...
```

### Issue: Slow API responses
**Solution**: Check cache hit rate and rate limiter:
```python
# Monitor cache metrics
logger.info(f"Cache hit rate: {cache.hit_rate()}")
```

### Issue: WebSocket connection fails
**Solution**: Ensure WebSocket protocol is allowed:
```nginx
# Nginx reverse proxy
location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 📚 References

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Railway Documentation](https://docs.railway.app/)
- [Render Documentation](https://render.com/docs)
- [AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
