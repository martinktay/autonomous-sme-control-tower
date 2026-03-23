"""
Invoice service — CRUD for outbound invoices (QuickBooks-style).

Handles invoice creation, numbering, status updates, and payment tracking.
All records scoped by org_id for multi-tenant isolation.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from functools import lru_cache

from app.config import get_settings
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()


class InvoiceService:
    """Service for managing outbound invoices."""

    def __init__(self):
        import boto3
        self.ddb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        self.table = self.ddb.Table(settings.outbound_invoices_table)

    def _next_invoice_number(self, org_id: str) -> str:
        """Generate next sequential invoice number for the org."""
        try:
            resp = self.table.query(
                KeyConditionExpression="org_id = :oid",
                ExpressionAttributeValues={":oid": org_id},
                Select="COUNT",
            )
            count = resp.get("Count", 0)
        except Exception:
            count = 0
        return f"INV-{count + 1:05d}"

    def create_invoice(self, org_id: str, data: Dict[str, Any], business_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new outbound invoice."""
        now = datetime.now(timezone.utc).isoformat()
        invoice_id = generate_id("invoice")
        invoice_number = self._next_invoice_number(org_id)

        line_items = data.get("line_items", [])
        subtotal = round(sum(item.get("amount", item.get("quantity", 0) * item.get("unit_price", 0)) for item in line_items), 2)
        tax_rate = data.get("tax_rate", 0)
        tax_amount = round(subtotal * tax_rate / 100, 2)
        discount = data.get("discount", 0)
        total = round(subtotal + tax_amount - discount, 2)

        due_days = data.get("due_days", 30)
        due_date = (datetime.now(timezone.utc) + timedelta(days=due_days)).strftime("%Y-%m-%d")

        biz = business_info or {}
        item = {
            "org_id": org_id,
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "customer_name": data["customer_name"],
            "customer_email": data.get("customer_email", ""),
            "customer_phone": data.get("customer_phone", ""),
            "customer_address": data.get("customer_address", ""),
            "line_items": line_items,
            "subtotal": str(subtotal),
            "tax_rate": str(tax_rate),
            "tax_amount": str(tax_amount),
            "discount": str(discount),
            "total": str(total),
            "currency": data.get("currency", "NGN"),
            "status": "draft",
            "due_date": due_date,
            "issued_date": now[:10],
            "notes": data.get("notes", ""),
            "payment_method": data.get("payment_method", ""),
            "business_name": biz.get("business_name", ""),
            "business_email": biz.get("email", ""),
            "business_phone": biz.get("phone", ""),
            "created_at": now,
            "updated_at": now,
        }

        self.table.put_item(Item=item)
        logger.info("Created invoice %s (%s) for org %s", invoice_id, invoice_number, org_id)
        return item

    def list_invoices(self, org_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List all outbound invoices for an org."""
        try:
            resp = self.table.query(
                KeyConditionExpression="org_id = :oid",
                ExpressionAttributeValues={":oid": org_id},
                ScanIndexForward=False,
                Limit=limit,
            )
            return resp.get("Items", [])
        except Exception as e:
            logger.error("Failed to list invoices for org %s: %s", org_id, e)
            return []

    def get_invoice(self, org_id: str, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get a single invoice by ID."""
        try:
            resp = self.table.get_item(Key={"org_id": org_id, "invoice_id": invoice_id})
            return resp.get("Item")
        except Exception as e:
            logger.error("Failed to get invoice %s: %s", invoice_id, e)
            return None

    def get_invoice_public(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get an invoice by ID without requiring org_id (for public payment links).
        Uses a scan with filter — acceptable for single-item lookups.
        """
        try:
            resp = self.table.scan(
                FilterExpression="invoice_id = :iid",
                ExpressionAttributeValues={":iid": invoice_id},
                Limit=1,
            )
            items = resp.get("Items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error("Failed to get public invoice %s: %s", invoice_id, e)
            return None

    def update_status(self, org_id: str, invoice_id: str, status: str, payment_ref: str = None) -> Optional[Dict[str, Any]]:
        """Update invoice status (e.g. sent, paid, cancelled)."""
        now = datetime.now(timezone.utc).isoformat()
        update_expr = "SET #s = :status, updated_at = :now"
        expr_values: Dict[str, Any] = {":status": status, ":now": now}
        expr_names = {"#s": "status"}

        if status == "paid" and payment_ref:
            update_expr += ", payment_reference = :pref, paid_date = :pd"
            expr_values[":pref"] = payment_ref
            expr_values[":pd"] = now[:10]

        try:
            resp = self.table.update_item(
                Key={"org_id": org_id, "invoice_id": invoice_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ExpressionAttributeNames=expr_names,
                ReturnValues="ALL_NEW",
            )
            return resp.get("Attributes")
        except Exception as e:
            logger.error("Failed to update invoice %s status: %s", invoice_id, e)
            return None

    def get_invoice_summary(self, org_id: str) -> Dict[str, Any]:
        """Get invoice summary stats for the org."""
        invoices = self.list_invoices(org_id, limit=500)
        total_invoiced = sum(float(inv.get("total", 0)) for inv in invoices)
        total_paid = sum(float(inv.get("total", 0)) for inv in invoices if inv.get("status") == "paid")
        total_outstanding = sum(float(inv.get("total", 0)) for inv in invoices if inv.get("status") in ("draft", "sent", "viewed"))
        total_overdue = sum(float(inv.get("total", 0)) for inv in invoices if inv.get("status") == "overdue")

        return {
            "total_invoices": len(invoices),
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_outstanding": total_outstanding,
            "total_overdue": total_overdue,
            "currency": invoices[0].get("currency", "NGN") if invoices else "NGN",
            "by_status": {
                s: len([i for i in invoices if i.get("status") == s])
                for s in ("draft", "sent", "viewed", "paid", "overdue", "cancelled")
            },
        }


@lru_cache()
def get_invoice_service() -> InvoiceService:
    return InvoiceService()
