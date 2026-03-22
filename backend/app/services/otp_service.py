"""
OTP service — generates, stores, and verifies 6-digit email OTP codes.

Uses DynamoDB for OTP storage with TTL-based expiry (10 minutes).
Sends OTP emails via SES. Supports email verification and password reset flows.
"""

import hashlib
import logging
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings
from app.services.ses_service import get_ses_service

logger = logging.getLogger(__name__)
settings = get_settings()

OTP_EXPIRY_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def _generate_otp() -> str:
    """Generate a cryptographically secure 6-digit OTP."""
    return f"{secrets.randbelow(900000) + 100000}"


def _hash_otp(code: str) -> str:
    """Hash OTP for storage (never store plaintext)."""
    return hashlib.sha256(code.encode()).hexdigest()


class OTPService:
    """Manages OTP generation, storage, verification, and email delivery."""

    def __init__(self):
        ddb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        self.users_table = ddb.Table(settings.users_table)

    async def send_verification_otp(self, email: str) -> Dict[str, Any]:
        """Generate and send an email verification OTP."""
        email = email.strip().lower()
        code = _generate_otp()
        self._store_otp(email, code, purpose="email_verification")
        self._send_otp_email(email, code, purpose="email_verification")
        logger.info("Verification OTP sent to %s", email)
        return {"email": email, "status": "otp_sent", "expires_in_minutes": OTP_EXPIRY_MINUTES}

    async def send_password_reset_otp(self, email: str) -> Dict[str, Any]:
        """Generate and send a password reset OTP."""
        email = email.strip().lower()
        # Check user exists
        user = self._get_user(email)
        if not user:
            # Don't reveal whether email exists — return success either way
            logger.info("Password reset requested for non-existent email %s", email)
            return {"email": email, "status": "otp_sent", "expires_in_minutes": OTP_EXPIRY_MINUTES}

        code = _generate_otp()
        self._store_otp(email, code, purpose="password_reset")
        self._send_otp_email(email, code, purpose="password_reset")
        logger.info("Password reset OTP sent to %s", email)
        return {"email": email, "status": "otp_sent", "expires_in_minutes": OTP_EXPIRY_MINUTES}

    async def verify_otp(self, email: str, code: str, purpose: str = "email_verification") -> bool:
        """Verify an OTP code. Returns True if valid."""
        email = email.strip().lower()
        user = self._get_user(email)
        if not user:
            return False

        otp_data = user.get("otp_data", {})
        if not otp_data:
            return False

        # Check purpose matches
        if otp_data.get("purpose") != purpose:
            return False

        # Check expiry
        expires_at = otp_data.get("expires_at", "")
        if expires_at:
            exp = datetime.fromisoformat(expires_at)
            if datetime.now(timezone.utc) > exp:
                self._clear_otp(email)
                return False

        # Check attempts
        attempts = int(otp_data.get("attempts", 0))
        if attempts >= OTP_MAX_ATTEMPTS:
            self._clear_otp(email)
            return False

        # Increment attempts
        self._increment_attempts(email, attempts + 1)

        # Verify hash
        stored_hash = otp_data.get("code_hash", "")
        if _hash_otp(code) != stored_hash:
            return False

        # OTP valid — clear it and mark verified if email verification
        self._clear_otp(email)
        if purpose == "email_verification":
            self._mark_email_verified(email)

        return True

    async def resend_otp(self, email: str, purpose: str = "email_verification") -> Dict[str, Any]:
        """Resend OTP (generates a new code)."""
        if purpose == "password_reset":
            return await self.send_password_reset_otp(email)
        return await self.send_verification_otp(email)

    # ── Internal helpers ──

    def _store_otp(self, email: str, code: str, purpose: str) -> None:
        """Store hashed OTP in user record."""
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat()
        otp_data = {
            "code_hash": _hash_otp(code),
            "purpose": purpose,
            "expires_at": expires_at,
            "attempts": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET otp_data = :o",
                ExpressionAttributeValues={":o": otp_data},
            )
        except ClientError as exc:
            logger.error("Failed to store OTP for %s: %s", email, exc)
            raise ValueError("Failed to generate verification code")

    def _clear_otp(self, email: str) -> None:
        """Remove OTP data from user record."""
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="REMOVE otp_data",
            )
        except ClientError:
            pass

    def _increment_attempts(self, email: str, count: int) -> None:
        """Increment OTP attempt counter."""
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET otp_data.attempts = :a",
                ExpressionAttributeValues={":a": count},
            )
        except ClientError:
            pass

    def _mark_email_verified(self, email: str) -> None:
        """Set email_verified = True on user record."""
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET email_verified = :v",
                ExpressionAttributeValues={":v": True},
            )
            logger.info("Email verified for %s", email)
        except ClientError as exc:
            logger.error("Failed to mark email verified for %s: %s", email, exc)

    def _get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch user record by email."""
        try:
            resp = self.users_table.get_item(Key={"email": email})
            return resp.get("Item")
        except ClientError:
            return None

    def _send_otp_email(self, email: str, code: str, purpose: str) -> None:
        """Send OTP code via SES."""
        ses = get_ses_service()
        if purpose == "password_reset":
            subject = "SME Control Tower — Password Reset Code"
            body_text = (
                f"Your password reset code is: {code}\n\n"
                f"This code expires in {OTP_EXPIRY_MINUTES} minutes.\n"
                f"If you did not request this, please ignore this email.\n\n"
                f"— SME Control Tower"
            )
            body_html = (
                f"<div style='font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px'>"
                f"<h2 style='color:#1a1a1a'>Password Reset</h2>"
                f"<p>Your password reset code is:</p>"
                f"<div style='font-size:32px;font-weight:bold;letter-spacing:8px;text-align:center;"
                f"background:#f4f4f5;padding:16px;border-radius:8px;margin:16px 0'>{code}</div>"
                f"<p style='color:#666;font-size:14px'>This code expires in {OTP_EXPIRY_MINUTES} minutes.</p>"
                f"<p style='color:#999;font-size:12px'>If you did not request this, ignore this email.</p>"
                f"</div>"
            )
        else:
            subject = "SME Control Tower — Verify Your Email"
            body_text = (
                f"Welcome to SME Control Tower!\n\n"
                f"Your verification code is: {code}\n\n"
                f"Enter this code to complete your registration.\n"
                f"This code expires in {OTP_EXPIRY_MINUTES} minutes.\n\n"
                f"— SME Control Tower"
            )
            body_html = (
                f"<div style='font-family:sans-serif;max-width:480px;margin:0 auto;padding:24px'>"
                f"<h2 style='color:#1a1a1a'>Welcome to SME Control Tower</h2>"
                f"<p>Your verification code is:</p>"
                f"<div style='font-size:32px;font-weight:bold;letter-spacing:8px;text-align:center;"
                f"background:#f4f4f5;padding:16px;border-radius:8px;margin:16px 0'>{code}</div>"
                f"<p style='color:#666;font-size:14px'>Enter this code to complete your registration.</p>"
                f"<p style='color:#666;font-size:14px'>This code expires in {OTP_EXPIRY_MINUTES} minutes.</p>"
                f"</div>"
            )

        try:
            ses.send_email(to=email, subject=subject, body_text=body_text, body_html=body_html)
        except Exception as exc:
            logger.error("Failed to send OTP email to %s: %s", email, exc)
            # Don't fail registration if SES is not configured — log and continue
            # In production, SES must be configured for this to work


_otp_service: Optional[OTPService] = None


def get_otp_service() -> OTPService:
    """Singleton accessor."""
    global _otp_service
    if _otp_service is None:
        _otp_service = OTPService()
    return _otp_service
