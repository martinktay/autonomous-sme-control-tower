from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class LineItem(BaseModel):
    """Invoice line item"""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: float


class Invoice(BaseModel):
    """Extracted invoice data"""
    
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = "USD"
    line_items: List[LineItem] = Field(default_factory=list)
    payment_terms: Optional[str] = None
    tax_amount: Optional[float] = None
