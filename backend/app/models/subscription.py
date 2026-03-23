"""
Subscription model — tracks payment subscriptions for SME organisations.

Supports multiple payment methods common across Africa and globally:
- Paystack (cards, bank transfer, USSD — Nigeria, Ghana, South Africa, Kenya)
- Flutterwave (cards, mobile money, bank transfer — 30+ African countries)
- Bank transfer (direct/manual — all countries)
- USSD (feature phone payments — Nigeria, Ghana, Kenya)
- Mobile money (M-Pesa, MTN MoMo, Airtel Money — East/West Africa)
- Stripe (international cards — global)
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


VALID_PAYMENT_METHODS = {
    "paystack",
    "flutterwave",
    "bank_transfer",
    "ussd",
    "mobile_money",
    "stripe",
    "free",
}

VALID_STATUSES = {
    "active",
    "cancelled",
    "expired",
    "past_due",
    "trialing",
    "pending",
}


class Subscription(BaseModel):
    """Active subscription record for an organisation."""
    subscription_id: str
    org_id: str
    tier: str = Field(default="starter")
    payment_method: str = Field(default="free")
    payment_provider_ref: str = Field(default="", description="External reference from Paystack/Flutterwave/Stripe")
    status: str = Field(default="active")
    currency: str = Field(default="NGN")
    amount: float = Field(default=0, ge=0)
    billing_cycle: str = Field(default="monthly", description="monthly or annual")
    current_period_start: str = ""
    current_period_end: str = ""
    cancelled_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: _utc_now().isoformat())
    updated_at: str = Field(default_factory=lambda: _utc_now().isoformat())

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        if v not in VALID_PAYMENT_METHODS:
            raise ValueError(f"Payment method must be one of: {VALID_PAYMENT_METHODS}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {VALID_STATUSES}")
        return v

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        valid = {"starter", "growth", "business", "enterprise"}
        if v not in valid:
            raise ValueError(f"Tier must be one of: {valid}")
        return v


class SubscriptionCreate(BaseModel):
    """Payload for initiating a subscription."""
    tier: str
    payment_method: str
    billing_cycle: str = "monthly"
    currency: str = "NGN"

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        valid = {"growth", "business", "enterprise"}
        if v not in valid:
            raise ValueError("Cannot subscribe to starter — it is free")
        return v

    @field_validator("payment_method")
    @classmethod
    def validate_payment_method(cls, v: str) -> str:
        if v not in VALID_PAYMENT_METHODS:
            raise ValueError(f"Payment method must be one of: {VALID_PAYMENT_METHODS}")
        return v
