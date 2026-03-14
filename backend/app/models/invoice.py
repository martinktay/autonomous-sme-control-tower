from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Invoice(BaseModel):
    """Invoice data model for operational signals"""
    
    invoice_id: str = Field(..., description="Unique invoice identifier")
    org_id: str = Field(..., description="Organization identifier")
    vendor_name: str = Field(..., description="Vendor or supplier name")
    amount: float = Field(..., gt=0, description="Invoice amount (must be positive)")
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")
    due_date: datetime = Field(..., description="Payment due date")
    description: str = Field(..., description="Invoice description or purpose")
    status: str = Field(default="pending", description="Invoice status: pending, paid, overdue")
    created_at: datetime = Field(default_factory=_utc_now, description="Record creation timestamp")
    s3_key: Optional[str] = Field(None, description="S3 object key for invoice document")
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code format"""
        if len(v) != 3 or not v.isupper():
            raise ValueError('Currency must be a 3-letter uppercase ISO 4217 code')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate invoice status"""
        valid_statuses = {'pending', 'paid', 'overdue', 'cancelled'}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
