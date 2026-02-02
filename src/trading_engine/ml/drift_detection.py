"""
Concept Drift Detection for Market Regime Changes.

Implements statistical drift detection methods to identify when model
performance degrades due to changing market conditions.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Base class for drift detection algorithms.

    Monitors prediction accuracy/error over time and triggers alerts
    when significant drift is detected.
    """

    def __init__(self, name: str = "DriftDetector"):
        """Initialize drift detector."""
        self.name = name
        self.drift_detected = False
        self.warning_detected = False
        self.n_samples = 0
        self.detection_history: List[Dict[str, Any]] = []

    def update(self, prediction: int, actual: int) -> Dict[str, bool]:
        """
        Update detector with new prediction result.

        Args:
            prediction: Model prediction (0 or 1)
            actual: Actual label (0 or 1)

        Returns:
            Dict with drift and warning status
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Reset detector state."""
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            "name": self.name,
            "drift_detected": self.drift_detected,
            "warning_detected": self.warning_detected,
            "n_samples": self.n_samples,
            "detections": len(self.detection_history),
        }


class DDM(DriftDetector):
    """
    Drift Detection Method (DDM).

    Monitors error rate and standard deviation. Drift is detected when
    error rate increases significantly beyond normal variation.

    Reference: Gama et al. (2004) - "Learning with Drift Detection"
    """

    def __init__(
        self,
        warning_level: float = 2.0,
        drift_level: float = 3.0,
        min_samples: int = 30,
    ):
        """
        Initialize DDM detector.

        Args:
            warning_level: Std deviations for warning threshold
            drift_level: Std deviations for drift threshold
            min_samples: Minimum samples before detection
        """
        super().__init__(name="DDM")
        self.warning_level = warning_level
        self.drift_level = drift_level
        self.min_samples = min_samples

        self.error_rate = 0.0
        self.std_dev = 0.0
        self.min_error_rate = float("inf")
        self.min_std_dev = float("inf")

        self.n_errors = 0
        self.n_samples = 0

    def update(self, prediction: int, actual: int) -> Dict[str, bool]:
        """Update DDM with new prediction."""
        error = 1 if prediction != actual else 0
        self.n_errors += error
        self.n_samples += 1

        # Calculate error rate and std dev
        self.error_rate = self.n_errors / self.n_samples
        self.std_dev = np.sqrt(self.error_rate * (1 - self.error_rate) / self.n_samples)

        # Update minimums
        if self.error_rate + self.std_dev < self.min_error_rate + self.min_std_dev:
            self.min_error_rate = self.error_rate
            self.min_std_dev = self.std_dev

        # Reset flags
        self.drift_detected = False
        self.warning_detected = False

        # Check for drift/warning (only after min_samples)
        if self.n_samples >= self.min_samples:
            threshold_warning = self.min_error_rate + self.warning_level * self.min_std_dev
            threshold_drift = self.min_error_rate + self.drift_level * self.min_std_dev

            if self.error_rate + self.std_dev >= threshold_drift:
                self.drift_detected = True
                self.detection_history.append(
                    {
                        "type": "drift",
                        "n_samples": self.n_samples,
                        "error_rate": self.error_rate,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                logger.warning(
                    f"DDM: Drift detected at sample {self.n_samples} "
                    f"(error_rate={self.error_rate:.3f})"
                )
            elif self.error_rate + self.std_dev >= threshold_warning:
                self.warning_detected = True
                logger.info(f"DDM: Warning at sample {self.n_samples}")

        return {"drift": self.drift_detected, "warning": self.warning_detected}

    def reset(self) -> None:
        """Reset DDM state."""
        logger.info(f"DDM reset after {self.n_samples} samples")
        self.error_rate = 0.0
        self.std_dev = 0.0
        self.min_error_rate = float("inf")
        self.min_std_dev = float("inf")
        self.n_errors = 0
        self.n_samples = 0
        self.drift_detected = False
        self.warning_detected = False


class PageHinkley(DriftDetector):
    """
    Page-Hinkley Test for drift detection.

    Monitors cumulative sum of differences from mean. Detects drift
    when cumulative sum exceeds threshold, indicating sustained change
    in data distribution.

    Reference: Page (1954) - "Continuous Inspection Schemes"
    """

    def __init__(
        self,
        threshold: float = 50.0,
        delta: float = 0.005,
        min_samples: int = 30,
    ):
        """
        Initialize Page-Hinkley detector.

        Args:
            threshold: Detection threshold (higher = less sensitive)
            delta: Magnitude of change to detect
            min_samples: Minimum samples before detection
        """
        super().__init__(name="PageHinkley")
        self.threshold = threshold
        self.delta = delta
        self.min_samples = min_samples

        self.cumsum = 0.0
        self.min_cumsum = 0.0
        self.n_samples = 0

    def update(self, prediction: int, actual: int) -> Dict[str, bool]:
        """Update Page-Hinkley test."""
        error = 1 if prediction != actual else 0
        self.n_samples += 1

        # Update cumulative sum
        self.cumsum += error - self.delta

        # Track minimum
        if self.cumsum < self.min_cumsum:
            self.min_cumsum = self.cumsum

        # Reset flags
        self.drift_detected = False
        self.warning_detected = False

        # Check for drift
        if self.n_samples >= self.min_samples:
            ph_value = self.cumsum - self.min_cumsum

            if ph_value > self.threshold:
                self.drift_detected = True
                self.detection_history.append(
                    {
                        "type": "drift",
                        "n_samples": self.n_samples,
                        "ph_value": ph_value,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                logger.warning(
                    f"PageHinkley: Drift detected at sample {self.n_samples} "
                    f"(PH={ph_value:.2f})"
                )
            elif ph_value > self.threshold * 0.7:
                self.warning_detected = True

        return {"drift": self.drift_detected, "warning": self.warning_detected}

    def reset(self) -> None:
        """Reset Page-Hinkley state."""
        logger.info(f"PageHinkley reset after {self.n_samples} samples")
        self.cumsum = 0.0
        self.min_cumsum = 0.0
        self.n_samples = 0
        self.drift_detected = False
        self.warning_detected = False


class KSWIN:
    """
    Kolmogorov-Smirnov Windowing (KSWIN) drift detector.

    Uses statistical test to compare recent window with reference window.
    Detects distribution changes using KS test.
    """

    def __init__(
        self,
        window_size: int = 100,
        stat_size: int = 30,
        alpha: float = 0.05,
    ):
        """
        Initialize KSWIN detector.

        Args:
            window_size: Size of sliding window
            stat_size: Size of statistical test window
            alpha: Significance level for KS test
        """
        self.window_size = window_size
        self.stat_size = stat_size
        self.alpha = alpha

        self.window: List[float] = []
        self.drift_detected = False
        self.n_samples = 0

    def update(self, value: float) -> bool:
        """
        Update KSWIN with new value.

        Args:
            value: New observation (e.g., prediction probability)

        Returns:
            True if drift detected
        """
        self.window.append(value)
        self.n_samples += 1

        # Maintain window size
        if len(self.window) > self.window_size:
            self.window.pop(0)

        self.drift_detected = False

        # Perform KS test when enough samples
        if len(self.window) >= self.window_size:
            # Split window
            ref_window = self.window[: self.stat_size]
            test_window = self.window[-self.stat_size :]

            # Two-sample KS test
            statistic, p_value = stats.ks_2samp(ref_window, test_window)

            if p_value < self.alpha:
                self.drift_detected = True
                logger.warning(
                    f"KSWIN: Drift detected at sample {self.n_samples} "
                    f"(p={p_value:.4f}, stat={statistic:.4f})"
                )

        return self.drift_detected

    def reset(self) -> None:
        """Reset KSWIN state."""
        self.window = []
        self.drift_detected = False


class DriftMonitor:
    """
    Monitor multiple drift detectors and aggregate results.

    Combines DDM, Page-Hinkley, and KSWIN for robust drift detection.
    """

    def __init__(self, enable_kswin: bool = True):
        """
        Initialize drift monitor with multiple detectors.

        Args:
            enable_kswin: Whether to use KSWIN (requires probability values)
        """
        self.ddm = DDM()
        self.page_hinkley = PageHinkley()
        self.enable_kswin = enable_kswin

        if enable_kswin:
            self.kswin = KSWIN()

        self.n_updates = 0
        self.drift_count = 0

        logger.info(
            f"DriftMonitor initialized (DDM + PageHinkley" f"{' + KSWIN' if enable_kswin else ''})"
        )

    def update(
        self,
        prediction: int,
        actual: int,
        proba: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Update all detectors with new prediction.

        Args:
            prediction: Model prediction (0 or 1)
            actual: Actual label (0 or 1)
            proba: Prediction probability (for KSWIN)

        Returns:
            Dict with aggregated drift detection results
        """
        self.n_updates += 1

        # Update DDM and Page-Hinkley
        ddm_result = self.ddm.update(prediction, actual)
        ph_result = self.page_hinkley.update(prediction, actual)

        # Update KSWIN if enabled and proba provided
        kswin_drift = False
        if self.enable_kswin and proba is not None:
            kswin_drift = self.kswin.update(proba)

        # Aggregate results
        drift_detected = ddm_result["drift"] or ph_result["drift"] or kswin_drift
        warning_detected = ddm_result["warning"] or ph_result["warning"]

        if drift_detected:
            self.drift_count += 1

        return {
            "drift_detected": drift_detected,
            "warning_detected": warning_detected,
            "ddm": ddm_result,
            "page_hinkley": ph_result,
            "kswin_drift": kswin_drift if self.enable_kswin else None,
            "n_updates": self.n_updates,
            "drift_count": self.drift_count,
        }

    def reset_all(self) -> None:
        """Reset all detectors."""
        self.ddm.reset()
        self.page_hinkley.reset()
        if self.enable_kswin:
            self.kswin.reset()
        logger.info("All drift detectors reset")

    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics from all detectors."""
        stats = {
            "n_updates": self.n_updates,
            "drift_count": self.drift_count,
            "ddm": self.ddm.get_stats(),
            "page_hinkley": self.page_hinkley.get_stats(),
        }

        if self.enable_kswin:
            stats["kswin"] = {
                "n_samples": self.kswin.n_samples,
                "window_size": len(self.kswin.window),
            }

        return stats
