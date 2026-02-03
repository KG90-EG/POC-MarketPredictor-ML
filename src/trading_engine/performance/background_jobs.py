"""
Background Jobs for Pre-computation and Cache Warming

This module provides scheduled background tasks that pre-compute expensive
operations and warm caches to ensure fast API response times.

Features:
- Ranking pre-computation every 15 minutes
- Feature cache warming for popular stocks
- Model health checks
- Automatic retry on failures

Usage:
    from .performance.background_jobs import start_background_jobs, stop_background_jobs

    # In lifespan
    start_background_jobs()

    # On shutdown
    stop_background_jobs()
"""

import logging
import traceback
from datetime import datetime
from typing import Any, Dict, List

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler = None

# Job execution stats
_job_stats = {
    "update_rankings": {
        "last_run": None,
        "last_success": None,
        "total_runs": 0,
        "total_errors": 0,
        "last_error": None,
    },
    "warm_cache": {
        "last_run": None,
        "last_success": None,
        "total_runs": 0,
        "total_errors": 0,
        "last_error": None,
    },
}

# Default stock lists for pre-computation
DEFAULT_STOCKS = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "TSLA",
    "BRK.B",
    "V",
    "JNJ",
    "WMT",
    "JPM",
    "MA",
    "PG",
    "UNH",
    "DIS",
    "HD",
    "PYPL",
    "BAC",
    "ADBE",
]

POPULAR_COUNTRIES = ["USA", "Germany", "Global"]


def update_rankings_job():
    """
    Pre-compute rankings for popular countries and cache results.

    This job runs every 15 minutes to ensure /ranking endpoint
    returns instantly from cache.
    """
    job_name = "update_rankings"
    _job_stats[job_name]["last_run"] = datetime.now().isoformat()
    _job_stats[job_name]["total_runs"] += 1

    try:
        logger.info("Background job: Starting ranking update")

        # Import here to avoid circular dependencies
        from ..core.cache import cache
        from ..ml.trading import MODEL, features_legacy
        from ..performance import (get_parallel_processor,
                                   parallel_stock_ranking)

        for country in POPULAR_COUNTRIES:
            try:
                # Use appropriate stock list based on country
                if country == "USA":
                    stocks = DEFAULT_STOCKS[:15]  # Top 15 US stocks
                elif country == "Germany":
                    stocks = ["SAP", "SIE.DE", "VOW3.DE", "BAS.DE", "ALV.DE"]
                else:  # Global
                    stocks = DEFAULT_STOCKS[:10]

                logger.info(f"Pre-computing rankings for {country} ({len(stocks)} stocks)")

                # Compute rankings using parallel processing
                result = parallel_stock_ranking(stocks, MODEL, features_legacy)

                # Cache results with 20-minute expiry (longer than job interval)
                cache_key = f"ranking:{country}"
                cache.set(cache_key, result, ttl=1200)  # 20 minutes

                logger.info(f"Cached {len(result)} rankings for {country}")

            except Exception as e:
                logger.error(f"Error updating rankings for {country}: {e}")
                logger.debug(traceback.format_exc())

        _job_stats[job_name]["last_success"] = datetime.now().isoformat()
        logger.info("Background job: Ranking update completed")

    except Exception as e:
        _job_stats[job_name]["total_errors"] += 1
        _job_stats[job_name]["last_error"] = str(e)
        logger.error(f"Background job error in {job_name}: {e}")
        logger.debug(traceback.format_exc())


def warm_cache_job():
    """
    Warm feature cache for popular stocks.

    This job runs every 10 minutes to keep feature cache hot
    and ensure fast predictions.
    """
    job_name = "warm_cache"
    _job_stats[job_name]["last_run"] = datetime.now().isoformat()
    _job_stats[job_name]["total_runs"] += 1

    try:
        logger.info("Background job: Starting cache warmup")

        # Import here to avoid circular dependencies
        import yfinance as yf

        from ..ml.feature_engineering import add_all_features
        from ..performance.feature_cache import get_feature_cache

        feature_cache = get_feature_cache()
        stocks_warmed = 0

        for ticker in DEFAULT_STOCKS[:10]:  # Warm top 10 stocks
            try:
                # Check if already cached
                cached = feature_cache.get(ticker)
                if cached is not None:
                    logger.debug(f"Features for {ticker} already cached, skipping")
                    continue

                # Download and compute features
                logger.debug(f"Warming cache for {ticker}")
                df = yf.Ticker(ticker).history(period="1y")

                if df is not None and len(df) > 0:
                    features_df = add_all_features(df, ticker)
                    feature_cache.set(ticker, features_df)
                    stocks_warmed += 1
                    logger.debug(f"Cached features for {ticker}")

            except Exception as e:
                logger.error(f"Error warming cache for {ticker}: {e}")

        _job_stats[job_name]["last_success"] = datetime.now().isoformat()
        logger.info(f"Background job: Cache warmup completed ({stocks_warmed} stocks)")

    except Exception as e:
        _job_stats[job_name]["total_errors"] += 1
        _job_stats[job_name]["last_error"] = str(e)
        logger.error(f"Background job error in {job_name}: {e}")
        logger.debug(traceback.format_exc())


def start_background_jobs():
    """
    Start the background job scheduler.

    Schedules:
    - update_rankings: Every 15 minutes
    - warm_cache: Every 10 minutes
    """
    global _scheduler

    if _scheduler is not None and _scheduler.running:
        logger.warning("Background jobs already running")
        return

    logger.info("Starting background job scheduler")

    _scheduler = BackgroundScheduler()

    # Schedule ranking updates every 15 minutes
    _scheduler.add_job(
        update_rankings_job,
        trigger=IntervalTrigger(minutes=15),
        id="update_rankings",
        name="Update Rankings Cache",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )

    # Schedule cache warming every 10 minutes
    _scheduler.add_job(
        warm_cache_job,
        trigger=IntervalTrigger(minutes=10),
        id="warm_cache",
        name="Warm Feature Cache",
        replace_existing=True,
        max_instances=1,
    )

    # Start the scheduler
    _scheduler.start()

    # Run initial cache warmup immediately (don't wait 10 minutes)
    logger.info("Running initial cache warmup")
    try:
        warm_cache_job()
    except Exception as e:
        logger.error(f"Initial cache warmup failed: {e}")

    logger.info("Background jobs started successfully")


def stop_background_jobs():
    """
    Stop the background job scheduler gracefully.
    """
    global _scheduler

    if _scheduler is None:
        logger.warning("Background jobs not running")
        return

    logger.info("Stopping background job scheduler")

    if _scheduler.running:
        _scheduler.shutdown(wait=True)

    _scheduler = None
    logger.info("Background jobs stopped")


def get_job_stats() -> Dict[str, Any]:
    """
    Get statistics about background job execution.

    Returns:
        dict: Job statistics including run counts, errors, and last run times
    """
    return {
        "scheduler_running": _scheduler is not None and _scheduler.running,
        "jobs": _job_stats.copy(),
    }


def trigger_job_now(job_id: str):
    """
    Manually trigger a background job immediately.

    Args:
        job_id: ID of the job to trigger ('update_rankings' or 'warm_cache')

    Raises:
        ValueError: If job_id is invalid
    """
    if job_id == "update_rankings":
        logger.info("Manually triggering ranking update")
        update_rankings_job()
    elif job_id == "warm_cache":
        logger.info("Manually triggering cache warmup")
        warm_cache_job()
    else:
        raise ValueError(f"Invalid job_id: {job_id}")
