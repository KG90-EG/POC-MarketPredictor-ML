"""
Prometheus Metrics for Market Predictor ML API

This module provides custom Prometheus metrics for monitoring API performance,
model status, cache hit rates, and business metrics.
"""

from prometheus_client import Counter, Gauge, Histogram

# Request metrics
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

# Model metrics
model_predictions_total = Counter(
    "model_predictions_total", "Total number of model predictions", ["model", "outcome"]
)

model_prediction_confidence = Histogram(
    "model_prediction_confidence", "Model prediction confidence scores", ["model"]
)

# System metrics
model_loaded = Gauge("model_loaded", "Whether ML model is loaded (1=loaded, 0=not loaded)")

openai_configured = Gauge("openai_configured", "Whether OpenAI is configured (1=yes, 0=no)")

# Cache metrics
cache_hits_total = Counter("cache_hits_total", "Total number of cache hits", ["cache_type"])

cache_misses_total = Counter("cache_misses_total", "Total number of cache misses", ["cache_type"])

# Business metrics
simulations_created_total = Counter(
    "simulations_created_total", "Total number of simulations created"
)

simulation_trades_total = Counter(
    "simulation_trades_total",
    "Total number of simulation trades",
    ["action"],  # BUY or SELL
)

simulation_portfolio_value = Gauge(
    "simulation_portfolio_value",
    "Current simulation portfolio value",
    ["simulation_id"],
)


def initialize_metrics(model_is_loaded: bool, openai_is_configured: bool):
    """Initialize gauge metrics on startup."""
    model_loaded.set(1 if model_is_loaded else 0)
    openai_configured.set(1 if openai_is_configured else 0)


def track_model_prediction(model_name: str, confidence: float, duration: float):
    """Track model prediction metrics."""
    outcome = "high_confidence" if confidence > 0.7 else "low_confidence"
    model_predictions_total.labels(model=model_name, outcome=outcome).inc()
    model_prediction_confidence.labels(model=model_name).observe(confidence)


def track_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """Track HTTP request metrics."""
    http_requests_total.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_ranking_generation(country: str, stock_count: int, duration: float):
    """Track ranking generation metrics (stub for backward compatibility)."""
    # Currently just logs, can be extended with specific metrics later
    pass
