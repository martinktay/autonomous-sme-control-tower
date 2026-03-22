"""Unified transaction model for revenue, expense, and payment tracking."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Transaction(BaseModel):
    """Unified transaction record — covers revenue, expense, payment, transfer."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    business_id: str = Field(..., description="Business identifier (org_id)")
    branch_id: Optional[str] = Field(None, description="Branch if multi-location")
    transaction_type: str = Field(..., description="revenue | expense | payment | transfer")
    category: Optional[str] = Field(None, description="AI-classified or user-set category")
    amount: float = Field(..., gt=0, description="Transaction amount (positive)")
    currency: str = Field(default="NGN", max_length=3)
    counterparty_id: Optional[str] = None
    counterparty_name: Optional[str] = None
    description: Optional[str] = None
    date: datetime = Field(..., description="Transaction date")
    payment_status: str = Field(default="pending", description="pending | paid | overdue | partial")
    source_document_id: Optional[str] = None
    extension_attrs: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)

    @field_validator("transaction_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid = {"revenue", "expense", "payment", "transfer"}
        if v not in valid:
            raise ValueError(f"transaction_type must be one of: {valid}")
        return v

    @field_validator("payment_status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"pending", "paid", "overdue", "partial"}
        if v not in valid:
            raise ValueError(f"payment_status must be one of: {valid}")
        return v


class TransactionCreate(BaseModel):
    """Request body for creating a transaction."""

    branch_id: Optional[str] = None
    transaction_type: str
    category: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "NGN"
    counterparty_name: Optional[str] = None
    description: Optional[str] = None
    date: datetime
    payment_status: str = "pending"
