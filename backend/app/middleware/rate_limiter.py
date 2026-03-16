"""
Simple in-memory rate limiter middleware.

Uses a sliding-window counter per client IP.  Good enough for a single-process
deployment; swap for Redis-backed limiter in a multi-instance setup.
"""

import time
import logging
from collections import defaultdict
from threading import Lock
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Paths exempt from rate limiting
_EXEMPT = {"/", "/health", "/docs", "/openapi.json", "/redoc"}

# Path prefixes that involve file uploads — exempt to avoid BaseHTTPMiddleware
# body-stream conflicts with multipart form data.
_UPLOAD_PREFIXES = ("/api/invoices/upload", "/api/finance/upload", "/api/finance/")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP.

    Tracks request timestamps per IP within a 60-second window.
    Returns HTTP 429 with Retry-After header when the limit is exceeded.
    """

    def __init__(self, app, rpm: int = 120):
        super().__init__(app)
        self.rpm = rpm
        self._lock = Lock()
        # ip -> list of request timestamps
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit for non-exempt paths; return 429 if exceeded."""
        path = request.url.path
        if path in _EXEMPT or request.method == "OPTIONS":
            return await call_next(request)
        # Skip rate limiting for upload endpoints (multipart body-stream conflict)
        if any(path.startswith(p) for p in _UPLOAD_PREFIXES):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0  # 1 minute

        with self._lock:
            timestamps = self._requests[client_ip]
            # Prune timestamps older than the 60s window
            self._requests[client_ip] = [t for t in timestamps if now - t < window]
            if len(self._requests[client_ip]) >= self.rpm:
                logger.warning("Rate limit exceeded for %s", client_ip)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Try again shortly."},
                    headers={"Retry-After": "60"},
                )
            self._requests[client_ip].append(now)

        return await call_next(request)
