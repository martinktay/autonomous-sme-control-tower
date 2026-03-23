"""
FastAPI application entry point for the Autonomous SME Control Tower.

Configures the middleware stack (CORS, rate limiting, org isolation),
registers all API routers, and exposes health-check endpoints that
verify connectivity to DynamoDB, S3, and SES.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.config import get_settings
from app.routers import (
    auth,
    invoices, signals, memory, stability, strategy, actions, voice,
    orchestration, insights, finance, emails,
    businesses, pricing, inventory, transactions, counterparties, alerts,
    upload_jobs, whatsapp, desktop_sync, supplier_intelligence, predictions,
    pos_connector, bank_sync, forecasting, branch_optimisation,
    admin, tax, team, outbound_invoices, subscriptions,
)
from app.middleware import OrgIsolationMiddleware, AuthMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.tier_enforcement import TierEnforcementMiddleware

logger = logging.getLogger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("SME Control Tower starting up")
    yield
    logger.info("SME Control Tower shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Autonomous operations platform for SMEs",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware (applied bottom-up: last added runs first on request) ---

# CORS — restrict to configured origins (comma-separated in settings)
_cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Org-ID"],
)

# Rate limiting — sliding-window counter per client IP
app.add_middleware(RateLimiterMiddleware, rpm=settings.rate_limit_rpm)

# Tier enforcement — checks feature access against pricing tier
app.add_middleware(TierEnforcementMiddleware)

# Org isolation — validates org_id from JWT matches path org_id
app.add_middleware(OrgIsolationMiddleware)

# JWT authentication — validates Bearer token, sets request.state.user_id/org_id
app.add_middleware(AuthMiddleware)

# Security headers — X-Content-Type-Options, X-Frame-Options, HSTS, etc.
app.add_middleware(SecurityHeadersMiddleware)

# --- Routers (one per domain: invoices, signals, voice, finance, etc.) ---
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(signals.router)
app.include_router(memory.router)
app.include_router(stability.router)
app.include_router(strategy.router)
app.include_router(actions.router)
app.include_router(voice.router)
app.include_router(orchestration.router)
app.include_router(insights.router)
app.include_router(finance.router)
app.include_router(emails.router)
app.include_router(businesses.router)
app.include_router(pricing.router)
app.include_router(inventory.router)
app.include_router(transactions.router)
app.include_router(counterparties.router)
app.include_router(alerts.router)
app.include_router(upload_jobs.router)
app.include_router(whatsapp.router)
app.include_router(desktop_sync.router)
app.include_router(supplier_intelligence.router)
app.include_router(predictions.router)
app.include_router(pos_connector.router)
app.include_router(bank_sync.router)
app.include_router(forecasting.router)
app.include_router(branch_optimisation.router)
app.include_router(admin.router)
app.include_router(tax.router)
app.include_router(team.router)
app.include_router(outbound_invoices.router)
app.include_router(subscriptions.router)


@app.get("/")
async def root():
    return {
        "message": "Autonomous SME Control Tower API",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check — probes DynamoDB, S3, and SES.

    In production (debug=False) only returns status without internal error
    details to avoid leaking infrastructure information.
    """
    checks: dict = {"api": "ok"}

    # DynamoDB
    try:
        from app.services.ddb_service import get_ddb_service
        ddb = get_ddb_service()
        ddb.client.meta.client.list_tables(Limit=1)
        checks["dynamodb"] = "ok"
    except Exception as exc:
        logger.error("Health check — DynamoDB error: %s", exc)
        checks["dynamodb"] = "error"

    # S3
    try:
        from app.services.s3_service import get_s3_service
        s3 = get_s3_service()
        s3.client.head_bucket(Bucket=settings.documents_bucket)
        checks["s3"] = "ok"
    except Exception as exc:
        logger.error("Health check — S3 error: %s", exc)
        checks["s3"] = "error"

    # SES
    try:
        from app.services.ses_service import get_ses_service
        ses = get_ses_service()
        quota = ses.check_sending_enabled()
        checks["ses"] = "ok" if "error" not in quota else "error"
    except Exception as exc:
        logger.error("Health check — SES error: %s", exc)
        checks["ses"] = "error"

    all_ok = all(v == "ok" for v in checks.values())

    # In production, only expose per-service ok/error — no exception text
    if settings.debug:
        return {"status": "healthy" if all_ok else "degraded", "checks": checks}
    return {"status": "healthy" if all_ok else "degraded"}
