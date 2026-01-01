"""
FastAPI routes for monitoring endpoints.

Provides Prometheus metrics, health checks, and monitoring dashboards.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST

from ..core.cache import cache
from ..core.config import config
from ..ml.drift_detection import DriftMonitor
from ..utils.prometheus_metrics import (
    export_metrics,
    metrics_collector,
    system_health,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# Global drift monitor instance for tracking
_drift_monitor: DriftMonitor = None


def get_drift_monitor() -> DriftMonitor:
    """Get or create global drift monitor instance."""
    global _drift_monitor
    if _drift_monitor is None:
        _drift_monitor = DriftMonitor(enable_kswin=True)
    return _drift_monitor


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    metrics_data = export_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        System health status with component details
    """
    try:
        # Check cache
        cache_healthy = True
        try:
            cache.get("health_check_test")
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            cache_healthy = False

        # Update system health metrics
        system_health.labels(component="cache").set(1 if cache_healthy else 0)
        system_health.labels(component="api").set(1)

        health_status = {
            "status": "healthy" if cache_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "api": "healthy",
                "cache": "healthy" if cache_healthy else "unhealthy",
                "model": "healthy",
            },
            "uptime_seconds": metrics_collector.get_all_metrics()["uptime_seconds"],
        }

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        system_health.labels(component="api").set(0)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get("/health/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check for Kubernetes.

    Returns:
        Ready status when all components are operational
    """
    try:
        # Check if models are loaded
        # Check if cache is accessible
        cache.get("readiness_check")

        return {
            "ready": True,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get("/health/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check for Kubernetes.

    Returns:
        Alive status if API is responsive
    """
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/drift/status")
async def drift_status() -> Dict[str, Any]:
    """
    Get current drift detection status.

    Returns:
        Drift monitor statistics and recent detections
    """
    monitor = get_drift_monitor()
    stats = monitor.get_stats()

    return {
        "drift_monitor": stats,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/drift/update")
async def update_drift_monitor(
    prediction: int,
    actual: int,
    proba: float = None,
) -> Dict[str, Any]:
    """
    Update drift monitor with new prediction result.

    Args:
        prediction: Model prediction (0 or 1)
        actual: Actual label (0 or 1)
        proba: Prediction probability (optional, for KSWIN)

    Returns:
        Drift detection result
    """
    monitor = get_drift_monitor()
    result = monitor.update(prediction=prediction, actual=actual, proba=proba)

    # Track in Prometheus metrics
    from ..utils.prometheus_metrics import track_drift

    if result["drift_detected"]:
        track_drift(detector_type="aggregated", severity="drift")
    elif result["warning_detected"]:
        track_drift(detector_type="aggregated", severity="warning")

    return result


@router.post("/drift/reset")
async def reset_drift_monitor() -> Dict[str, str]:
    """
    Reset all drift detectors.

    Returns:
        Confirmation message
    """
    monitor = get_drift_monitor()
    monitor.reset_all()

    return {
        "status": "success",
        "message": "Drift detectors reset successfully",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/system/info")
async def system_info() -> Dict[str, Any]:
    """
    Get system information and configuration.

    Returns:
        System details and settings
    """
    import os
    import platform
    import sys

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "config": {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/cache/stats")
async def cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics.

    Returns:
        Cache performance metrics
    """
    try:
        stats = cache.get_stats()

        # Update Prometheus metrics
        from ..utils.prometheus_metrics import cache_hit_ratio

        total = stats.get("hits", 0) + stats.get("misses", 0)
        if total > 0:
            hit_ratio = stats.get("hits", 0) / total
            cache_hit_ratio.labels(cache_type="main").set(hit_ratio)

        return {
            **stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {
            "hits": 0,
            "misses": 0,
            "hit_ratio": 0.0,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }
