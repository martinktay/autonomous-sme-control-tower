"""
Tier enforcement middleware — checks feature access against business pricing tier.

Intercepts requests to tier-gated endpoints and validates that the business's
current tier allows access. Returns 403 if the feature is not available.
"""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.tier_service import get_tier_service

logger = logging.getLogger(__name__)

# Map URL path prefixes to required feature keys
TIER_GATED_ROUTES: dict[str, str] = {
    "/api/inventory/analytics": "inventory_intelligence",
    "/api/counterparties": "supplier_tracking",
    "/api/transactions/cashflow": "cashflow_insights",
}


class TierEnforcementMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces pricing tier feature gates on API routes."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Only check tier-gated routes
        required_feature = None
        for route_prefix, feature in TIER_GATED_ROUTES.items():
            if path.startswith(route_prefix):
                required_feature = feature
                break

        if required_feature is None:
            return await call_next(request)

        # Use authenticated org_id from JWT (set by AuthMiddleware)
        business_id = getattr(request.state, "org_id", "")
        if not business_id:
            business_id = request.headers.get("X-Org-ID", "")

        if not business_id:
            # No business context — let the request through (org isolation will catch it)
            return await call_next(request)

        try:
            tier_service = get_tier_service()
            has_access = tier_service.check_feature(business_id, required_feature)
            if not has_access:
                logger.warning(
                    "Tier gate blocked %s for business %s (feature: %s)",
                    path, business_id, required_feature,
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": f"Upgrade your plan to access this feature.",
                        "feature": required_feature,
                        "upgrade_url": "/pricing",
                    },
                )
        except Exception as e:
            # Don't block requests if tier service fails — log and allow
            logger.error("Tier enforcement error: %s", e)

        return await call_next(request)
