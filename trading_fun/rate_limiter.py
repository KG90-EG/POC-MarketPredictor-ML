"""
Rate limiting middleware for FastAPI.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter(BaseHTTPMiddleware):
    """
    Simple rate limiter using sliding window algorithm.
    Tracks requests per IP address per endpoint.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        # Store: {ip: {endpoint: [(timestamp, request_count)]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    
    def _clean_old_requests(self, request_list: list, current_time: float):
        """Remove requests older than the window."""
        cutoff_time = current_time - self.window_seconds
        return [req for req in request_list if req[0] > cutoff_time]
    
    def _get_request_count(self, request_list: list) -> int:
        """Get total request count from list of (timestamp, count) tuples."""
        return sum(count for _, count in request_list)
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get endpoint path
        endpoint = request.url.path
        
        # Current time
        current_time = time.time()
        
        # Clean old requests for this IP and endpoint
        self.requests[client_ip][endpoint] = self._clean_old_requests(
            self.requests[client_ip][endpoint],
            current_time
        )
        
        # Count requests in current window
        request_count = self._get_request_count(self.requests[client_ip][endpoint])
        
        # Check if rate limit exceeded
        if request_count >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute.",
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.requests[client_ip][endpoint].append((current_time, 1))
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - request_count - 1
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        total_ips = len(self.requests)
        total_tracked = sum(
            len(endpoints) 
            for endpoints in self.requests.values()
        )
        
        return {
            "tracked_ips": total_ips,
            "tracked_endpoints": total_tracked,
            "requests_per_minute": self.requests_per_minute
        }
