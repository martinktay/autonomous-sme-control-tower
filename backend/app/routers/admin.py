"""
Admin router — super_admin-only endpoints for user/org management.

All endpoints require a valid JWT with role=super_admin.
  GET    /api/admin/users          — list all users
  PUT    /api/admin/users/role     — change a user's role
  PUT    /api/admin/users/tier     — change a user's pricing tier
  PUT    /api/admin/users/deactivate — deactivate a user
"""

import logging
from typing import Literal
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from app.services.auth_service import get_auth_service
from app.services.country_tax_config import get_dial_codes, COUNTRY_TAX_CONFIG

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_super_admin(request: Request):
    """Raise 403 if the caller is not a super_admin."""
    user_id = getattr(request.state, "user_id", "")
    role = getattr(request.state, "role", "")
    if not user_id or role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")


class RoleUpdate(BaseModel):
    email: EmailStr
    role: Literal["super_admin", "owner", "admin", "member", "viewer"]


class TierUpdate(BaseModel):
    email: EmailStr
    tier: Literal["starter", "growth", "business", "enterprise"]


class DeactivateUser(BaseModel):
    email: EmailStr


@router.get("/users")
async def list_users(request: Request):
    """List all registered users (super_admin only)."""
    _require_super_admin(request)
    svc = get_auth_service()
    users = await svc.list_users()
    return {"users": users, "count": len(users)}


@router.put("/users/role")
async def update_role(payload: RoleUpdate, request: Request):
    """Change a user's role (super_admin only)."""
    _require_super_admin(request)
    svc = get_auth_service()
    try:
        result = await svc.update_user_role(payload.email, payload.role)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/users/tier")
async def update_tier(payload: TierUpdate, request: Request):
    """Change a user's pricing tier (super_admin only)."""
    _require_super_admin(request)
    svc = get_auth_service()
    try:
        result = await svc.update_user_tier(payload.email, payload.tier)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/users/deactivate")
async def deactivate_user(payload: DeactivateUser, request: Request):
    """Deactivate a user account (super_admin only)."""
    _require_super_admin(request)
    svc = get_auth_service()
    try:
        result = await svc.deactivate_user(payload.email)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/stats")
async def get_platform_stats(request: Request):
    """Agentic SaaS metrics dashboard (super_admin only).

    Returns user counts, tier distribution, country distribution,
    email verification rate, and signal/agent activity metrics.
    """
    _require_super_admin(request)
    svc = get_auth_service()
    users = await svc.list_users()

    total_users = len(users)
    active_users = sum(1 for u in users if u.get("is_active") is not False)
    verified_users = sum(1 for u in users if u.get("email_verified") is True)

    # Tier distribution
    tier_dist: dict[str, int] = {}
    for u in users:
        t = u.get("tier", "starter")
        tier_dist[t] = tier_dist.get(t, 0) + 1

    # Country distribution
    country_dist: dict[str, int] = {}
    for u in users:
        c = u.get("country", "NG") or "NG"
        country_dist[c] = country_dist.get(c, 0) + 1

    # Business type distribution
    btype_dist: dict[str, int] = {}
    for u in users:
        bt = u.get("business_type", "other") or "other"
        btype_dist[bt] = btype_dist.get(bt, 0) + 1

    # Signal and agent metrics from DynamoDB
    total_signals = 0
    email_signals = 0
    whatsapp_signals = 0
    total_actions = 0
    total_strategies = 0
    try:
        from app.services.ddb_service import get_ddb_service
        ddb = get_ddb_service()
        # Scan signals table for counts
        sig_resp = ddb.signals_table.scan(Select="COUNT")
        total_signals = sig_resp.get("Count", 0)
        # Count by type (sample scan — limited for performance)
        sig_items = ddb.signals_table.scan(
            ProjectionExpression="signal_type",
            Limit=5000,
        ).get("Items", [])
        for s in sig_items:
            st = s.get("signal_type", "")
            if st == "email":
                email_signals += 1
            elif st == "whatsapp":
                whatsapp_signals += 1
        # Actions count
        act_resp = ddb.actions_table.scan(Select="COUNT")
        total_actions = act_resp.get("Count", 0)
        # Strategies count
        strat_resp = ddb.strategies_table.scan(Select="COUNT")
        total_strategies = strat_resp.get("Count", 0)
    except Exception as e:
        logger.warning("Could not fetch signal/action metrics: %s", e)

    # Revenue estimate (paid tiers — enterprise is custom/contact-us, excluded from auto-calc)
    tier_prices = {"starter": 0, "growth": 14900, "business": 39900, "enterprise": 0}
    monthly_revenue = sum(tier_prices.get(u.get("tier", "starter"), 0) for u in users if u.get("is_active") is not False)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "verification_rate": round(verified_users / max(total_users, 1) * 100, 1),
        "tier_distribution": tier_dist,
        "country_distribution": country_dist,
        "business_type_distribution": btype_dist,
        "total_signals": total_signals,
        "email_signals": email_signals,
        "whatsapp_signals": whatsapp_signals,
        "total_actions": total_actions,
        "total_strategies": total_strategies,
        "estimated_mrr": monthly_revenue,
        "paid_users": sum(1 for u in users if u.get("tier", "starter") != "starter"),
    }


@router.get("/config/dial-codes")
async def get_dial_codes_endpoint():
    """Return supported dial codes for phone input (public endpoint)."""
    return {"dial_codes": get_dial_codes()}


# ── Super Admin: Delete User ──────────────────────────────────────────────────

class DeleteUser(BaseModel):
    email: EmailStr


@router.delete("/users")
async def delete_user(payload: DeleteUser, request: Request):
    """Permanently delete a user account and all associated data (super_admin only)."""
    _require_super_admin(request)
    svc = get_auth_service()
    user = svc._get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("role") == "super_admin":
        raise HTTPException(status_code=400, detail="Cannot delete a super_admin account")
    try:
        svc.users_table.delete_item(Key={"email": payload.email})
        logger.info("Super admin deleted user: %s", payload.email)
        return {"message": f"User {payload.email} deleted permanently", "email": payload.email}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Super Admin: Reactivate User ─────────────────────────────────────────────

class ReactivateUser(BaseModel):
    email: EmailStr


@router.put("/users/reactivate")
async def reactivate_user(payload: ReactivateUser, request: Request):
    """Reactivate a previously deactivated user (super_admin only)."""
    _require_super_admin(request)
    svc = get_auth_service()
    user = svc._get_user_by_email(payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        svc.users_table.update_item(
            Key={"email": payload.email},
            UpdateExpression="SET is_active = :a",
            ExpressionAttributeValues={":a": True},
        )
        return {"message": f"User {payload.email} reactivated", "email": payload.email}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ── Super Admin: Subscription Management ─────────────────────────────────────

@router.get("/subscriptions")
async def list_all_subscriptions(request: Request):
    """List all subscriptions across the platform (super_admin only)."""
    _require_super_admin(request)
    try:
        from app.services.subscription_service import get_subscription_service
        svc = get_subscription_service()
        subs = svc.list_all_subscriptions()
        return {"subscriptions": subs, "count": len(subs)}
    except Exception as e:
        logger.warning("Could not fetch subscriptions: %s", e)
        return {"subscriptions": [], "count": 0}


class AdminSubscriptionUpdate(BaseModel):
    email: EmailStr
    tier: Literal["starter", "growth", "business", "enterprise"]
    payment_method: str = "admin_override"


@router.put("/subscriptions/override")
async def override_subscription(payload: AdminSubscriptionUpdate, request: Request):
    """Override a user's subscription tier directly (super_admin only).
    Useful for granting complimentary access or resolving payment issues.
    """
    _require_super_admin(request)
    svc = get_auth_service()
    try:
        result = await svc.update_user_tier(payload.email, payload.tier)
        logger.info("Super admin overrode tier for %s to %s", payload.email, payload.tier)
        return {**result, "message": f"Tier overridden to {payload.tier} for {payload.email}"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ── Super Admin: Platform Configuration ──────────────────────────────────────

@router.get("/config/platform")
async def get_platform_config(request: Request):
    """Get current platform configuration (super_admin only)."""
    _require_super_admin(request)
    from app.config import get_settings
    s = get_settings()
    return {
        "region": s.aws_region,
        "debug": s.debug,
        "cors_origins": s.cors_origins,
        "rate_limit_rpm": s.rate_limit_rpm,
        "documents_bucket": s.documents_bucket,
        "models": {
            "nova_lite": s.nova_lite_model_id,
            "nova_embeddings": s.nova_embeddings_model_id,
            "nova_act": s.nova_act_model_id,
            "nova_sonic": s.nova_sonic_model_id,
        },
        "tables": {
            "users": s.users_table,
            "signals": s.signals_table,
            "strategies": s.strategies_table,
            "actions": s.actions_table,
            "transactions": getattr(s, "transactions_table", ""),
            "inventory": getattr(s, "inventory_table", ""),
            "subscriptions": getattr(s, "subscriptions_table", ""),
            "outbound_invoices": getattr(s, "outbound_invoices_table", ""),
        },
    }


