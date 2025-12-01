"""
Prometheus metrics collection for Trading Fun API.

This module provides comprehensive metrics for monitoring API performance,
model predictions, cache efficiency, and system health.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# ============================================================================
# API Metrics
# ============================================================================

# Request counters
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# ============================================================================
# Model Metrics
# ============================================================================

model_predictions_total = Counter(
    "model_predictions_total",
    "Total number of model predictions",
    ["model_type"],
)

model_prediction_duration_seconds = Histogram(
    "model_prediction_duration_seconds",
    "Model prediction latency in seconds",
    ["model_type"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)

model_prediction_probability = Histogram(
    "model_prediction_probability",
    "Distribution of model prediction probabilities",
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
)

# ============================================================================
# Cache Metrics
# ============================================================================

cache_hits_total = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["cache_type"],
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total number of cache misses",
    ["cache_type"],
)

cache_size_bytes = Gauge(
    "cache_size_bytes",
    "Current cache size in bytes",
    ["cache_type"],
)

# ============================================================================
# Data Source Metrics
# ============================================================================

data_fetch_duration_seconds = Histogram(
    "data_fetch_duration_seconds",
    "Data fetch latency in seconds",
    ["source"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
)

data_fetch_errors_total = Counter(
    "data_fetch_errors_total",
    "Total number of data fetch errors",
    ["source", "error_type"],
)

# ============================================================================
# Stock Ranking Metrics
# ============================================================================

ranking_generation_duration_seconds = Histogram(
    "ranking_generation_duration_seconds",
    "Ranking generation latency in seconds",
    ["country"],
    buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0),
)

ranking_tickers_processed = Histogram(
    "ranking_tickers_processed",
    "Number of tickers processed in ranking",
    buckets=(10, 25, 50, 100, 200, 500),
)

# ============================================================================
# Crypto Metrics
# ============================================================================

crypto_fetch_duration_seconds = Histogram(
    "crypto_fetch_duration_seconds",
    "Cryptocurrency data fetch latency",
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0),
)

crypto_items_fetched = Histogram(
    "crypto_items_fetched",
    "Number of crypto items fetched per request",
    buckets=(20, 50, 100, 200, 250),
)

# ============================================================================
# AI Analysis Metrics
# ============================================================================

ai_analysis_requests_total = Counter(
    "ai_analysis_requests_total",
    "Total AI analysis requests",
    ["cached"],
)

ai_analysis_duration_seconds = Histogram(
    "ai_analysis_duration_seconds",
    "AI analysis latency in seconds",
    buckets=(1.0, 5.0, 10.0, 20.0, 30.0, 60.0),
)

ai_analysis_tokens_used = Histogram(
    "ai_analysis_tokens_used",
    "Tokens used in AI analysis",
    buckets=(100, 500, 1000, 2000, 5000, 10000),
)

# ============================================================================
# System Health Metrics
# ============================================================================

model_loaded = Gauge(
    "model_loaded",
    "Whether the ML model is loaded (1 = loaded, 0 = not loaded)",
)

openai_configured = Gauge(
    "openai_configured",
    "Whether OpenAI is configured (1 = yes, 0 = no)",
)

system_info = Info(
    "system_info",
    "System information",
)

# ============================================================================
# Rate Limiting Metrics
# ============================================================================

rate_limit_exceeded_total = Counter(
    "rate_limit_exceeded_total",
    "Total number of rate limit violations",
    ["endpoint"],
)

# ============================================================================
# Helper Functions
# ============================================================================


def track_request_metrics(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics."""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
        duration
    )


def track_model_prediction(model_type: str, probability: float, duration: float):
    """Track model prediction metrics."""
    model_predictions_total.labels(model_type=model_type).inc()
    model_prediction_duration_seconds.labels(model_type=model_type).observe(duration)
    model_prediction_probability.observe(probability)


def track_cache_hit(cache_type: str):
    """Track cache hit."""
    cache_hits_total.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """Track cache miss."""
    cache_misses_total.labels(cache_type=cache_type).inc()


def update_cache_size(cache_type: str, size_bytes: int):
    """Update cache size gauge."""
    cache_size_bytes.labels(cache_type=cache_type).set(size_bytes)


def track_data_fetch(source: str, duration: float, error_type: str = None):
    """Track data fetch metrics."""
    data_fetch_duration_seconds.labels(source=source).observe(duration)
    if error_type:
        data_fetch_errors_total.labels(source=source, error_type=error_type).inc()


def track_ranking_generation(country: str, num_tickers: int, duration: float):
    """Track ranking generation metrics."""
    ranking_generation_duration_seconds.labels(country=country).observe(duration)
    ranking_tickers_processed.observe(num_tickers)


def track_crypto_fetch(num_items: int, duration: float):
    """Track crypto fetch metrics."""
    crypto_fetch_duration_seconds.observe(duration)
    crypto_items_fetched.observe(num_items)


def track_ai_analysis(cached: bool, duration: float, tokens_used: int = None):
    """Track AI analysis metrics."""
    ai_analysis_requests_total.labels(cached="yes" if cached else "no").inc()
    ai_analysis_duration_seconds.observe(duration)
    if tokens_used:
        ai_analysis_tokens_used.observe(tokens_used)


def track_rate_limit_exceeded(endpoint: str):
    """Track rate limit violation."""
    rate_limit_exceeded_total.labels(endpoint=endpoint).inc()


def timer(metric_func):
    """Decorator to time a function and record to a metric."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric_func(duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                metric_func(duration)

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# ============================================================================
# Initialization
# ============================================================================


def initialize_metrics(model_is_loaded: bool, openai_is_configured: bool):
    """Initialize system metrics on startup."""
    model_loaded.set(1 if model_is_loaded else 0)
    openai_configured.set(1 if openai_is_configured else 0)
    system_info.info(
        {
            "service": "trading-fun-api",
            "version": "1.0.0",
        }
    )
