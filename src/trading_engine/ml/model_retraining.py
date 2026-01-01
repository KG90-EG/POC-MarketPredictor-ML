"""
Automated Model Retraining System.

This module implements daily automatic model retraining to keep the ML model
fresh and prevent concept drift.

Features:
- Scheduled daily retraining (2 AM)
- Performance validation before deployment
- Model versioning and rollback
- Training metrics tracking
- Alert system for degraded performance

Usage:
    from model_retraining import start_retraining_scheduler

    # Start background scheduler
    start_retraining_scheduler()
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import joblib
from apscheduler.schedulers.background import BackgroundScheduler

from ..core.config import config
from .trading import build_dataset, train_model

logger = logging.getLogger(__name__)

# Model storage paths
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

PROD_MODEL_PATH = MODEL_DIR / "prod_model.bin"
BACKUP_MODEL_PATH = MODEL_DIR / "backup_model.bin"
METRICS_PATH = MODEL_DIR / "training_metrics.json"

# Performance thresholds
MIN_F1_SCORE = 0.65
MIN_ACCURACY = 0.70
MAX_PERFORMANCE_DROP = 0.10  # 10% drop triggers alert


class ModelRetrainingService:
    """Manages automated model retraining and deployment"""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.current_metrics = self._load_current_metrics()
        self.is_running = False

    def _load_current_metrics(self) -> Dict[str, float]:
        """Load metrics from last successful training"""
        if METRICS_PATH.exists():
            import json

            with open(METRICS_PATH, "r") as f:
                return json.load(f)
        return {"f1_score": 0.0, "accuracy": 0.0, "precision": 0.0, "recall": 0.0}

    def _save_metrics(self, metrics: Dict[str, float]):
        """Save training metrics to file"""
        import json

        with open(METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=2)

    def _backup_current_model(self):
        """Backup current production model"""
        if PROD_MODEL_PATH.exists():
            import shutil

            shutil.copy(PROD_MODEL_PATH, BACKUP_MODEL_PATH)
            logger.info("Current model backed up")

    def _validate_model(self, metrics: Dict[str, float]) -> bool:
        """Validate if new model meets quality thresholds"""

        # Check absolute thresholds
        if metrics["f1_score"] < MIN_F1_SCORE:
            logger.warning(f"F1 score {metrics['f1_score']:.3f} below threshold {MIN_F1_SCORE}")
            return False

        if metrics["accuracy"] < MIN_ACCURACY:
            logger.warning(f"Accuracy {metrics['accuracy']:.3f} below threshold {MIN_ACCURACY}")
            return False

        # Check for performance degradation
        if self.current_metrics["f1_score"] > 0:
            f1_drop = self.current_metrics["f1_score"] - metrics["f1_score"]
            if f1_drop > MAX_PERFORMANCE_DROP:
                logger.warning(f"F1 score dropped by {f1_drop:.3f} (>{MAX_PERFORMANCE_DROP})")
                return False

        return True

    def _send_alert(self, subject: str, message: str):
        """Send alert notification (email/slack)"""
        logger.error(f"ALERT: {subject}\n{message}")

        # TODO: Implement actual email/Slack notification
        # For now, just log to file
        alert_file = MODEL_DIR / "alerts.log"
        with open(alert_file, "a") as f:
            f.write(f"[{datetime.now()}] {subject}\n{message}\n\n")

    def retrain_model(self, force: bool = False) -> bool:
        """
        Retrain model with latest data

        Args:
            force: Skip validation and deploy anyway

        Returns:
            True if retraining succeeded and model was deployed
        """
        logger.info("=" * 60)
        logger.info("Starting automated model retraining")
        logger.info("=" * 60)

        start_time = datetime.now()

        try:
            # 1. Fetch latest data (last 5 years)
            logger.info("Fetching training data...")
            tickers = config.market.default_stocks[:50]  # Top 50 stocks
            data = build_dataset(tickers, period="5y")

            if data.empty:
                raise ValueError("No training data available")

            logger.info(f"Training data: {len(data)} samples, {len(tickers)} tickers")

            # 2. Train new model
            logger.info("Training model...")
            model, metrics = train_model(data, model_type="xgb")

            logger.info("Training completed:")
            logger.info(f"  F1 Score:  {metrics['f1_score']:.3f}")
            logger.info(f"  Accuracy:  {metrics['accuracy']:.3f}")
            logger.info(f"  Precision: {metrics['precision']:.3f}")
            logger.info(f"  Recall:    {metrics['recall']:.3f}")

            # 3. Validate performance
            if not force and not self._validate_model(metrics):
                self._send_alert(
                    "Model Retraining Failed",
                    f"""
                    New model failed validation checks:

                    Current Model:
                    - F1 Score: {self.current_metrics['f1_score']:.3f}
                    - Accuracy: {self.current_metrics['accuracy']:.3f}

                    New Model:
                    - F1 Score: {metrics['f1_score']:.3f}
                    - Accuracy: {metrics['accuracy']:.3f}

                    Model NOT deployed. Using previous version.
                    """,
                )
                return False

            # 4. Backup old model
            self._backup_current_model()

            # 5. Deploy new model
            joblib.dump(model, PROD_MODEL_PATH)
            self._save_metrics(metrics)
            self.current_metrics = metrics

            # 6. Calculate training time
            duration = (datetime.now() - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info(f"Model successfully deployed! (took {duration:.1f}s)")
            logger.info("=" * 60)

            # Send success notification
            self._send_alert(
                "Model Retraining Success",
                f"""
                ✅ New model deployed successfully!

                Training Duration: {duration:.1f}s
                Training Samples: {len(data)}
                Tickers: {len(tickers)}

                Metrics:
                - F1 Score:  {metrics['f1_score']:.3f} (prev: {self.current_metrics.get('f1_score', 0):.3f})
                - Accuracy:  {metrics['accuracy']:.3f} (prev: {self.current_metrics.get('accuracy', 0):.3f})
                - Precision: {metrics['precision']:.3f}
                - Recall:    {metrics['recall']:.3f}

                Model Path: {PROD_MODEL_PATH}
                Backup: {BACKUP_MODEL_PATH}
                """,
            )

            return True

        except Exception as e:
            logger.error(f"Model retraining failed: {e}", exc_info=True)

            self._send_alert(
                "Model Retraining Error",
                f"""
                ❌ Model retraining failed with error:

                {str(e)}

                Using previous model version.
                Check logs for details.
                """,
            )

            return False

    def rollback_model(self):
        """Rollback to backup model"""
        if not BACKUP_MODEL_PATH.exists():
            raise FileNotFoundError("No backup model available")

        import shutil

        shutil.copy(BACKUP_MODEL_PATH, PROD_MODEL_PATH)
        logger.info("Rolled back to backup model")

        # Reload metrics from backup
        # Note: This is simplified - in production, track backup metrics too
        self._send_alert(
            "Model Rollback",
            "Model rolled back to previous version due to issues.",
        )

    def start(self):
        """Start the retraining scheduler"""
        if self.is_running:
            logger.warning("Retraining scheduler already running")
            return

        # Schedule daily retraining at 2 AM
        self.scheduler.add_job(
            self.retrain_model,
            trigger="cron",
            hour=2,
            minute=0,
            id="daily_retraining",
            name="Daily Model Retraining",
            replace_existing=True,
        )

        # Also retrain every Sunday at 3 AM with extended data
        self.scheduler.add_job(
            lambda: self.retrain_model(),
            trigger="cron",
            day_of_week="sun",
            hour=3,
            minute=0,
            id="weekly_full_retrain",
            name="Weekly Full Retraining",
            replace_existing=True,
        )

        self.scheduler.start()
        self.is_running = True

        logger.info("Model retraining scheduler started")
        logger.info("  Daily retraining: 2:00 AM")
        logger.info("  Weekly full retrain: Sunday 3:00 AM")

    def stop(self):
        """Stop the retraining scheduler"""
        if not self.is_running:
            return

        self.scheduler.shutdown(wait=False)
        self.is_running = False
        logger.info("Model retraining scheduler stopped")

    def get_status(self) -> Dict:
        """Get current retraining status"""
        jobs = self.scheduler.get_jobs() if self.is_running else []

        return {
            "running": self.is_running,
            "current_metrics": self.current_metrics,
            "next_retraining": (jobs[0].next_run_time.isoformat() if jobs else None),
            "scheduled_jobs": [{"name": job.name, "next_run": job.next_run_time.isoformat()} for job in jobs],
            "model_path": str(PROD_MODEL_PATH),
            "backup_path": str(BACKUP_MODEL_PATH),
        }


# Singleton instance
_retraining_service: Optional[ModelRetrainingService] = None


def get_retraining_service() -> ModelRetrainingService:
    """Get or create retraining service singleton"""
    global _retraining_service
    if _retraining_service is None:
        _retraining_service = ModelRetrainingService()
    return _retraining_service


def start_retraining_scheduler():
    """Start the automated retraining scheduler"""
    service = get_retraining_service()
    service.start()
    return service


def stop_retraining_scheduler():
    """Stop the automated retraining scheduler"""
    service = get_retraining_service()
    service.stop()
