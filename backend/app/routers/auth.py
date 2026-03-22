"""
Authentication router — register, login, profile, OTP verification, password reset.

Public endpoints (no JWT required):
  POST /api/auth/register
  POST /api/auth/login
  POST /api/auth/otp/send
  POST /api/auth/otp/verify
  POST /api/auth/otp/resend
  POST /api/auth/password-reset/request
  POST /api/auth/password-reset/confirm

Protected endpoints (JWT required):
  GET  /api/auth/me
"""

import logging
from fastapi import APIRouter, HTTPException, Request

from app.models.user import (
    UserCreate, UserLogin, TokenResponse,
    OTPRequest, OTPVerify,
    PasswordResetRequest, PasswordResetConfirm,
)
from app.services.auth_service import get_auth_service
from app.services.otp_service import get_otp_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserCreate):
    """Create a new user account, send verification OTP, and return a JWT."""
    svc = get_auth_service()
    try:
        result = await svc.register(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            phone=payload.phone,
            business_name=payload.business_name,
            business_type=payload.business_type,
        )
        # Send verification OTP (non-blocking — don't fail registration if SES fails)
        try:
            otp_svc = get_otp_service()
            await otp_svc.send_verification_otp(payload.email)
        except Exception as exc:
            logger.warning("OTP send failed during registration for %s: %s", payload.email, exc)

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


# ── OTP Verification ──


@router.post("/otp/send")
async def send_otp(payload: OTPRequest):
    """Send a verification OTP to the user's email."""
    otp_svc = get_otp_service()
    try:
        result = await otp_svc.send_verification_otp(payload.email)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to send OTP")
        raise HTTPException(status_code=500, detail="Failed to send verification code")


@router.post("/otp/verify")
async def verify_otp(payload: OTPVerify):
    """Verify an email OTP code."""
    otp_svc = get_otp_service()
    try:
        valid = await otp_svc.verify_otp(payload.email, payload.code, purpose="email_verification")
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
        return {"email": payload.email, "verified": True}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("OTP verification failed")
        raise HTTPException(status_code=500, detail="Verification failed")


@router.post("/otp/resend")
async def resend_otp(payload: OTPRequest):
    """Resend a verification OTP."""
    otp_svc = get_otp_service()
    try:
        result = await otp_svc.resend_otp(payload.email, purpose="email_verification")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Failed to resend OTP")
        raise HTTPException(status_code=500, detail="Failed to resend verification code")


# ── Password Reset ──


@router.post("/password-reset/request")
async def request_password_reset(payload: PasswordResetRequest):
    """Send a password reset OTP to the user's email."""
    otp_svc = get_otp_service()
    try:
        result = await otp_svc.send_password_reset_otp(payload.email)
        return result
    except Exception as exc:
        logger.exception("Password reset request failed")
        # Always return success to avoid email enumeration
        return {"email": payload.email, "status": "otp_sent", "expires_in_minutes": 10}


@router.post("/password-reset/confirm")
async def confirm_password_reset(payload: PasswordResetConfirm):
    """Verify OTP and set new password."""
    otp_svc = get_otp_service()
    auth_svc = get_auth_service()
    try:
        valid = await otp_svc.verify_otp(payload.email, payload.code, purpose="password_reset")
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid or expired reset code")
        await auth_svc.reset_password(payload.email, payload.new_password)
        return {"email": payload.email, "status": "password_reset_complete"}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.exception("Password reset confirmation failed")
        raise HTTPException(status_code=500, detail="Password reset failed")
