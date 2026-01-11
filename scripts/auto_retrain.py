"""
Automatic Model Retraining Scheduler

This module implements automatic retraining of the ML model on a schedule
using APScheduler. It can run as a standalone service or be integrated into
the main FastAPI application.

Features:
- Scheduled retraining (daily, weekly, or custom)
- Health checks before training
- Automatic deployment of better models
- Email notifications (optional)
- MLflow tracking integration

Usage as standalone service:
    python scripts/auto_retrain.py --schedule daily --time "02:00"

Usage integrated in FastAPI:
    from scripts.auto_retrain import setup_auto_retraining
    setup_auto_retraining(app, schedule="weekly", day_of_week="sun", time="02:00")
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/auto_retrain.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def run_training():
    """Execute the production training script."""
    logger.info("=" * 80)
    logger.info("Starting automatic model retraining...")
    logger.info("=" * 80)

    try:
        # Import here to avoid circular dependencies
        from scripts.train_production import main as train_main

        # Run training
        result = train_main()

        if result == 0:
            logger.info("✅ Automatic retraining completed successfully")
            return True
        else:
            logger.error("❌ Automatic retraining failed")
            return False

    except Exception as e:
        logger.error(f"❌ Error during automatic retraining: {e}", exc_info=True)
        return False


def setup_auto_retraining(
    app=None, schedule="weekly", day_of_week="sun", time="02:00", enabled=True
):
    """
    Setup automatic retraining scheduler.

    Args:
        app: FastAPI app instance (optional, for integration)
        schedule: "daily", "weekly", or "monthly"
        day_of_week: Day of week for weekly schedule (mon-sun)
        time: Time to run (HH:MM format, 24-hour)
        enabled: Whether to enable auto-retraining

    Returns:
        BackgroundScheduler instance
    """
    if not enabled:
        logger.info("⚠️  Auto-retraining is disabled")
        return None

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Parse time
    hour, minute = map(int, time.split(":"))

    # Create scheduler
    scheduler = BackgroundScheduler()

    # Configure trigger based on schedule type
    if schedule == "daily":
        trigger = CronTrigger(hour=hour, minute=minute)
        logger.info(f"📅 Scheduled daily retraining at {time}")

    elif schedule == "weekly":
        # Convert day_of_week to APScheduler format
        day_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
        day = day_map.get(day_of_week.lower(), 6)  # Default to Sunday
        trigger = CronTrigger(day_of_week=day, hour=hour, minute=minute)
        logger.info(
            f"📅 Scheduled weekly retraining on {day_of_week.upper()} at {time}"
        )

    elif schedule == "monthly":
        trigger = CronTrigger(day=1, hour=hour, minute=minute)
        logger.info(f"📅 Scheduled monthly retraining on 1st at {time}")

    else:
        logger.error(f"Invalid schedule type: {schedule}")
        return None

    # Add job to scheduler
    scheduler.add_job(
        run_training,
        trigger=trigger,
        id="auto_retrain_job",
        name="Automatic Model Retraining",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping executions
    )

    # Start scheduler
    scheduler.start()
    logger.info("✅ Auto-retraining scheduler started successfully")

    # If integrating with FastAPI, add shutdown hook
    if app is not None:

        @app.on_event("shutdown")
        def shutdown_scheduler():
            logger.info("Shutting down auto-retraining scheduler...")
            scheduler.shutdown()

    return scheduler


def main():
    """Run as standalone scheduler service."""
    parser = argparse.ArgumentParser(description="Automatic model retraining scheduler")
    parser.add_argument(
        "--schedule",
        type=str,
        default="weekly",
        choices=["daily", "weekly", "monthly"],
        help="Retraining schedule frequency",
    )
    parser.add_argument(
        "--day",
        type=str,
        default="sun",
        choices=["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
        help="Day of week for weekly schedule",
    )
    parser.add_argument(
        "--time",
        type=str,
        default="02:00",
        help="Time to run retraining (HH:MM, 24-hour format)",
    )
    parser.add_argument(
        "--run-now", action="store_true", help="Run training immediately on startup"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🤖 AUTO-RETRAINING SCHEDULER")
    print("=" * 80)
    print(f"\nSchedule: {args.schedule}")
    if args.schedule == "weekly":
        print(f"Day: {args.day.upper()}")
    print(f"Time: {args.time}")
    print("\nPress Ctrl+C to stop the scheduler")
    print("=" * 80)

    # Setup scheduler
    scheduler = setup_auto_retraining(
        schedule=args.schedule, day_of_week=args.day, time=args.time, enabled=True
    )

    if scheduler is None:
        print("❌ Failed to setup scheduler")
        return 1

    # Run immediately if requested
    if args.run_now:
        print("\n🚀 Running initial training...")
        run_training()

    # Keep the script running
    try:
        import time

        while True:
            time.sleep(60)  # Sleep for 1 minute
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutting down scheduler...")
        scheduler.shutdown()
        print("✅ Scheduler stopped")
        return 0


if __name__ == "__main__":
    sys.exit(main())
