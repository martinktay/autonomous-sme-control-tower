"""
Authentication service — JWT-based auth with DynamoDB user storage.

Handles user registration, login, password hashing, and JWT token
generation/validation. Uses DynamoDB for user persistence (keyed by email).
"""

import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import boto3
from jose import jwt, JWTError

from app.config import get_settings
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-SHA256 — no extra deps needed)
# ---------------------------------------------------------------------------

def _hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password with PBKDF2-SHA256. Returns (hash_hex, salt_hex)."""
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
    return dk.hex(), salt


def _verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify a password against stored hash + salt."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
    return hmac.compare_digest(dk.hex(), stored_hash)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_hours: int = 0) -> str:
    """Create a signed JWT access token."""
    exp_hours = expires_hours or settings.jwt_expiry_hours
    expire = datetime.now(timezone.utc) + timedelta(hours=exp_hours)
    payload = {**data, "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT. Returns claims dict or None."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        logger.debug("JWT decode failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Auth service (DynamoDB-backed)
# ---------------------------------------------------------------------------

class AuthService:
    """Manages user registration, login, and token operations."""

    def __init__(self):
        ddb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        self.users_table = ddb.Table(settings.users_table)

    # ---- Registration ----

    async def register(
        self,
        email: str,
        password: str,
        full_name: str = "",
        business_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new user. Creates an org_id automatically."""
        email = email.strip().lower()

        # Check if email already exists
        existing = self._get_user_by_email(email)
        if existing:
            raise ValueError("An account with this email already exists")

        user_id = generate_id("user")
        org_id = generate_id("org")
        pw_hash, pw_salt = _hash_password(password)
        now = datetime.now(timezone.utc).isoformat()

        item = {
            "email": email,
            "user_id": user_id,
            "org_id": org_id,
            "full_name": full_name,
            "business_name": business_name or "",
            "role": "owner",
            "tier": "starter",
            "pw_hash": pw_hash,
            "pw_salt": pw_salt,
            "is_active": True,
            "created_at": now,
            "last_login": now,
        }
        self.users_table.put_item(Item=item)
        logger.info("Registered user %s for org %s", user_id, org_id)

        token = create_access_token({
            "sub": user_id,
            "email": email,
            "org_id": org_id,
            "role": "owner",
            "tier": "starter",
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expiry_hours * 3600,
            "user_id": user_id,
            "org_id": org_id,
            "email": email,
            "full_name": full_name,
            "role": "owner",
            "business_name": business_name or "",
            "tier": "starter",
        }

    # ---- Login ----

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return JWT."""
        email = email.strip().lower()
        user = self._get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not _verify_password(password, user["pw_hash"], user["pw_salt"]):
            raise ValueError("Invalid email or password")

        if not user.get("is_active", True):
            raise ValueError("Account is deactivated")

        # Update last_login
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET last_login = :t",
                ExpressionAttributeValues={":t": datetime.now(timezone.utc).isoformat()},
            )
        except Exception:
            pass  # non-critical

        token = create_access_token({
            "sub": user["user_id"],
            "email": email,
            "org_id": user["org_id"],
            "role": user.get("role", "owner"),
            "tier": user.get("tier", "starter"),
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expiry_hours * 3600,
            "user_id": user["user_id"],
            "org_id": user["org_id"],
            "email": email,
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "owner"),
            "business_name": user.get("business_name", ""),
            "tier": user.get("tier", "starter"),
        }

    # ---- Profile ----

    async def get_me(self, user_id: str, email: str) -> Optional[Dict[str, Any]]:
        """Return user profile (no password fields)."""
        user = self._get_user_by_email(email)
        if not user or user["user_id"] != user_id:
            return None
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "org_id": user["org_id"],
            "full_name": user.get("full_name", ""),
            "role": user.get("role", "owner"),
            "business_name": user.get("business_name", ""),
            "is_active": user.get("is_active", True),
            "created_at": user.get("created_at", ""),
        }

    # ---- Internal helpers ----

    def _get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch user record by email (partition key)."""
        try:
            resp = self.users_table.get_item(Key={"email": email})
            return resp.get("Item")
        except Exception as exc:
            logger.error("DynamoDB get_item failed: %s", exc)
            return None

    # ---- Admin operations ----

    async def list_users(self) -> list[Dict[str, Any]]:
        """List all users (admin only). Returns list without password fields."""
        try:
            resp = self.users_table.scan(
                ProjectionExpression="user_id, email, org_id, full_name, business_name, #r, is_active, created_at, last_login, tier",
                ExpressionAttributeNames={"#r": "role"},
            )
            return resp.get("Items", [])
        except Exception as exc:
            logger.error("Failed to list users: %s", exc)
            return []

    async def update_user_role(self, email: str, new_role: str) -> Optional[Dict[str, Any]]:
        """Change a user's role (admin only)."""
        valid_roles = {"super_admin", "owner", "admin", "member", "viewer"}
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET #r = :r",
                ExpressionAttributeNames={"#r": "role"},
                ExpressionAttributeValues={":r": new_role},
            )
            return {"email": email, "role": new_role}
        except Exception as exc:
            logger.error("Failed to update role: %s", exc)
            raise ValueError("Failed to update user role")

    async def update_user_tier(self, email: str, tier: str) -> Optional[Dict[str, Any]]:
        """Change a user's pricing tier (admin only)."""
        valid_tiers = {"starter", "growth", "business", "enterprise"}
        if tier not in valid_tiers:
            raise ValueError(f"Invalid tier. Must be one of: {valid_tiers}")
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET tier = :t",
                ExpressionAttributeValues={":t": tier},
            )
            return {"email": email, "tier": tier}
        except Exception as exc:
            logger.error("Failed to update tier: %s", exc)
            raise ValueError("Failed to update user tier")

    async def deactivate_user(self, email: str) -> Dict[str, Any]:
        """Deactivate a user account (admin only)."""
        try:
            self.users_table.update_item(
                Key={"email": email},
                UpdateExpression="SET is_active = :a",
                ExpressionAttributeValues={":a": False},
            )
            return {"email": email, "is_active": False}
        except Exception as exc:
            logger.error("Failed to deactivate user: %s", exc)
            raise ValueError("Failed to deactivate user")


_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Singleton accessor."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
