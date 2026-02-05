"""
Rate limiting middleware for Chat API.

Implements token bucket rate limiting to prevent abuse.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict
import time
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter.

    Allows burst traffic while maintaining average rate limit.
    """

    def __init__(self, rate: int = 100, per: int = 60):
        """
        Initialize rate limiter.

        Args:
            rate: Number of requests allowed
            per: Time period in seconds
        """
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()

    def is_allowed(self) -> bool:
        """
        Check if request is allowed.

        Returns:
            True if request is allowed, False otherwise
        """
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current

        # Add tokens based on time passed
        self.allowance += time_passed * (self.rate / self.per)

        # Cap at rate limit
        if self.allowance > self.rate:
            self.allowance = self.rate

        # Check if we have tokens
        if self.allowance < 1.0:
            return False
        else:
            self.allowance -= 1.0
            return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.

    Limits requests per IP address or user ID.
    """

    def __init__(self, app, rate: int = 100, per: int = 60):
        """
        Initialize middleware.

        Args:
            app: FastAPI application
            rate: Number of requests allowed
            per: Time period in seconds
        """
        super().__init__(app)
        self.rate = rate
        self.per = per
        self.limiters: Dict[str, RateLimiter] = {}

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response
        """
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Get client identifier (IP address or user ID)
        client_id = self._get_client_id(request)

        # Get or create rate limiter for client
        if client_id not in self.limiters:
            self.limiters[client_id] = RateLimiter(self.rate, self.per)

        limiter = self.limiters[client_id]

        # Check rate limit
        if not limiter.is_allowed():
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.rate} requests per {self.per} seconds",
                    "retry_after": self.per
                },
                headers={
                    "Retry-After": str(self.per),
                    "X-RateLimit-Limit": str(self.rate),
                    "X-RateLimit-Remaining": "0"
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate)
        response.headers["X-RateLimit-Remaining"] = str(int(limiter.allowance))

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request.

        Args:
            request: HTTP request

        Returns:
            Client identifier (IP address or user ID)
        """
        # Try to get user ID from headers
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    def cleanup_old_limiters(self):
        """
        Clean up rate limiters for inactive clients.

        Should be called periodically to prevent memory leaks.
        """
        current_time = time.time()
        inactive_threshold = self.per * 10  # 10x the rate limit period

        to_remove = []
        for client_id, limiter in self.limiters.items():
            if current_time - limiter.last_check > inactive_threshold:
                to_remove.append(client_id)

        for client_id in to_remove:
            del self.limiters[client_id]

        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive rate limiters")
