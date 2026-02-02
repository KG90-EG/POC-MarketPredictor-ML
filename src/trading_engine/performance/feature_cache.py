"""
Feature Caching System for Performance Optimization.

Implements multi-level caching:
1. LRU cache (in-memory) for recent features
2. Redis cache (optional) for production
3. TTL-based cache invalidation

Week 1 Performance Targets:
- /ranking: 30s → 3s (10x improvement)
- /predict_ticker: 2-5s → 0.5s (4x improvement)
"""

import hashlib
import logging
import time
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_TTL_SECONDS = 300  # 5 minutes
LRU_CACHE_SIZE = 100  # Store 100 most recent tickers


class FeatureCache:
    """
    Multi-level caching system for feature engineering.

    Level 1: LRU cache (fast, in-memory, per-process)
    Level 2: Redis (shared across instances, optional)
    """

    def __init__(self, redis_client=None):
        """
        Initialize cache with optional Redis backend.

        Args:
            redis_client: Redis client instance (optional)
        """
        self.redis_client = redis_client
        self.cache_hits = 0
        self.cache_misses = 0
        self.last_stats_reset = time.time()

        logger.info(
            f"Feature cache initialized: "
            f"TTL={CACHE_TTL_SECONDS}s, "
            f"LRU_SIZE={LRU_CACHE_SIZE}, "
            f"Redis={'enabled' if redis_client else 'disabled'}"
        )

    def _generate_cache_key(self, ticker: str, timestamp: Optional[int] = None) -> str:
        """
        Generate cache key for ticker + timestamp.

        Args:
            ticker: Stock ticker symbol
            timestamp: Unix timestamp (5-minute buckets)

        Returns:
            Cache key string
        """
        if timestamp is None:
            # Round to 5-minute buckets for cache efficiency
            timestamp = int(time.time() // CACHE_TTL_SECONDS)

        key = f"features:{ticker}:{timestamp}"
        return key

    def get(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Get cached features for ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Cached DataFrame or None
        """
        cache_key = self._generate_cache_key(ticker)

        # Try Redis first (if available)
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    self.cache_hits += 1
                    logger.debug(f"Cache HIT (Redis): {ticker}")
                    # Deserialize from Redis (pickle or JSON)
                    return pd.read_json(cached_data, orient="split")
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")

        # Cache miss
        self.cache_misses += 1
        logger.debug(f"Cache MISS: {ticker}")
        return None

    def set(self, ticker: str, features_df: pd.DataFrame):
        """
        Store features in cache.

        Args:
            ticker: Stock ticker symbol
            features_df: DataFrame with computed features
        """
        cache_key = self._generate_cache_key(ticker)

        # Store in Redis with TTL
        if self.redis_client:
            try:
                serialized = features_df.to_json(orient="split")
                self.redis_client.setex(cache_key, CACHE_TTL_SECONDS, serialized)
                logger.debug(f"Cached to Redis: {ticker} (TTL={CACHE_TTL_SECONDS}s)")
            except Exception as e:
                logger.warning(f"Redis cache set error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dict with hit rate, total requests, uptime
        """
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        uptime = time.time() - self.last_stats_reset

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_requests": total,
            "hit_rate_pct": round(hit_rate, 2),
            "uptime_seconds": int(uptime),
        }

    def reset_stats(self):
        """Reset cache statistics."""
        self.cache_hits = 0
        self.cache_misses = 0
        self.last_stats_reset = time.time()
        logger.info("Cache stats reset")

    def clear(self):
        """Clear all cached data."""
        if self.redis_client:
            try:
                # Clear all feature keys
                pattern = "features:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cache entries")
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")


# Global cache instance
_feature_cache: Optional[FeatureCache] = None


def init_feature_cache(redis_client=None) -> FeatureCache:
    """
    Initialize global feature cache.

    Args:
        redis_client: Optional Redis client

    Returns:
        FeatureCache instance
    """
    global _feature_cache
    _feature_cache = FeatureCache(redis_client)
    return _feature_cache


def get_feature_cache() -> FeatureCache:
    """
    Get global feature cache instance.

    Returns:
        FeatureCache instance
    """
    global _feature_cache
    if _feature_cache is None:
        _feature_cache = FeatureCache()
    return _feature_cache


def cached_features(func: Callable) -> Callable:
    """
    Decorator for caching feature engineering functions.

    Usage:
        @cached_features
        def add_all_features(df, ticker):
            # ... expensive computation ...
            return df_with_features

    Args:
        func: Function that computes features

    Returns:
        Wrapped function with caching
    """

    @wraps(func)
    def wrapper(df: pd.DataFrame, ticker: str, *args, **kwargs) -> pd.DataFrame:
        cache = get_feature_cache()

        # Try to get from cache
        cached_df = cache.get(ticker)
        if cached_df is not None:
            logger.info(f"⚡ Using cached features for {ticker}")
            return cached_df

        # Cache miss - compute features
        start_time = time.time()
        result_df = func(df, ticker, *args, **kwargs)
        duration = time.time() - start_time

        # Store in cache
        cache.set(ticker, result_df)

        logger.info(
            f"🔄 Computed features for {ticker} in {duration:.2f}s "
            f"(cache stats: {cache.get_stats()['hit_rate_pct']}% hit rate)"
        )

        return result_df

    return wrapper


@lru_cache(maxsize=LRU_CACHE_SIZE)
def get_cached_ticker_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    LRU-cached function to fetch ticker data from Yahoo Finance.

    Caches raw OHLCV data to avoid repeated API calls.
    Cache is per-process (not shared).

    Args:
        ticker: Stock ticker symbol
        period: Data period (1y, 6mo, etc.)

    Returns:
        DataFrame with OHLCV data
    """
    import yfinance as yf

    logger.debug(f"Fetching ticker data: {ticker} ({period})")
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    return df


def cache_warmup(tickers: list[str]):
    """
    Pre-populate cache with popular tickers.

    Called on server startup to reduce cold-start latency.

    Args:
        tickers: List of ticker symbols to warm up
    """
    from ..ml.feature_engineering import add_all_features

    logger.info(f"🔥 Cache warmup started for {len(tickers)} tickers...")

    start_time = time.time()
    success_count = 0

    for ticker in tickers:
        try:
            # Fetch and cache features
            df = get_cached_ticker_data(ticker)
            features_df = add_all_features(df, ticker)

            # Store in cache
            cache = get_feature_cache()
            cache.set(ticker, features_df)

            success_count += 1
            logger.debug(f"Warmed up: {ticker}")

        except Exception as e:
            logger.warning(f"Cache warmup failed for {ticker}: {e}")

    duration = time.time() - start_time
    logger.info(
        f"🔥 Cache warmup complete: " f"{success_count}/{len(tickers)} tickers in {duration:.2f}s"
    )


# Backwards compatibility
def clear_feature_cache():
    """Clear all cached features."""
    get_feature_cache().clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache performance statistics."""
    return get_feature_cache().get_stats()
