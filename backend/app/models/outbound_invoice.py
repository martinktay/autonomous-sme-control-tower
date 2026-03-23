"""
Outbound invoice models — for generating invoices to customers (like QuickBooks).

Supports line items, tax, discounts, payment tracking, and shareable payment links.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InvoiceLineItem(BaseModel):
    """A single line item on an invoice."""
    description: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    amount: float = Field(default=0)

    def model_post_init(self, __context) -> None:
        if self.amount == 0:
            self.amount = round(self.quantity * self.unit_price, 2)


class OutboundInvoiceCreate(BaseModel):
    """Payload for creating a new outbound invoice."""
    customer_name: str = Field(..., min_length=1)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    line_items: List[InvoiceLineItem] = Field(..., min_length=1)
    currency: str = Field(default="NGN")
    tax_rate: float = Field(default=0, ge=0, le=100)
    discount: float = Field(default=0, ge=0)
    notes: Optional[str] = None
    due_days: int = Field(default=30, ge=1, le=365)
    payment_method: Optional[str] = None


class OutboundInvoice(BaseModel):
    """Full outbound invoice record stored in DynamoDB."""
    invoice_id: str
    org_id: str
    invoice_number: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    line_items: List[dict] = Field(default_factory=list)
    subtotal: float = 0
    tax_rate: float = 0
    tax_amount: float = 0
    discount: float = 0
    total: float = 0
    currency: str = "NGN"
    status: str = "draft"
    due_date: str = ""
    issued_date: str = ""
    paid_date: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_link: Optional[str] = None
    notes: Optional[str] = None
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"draft", "sent", "viewed", "paid", "overdue", "cancelled"}
        if v not in valid:
            raise ValueError(f"Status must be one of: {valid}")
        return v
