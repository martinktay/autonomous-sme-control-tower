"""
Organization data isolation middleware for multi-tenant security.

Enforces that the X-Org-ID header (authenticated identity) matches the org_id
in the request path/query. Logs security events on mismatch and returns 403.
Exempts health-check, docs, and CORS preflight requests.
"""

import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)


class SecurityEvent:
    """Structured security event logger for audit trails."""
    
    @staticmethod
    def log_access_violation(
        org_id: str,
        requested_org_id: str,
        path: str,
        method: str,
        client_ip: str
    ) -> None:
        """Log security event for cross-organization access attempt"""
        event = {
            "event_type": "access_violation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "high",
            "authenticated_org_id": org_id,
            "requested_org_id": requested_org_id,
            "path": path,
            "method": method,
            "client_ip": client_ip,
            "message": f"Organization {org_id} attempted to access data for organization {requested_org_id}"
        }
        logger.warning(f"SECURITY_EVENT: {json.dumps(event)}")
    
    @staticmethod
    def log_missing_org_id(
        path: str,
        method: str,
        client_ip: str
    ) -> None:
        """Log security event for missing org_id"""
        event = {
            "event_type": "missing_org_id",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "medium",
            "path": path,
            "method": method,
            "client_ip": client_ip,
            "message": "Request missing required org_id"
        }
        logger.warning(f"SECURITY_EVENT: {json.dumps(event)}")


class OrgIsolationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce organization data isolation
    
    This middleware:
    1. Validates org_id from request headers or path parameters
    2. Prevents cross-organization data access
    3. Logs security events for access violations
    4. Returns HTTP 403 for unauthorized access attempts
    """
    
    # Paths that don't require org_id validation
    EXEMPT_PATHS = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and enforce org_id validation"""
        
        # Skip validation for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)
        
        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        
        # Extract org_id from request
        authenticated_org_id = self._extract_authenticated_org_id(request)
        
        # Extract requested org_id from path or query params (not body to avoid consuming it)
        requested_org_id = self._extract_requested_org_id_from_path(request)
        
        # For now, if no authenticated org_id in header, we'll allow the request
        # In production, this should be enforced via authentication
        if not authenticated_org_id:
            if requested_org_id:
                # Store for downstream use
                request.state.org_id = requested_org_id
            else:
                # Log missing org_id for non-exempt paths that need it
                if self._requires_org_id(request.url.path):
                    SecurityEvent.log_missing_org_id(
                        path=request.url.path,
                        method=request.method,
                        client_ip=client_ip
                    )
            
            return await call_next(request)
        
        # If no org_id in request path/query, allow (might be a list endpoint or body-based)
        if not requested_org_id:
            request.state.org_id = authenticated_org_id
            return await call_next(request)
        
        # Validate org_id matches authenticated org_id
        if authenticated_org_id != requested_org_id:
            # Log security violation
            SecurityEvent.log_access_violation(
                org_id=authenticated_org_id,
                requested_org_id=requested_org_id,
                path=request.url.path,
                method=request.method,
                client_ip=client_ip
            )
            
            # Return 403 Forbidden
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Access denied: insufficient permissions to access this organization's data",
                    "error_code": "ORG_ACCESS_DENIED"
                }
            )
        
        # Store validated org_id in request state
        request.state.org_id = authenticated_org_id
        
        return await call_next(request)
    
    def _extract_authenticated_org_id(self, request: Request) -> str:
        """
        Extract authenticated org_id from request headers
        
        In production, this would come from JWT token or session.
        For now, we check X-Org-ID header.
        """
        return request.headers.get("X-Org-ID", "")
    
    def _extract_requested_org_id_from_path(self, request: Request) -> str:
        """
        Extract org_id from request path or query parameters only
        
        Does NOT read request body to avoid consuming it.
        Body validation should be done in route handlers.
        
        Checks:
        1. Query parameters (e.g., ?org_id=...)
        2. Path parameters (e.g., /api/invoices/{org_id}/details)
        """
        # Check query parameters first
        org_id = request.query_params.get("org_id", "")
        if org_id:
            return org_id
        
        # Check path parameters - look for org_id pattern in path
        # Common patterns: /api/resource/{org_id} or /api/resource/{org_id}/subresource
        path_parts = request.url.path.split("/")
        
        # Look for segments that look like org IDs (start with "org" or are UUIDs)
        for part in path_parts:
            if part and (part.startswith("org") or self._looks_like_uuid(part)):
                return part
        
        return ""
    
    def _looks_like_uuid(self, value: str) -> bool:
        """Check if a string looks like a UUID"""
        import re
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(value))
    
    def _requires_org_id(self, path: str) -> bool:
        """Check if path requires org_id validation"""
        # API endpoints require org_id
        return path.startswith("/api/")


def get_org_id_from_request(request: Request) -> str:
    """Get the validated org_id stored by OrgIsolationMiddleware in request.state."""
    return getattr(request.state, "org_id", "")


def validate_org_id_from_body(request: Request, body_org_id: str) -> None:
    """Validate org_id from request body against the X-Org-ID header.

    Call this in route handlers that receive org_id in the JSON body
    (the middleware only checks path/query params, not the body).

    Args:
        request: The FastAPI request object.
        body_org_id: The org_id extracted from the request body.

    Raises:
        HTTPException: 403 if org_id does not match the authenticated identity.
    """
    authenticated_org_id = request.headers.get("X-Org-ID", "")
    
    # If no authenticated org_id, allow (for now - in production this should be enforced)
    if not authenticated_org_id:
        request.state.org_id = body_org_id
        return
    
    # Validate org_id matches
    if authenticated_org_id != body_org_id:
        client_ip = request.client.host if request.client else "unknown"
        
        # Log security violation
        SecurityEvent.log_access_violation(
            org_id=authenticated_org_id,
            requested_org_id=body_org_id,
            path=request.url.path,
            method=request.method,
            client_ip=client_ip
        )
        
        raise HTTPException(
            status_code=403,
            detail="Access denied: insufficient permissions to access this organization's data"
        )
    
    request.state.org_id = authenticated_org_id
