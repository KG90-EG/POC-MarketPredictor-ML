"""
Simple rate limiter implementation.

This module provides basic rate limiting for API endpoints.
In production, use Redis-based rate limiting for distributed systems.
"""

import logging
import time
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class InMemoryRateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.

    Tracks requests per IP address and enforces limits.
    """

    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds

        # Track requests: {ip: [(timestamp1, endpoint1), (timestamp2, endpoint2), ...]}
        self._requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, ip: str, endpoint: str = "") -> bool:
        """
        Check if request is allowed.

        Args:
            ip: Client IP address
            endpoint: API endpoint being accessed

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = time.time()
        cutoff = now - self.window_size

        # Remove expired entries
        if ip in self._requests:
            self._requests[ip] = [(ts, ep) for ts, ep in self._requests[ip] if ts > cutoff]

        # Check limit
        if len(self._requests[ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP {ip} ({len(self._requests[ip])} requests)")
            return False

        # Add this request
        self._requests[ip].append((now, endpoint))
        return True

    def get_remaining(self, ip: str) -> int:
        """
        Get remaining requests for IP.

        Args:
            ip: Client IP address

        Returns:
            Number of remaining requests in current window
        """
        now = time.time()
        cutoff = now - self.window_size

        # Clean expired
        if ip in self._requests:
            self._requests[ip] = [(ts, ep) for ts, ep in self._requests[ip] if ts > cutoff]
            current_count = len(self._requests[ip])
        else:
            current_count = 0

        return max(0, self.requests_per_minute - current_count)

    def get_stats(self) -> Dict:
        """
        Get rate limiter statistics.

        Returns:
            Dict with rate limiter stats
        """
        now = time.time()
        cutoff = now - self.window_size

        # Count active IPs and total requests
        active_ips = 0
        total_requests = 0

        for ip, requests in self._requests.items():
            recent_requests = [ts for ts, ep in requests if ts > cutoff]
            if recent_requests:
                active_ips += 1
                total_requests += len(recent_requests)

        return {
            "backend": "in_memory",
            "tracked_ips": len(self._requests),
            "active_ips": active_ips,
            "tracked_endpoints": sum(
                len(set(ep for _, ep in reqs)) for reqs in self._requests.values()
            ),
            "requests_per_minute": self.requests_per_minute,
            "current_requests": total_requests,
        }

    def reset(self, ip: Optional[str] = None) -> None:
        """
        Reset rate limit counters.

        Args:
            ip: IP to reset (None = reset all)
        """
        if ip:
            if ip in self._requests:
                del self._requests[ip]
        else:
            self._requests.clear()


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter(requests_per_minute=60)
