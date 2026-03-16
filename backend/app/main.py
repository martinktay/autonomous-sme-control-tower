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
from app.config import get_settings
from app.routers import invoices, signals, memory, stability, strategy, actions, voice, orchestration, insights, finance, emails
from app.middleware import OrgIsolationMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware

logger = logging.getLogger(__name__)
settings = get_settings()


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

# CORS — allow all origins for hackathon deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting — sliding-window counter per client IP
app.add_middleware(RateLimiterMiddleware, rpm=settings.rate_limit_rpm)

# Org isolation — validates X-Org-ID header matches path org_id
app.add_middleware(OrgIsolationMiddleware)

# --- Routers (one per domain: invoices, signals, voice, finance, etc.) ---
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


@app.get("/")
async def root():
    return {
        "message": "Autonomous SME Control Tower API",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Deep health check — probes DynamoDB, S3, and SES to surface degraded state."""
    checks: dict = {"api": "ok"}

    # DynamoDB
    try:
        from app.services.ddb_service import get_ddb_service
        ddb = get_ddb_service()
        ddb.client.meta.client.list_tables(Limit=1)
        checks["dynamodb"] = "ok"
    except Exception as exc:
        checks["dynamodb"] = f"error: {exc}"

    # S3
    try:
        from app.services.s3_service import get_s3_service
        s3 = get_s3_service()
        s3.client.head_bucket(Bucket=settings.documents_bucket)
        checks["s3"] = "ok"
    except Exception as exc:
        checks["s3"] = f"error: {exc}"

    # SES
    try:
        from app.services.ses_service import get_ses_service
        ses = get_ses_service()
        quota = ses.check_sending_enabled()
        checks["ses"] = "ok" if "error" not in quota else f"error: {quota['error']}"
    except Exception as exc:
        checks["ses"] = f"error: {exc}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "healthy" if all_ok else "degraded", "checks": checks}
