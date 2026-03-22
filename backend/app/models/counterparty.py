"""Counterparty model for supplier and customer tracking."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Counterparty(BaseModel):
    """A supplier or customer linked to a business."""

    counterparty_id: str = Field(..., description="Unique counterparty identifier")
    business_id: str = Field(..., description="Business identifier")
    name: str = Field(..., min_length=1, max_length=300)
    counterparty_type: str = Field(..., description="supplier | customer")
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    balance_owed: float = Field(default=0.0, description="What we owe them")
    balance_owing: float = Field(default=0.0, description="What they owe us")
    last_transaction_date: Optional[datetime] = None
    extension_attrs: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)

    @field_validator("counterparty_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"supplier", "customer"}
        if v not in valid:
            raise ValueError(f"counterparty_type must be one of: {valid}")
        return v


class CounterpartyCreate(BaseModel):
    """Request body for creating a counterparty."""

    name: str = Field(..., min_length=1, max_length=300)
    counterparty_type: str
    phone: Optional[str] = None
    email: Optional[str] = None
