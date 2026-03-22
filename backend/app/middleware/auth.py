"""
JWT authentication middleware + RBAC helpers.

Validates the Authorization Bearer token on all /api/ routes except
public endpoints (auth, health, pricing, docs). Extracts user_id and
org_id from JWT claims and sets them on request.state for downstream use.

RBAC hierarchy (ascending privilege):
  viewer < member < admin < owner < super_admin
"""

import logging
from typing import Callable

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.auth_service import decode_access_token

logger = logging.getLogger(__name__)

# Paths that do NOT require authentication
PUBLIC_PREFIXES = [
    "/api/auth/",
    "/api/pricing",
    "/docs",
    "/openapi.json",
    "/redoc",
]

PUBLIC_EXACT = ["/", "/health"]

# ---------------------------------------------------------------------------
# RBAC helpers
# ---------------------------------------------------------------------------

ROLE_HIERARCHY = ["viewer", "member", "admin", "owner", "super_admin"]


def _role_level(role: str) -> int:
    """Return numeric level for a role (higher = more privilege)."""
    try:
        return ROLE_HIERARCHY.index(role)
    except ValueError:
        return 0


def require_role(request: Request, min_role: str = "member") -> None:
    """Raise 403 if the caller's role is below *min_role*.

    Usage in a router endpoint::

        from app.middleware.auth import require_role
        @router.post("/something")
        async def create_something(request: Request, ...):
            require_role(request, "member")
            ...
    """
    user_role = getattr(request.state, "role", "viewer")
    if _role_level(user_role) < _role_level(min_role):
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Requires at least '{min_role}' role.",
        )


class AuthMiddleware(BaseHTTPMiddleware):
    """Enforce JWT auth on protected API routes."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Skip auth for public / non-API paths
        if path in PUBLIC_EXACT:
            return await call_next(request)
        if any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)

        # Extract Bearer token
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = auth_header[7:]
        claims = decode_access_token(token)
        if claims is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        # Populate request.state for downstream handlers & org isolation
        request.state.user_id = claims.get("sub", "")
        request.state.org_id = claims.get("org_id", "")
        request.state.email = claims.get("email", "")
        request.state.role = claims.get("role", "owner")
        request.state.tier = claims.get("tier", "starter")

        # Also set X-Org-ID header equivalent so org isolation middleware works
        # (it reads from request.state.org_id which we just set)

        return await call_next(request)
