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
