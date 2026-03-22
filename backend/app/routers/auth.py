"""
Authentication router — register, login, profile.

Public endpoints (no JWT required):
  POST /api/auth/register
  POST /api/auth/login

Protected endpoints (JWT required):
  GET  /api/auth/me
"""

import logging
from fastapi import APIRouter, HTTPException, Request

from app.models.user import UserCreate, UserLogin, TokenResponse
from app.services.auth_service import get_auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    """Create a new user account and return a JWT."""
    svc = get_auth_service()
    try:
        result = await svc.register(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            business_name=payload.business_name,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Registration failed")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    """Authenticate and return a JWT."""
    svc = get_auth_service()
    try:
        result = await svc.login(email=payload.email, password=payload.password)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as exc:
        logger.exception("Login failed")
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/me")
async def get_me(request: Request):
    """Return the current user's profile (requires valid JWT)."""
    user_id = getattr(request.state, "user_id", "")
    email = getattr(request.state, "email", "")
    if not user_id or not email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_auth_service()
    profile = await svc.get_me(user_id=user_id, email=email)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile
