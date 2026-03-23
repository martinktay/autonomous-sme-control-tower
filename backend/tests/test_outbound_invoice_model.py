"""Unit tests for Outbound Invoice models."""

import pytest
from pydantic import ValidationError
from app.models.outbound_invoice import (
    InvoiceLineItem, OutboundInvoiceCreate, OutboundInvoice,
)


class TestInvoiceLineItem:
    def test_valid_line_item(self):
        item = InvoiceLineItem(description="Rice 50kg", quantity=2, unit_price=25000)
        assert item.amount == 50000.0

    def test_auto_calculates_amount(self):
        item = InvoiceLineItem(description="Flour", quantity=3, unit_price=10000)
        assert item.amount == 30000.0

    def test_explicit_amount_preserved_if_nonzero(self):
        item = InvoiceLineItem(description="Custom", quantity=1, unit_price=100, amount=150)
        assert item.amount == 150

    def test_empty_description_rejected(self):
        with pytest.raises(ValidationError):
            InvoiceLineItem(description="", quantity=1, unit_price=100)

    def test_zero_quantity_rejected(self):
        with pytest.raises(ValidationError):
            InvoiceLineItem(description="Item", quantity=0, unit_price=100)

    def test_negative_unit_price_rejected(self):
        with pytest.raises(ValidationError):
            InvoiceLineItem(description="Item", quantity=1, unit_price=-50)


class TestOutboundInvoiceCreate:
    def test_valid_create(self):
        inv = OutboundInvoiceCreate(
            customer_name="Mama Nkechi",
            line_items=[InvoiceLineItem(description="Garri", quantity=5, unit_price=2000)],
        )
        assert inv.currency == "NGN"
        assert inv.due_days == 30

    def test_empty_customer_name_rejected(self):
        with pytest.raises(ValidationError):
            OutboundInvoiceCreate(
                customer_name="",
                line_items=[InvoiceLineItem(description="X", quantity=1, unit_price=100)],
            )

    def test_empty_line_items_rejected(self):
        with pytest.raises(ValidationError):
            OutboundInvoiceCreate(customer_name="Test", line_items=[])

    def test_tax_rate_bounds(self):
        with pytest.raises(ValidationError):
            OutboundInvoiceCreate(
                customer_name="Test",
                line_items=[InvoiceLineItem(description="X", quantity=1, unit_price=100)],
                tax_rate=150,
            )

    def test_due_days_bounds(self):
        with pytest.raises(ValidationError):
            OutboundInvoiceCreate(
                customer_name="Test",
                line_items=[InvoiceLineItem(description="X", quantity=1, unit_price=100)],
                due_days=0,
            )


class TestOutboundInvoice:
    def test_valid_statuses(self):
        for status in ["draft", "sent", "viewed", "paid", "overdue", "cancelled"]:
            inv = OutboundInvoice(
                invoice_id="inv-1", org_id="org-1", invoice_number="INV-001",
                customer_name="Test", status=status,
            )
            assert inv.status == status

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            OutboundInvoice(
                invoice_id="inv-1", org_id="org-1", invoice_number="INV-001",
                customer_name="Test", status="deleted",
            )

    def test_defaults(self):
        inv = OutboundInvoice(
            invoice_id="inv-1", org_id="org-1", invoice_number="INV-001",
            customer_name="Test",
        )
        assert inv.currency == "NGN"
        assert inv.status == "draft"
        assert inv.total == 0
