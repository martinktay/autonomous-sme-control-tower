"""
Team management router — invite members, list team, update roles, remove.

Requires owner or admin role for write operations.
  POST   /api/team/invite              — invite a member to the org
  GET    /api/team/members             — list org members
  PUT    /api/team/members/{email}/role — change a member's role
  DELETE /api/team/members/{email}     — remove a member
"""

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from app.middleware.auth import require_role
from app.services.auth_service import get_auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/team", tags=["team"])


class InvitePayload(BaseModel):
    email: EmailStr
    role: Literal["admin", "member", "viewer"] = "member"


class RoleUpdatePayload(BaseModel):
    role: Literal["admin", "member", "viewer"]


@router.post("/invite")
async def invite_member(payload: InvitePayload, request: Request):
    """Invite a new member to the caller's org (owner/admin only)."""
    require_role(request, "admin")
    org_id = getattr(request.state, "org_id", "")
    email = getattr(request.state, "email", "")
    tier = getattr(request.state, "tier", "starter")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_auth_service()
    # Look up the org's business name from the inviter's record
    inviter = svc._get_user_by_email(email)
    biz_name = inviter.get("business_name", "") if inviter else ""

    try:
        result = await svc.invite_member(
            org_id=org_id,
            email=payload.email,
            role=payload.role,
            invited_by=email,
            business_name=biz_name,
            tier=tier,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/members")
async def list_members(request: Request):
    """List all members of the caller's org."""
    require_role(request, "viewer")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_auth_service()
    members = await svc.list_org_members(org_id)
    return {"members": members, "count": len(members)}


@router.put("/members/{member_email}/role")
async def update_member_role(member_email: str, payload: RoleUpdatePayload, request: Request):
    """Change a team member's role (owner/admin only)."""
    require_role(request, "admin")
    org_id = getattr(request.state, "org_id", "")
    role = getattr(request.state, "role", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_auth_service()
    try:
        result = await svc.update_member_role(org_id, member_email, payload.role, role)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/members/{member_email}")
async def remove_member(member_email: str, request: Request):
    """Remove a member from the org (owner only)."""
    require_role(request, "owner")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_auth_service()
    try:
        result = await svc.remove_member(org_id, member_email)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
