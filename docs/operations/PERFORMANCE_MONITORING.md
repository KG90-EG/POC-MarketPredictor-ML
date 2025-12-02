# Performance Monitoring Guide

**Last Updated**: December 1, 2025

This guide covers the performance monitoring setup for Trading Fun using Prometheus and Grafana.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Available Metrics](#available-metrics)
5. [Grafana Dashboards](#grafana-dashboards)
6. [Alerting](#alerting)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

The monitoring stack consists of:
- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Visualization and dashboards
- **Trading Fun API**: Exposes metrics via `/prometheus` endpoint

### Why Monitoring?

- 📊 Track API performance and bottlenecks
- 🎯 Monitor model prediction accuracy and latency
- 💾 Measure cache efficiency
- 🚨 Set up alerts for anomalies
- 📈 Capacity planning and optimization

---

## Architecture

```
┌─────────────────┐
│  Trading Fun API│
│  (Port 8000)    │
│  /prometheus    │
└────────┬────────┘
         │ scrapes metrics
         │ every 10s
         ▼
┌─────────────────┐
│  Prometheus     │
│  (Port 9090)    │
│  Storage: TSDB  │
└────────┬────────┘
         │ queries
         ▼
┌─────────────────┐
│  Grafana        │
│  (Port 3001)    │
│  Dashboards     │
└─────────────────┘
```

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Trading Fun API running on port 8000
- Ports 9090 (Prometheus) and 3001 (Grafana) available

### Step 1: Install Dependencies

```bash
# Install prometheus-client
pip install prometheus-client==0.21.0

# Or use requirements.txt
pip install -r requirements.txt
```

### Step 2: Start Monitoring Stack

```bash
# Start Prometheus and Grafana
docker-compose up -d prometheus grafana

# Check status
docker-compose ps

# View logs
docker-compose logs -f prometheus grafana
```

### Step 3: Start Trading Fun API

```bash
# Ensure the API is running
uvicorn trading_fun.server:app --reload --port 8000
```

### Step 4: Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Trading Fun API | http://localhost:8000 | - |
| API Metrics (Prometheus format) | http://localhost:8000/prometheus | - |
| API Metrics (JSON) | http://localhost:8000/metrics | - |
| Prometheus UI | http://localhost:9090 | - |
| Grafana | http://localhost:3001 | admin / admin |

### Step 5: View Dashboard

1. Open Grafana: http://localhost:3001
2. Login with `admin / admin` (change password on first login)
3. Navigate to **Dashboards** → **Trading Fun API - Performance Monitoring**
4. Dashboard auto-refreshes every 10 seconds

---

## Available Metrics

### API Performance Metrics

#### `http_requests_total`
- **Type**: Counter
- **Description**: Total number of HTTP requests
- **Labels**: `method`, `endpoint`, `status`
- **Usage**: Track request volume and error rates

```promql
# Requests per second by endpoint
rate(http_requests_total[5m])

# Error rate (5xx errors)
rate(http_requests_total{status=~"5.."}[5m])
```

#### `http_request_duration_seconds`
- **Type**: Histogram
- **Description**: HTTP request latency in seconds
- **Labels**: `method`, `endpoint`
- **Buckets**: 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0

```promql
# p95 response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

### Model Metrics

#### `model_predictions_total`
- **Type**: Counter
- **Description**: Total number of model predictions
- **Labels**: `model_type`

```promql
# Predictions per minute
rate(model_predictions_total[1m]) * 60
```

#### `model_prediction_duration_seconds`
- **Type**: Histogram
- **Description**: Model prediction latency
- **Labels**: `model_type`

```promql
# p99 prediction time
histogram_quantile(0.99, rate(model_prediction_duration_seconds_bucket[5m]))
```

#### `model_prediction_probability`
- **Type**: Histogram
- **Description**: Distribution of prediction probabilities
- **Buckets**: 0.0 to 1.0 in 0.1 increments

```promql
# Predictions with high confidence (>0.7)
rate(model_prediction_probability_bucket{le="0.8"}[5m]) - rate(model_prediction_probability_bucket{le="0.7"}[5m])
```

### Cache Metrics

#### `cache_hits_total` / `cache_misses_total`
- **Type**: Counter
- **Description**: Cache hit/miss counts
- **Labels**: `cache_type`

```promql
# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) * 100
```

#### `cache_size_bytes`
- **Type**: Gauge
- **Description**: Current cache size in bytes
- **Labels**: `cache_type`

### Ranking Metrics

#### `ranking_generation_duration_seconds`
- **Type**: Histogram
- **Description**: Time to generate rankings
- **Labels**: `country`

```promql
# Average ranking time by country
histogram_quantile(0.5, rate(ranking_generation_duration_seconds_bucket[5m]))
```

#### `ranking_tickers_processed`
- **Type**: Histogram
- **Description**: Number of tickers processed per ranking

### Crypto Metrics

#### `crypto_fetch_duration_seconds`
- **Type**: Histogram
- **Description**: Cryptocurrency data fetch latency

#### `crypto_items_fetched`
- **Type**: Histogram
- **Description**: Number of crypto items per request

### AI Analysis Metrics

#### `ai_analysis_requests_total`
- **Type**: Counter
- **Description**: Total AI analysis requests
- **Labels**: `cached` (yes/no)

#### `ai_analysis_duration_seconds`
- **Type**: Histogram
- **Description**: AI analysis latency

#### `ai_analysis_tokens_used`
- **Type**: Histogram
- **Description**: OpenAI tokens consumed

```promql
# Token usage rate
rate(ai_analysis_tokens_used_sum[1h])

# Average tokens per request
rate(ai_analysis_tokens_used_sum[5m]) / rate(ai_analysis_tokens_used_count[5m])
```

### System Health Metrics

#### `model_loaded`
- **Type**: Gauge
- **Description**: Model load status (1 = loaded, 0 = not loaded)

#### `openai_configured`
- **Type**: Gauge
- **Description**: OpenAI configuration status

#### `system_info`
- **Type**: Info
- **Description**: System information (service name, version)

### Error Metrics

#### `data_fetch_errors_total`
- **Type**: Counter
- **Description**: Data fetch errors
- **Labels**: `source`, `error_type`

#### `rate_limit_exceeded_total`
- **Type**: Counter
- **Description**: Rate limit violations
- **Labels**: `endpoint`

---

## Grafana Dashboards

### Pre-configured Dashboard

The default dashboard includes:

1. **API Request Rate**: Real-time request volume by endpoint
2. **API Response Time (p95)**: 95th percentile latency
3. **Model Predictions Per Minute**: ML inference rate
4. **Cache Hit Rate**: Cache efficiency gauge
5. **Model Loaded Status**: Health indicator
6. **OpenAI Configured**: Configuration status
7. **Ranking Generation Time**: Performance by country
8. **Model Prediction Distribution**: Probability heatmap
9. **Data Fetch Duration**: External API latency
10. **AI Analysis Requests**: Cached vs. fresh requests
11. **Rate Limit Violations**: Rate limiting alerts
12. **Data Fetch Errors**: Error tracking by source

### Creating Custom Dashboards

1. Go to Grafana → Dashboards → New Dashboard
2. Add Panel → Choose visualization type
3. Select Prometheus datasource
4. Write PromQL query
5. Configure panel options
6. Save dashboard

### Useful PromQL Queries

```promql
# Top 5 slowest endpoints
topk(5, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])))

# Request rate by status code
sum(rate(http_requests_total[5m])) by (status)

# Prediction success rate (probability > 0.5)
rate(model_prediction_probability_bucket{le="1.0"}[5m]) - rate(model_prediction_probability_bucket{le="0.5"}[5m])

# Cache efficiency
(rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))) * 100

# Error rate percentage
(sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100
```

---

## Alerting

### Setting Up Alerts in Grafana

1. **Create Alert Rule**:
   - Edit panel → Alert tab
   - Define condition (e.g., error rate > 1%)
   - Set evaluation interval
   - Configure notifications

2. **Notification Channels**:
   - Email
   - Slack
   - PagerDuty
   - Webhooks

### Example Alert Rules

#### High Error Rate
```yaml
Alert: High Error Rate
Condition: (error_rate > 5% for 5m)
Severity: Warning
Message: API error rate is above 5%
```

#### Slow Response Time
```yaml
Alert: Slow API Response
Condition: (p95_latency > 2s for 5m)
Severity: Warning
Message: API response time exceeds 2 seconds
```

#### Cache Miss Rate
```yaml
Alert: Low Cache Hit Rate
Condition: (cache_hit_rate < 50% for 10m)
Severity: Info
Message: Cache efficiency below 50%
```

#### Model Not Loaded
```yaml
Alert: Model Not Loaded
Condition: (model_loaded == 0)
Severity: Critical
Message: ML model is not loaded
```

### Prometheus Alert Rules (Optional)

Create `monitoring/alert_rules.yml`:

```yaml
groups:
  - name: trading_fun_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}%"
      
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API response time"
          description: "p95 latency is {{ $value }}s"
      
      - alert: ModelNotLoaded
        expr: model_loaded == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ML model not loaded"
          description: "The prediction model is not available"
```

Update `prometheus.yml`:
```yaml
rule_files:
  - "alert_rules.yml"
```

---

## Troubleshooting

### Prometheus Not Scraping Metrics

**Problem**: Prometheus shows target as "DOWN"

**Solutions**:
1. Check API is running: `curl http://localhost:8000/prometheus`
2. Verify Docker network: Use `host.docker.internal` on Mac/Windows
3. Check Prometheus logs: `docker-compose logs prometheus`
4. Verify scrape config in `monitoring/prometheus.yml`

### Grafana Dashboard Shows "No Data"

**Problem**: Panels show no data

**Solutions**:
1. Check Prometheus datasource connection
2. Verify time range (default: last 1 hour)
3. Run queries in Prometheus UI first
4. Check if metrics are being generated (make API requests)
5. Refresh dashboard or browser

### Metrics Not Updating

**Problem**: Metrics are stale

**Solutions**:
1. Check API middleware is active
2. Verify requests are reaching the API
3. Check for Python errors: `docker-compose logs api`
4. Restart services: `docker-compose restart`

### High Memory Usage

**Problem**: Prometheus consuming too much memory

**Solutions**:
1. Reduce retention period in `prometheus.yml`:
   ```yaml
   command:
     - '--storage.tsdb.retention.time=7d'
   ```
2. Increase scrape interval to 30s or 1m
3. Limit metric cardinality (fewer labels)

---

## Best Practices

### Performance

1. **Scrape Intervals**:
   - API metrics: 10-15 seconds
   - System metrics: 30-60 seconds
   - External services: 1-5 minutes

2. **Retention**:
   - Development: 7-14 days
   - Production: 30-90 days
   - Long-term: Export to cold storage

3. **Cardinality**:
   - Limit label values (avoid user IDs, UUIDs)
   - Use aggregation for high-cardinality metrics
   - Monitor Prometheus performance

### Monitoring

1. **Key Metrics** (Golden Signals):
   - **Latency**: Response time percentiles
   - **Traffic**: Request rate
   - **Errors**: Error rate and types
   - **Saturation**: Resource utilization

2. **Dashboard Organization**:
   - Overview dashboard (high-level)
   - Detailed dashboards per service
   - Debug dashboards for troubleshooting

3. **Alerting**:
   - Alert on symptoms, not causes
   - Actionable alerts only
   - Clear ownership and escalation

### Security

1. **Authentication**:
   - Change default Grafana password
   - Use strong passwords
   - Enable HTTPS in production

2. **Network**:
   - Limit Prometheus scrape targets
   - Use firewall rules
   - Internal network only

3. **Data Retention**:
   - GDPR compliance for user data
   - Anonymize sensitive metrics
   - Regular backups

---

## Advanced Configuration

### Prometheus Configuration

**High Availability**:
```yaml
global:
  external_labels:
    cluster: 'prod'
    replica: 'prometheus-1'
```

**Remote Write** (to long-term storage):
```yaml
remote_write:
  - url: "https://prometheus-storage.example.com/api/v1/write"
```

### Grafana Configuration

**LDAP Authentication**:
```ini
[auth.ldap]
enabled = true
config_file = /etc/grafana/ldap.toml
```

**SMTP for Alerts**:
```ini
[smtp]
enabled = true
host = smtp.gmail.com:587
user = alerts@example.com
password = secret
```

---

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboard Gallery](https://grafana.com/grafana/dashboards/)
- [Best Practices for Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review Prometheus targets: http://localhost:9090/targets
3. Test queries in Prometheus UI
4. Consult documentation or team

---

**Last Updated**: December 1, 2025  
**Version**: 1.0.0
