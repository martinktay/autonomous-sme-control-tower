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

# Path prefixes that involve file uploads — use a separate, stricter limit
_UPLOAD_PREFIXES = ("/api/invoices/upload", "/api/finance/upload")

# Auth endpoints get a much stricter limit to prevent brute force
_AUTH_PREFIXES = ("/api/auth/login", "/api/auth/register")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter keyed by client IP.

    Tracks request timestamps per IP within a 60-second window.
    Returns HTTP 429 with Retry-After header when the limit is exceeded.
    Auth endpoints have a stricter limit (10/min) to prevent brute force.
    Upload endpoints have a separate limit (20/min) to prevent abuse.
    """

    def __init__(self, app, rpm: int = 120):
        super().__init__(app)
        self.rpm = rpm
        self.auth_rpm = 10       # Strict limit for login/register
        self.upload_rpm = 20     # Separate limit for file uploads
        self._lock = Lock()
        # ip -> list of request timestamps
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._auth_requests: dict[str, list[float]] = defaultdict(list)
        self._upload_requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit for non-exempt paths; return 429 if exceeded."""
        path = request.url.path
        if path in _EXEMPT or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0  # 1 minute

        # Auth endpoints — strict limit
        if any(path.startswith(p) for p in _AUTH_PREFIXES):
            with self._lock:
                timestamps = self._auth_requests[client_ip]
                self._auth_requests[client_ip] = [t for t in timestamps if now - t < window]
                if len(self._auth_requests[client_ip]) >= self.auth_rpm:
                    logger.warning("Auth rate limit exceeded for %s", client_ip)
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many login attempts. Try again in a minute."},
                        headers={"Retry-After": "60"},
                    )
                self._auth_requests[client_ip].append(now)
            return await call_next(request)

        # Upload endpoints — separate limit (skip BaseHTTPMiddleware body conflict
        # by only counting, not consuming body)
        if any(path.startswith(p) for p in _UPLOAD_PREFIXES):
            with self._lock:
                timestamps = self._upload_requests[client_ip]
                self._upload_requests[client_ip] = [t for t in timestamps if now - t < window]
                if len(self._upload_requests[client_ip]) >= self.upload_rpm:
                    logger.warning("Upload rate limit exceeded for %s", client_ip)
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Upload rate limit exceeded. Try again shortly."},
                        headers={"Retry-After": "60"},
                    )
                self._upload_requests[client_ip].append(now)
            return await call_next(request)

        # General rate limit
        with self._lock:
            timestamps = self._requests[client_ip]
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
