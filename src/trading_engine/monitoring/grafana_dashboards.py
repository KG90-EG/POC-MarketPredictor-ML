"""Grafana dashboard configuration for ML monitoring."""

DASHBOARD_CONFIG = {
    "dashboard": {
        "title": "ML Trading Predictor Monitoring",
        "tags": ["ml", "trading", "production"],
        "timezone": "browser",
        "refresh": "30s",
        "time": {"from": "now-6h", "to": "now"},
        "panels": [
            # Row 1: Model Performance
            {
                "title": "Model Accuracy",
                "type": "graph",
                "targets": [
                    {
                        "expr": "ml_model_accuracy",
                        "legendFormat": "{{model_name}} v{{model_version}}",
                    }
                ],
                "gridPos": {"x": 0, "y": 0, "w": 8, "h": 8},
                "yaxes": [
                    {"format": "percentunit", "min": 0, "max": 1},
                    {"format": "short"},
                ],
            },
            {
                "title": "Model F1 Score",
                "type": "graph",
                "targets": [
                    {
                        "expr": "ml_model_f1_score",
                        "legendFormat": "{{model_name}} v{{model_version}}",
                    }
                ],
                "gridPos": {"x": 8, "y": 0, "w": 8, "h": 8},
            },
            {
                "title": "Predictions per Minute",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(ml_predictions_total[1m])",
                        "legendFormat": "{{model_name}} - {{predicted_class}}",
                    }
                ],
                "gridPos": {"x": 16, "y": 0, "w": 8, "h": 8},
            },
            # Row 2: Prediction Distribution
            {
                "title": "Prediction Confidence Distribution",
                "type": "heatmap",
                "targets": [
                    {
                        "expr": "rate(ml_prediction_confidence_bucket[5m])",
                        "format": "heatmap",
                        "legendFormat": "{{le}}",
                    }
                ],
                "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8},
            },
            {
                "title": "Prediction Latency (p95)",
                "type": "graph",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(ml_prediction_latency_seconds_bucket[5m]))",
                        "legendFormat": "p95 {{model_name}}",
                    },
                    {
                        "expr": "histogram_quantile(0.99, rate(ml_prediction_latency_seconds_bucket[5m]))",
                        "legendFormat": "p99 {{model_name}}",
                    },
                ],
                "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
                "yaxes": [
                    {"format": "s", "label": "Latency"},
                    {"format": "short"},
                ],
            },
            # Row 3: Drift Detection
            {
                "title": "Drift Detections",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(ml_drift_detected_total[5m])",
                        "legendFormat": "{{detector_type}} - {{severity}}",
                    }
                ],
                "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8},
                "alert": {
                    "name": "High Drift Rate",
                    "conditions": [
                        {
                            "evaluator": {"params": [5], "type": "gt"},
                            "operator": {"type": "and"},
                            "query": {"params": ["A", "5m", "now"]},
                            "reducer": {"params": [], "type": "avg"},
                            "type": "query",
                        }
                    ],
                },
            },
            {
                "title": "Drift Score by Detector",
                "type": "graph",
                "targets": [
                    {
                        "expr": "ml_drift_score",
                        "legendFormat": "{{detector_type}}",
                    }
                ],
                "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
            },
            # Row 4: Training & Updates
            {
                "title": "Training Runs",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(ml_training_runs_total[1h])",
                        "legendFormat": "{{model_type}} - {{status}}",
                    }
                ],
                "gridPos": {"x": 0, "y": 24, "w": 8, "h": 8},
            },
            {
                "title": "Training Duration",
                "type": "graph",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(ml_training_duration_seconds_bucket[1h]))",
                        "legendFormat": "p95 {{model_type}}",
                    }
                ],
                "gridPos": {"x": 8, "y": 24, "w": 8, "h": 8},
            },
            {
                "title": "Online Learning Updates",
                "type": "stat",
                "targets": [
                    {
                        "expr": "ml_online_updates_total",
                        "legendFormat": "{{model_type}}",
                    }
                ],
                "gridPos": {"x": 16, "y": 24, "w": 8, "h": 8},
            },
            # Row 5: API Performance
            {
                "title": "API Request Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(api_requests_total[1m])",
                        "legendFormat": "{{endpoint}} - {{status}}",
                    }
                ],
                "gridPos": {"x": 0, "y": 32, "w": 12, "h": 8},
            },
            {
                "title": "API Latency (p95)",
                "type": "graph",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
                        "legendFormat": "{{endpoint}}",
                    }
                ],
                "gridPos": {"x": 12, "y": 32, "w": 12, "h": 8},
            },
            # Row 6: System Health
            {
                "title": "System Health Status",
                "type": "stat",
                "targets": [
                    {
                        "expr": "system_health_status",
                        "legendFormat": "{{component}}",
                    }
                ],
                "gridPos": {"x": 0, "y": 40, "w": 6, "h": 4},
                "thresholds": "0,0.5,1",
                "colors": ["red", "yellow", "green"],
            },
            {
                "title": "Cache Hit Ratio",
                "type": "gauge",
                "targets": [{"expr": "cache_hit_ratio", "legendFormat": "{{cache_type}}"}],
                "gridPos": {"x": 6, "y": 40, "w": 6, "h": 4},
            },
            {
                "title": "Active Connections",
                "type": "stat",
                "targets": [
                    {
                        "expr": "active_connections",
                        "legendFormat": "{{connection_type}}",
                    }
                ],
                "gridPos": {"x": 12, "y": 40, "w": 6, "h": 4},
            },
            {
                "title": "Uptime",
                "type": "stat",
                "targets": [{"expr": "time() - process_start_time_seconds"}],
                "gridPos": {"x": 18, "y": 40, "w": 6, "h": 4},
                "format": "dtdurations",
            },
        ],
    }
}


def generate_dashboard_json() -> dict:
    """Generate Grafana dashboard JSON configuration."""
    return DASHBOARD_CONFIG
