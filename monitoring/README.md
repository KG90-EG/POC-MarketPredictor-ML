# Monitoring Infrastructure

Complete monitoring stack for ML Trading Predictor using Prometheus and Grafana.

## Quick Start

### 1. Start Monitoring Stack

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

This starts:

- **Prometheus** (port 9090): Metrics collection and alerting
- **Grafana** (port 3000): Visualization dashboards
- **Alertmanager** (port 9093): Alert routing and notifications
- **Node Exporter** (port 9100): System metrics

### 2. Start Your ML API

Make sure your FastAPI application is running to expose metrics:

```bash
uvicorn src.trading_engine.api.server:app --reload
```

### 3. Access Dashboards

- **Grafana**: <http://localhost:3000>
  - Username: `admin`
  - Password: `admin123`
  - Dashboard: "ML Trading Predictor Monitoring"

- **Prometheus**: <http://localhost:9090>
  - Query metrics directly
  - View alert rules

- **Alertmanager**: <http://localhost:9093>
  - Manage alert routing

## Architecture

```
┌─────────────────┐
│   FastAPI App   │ (port 8000)
│  /monitoring/*  │
└────────┬────────┘
         │ scrape /monitoring/metrics
         ↓
┌─────────────────┐
│   Prometheus    │ (port 9090)
│  - Scrape       │
│  - Store        │
│  - Alert        │
└────────┬────────┘
         │ queries
         ↓
┌─────────────────┐
│    Grafana      │ (port 3000)
│  - Dashboards   │
│  - Visualize    │
└─────────────────┘
```

## Endpoints

### Metrics

- **`GET /monitoring/metrics`**: Prometheus scrape endpoint (text format)
  - Model performance metrics
  - Prediction statistics
  - Training metrics
  - Drift detection events
  - API performance
  - System health

### Health Checks

- **`GET /monitoring/health`**: Multi-component health check
  - Returns: `healthy` | `degraded` | `unhealthy`
  - Components: cache, API, model

- **`GET /monitoring/health/readiness`**: Kubernetes readiness probe
  - Checks if service is ready to accept traffic

- **`GET /monitoring/health/liveness`**: Kubernetes liveness probe
  - Simple alive check

### Drift Monitoring

- **`GET /monitoring/drift/status`**: Current drift detector statistics
- **`POST /monitoring/drift/update`**: Update drift monitor with prediction/actual
  - Query params: `prediction`, `actual`, `proba` (optional)
- **`POST /monitoring/drift/reset`**: Reset all drift detectors

### System Info

- **`GET /monitoring/system/info`**: System metadata (Python version, platform, config)
- **`GET /monitoring/cache/stats`**: Cache performance metrics

## Metrics Reference

### Model Performance

```promql
# Model accuracy
ml_model_accuracy{model_name="ensemble"}

# F1 score
ml_model_f1_score{model_name="ensemble"}

# Precision & Recall
ml_model_precision{model_name="ensemble"}
ml_model_recall{model_name="ensemble"}
```

### Predictions

```promql
# Prediction rate (per second)
rate(ml_predictions_total[1m])

# Prediction latency (95th percentile)
histogram_quantile(0.95, rate(ml_prediction_latency_seconds_bucket[5m]))

# Prediction confidence distribution
ml_prediction_confidence_bucket
```

### Training

```promql
# Training runs
rate(ml_training_runs_total{status="success"}[1h])

# Training duration
histogram_quantile(0.95, rate(ml_training_duration_seconds_bucket[1h]))

# Last training timestamp
ml_last_training_timestamp
```

### Drift Detection

```promql
# Drift events
rate(ml_drift_detected_total{severity="drift"}[5m])

# Drift score by detector
ml_drift_score{detector_type="ddm"}
```

### Online Learning

```promql
# Online updates
ml_online_updates_total{model_type="sgd"}

# Buffer size
ml_online_buffer_size{model_type="sgd"}
```

### API Performance

```promql
# Request rate
rate(api_requests_total{endpoint="/predict"}[1m])

# Latency (95th percentile)
histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))

# Error rate
rate(api_errors_total[1m])
```

## Alerts

Pre-configured alerts in `monitoring/prometheus/alert_rules.yml`:

### Critical

- **ConceptDriftDetected**: Drift detector triggered
- **HighErrorRate**: API error rate > 5%
- **ComponentUnhealthy**: System component unhealthy

### Warning

- **LowModelAccuracy**: Accuracy < 0.65
- **LowF1Score**: F1 < 0.70
- **HighDriftWarningRate**: Frequent drift warnings
- **HighAPILatency**: P95 latency > 1s
- **NoRecentTraining**: No training in 24+ hours
- **LowCacheHitRatio**: Cache hit ratio < 0.5

## Grafana Dashboard

The dashboard includes 15 panels across 6 rows:

1. **Model Performance**: Accuracy, F1 Score, Predictions/min
2. **Prediction Distribution**: Confidence heatmap, Latency percentiles
3. **Drift Detection**: Drift events timeline, Drift scores
4. **Training & Updates**: Training runs, Training duration, Online updates
5. **API Performance**: Request rate, Latency percentiles
6. **System Health**: Component health, Cache hit ratio, Uptime

### Customization

Edit `monitoring/grafana/dashboards/ml_monitoring.json` or use Grafana UI to customize.

## Configuration

### Prometheus Scrape Config

`monitoring/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ml-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/monitoring/metrics'
    scrape_interval: 10s
```

### Alertmanager Routing

`monitoring/alertmanager/config.yml`:

```yaml
receivers:
  - name: 'critical'
    webhook_configs:
      - url: 'http://localhost:5001/alerts/critical'
```

Replace webhook URLs with your notification service (Slack, PagerDuty, email, etc.).

## Integration with Code

### Track Predictions

```python
from trading_engine.utils.prometheus_metrics import track_prediction

@time_prediction(model_name="ensemble")
def predict(features):
    prediction = model.predict(features)
    proba = model.predict_proba(features).max()

    track_prediction(
        model_name="ensemble",
        predicted_class=int(prediction),
        confidence=float(proba)
    )

    return prediction
```

### Track Training

```python
from trading_engine.utils.prometheus_metrics import track_training
import time

start = time.time()
model.fit(X_train, y_train)
duration = time.time() - start

track_training(
    model_type="ensemble",
    duration=duration,
    n_samples=len(X_train),
    status="success"
)
```

### Track Drift

```python
from trading_engine.utils.prometheus_metrics import track_drift

if drift_monitor.update(prediction, actual):
    track_drift(detector_type="ddm", severity="drift")
```

## Production Deployment

### Kubernetes

Health check endpoints support Kubernetes probes:

```yaml
livenessProbe:
  httpGet:
    path: /monitoring/health/liveness
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /monitoring/health/readiness
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

### Persistent Storage

Update `docker-compose.monitoring.yml` volumes for production:

```yaml
volumes:
  prometheus_data:
    driver: local
    driver_opts:
      type: nfs
      o: addr=your-nfs-server,rw
      device: ":/path/to/prometheus"
```

### Alert Integrations

#### Slack

```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#ml-alerts'
        title: 'ML System Alert'
```

#### PagerDuty

```yaml
receivers:
  - name: 'critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_SERVICE_KEY'
```

## Troubleshooting

### Metrics not showing

1. Check FastAPI app is running: `curl http://localhost:8000/monitoring/health`
2. Check Prometheus can scrape: <http://localhost:9090/targets>
3. Verify metrics endpoint: `curl http://localhost:8000/monitoring/metrics`

### No data in Grafana

1. Check Prometheus datasource: Grafana → Configuration → Data Sources
2. Verify Prometheus URL: `http://prometheus:9090`
3. Test query in Prometheus UI first

### Alerts not firing

1. Check alert rules: <http://localhost:9090/alerts>
2. Verify Alertmanager: <http://localhost:9093>
3. Check webhook endpoint is reachable

## Development

### Add New Metric

1. Define in `prometheus_metrics.py`:

   ```python
   my_metric = Counter('my_metric_total', 'Description', ['label1', 'label2'])
   ```

2. Track in code:

   ```python
   my_metric.labels(label1="value1", label2="value2").inc()
   ```

3. Query in Prometheus:

   ```promql
   rate(my_metric_total[5m])
   ```

4. Add to Grafana dashboard

### Custom Alert

Add to `monitoring/prometheus/alert_rules.yml`:

```yaml
- alert: MyCustomAlert
  expr: my_metric_total > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "My custom alert triggered"
```

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alert Rule Best Practices](https://prometheus.io/docs/practices/alerting/)

## Monitoring Stack Versions

- Prometheus: latest
- Grafana: latest
- Alertmanager: latest
- Node Exporter: latest
- prometheus-client: 0.21.0 (Python library)

## License

MIT License - Same as main project
