"""
Prometheus Metrics for ML Model Monitoring.

Exposes comprehensive metrics for production monitoring:
- Model performance (accuracy, F1, latency)
- Prediction statistics (volume, distribution)
- Drift detection events
- API endpoint performance
- System health metrics
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict

from prometheus_client import Counter, Gauge, Histogram, Info, generate_latest

logger = logging.getLogger(__name__)

# ============================================================================
# MODEL PERFORMANCE METRICS
# ============================================================================

# Model accuracy tracking
model_accuracy = Gauge(
    "ml_model_accuracy",
    "Current model accuracy score",
    ["model_name", "model_version"],
)

model_f1_score = Gauge(
    "ml_model_f1_score",
    "Current model F1 score",
    ["model_name", "model_version"],
)

model_precision = Gauge(
    "ml_model_precision",
    "Current model precision score",
    ["model_name", "model_version"],
)

model_recall = Gauge(
    "ml_model_recall",
    "Current model recall score",
    ["model_name", "model_version"],
)

# Model predictions
predictions_total = Counter(
    "ml_predictions_total",
    "Total number of predictions made",
    ["model_name", "predicted_class"],
)

prediction_confidence = Histogram(
    "ml_prediction_confidence",
    "Distribution of prediction confidence scores",
    ["model_name"],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
)

# Prediction latency
prediction_latency = Histogram(
    "ml_prediction_latency_seconds",
    "Time to generate predictions",
    ["model_name"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

# ============================================================================
# TRAINING & RETRAINING METRICS
# ============================================================================

training_runs_total = Counter(
    "ml_training_runs_total",
    "Total number of training runs",
    ["model_type", "status"],
)

training_duration = Histogram(
    "ml_training_duration_seconds",
    "Duration of training runs",
    ["model_type"],
    buckets=[10, 30, 60, 120, 300, 600, 1200, 1800, 3600],
)

training_samples = Histogram(
    "ml_training_samples",
    "Number of samples used in training",
    ["model_type"],
    buckets=[100, 500, 1000, 5000, 10000, 50000, 100000],
)

last_training_timestamp = Gauge(
    "ml_last_training_timestamp",
    "Timestamp of last training run",
    ["model_type"],
)

# ============================================================================
# DRIFT DETECTION METRICS
# ============================================================================

drift_detected_total = Counter(
    "ml_drift_detected_total",
    "Total drift detections",
    ["detector_type", "severity"],
)

drift_score = Gauge(
    "ml_drift_score",
    "Current drift score from detector",
    ["detector_type"],
)

concept_drift_events = Counter(
    "ml_concept_drift_events_total",
    "Concept drift events requiring model update",
    ["detector_type"],
)

# ============================================================================
# ONLINE LEARNING METRICS
# ============================================================================

online_updates_total = Counter(
    "ml_online_updates_total",
    "Number of online/incremental learning updates",
    ["model_type"],
)

online_samples_processed = Counter(
    "ml_online_samples_processed_total",
    "Total samples processed in online learning",
    ["model_type"],
)

online_buffer_size = Gauge(
    "ml_online_buffer_size",
    "Current size of online learning buffer",
    ["model_type"],
)

# ============================================================================
# DATA QUALITY METRICS
# ============================================================================

data_quality_score = Gauge(
    "ml_data_quality_score",
    "Data quality score (0-1)",
    ["data_source"],
)

missing_values_ratio = Gauge(
    "ml_missing_values_ratio",
    "Ratio of missing values in features",
    ["feature_name"],
)

feature_distribution_shift = Gauge(
    "ml_feature_distribution_shift",
    "KL divergence between current and baseline feature distribution",
    ["feature_name"],
)

# ============================================================================
# API ENDPOINT METRICS
# ============================================================================

api_requests_total = Counter(
    "api_requests_total",
    "Total API requests",
    ["endpoint", "method", "status"],
)

api_request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["endpoint", "method"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

api_errors_total = Counter(
    "api_errors_total",
    "Total API errors",
    ["endpoint", "error_type"],
)

# ============================================================================
# SYSTEM HEALTH METRICS
# ============================================================================

model_info = Info(
    "ml_model_info",
    "Information about deployed ML models",
)

system_health = Gauge(
    "system_health_status",
    "Overall system health (1=healthy, 0=unhealthy)",
    ["component"],
)

cache_hit_ratio = Gauge(
    "cache_hit_ratio",
    "Cache hit ratio (0-1)",
    ["cache_type"],
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections",
    ["connection_type"],
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def track_prediction(model_name: str, predicted_class: int, confidence: float) -> None:
    """Track a single prediction."""
    predictions_total.labels(model_name=model_name, predicted_class=predicted_class).inc()
    prediction_confidence.labels(model_name=model_name).observe(confidence)


def track_training(
    model_type: str,
    duration: float,
    n_samples: int,
    status: str = "success",
) -> None:
    """Track a training run."""
    training_runs_total.labels(model_type=model_type, status=status).inc()
    training_duration.labels(model_type=model_type).observe(duration)
    training_samples.labels(model_type=model_type).observe(n_samples)
    last_training_timestamp.labels(model_type=model_type).set(time.time())


def track_drift(detector_type: str, severity: str = "warning") -> None:
    """Track drift detection."""
    drift_detected_total.labels(detector_type=detector_type, severity=severity).inc()


def track_online_update(model_type: str, n_samples: int, buffer_size: int) -> None:
    """Track online learning update."""
    online_updates_total.labels(model_type=model_type).inc()
    online_samples_processed.labels(model_type=model_type).inc(n_samples)
    online_buffer_size.labels(model_type=model_type).set(buffer_size)


def update_model_metrics(
    model_name: str,
    model_version: str,
    accuracy: float,
    f1: float,
    precision: float,
    recall: float,
) -> None:
    """Update model performance metrics."""
    model_accuracy.labels(model_name=model_name, model_version=model_version).set(accuracy)
    model_f1_score.labels(model_name=model_name, model_version=model_version).set(f1)
    model_precision.labels(model_name=model_name, model_version=model_version).set(precision)
    model_recall.labels(model_name=model_name, model_version=model_version).set(recall)


def set_model_info(info: Dict[str, str]) -> None:
    """Set model information."""
    model_info.info(info)


def time_prediction(model_name: str) -> Callable:
    """Decorator to time prediction latency."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            prediction_latency.labels(model_name=model_name).observe(duration)
            return result

        return wrapper

    return decorator


def time_api_request(endpoint: str, method: str) -> Callable:
    """Decorator to time API requests."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
                api_requests_total.labels(endpoint=endpoint, method=method, status="success").inc()
                return result
            except Exception as e:
                duration = time.time() - start_time
                api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
                api_requests_total.labels(endpoint=endpoint, method=method, status="error").inc()
                api_errors_total.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
                api_requests_total.labels(endpoint=endpoint, method=method, status="success").inc()
                return result
            except Exception as e:
                duration = time.time() - start_time
                api_request_duration.labels(endpoint=endpoint, method=method).observe(duration)
                api_requests_total.labels(endpoint=endpoint, method=method, status="error").inc()
                api_errors_total.labels(endpoint=endpoint, error_type=type(e).__name__).inc()
                raise

        # Return async wrapper if function is async
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def export_metrics() -> bytes:
    """Export metrics in Prometheus format."""
    return generate_latest()


# ============================================================================
# METRIC COLLECTORS
# ============================================================================


class MetricsCollector:
    """Aggregates and manages all metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.start_time = time.time()
        logger.info("MetricsCollector initialized")

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics as dictionary."""
        return {
            "uptime_seconds": time.time() - self.start_time,
            "metrics_exported": True,
        }

    def reset_metrics(self) -> None:
        """Reset all metrics (use with caution)."""
        logger.warning("Resetting all Prometheus metrics")
        # Note: Prometheus metrics are cumulative by design
        # This is mainly for testing purposes


# Global collector instance
metrics_collector = MetricsCollector()
