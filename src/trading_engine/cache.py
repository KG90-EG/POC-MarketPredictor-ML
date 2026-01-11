"""
Simple in-memory cache implementation.

This module provides a basic caching mechanism for development and testing.
In production, use Redis or another distributed cache system.
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class InMemoryCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self):
        """Initialize cache"""
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            self._misses += 1
            return None

        value, expiry = self._cache[key]

        # Check if expired
        if expiry > 0 and time.time() > expiry:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 0) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (0 = no expiry)
        """
        expiry = time.time() + ttl_seconds if ttl_seconds > 0 else 0
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "backend": "in_memory",
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 3),
        }


# Global cache instance
cache = InMemoryCache()
