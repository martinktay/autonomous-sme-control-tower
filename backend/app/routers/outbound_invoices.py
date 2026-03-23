"""
Outbound invoice router — create, list, view, and manage invoices.

Supports QuickBooks-style invoice generation with shareable payment links.
  POST   /api/outbound-invoices          — create a new invoice
  GET    /api/outbound-invoices          — list invoices for the org
  GET    /api/outbound-invoices/summary  — invoice summary stats
  GET    /api/outbound-invoices/{id}     — get a single invoice
  PUT    /api/outbound-invoices/{id}/status — update invoice status
  GET    /api/outbound-invoices/{id}/public — public view (no auth, for payment links)
"""

import logging
from typing import Literal
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional

from app.middleware.auth import require_role
from app.services.invoice_service import get_invoice_service
from app.models.outbound_invoice import InvoiceLineItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/outbound-invoices", tags=["outbound-invoices"])


class CreateInvoicePayload(BaseModel):
    customer_name: str = Field(..., min_length=1)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    line_items: List[InvoiceLineItem] = Field(..., min_length=1)
    currency: str = "NGN"
    tax_rate: float = Field(default=0, ge=0, le=100)
    discount: float = Field(default=0, ge=0)
    notes: Optional[str] = None
    due_days: int = Field(default=30, ge=1, le=365)
    payment_method: Optional[str] = None


class StatusUpdatePayload(BaseModel):
    status: Literal["draft", "sent", "viewed", "paid", "overdue", "cancelled"]
    payment_reference: Optional[str] = None


@router.post("")
async def create_invoice(payload: CreateInvoicePayload, request: Request):
    """Create a new outbound invoice (owner/admin only)."""
    require_role(request, "member")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_invoice_service()

    # Get business info from the user's JWT claims for invoice header
    business_info = {
        "business_name": getattr(request.state, "business_name", ""),
        "email": getattr(request.state, "email", ""),
        "phone": "",
    }

    data = payload.model_dump()
    # Convert line items to plain dicts for DynamoDB
    data["line_items"] = [item.model_dump() for item in payload.line_items]

    invoice = svc.create_invoice(org_id, data, business_info)
    return {"invoice": invoice, "message": "Invoice created successfully"}


@router.get("")
async def list_invoices(request: Request):
    """List all outbound invoices for the org."""
    require_role(request, "viewer")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_invoice_service()
    invoices = svc.list_invoices(org_id)
    return {"invoices": invoices, "count": len(invoices)}


@router.get("/summary")
async def invoice_summary(request: Request):
    """Get invoice summary stats for the org."""
    require_role(request, "viewer")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_invoice_service()
    return svc.get_invoice_summary(org_id)


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str, request: Request):
    """Get a single invoice by ID."""
    require_role(request, "viewer")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_invoice_service()
    invoice = svc.get_invoice(org_id, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"invoice": invoice}


@router.put("/{invoice_id}/status")
async def update_invoice_status(invoice_id: str, payload: StatusUpdatePayload, request: Request):
    """Update invoice status (e.g. mark as sent, paid, cancelled)."""
    require_role(request, "member")
    org_id = getattr(request.state, "org_id", "")
    if not org_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    svc = get_invoice_service()
    result = svc.update_status(org_id, invoice_id, payload.status, payload.payment_reference)
    if not result:
        raise HTTPException(status_code=404, detail="Invoice not found or update failed")
    return {"invoice": result, "message": f"Invoice status updated to {payload.status}"}


@router.get("/{invoice_id}/public")
async def get_invoice_public(invoice_id: str):
    """Public invoice view — no auth required. Used for shareable payment links."""
    svc = get_invoice_service()
    invoice = svc.get_invoice_public(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Return only safe fields for public view
    return {
        "invoice_id": invoice.get("invoice_id"),
        "invoice_number": invoice.get("invoice_number"),
        "business_name": invoice.get("business_name"),
        "business_email": invoice.get("business_email"),
        "business_phone": invoice.get("business_phone"),
        "customer_name": invoice.get("customer_name"),
        "line_items": invoice.get("line_items", []),
        "subtotal": invoice.get("subtotal"),
        "tax_rate": invoice.get("tax_rate"),
        "tax_amount": invoice.get("tax_amount"),
        "discount": invoice.get("discount"),
        "total": invoice.get("total"),
        "currency": invoice.get("currency"),
        "status": invoice.get("status"),
        "due_date": invoice.get("due_date"),
        "issued_date": invoice.get("issued_date"),
        "notes": invoice.get("notes"),
    }
