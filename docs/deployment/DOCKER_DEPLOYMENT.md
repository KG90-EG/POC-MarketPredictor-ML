# Docker Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- Trained ML model in `models/random_forest.joblib`

## Quick Start

### 1. Build the Image

```bash
# From project root
docker build -t market_predictor:latest .
```

### 2. Run with Docker Compose

```bash
# Basic deployment (backend + frontend)
docker-compose -f config/deployment/docker-compose.yml up -d

# With monitoring (Prometheus + Grafana)
docker-compose -f config/deployment/docker-compose.yml --profile monitoring up -d
```

### 3. Access Services

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Prometheus:** http://localhost:9090 (if monitoring enabled)
- **Grafana:** http://localhost:3000 (if monitoring enabled)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Nginx (Port 5173)                                  │
│  • Serves frontend static files                     │
│  • Proxies /api to backend                         │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Backend API (Port 8000)                            │
│  • FastAPI application                              │
│  • Market regime detection                          │
│  • ML predictions                                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Prometheus (Port 9090) - Optional                  │
│  • Metrics collection                               │
│  • /metrics endpoint scraping                       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Grafana (Port 3000) - Optional                     │
│  • Dashboards & visualization                       │
│  • Default: admin/admin                             │
└─────────────────────────────────────────────────────┘
```

## Build Options

### Production Build
```bash
docker build -t market_predictor:latest .
```

### Development Build (with source maps)
```bash
docker build --build-arg NODE_ENV=development -t market_predictor:dev .
```

### Build without cache
```bash
docker build --no-cache -t market_predictor:latest .
```

## Docker Compose Commands

### Start Services
```bash
# Start all services
docker-compose -f config/deployment/docker-compose.yml up -d

# Start specific service
docker-compose -f config/deployment/docker-compose.yml up -d backend

# Start with monitoring
docker-compose -f config/deployment/docker-compose.yml --profile monitoring up -d
```

### Stop Services
```bash
# Stop all
docker-compose -f config/deployment/docker-compose.yml down

# Stop and remove volumes
docker-compose -f config/deployment/docker-compose.yml down -v
```

### View Logs
```bash
# All services
docker-compose -f config/deployment/docker-compose.yml logs -f

# Specific service
docker-compose -f config/deployment/docker-compose.yml logs -f backend

# Last 100 lines
docker-compose -f config/deployment/docker-compose.yml logs --tail=100 backend
```

### Restart Services
```bash
# Restart all
docker-compose -f config/deployment/docker-compose.yml restart

# Restart specific
docker-compose -f config/deployment/docker-compose.yml restart backend
```

## Environment Variables

Create `.env` file in project root:

```bash
# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
MODEL_PATH=/app/models/random_forest.joblib

# API Keys (optional)
OPENAI_API_KEY=your_key_here
COINGECKO_API_KEY=your_key_here

# Database (if using external)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Volume Mounts

The docker-compose.yml mounts these directories:

- `models/` → `/app/models` (read-only) - ML models
- `logs/` → `/app/logs` (read-write) - Application logs
- `data/` → `/app/data` (read-write) - Cache & temp data

## Health Checks

The backend container includes automatic health checks:

```bash
# Check health
docker inspect market_predictor_backend | grep -A 10 Health

# Manual health check
curl http://localhost:8000/health
```

**Health Check Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "uptime": 3600.5,
  "timestamp": "2026-01-11T10:30:00Z"
}
```

## Monitoring (Optional)

Enable monitoring stack with `--profile monitoring`:

### Prometheus

**Access:** http://localhost:9090

**Metrics Available:**
- `http_requests_total` - Request count
- `http_request_duration_seconds` - Response times
- `model_predictions_total` - ML predictions
- `cache_hit_rate` - Cache efficiency

### Grafana

**Access:** http://localhost:3000  
**Default Credentials:** admin/admin

**Pre-configured Dashboards:**
- System Overview
- API Performance
- ML Model Metrics
- Cache Statistics

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs market_predictor_backend

# Check model file
docker exec market_predictor_backend ls -lh /app/models/

# Verify dependencies
docker exec market_predictor_backend pip list
```

### Frontend Can't Connect to Backend

```bash
# Check network
docker network ls
docker network inspect market_predictor_network

# Test backend from frontend container
docker exec market_predictor_frontend curl http://backend:8000/health
```

### Model Not Found

```bash
# Check model mount
docker exec market_predictor_backend ls -lh /app/models/

# Copy model into container
docker cp models/random_forest.joblib market_predictor_backend:/app/models/
docker restart market_predictor_backend
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Limit memory (in docker-compose.yml)
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

## Production Checklist

- [ ] Build frontend: `cd frontend && npm run build`
- [ ] Train ML model: `python -m src.training.trainer`
- [ ] Set environment variables (`.env` file)
- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Set up log rotation
- [ ] Configure monitoring (Prometheus + Grafana)
- [ ] Set up automated backups (models, data)
- [ ] Configure alerts (Prometheus AlertManager)
- [ ] Test health checks
- [ ] Load testing (k6, locust)

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # Add load balancer (nginx/traefik)
```

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t market_predictor:latest .
      
      - name: Push to registry
        run: |
          docker tag market_predictor:latest your-registry/market_predictor:latest
          docker push your-registry/market_predictor:latest
```

## Security

### Best Practices

1. **Don't run as root** (already configured in Dockerfile)
2. **Use secrets management** (Docker secrets, Kubernetes secrets)
3. **Scan images** regularly:
   ```bash
   docker scan market_predictor:latest
   ```
4. **Keep base images updated**
5. **Use multi-stage builds** (reduces attack surface)
6. **Limit container capabilities**

### Network Security

```yaml
# Restrict backend to internal network only
services:
  backend:
    networks:
      - internal
    # Don't expose port directly
```

## Support

- **Documentation:** [docs/](../../docs/)
- **Issues:** [GitHub Issues](https://github.com/KG90-EG/POC-MarketPredictor-ML/issues)
- **Requirements:** [DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md](../../docs/DECISION_SUPPORT_SYSTEM_REQUIREMENTS.md)

---

**Last Updated:** 2026-01-11  
**Docker Version:** 20.10+  
**Compose Version:** 2.0+
