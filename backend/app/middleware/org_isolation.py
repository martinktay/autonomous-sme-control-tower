"""
Organization data isolation middleware for multi-tenant security.

Now hardened: reads the authenticated org_id from request.state (set by
AuthMiddleware from the JWT) instead of trusting the X-Org-ID header.
Compares it against org_id in the request path/query and returns 403 on
mismatch. Exempts health-check, docs, auth, and CORS preflight requests.
"""

import re
import logging
import json
from typing import Callable
from datetime import datetime, timezone

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


class SecurityEvent:
    """Structured security event logger for audit trails."""

    @staticmethod
    def log_access_violation(
        org_id: str, requested_org_id: str, path: str, method: str, client_ip: str
    ) -> None:
        event = {
            "event_type": "access_violation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "high",
            "authenticated_org_id": org_id,
            "requested_org_id": requested_org_id,
            "path": path,
            "method": method,
            "client_ip": client_ip,
            "message": f"Organization {org_id} attempted to access data for {requested_org_id}",
        }
        logger.warning("SECURITY_EVENT: %s", json.dumps(event))

    @staticmethod
    def log_missing_org_id(path: str, method: str, client_ip: str) -> None:
        event = {
            "event_type": "missing_org_id",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "medium",
            "path": path,
            "method": method,
            "client_ip": client_ip,
            "message": "Request missing required org_id",
        }
        logger.warning("SECURITY_EVENT: %s", json.dumps(event))


class OrgIsolationMiddleware(BaseHTTPMiddleware):
    """
    Enforces that the JWT-authenticated org_id matches any org_id
    present in the request path or query parameters.
    """

    EXEMPT_PATHS = ["/", "/health", "/docs", "/openapi.json", "/redoc"]
    EXEMPT_PREFIXES = [
        "/api/auth/",
        "/api/pricing",
        "/api/invoices/upload",
        "/api/finance/upload",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        if path in self.EXEMPT_PATHS:
            return await call_next(request)
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)

        # org_id set by AuthMiddleware from JWT claims
        authenticated_org_id = getattr(request.state, "org_id", "")

        # If AuthMiddleware didn't set org_id (e.g. public route that slipped
        # through), allow but don't validate
        if not authenticated_org_id:
            return await call_next(request)

        # Check if the request path/query contains a different org_id
        requested_org_id = self._extract_requested_org_id(request)

        if requested_org_id and authenticated_org_id != requested_org_id:
            client_ip = request.client.host if request.client else "unknown"
            SecurityEvent.log_access_violation(
                org_id=authenticated_org_id,
                requested_org_id=requested_org_id,
                path=path,
                method=request.method,
                client_ip=client_ip,
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Access denied: insufficient permissions to access this organization's data",
                    "error_code": "ORG_ACCESS_DENIED",
                },
            )

        return await call_next(request)

    # ------------------------------------------------------------------

    def _extract_requested_org_id(self, request: Request) -> str:
        """Extract org_id from query params or path segments."""
        org_id = request.query_params.get("org_id", "")
        if org_id:
            return org_id

        for part in request.url.path.split("/"):
            if part and (part.startswith("org") or bool(_UUID_RE.match(part))):
                return part
        return ""


# ------------------------------------------------------------------
# Helpers used by route handlers
# ------------------------------------------------------------------


def get_org_id_from_request(request: Request) -> str:
    """Get the validated org_id stored in request.state by AuthMiddleware."""
    return getattr(request.state, "org_id", "")


def validate_org_id_from_body(request: Request, body_org_id: str) -> None:
    """Validate org_id from request body against the JWT-authenticated org_id.

    Call this in route handlers that receive org_id in the JSON body
    (the middleware only checks path/query params, not the body).

    Raises:
        HTTPException: 403 if org_id does not match.
    """
    authenticated_org_id = getattr(request.state, "org_id", "")

    if not authenticated_org_id:
        # AuthMiddleware didn't set it — store body value for downstream
        request.state.org_id = body_org_id
        return

    if authenticated_org_id != body_org_id:
        client_ip = request.client.host if request.client else "unknown"
        SecurityEvent.log_access_violation(
            org_id=authenticated_org_id,
            requested_org_id=body_org_id,
            path=request.url.path,
            method=request.method,
            client_ip=client_ip,
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied: insufficient permissions to access this organization's data",
        )

    request.state.org_id = authenticated_org_id
