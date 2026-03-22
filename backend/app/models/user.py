"""User model for authentication and org membership."""

import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(BaseModel):
    """Registered user linked to an organisation."""
    user_id: str = Field(..., description="Cognito sub or unique user ID")
    email: str = Field(..., description="User email address")
    full_name: str = Field("", description="Display name")
    org_id: str = Field(..., description="Organisation the user belongs to")
    role: str = Field(default="owner", description="Role: owner, admin, member, viewer")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=_utc_now)
    last_login: Optional[datetime] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email address")
        return v.lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        valid = {"owner", "admin", "member", "viewer"}
        if v not in valid:
            raise ValueError(f"Role must be one of: {valid}")
        return v


class UserCreate(BaseModel):
    """Payload for user registration."""
    email: str
    full_name: str = ""
    password: str = Field(..., min_length=8, description="Min 8 chars")
    org_id: Optional[str] = None
    business_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email address")
        return v.lower()


class UserLogin(BaseModel):
    """Payload for login."""
    email: str
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str
    org_id: str
    email: str
    full_name: str = ""
    role: str = "owner"
    business_name: str = ""
