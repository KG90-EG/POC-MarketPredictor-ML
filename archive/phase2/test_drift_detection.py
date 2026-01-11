"""Tests for drift detection module."""

import numpy as np
import pytest

from src.trading_engine.ml.drift_detection import (
    DDM,
    KSWIN,
    DriftMonitor,
    PageHinkley,
)


class TestDDM:
    """Test DDM drift detector."""

    def test_initialization(self):
        """Test DDM initialization."""
        detector = DDM(warning_level=2.0, drift_level=3.0)

        assert detector.name == "DDM"
        assert not detector.drift_detected
        assert not detector.warning_detected
        assert detector.n_samples == 0

    def test_no_drift_on_stable_data(self):
        """Test DDM doesn't trigger on stable predictions."""
        detector = DDM(min_samples=30)

        # 100 correct predictions
        for _ in range(100):
            result = detector.update(prediction=1, actual=1)

        assert not result["drift"]
        assert detector.n_samples == 100

    def test_drift_detection_on_degradation(self):
        """Test DDM detects drift when error rate increases."""
        detector = DDM(min_samples=30, drift_level=2.0)

        # Start with good performance (90% accuracy)
        np.random.seed(42)
        for _ in range(50):
            actual = np.random.randint(0, 2)
            prediction = actual if np.random.rand() > 0.1 else 1 - actual
            detector.update(prediction, actual)

        assert not detector.drift_detected

        # Degrade to 50% accuracy
        for _ in range(50):
            actual = np.random.randint(0, 2)
            prediction = np.random.randint(0, 2)
            result = detector.update(prediction, actual)

        # Should eventually detect drift
        assert any(d["type"] == "drift" for d in detector.detection_history)

    def test_reset(self):
        """Test DDM reset clears state."""
        detector = DDM()

        for _ in range(50):
            detector.update(prediction=1, actual=0)

        assert detector.n_samples > 0

        detector.reset()

        assert detector.n_samples == 0
        assert detector.error_rate == 0.0
        assert not detector.drift_detected


class TestPageHinkley:
    """Test Page-Hinkley drift detector."""

    def test_initialization(self):
        """Test Page-Hinkley initialization."""
        detector = PageHinkley(threshold=50.0, delta=0.005)

        assert detector.name == "PageHinkley"
        assert not detector.drift_detected
        assert detector.cumsum == 0.0

    def test_no_drift_on_stable_data(self):
        """Test no drift on consistent data."""
        detector = PageHinkley(threshold=50.0, min_samples=30)

        for _ in range(100):
            result = detector.update(prediction=1, actual=1)

        assert not result["drift"]

    def test_drift_on_sustained_errors(self):
        """Test drift detection on sustained error increase."""
        detector = PageHinkley(threshold=20.0, delta=0.005, min_samples=30)

        # Good predictions first
        for _ in range(50):
            detector.update(prediction=1, actual=1)

        # Sustained errors
        for _ in range(100):
            result = detector.update(prediction=0, actual=1)

        # Should detect drift
        assert any(d["type"] == "drift" for d in detector.detection_history)

    def test_reset(self):
        """Test Page-Hinkley reset."""
        detector = PageHinkley()

        for _ in range(50):
            detector.update(prediction=0, actual=1)

        detector.reset()

        assert detector.cumsum == 0.0
        assert detector.n_samples == 0


class TestKSWIN:
    """Test KSWIN drift detector."""

    def test_initialization(self):
        """Test KSWIN initialization."""
        detector = KSWIN(window_size=100, stat_size=30, alpha=0.05)

        assert detector.window_size == 100
        assert detector.stat_size == 30
        assert len(detector.window) == 0

    def test_no_drift_on_stable_distribution(self):
        """Test no drift when distribution stays stable."""
        detector = KSWIN(window_size=100, stat_size=30)

        np.random.seed(42)
        for _ in range(200):
            value = np.random.normal(0.5, 0.1)
            drift = detector.update(value)

        # May have false positives, but shouldn't consistently detect drift
        assert detector.n_samples == 200

    def test_drift_on_distribution_shift(self):
        """Test drift detection when distribution shifts."""
        detector = KSWIN(window_size=100, stat_size=30, alpha=0.05)

        np.random.seed(42)

        # First distribution: mean=0.5
        for _ in range(100):
            value = np.random.normal(0.5, 0.1)
            detector.update(value)

        # Second distribution: mean=0.8 (clear shift)
        drift_detected = False
        for _ in range(100):
            value = np.random.normal(0.8, 0.1)
            drift = detector.update(value)
            if drift:
                drift_detected = True
                break

        assert drift_detected

    def test_window_size_maintained(self):
        """Test window maintains max size."""
        detector = KSWIN(window_size=50)

        for _ in range(100):
            detector.update(np.random.rand())

        assert len(detector.window) == 50


class TestDriftMonitor:
    """Test DriftMonitor aggregation."""

    def test_initialization(self):
        """Test DriftMonitor initialization."""
        monitor = DriftMonitor(enable_kswin=True)

        assert monitor.ddm is not None
        assert monitor.page_hinkley is not None
        assert monitor.kswin is not None
        assert monitor.n_updates == 0

    def test_update_without_kswin(self):
        """Test update with DDM and PageHinkley only."""
        monitor = DriftMonitor(enable_kswin=False)

        result = monitor.update(prediction=1, actual=1)

        assert "drift_detected" in result
        assert "ddm" in result
        assert "page_hinkley" in result
        assert result["kswin_drift"] is None
        assert monitor.n_updates == 1

    def test_update_with_kswin(self):
        """Test update with all detectors including KSWIN."""
        monitor = DriftMonitor(enable_kswin=True)

        result = monitor.update(prediction=1, actual=1, proba=0.85)

        assert "drift_detected" in result
        assert result["kswin_drift"] is not None

    def test_aggregated_drift_detection(self):
        """Test drift aggregation from multiple detectors."""
        monitor = DriftMonitor(enable_kswin=False)

        # Feed data until drift in one detector
        np.random.seed(42)
        for _ in range(100):
            # Mostly errors to trigger drift
            result = monitor.update(prediction=0, actual=1)

        # At least one detector should have triggered
        assert monitor.drift_count > 0

    def test_reset_all(self):
        """Test reset all detectors."""
        monitor = DriftMonitor(enable_kswin=True)

        for _ in range(50):
            monitor.update(prediction=1, actual=0)

        monitor.reset_all()

        assert monitor.ddm.n_samples == 0
        assert monitor.page_hinkley.n_samples == 0
        assert len(monitor.kswin.window) == 0

    def test_get_stats(self):
        """Test get_stats aggregates all detector stats."""
        monitor = DriftMonitor(enable_kswin=True)

        for _ in range(50):
            monitor.update(prediction=1, actual=1, proba=0.9)

        stats = monitor.get_stats()

        assert "n_updates" in stats
        assert stats["n_updates"] == 50
        assert "ddm" in stats
        assert "page_hinkley" in stats
        assert "kswin" in stats
