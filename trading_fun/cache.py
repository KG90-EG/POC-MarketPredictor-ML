"""
Redis-based caching with fallback to in-memory cache.
"""

import json
import logging
import os
from datetime import timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import Redis, but make it optional
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - using in-memory cache only")


class CacheManager:
    """Unified cache manager with Redis backend and in-memory fallback."""

    def __init__(self):
        self.redis_client = None
        self.in_memory_cache = {}
        self.cache_timestamps = {}

        # Try to connect to Redis if available
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                # Test connection
                self.redis_client.ping()
                logger.info(f"Connected to Redis at {redis_url}")
            except Exception as e:
                logger.warning(
                    f"Could not connect to Redis: {e}. Using in-memory cache."
                )
                self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (Redis or in-memory)."""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error for key {key}: {e}")

        # Fallback to in-memory cache
        if key in self.in_memory_cache:
            import time

            if key in self.cache_timestamps:
                # Check if expired (default 1 hour)
                if time.time() - self.cache_timestamps[key] < 3600:
                    return self.in_memory_cache[key]
                else:
                    # Expired, remove it
                    del self.in_memory_cache[key]
                    del self.cache_timestamps[key]

        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Set value in cache with TTL (Redis or in-memory)."""
        # Try Redis first
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key, ttl_seconds, json.dumps(value, default=str)
                )
                return True
            except Exception as e:
                logger.error(f"Redis set error for key {key}: {e}")

        # Fallback to in-memory cache
        import time

        self.in_memory_cache[key] = value
        self.cache_timestamps[key] = time.time()
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        success = False

        # Try Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                success = True
            except Exception as e:
                logger.error(f"Redis delete error for key {key}: {e}")

        # Also delete from in-memory cache
        if key in self.in_memory_cache:
            del self.in_memory_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
            success = True

        return success

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern (e.g., 'ticker_info:*')."""
        count = 0

        # Try Redis
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
                logger.info(f"Cleared {count} Redis keys matching {pattern}")
            except Exception as e:
                logger.error(f"Redis clear pattern error for {pattern}: {e}")

        # Also clear from in-memory cache
        keys_to_delete = [
            k for k in self.in_memory_cache.keys() if self._matches_pattern(k, pattern)
        ]
        for key in keys_to_delete:
            del self.in_memory_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
            count += 1

        return count

    @staticmethod
    def _matches_pattern(key: str, pattern: str) -> bool:
        """Simple pattern matching for in-memory cache (supports * wildcard)."""
        import re

        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", key))

    def get_stats(self) -> dict:
        """Get cache statistics."""
        stats = {
            "backend": "redis" if self.redis_client else "in-memory",
            "in_memory_keys": len(self.in_memory_cache),
        }

        if self.redis_client:
            try:
                info = self.redis_client.info("stats")
                stats["redis_keys"] = self.redis_client.dbsize()
                stats["redis_hits"] = info.get("keyspace_hits", 0)
                stats["redis_misses"] = info.get("keyspace_misses", 0)
            except Exception as e:
                logger.error(f"Error getting Redis stats: {e}")

        return stats


# Global cache instance
cache = CacheManager()
