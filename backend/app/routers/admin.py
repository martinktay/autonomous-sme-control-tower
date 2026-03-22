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
