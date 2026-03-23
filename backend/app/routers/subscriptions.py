"""
Subscription router — payment and subscription management.

Supports multiple payment methods for African SMEs and global businesses:
  GET    /api/subscriptions/payment-methods  — available payment methods by country
  GET    /api/subscriptions/pricing          — pricing tiers with amounts
  POST   /api/subscriptions                  — create a subscription
  GET    /api/subscriptions/current          — get current subscription
  POST   /api/subscriptions/activate         — activate after payment
  POST   /api/subscriptions/cancel           — cancel subscription
  POST   /api/subscriptions/webhook/paystack — Paystack webhook
  POST   /api/subscriptions/webhook/flutterwave — Flutterwave webhook
"""

import hashlib
import hmac
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.services.subscription_service import get_subscription_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
settings = get_settings()


def _verify_paystack_signature(body: bytes, signature: str) -> bool:
    """Verify Paystack webhook HMAC-SHA512 signature."""
    secret = getattr(settings, "paystack_secret_key", "")
    if not secret:
        logger.warning("PAYSTACK_SECRET_KEY not set — skipping webhook signature check")
        return True  # Allow in dev; enforce in prod
    expected = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature)


def _verify_flutterwave_signature(body: bytes, signature: str) -> bool:
    """Verify Flutterwave webhook hash."""
    secret = getattr(settings, "flutterwave_secret_hash", "")
    if not secret:
        logger.warning("FLUTTERWAVE_SECRET_HASH not set — skipping webhook signature check")
        return True
    return hmac.compare_digest(secret, signature)


class CreateSubscriptionPayload(BaseModel):
    tier: str
    payment_method: str
    billing_cycle: str = "monthly"
    currency: str = "NGN"


class ActivatePayload(BaseModel):
    subscription_id: str
    provider_ref: str = ""


class CancelPayload(BaseModel):
    subscription_id: str


@router.get("/payment-methods")
async def get_payment_methods(country_code: str = "NG"):
    """Return available payment methods for a country/region."""
    svc = get_subscription_service()
    methods = svc.get_payment_methods(country_code)
    return {"payment_methods": methods, "country_code": country_code.upper()}


@router.get("/pricing")
async def get_pricing(currency: str = "NGN"):
    """Return pricing tiers with amounts."""
    svc = get_subscription_service()
    tiers = svc.get_pricing(currency)
    return {"tiers": tiers, "currency": currency.upper()}


@router.post("")
async def create_subscription(payload: CreateSubscriptionPayload, request: Request):
    """Create a new subscription (initiates payment flow)."""
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_subscription_service()
    sub = svc.create_subscription(
        org_id=org_id,
        tier=payload.tier,
        payment_method=payload.payment_method,
        billing_cycle=payload.billing_cycle,
        currency=payload.currency,
    )
    return {"subscription": sub, "message": f"Subscription created. Complete payment via {payload.payment_method}."}


@router.get("/current")
async def get_current_subscription(request: Request):
    """Get the current subscription for the authenticated org."""
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_subscription_service()
    sub = svc.get_subscription(org_id)
    if not sub:
        return {"subscription": None, "tier": "starter", "message": "No active subscription — using free Starter plan"}
    return {"subscription": sub}


@router.post("/activate")
async def activate_subscription(payload: ActivatePayload, request: Request):
    """Activate a subscription after payment confirmation."""
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_subscription_service()
    result = svc.activate_subscription(org_id, payload.subscription_id, payload.provider_ref)
    if not result:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Also update the user's tier in the auth service
    try:
        from app.services.auth_service import get_auth_service
        auth = get_auth_service()
        email = getattr(request.state, "email", "")
        if email:
            await auth.update_user_tier(email, result.get("tier", "starter"))
    except Exception as e:
        logger.warning("Could not update user tier after activation: %s", e)

    return {"subscription": result, "message": "Subscription activated"}


@router.post("/cancel")
async def cancel_subscription(payload: CancelPayload, request: Request):
    """Cancel a subscription."""
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_subscription_service()
    result = svc.cancel_subscription(org_id, payload.subscription_id)
    if not result:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"subscription": result, "message": "Subscription cancelled. Access continues until period end."}


@router.post("/webhook/paystack")
async def paystack_webhook(request: Request):
    """Handle Paystack payment webhook notifications."""
    raw_body = await request.body()
    signature = request.headers.get("x-paystack-signature", "")
    if not _verify_paystack_signature(raw_body, signature):
        logger.warning("Paystack webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid signature")

    body = await request.json()
    event = body.get("event", "")
    data = body.get("data", {})
    logger.info("Paystack webhook: event=%s ref=%s", event, data.get("reference", ""))

    if event == "charge.success":
        # Extract org_id and subscription_id from metadata
        metadata = data.get("metadata", {})
        org_id = metadata.get("org_id", "")
        sub_id = metadata.get("subscription_id", "")
        ref = data.get("reference", "")
        if org_id and sub_id:
            svc = get_subscription_service()
            svc.activate_subscription(org_id, sub_id, ref)
            logger.info("Paystack payment confirmed for org %s sub %s", org_id, sub_id)

    return {"status": "ok"}


@router.post("/webhook/flutterwave")
async def flutterwave_webhook(request: Request):
    """Handle Flutterwave payment webhook notifications."""
    raw_body = await request.body()
    signature = request.headers.get("verif-hash", "")
    if not _verify_flutterwave_signature(raw_body, signature):
        logger.warning("Flutterwave webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid signature")

    body = await request.json()
    event = body.get("event", "")
    data = body.get("data", {})
    logger.info("Flutterwave webhook: event=%s", event)

    if event == "charge.completed" and data.get("status") == "successful":
        metadata = data.get("meta", {})
        org_id = metadata.get("org_id", "")
        sub_id = metadata.get("subscription_id", "")
        ref = str(data.get("id", ""))
        if org_id and sub_id:
            svc = get_subscription_service()
            svc.activate_subscription(org_id, sub_id, ref)
            logger.info("Flutterwave payment confirmed for org %s sub %s", org_id, sub_id)

    return {"status": "ok"}
