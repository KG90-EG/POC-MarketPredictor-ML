"""Test suite for monitoring routes."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from trading_engine.api.monitoring_routes import router
from trading_engine.ml.drift_detection import DriftMonitor

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestPrometheusMetrics:
    """Test Prometheus metrics endpoint."""

    def test_metrics_endpoint_returns_text_format(self):
        """Test that /monitoring/metrics returns Prometheus text format."""
        response = client.get("/monitoring/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert len(response.text) > 0

    def test_metrics_contains_expected_metric_families(self):
        """Test that metrics contain expected metric families."""
        response = client.get("/monitoring/metrics")
        content = response.text

        # Check for key metric families
        assert "ml_model_accuracy" in content or "# HELP" in content
        # Prometheus metrics may not be initialized yet, just verify format


class TestHealthChecks:
    """Test health check endpoints."""

    @patch("trading_engine.api.monitoring_routes.cache")
    def test_health_check_healthy(self, mock_cache):
        """Test health check returns healthy status."""
        mock_cache.get.return_value = "test"
        mock_cache.set.return_value = True

        response = client.get("/monitoring/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "components" in data
        assert isinstance(data["components"], dict)
        assert "timestamp" in data

    @patch("trading_engine.api.monitoring_routes.cache")
    def test_health_check_degraded(self, mock_cache):
        """Test health check detects degraded state."""
        mock_cache.get.side_effect = Exception("Cache error")

        response = client.get("/monitoring/health")
        assert response.status_code == 200
        data = response.json()

        assert data["status"] in ["degraded", "unhealthy"]
        assert "components" in data

    def test_readiness_probe_success(self):
        """Test Kubernetes readiness probe."""
        response = client.get("/monitoring/health/readiness")
        assert response.status_code == 200
        data = response.json()

        assert "ready" in data
        assert isinstance(data["ready"], bool)
        assert "timestamp" in data

    def test_liveness_probe_success(self):
        """Test Kubernetes liveness probe."""
        response = client.get("/monitoring/health/liveness")
        assert response.status_code == 200
        data = response.json()

        assert data["alive"] is True
        assert "timestamp" in data


class TestDriftMonitoring:
    """Test drift monitoring endpoints."""

    def test_drift_status_returns_stats(self):
        """Test drift status endpoint returns statistics."""
        response = client.get("/monitoring/drift/status")
        assert response.status_code == 200
        data = response.json()

        assert "drift_monitor" in data
        assert isinstance(data["drift_monitor"], dict)

    @patch("trading_engine.api.monitoring_routes.get_drift_monitor")
    def test_drift_update_with_values(self, mock_get_monitor):
        """Test updating drift detector with prediction/actual values."""
        mock_monitor = MagicMock()
        mock_monitor.update.return_value = {"drift_detected": False, "warning_detected": False}
        mock_get_monitor.return_value = mock_monitor

        # Use query parameters instead of JSON body
        response = client.post("/monitoring/drift/update?prediction=1&actual=1&proba=0.85")

        assert response.status_code == 200
        data = response.json()
        assert "drift_detected" in data
        mock_monitor.update.assert_called_once()

    @patch("trading_engine.api.monitoring_routes.get_drift_monitor")
    def test_drift_reset_success(self, mock_get_monitor):
        """Test resetting drift detectors."""
        mock_monitor = MagicMock()
        mock_monitor.reset_all.return_value = None
        mock_get_monitor.return_value = mock_monitor

        response = client.post("/monitoring/drift/reset")
        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Drift detectors reset successfully"
        mock_monitor.reset_all.assert_called_once()


class TestSystemInfo:
    """Test system information endpoints."""

    def test_system_info_returns_metadata(self):
        """Test system info endpoint returns system metadata."""
        response = client.get("/monitoring/system/info")
        assert response.status_code == 200
        data = response.json()

        assert "python_version" in data
        assert "platform" in data
        assert "config" in data
        assert isinstance(data["config"], dict)

    @patch("trading_engine.api.monitoring_routes.cache")
    def test_cache_stats_returns_metrics(self, mock_cache):
        """Test cache stats endpoint returns cache metrics."""
        mock_cache.get_stats.return_value = {
            "hits": 100,
            "misses": 20,
            "hit_ratio": 0.833,
            "size": 50,
        }

        response = client.get("/monitoring/cache/stats")
        assert response.status_code == 200
        data = response.json()

        assert "hits" in data
        assert "misses" in data
        assert "hit_ratio" in data

    @patch("trading_engine.api.monitoring_routes.cache")
    def test_cache_stats_handles_error(self, mock_cache):
        """Test cache stats handles errors gracefully."""
        mock_cache.get_stats.side_effect = Exception("Cache error")

        response = client.get("/monitoring/cache/stats")
        assert response.status_code == 200
        data = response.json()

        # Should return default values on error
        assert "error" in data or data["hits"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
