"""
Tests for subscription service — pricing, payment methods, lifecycle.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.services.subscription_service import (
    SubscriptionService,
    TIER_PRICES_NGN,
    TIER_PRICES_USD,
    PAYMENT_METHODS_BY_REGION,
    PAYMENT_METHOD_LABELS,
)


@pytest.fixture
def mock_table():
    table = Mock()
    table.put_item = Mock(return_value=None)
    table.query = Mock(return_value={"Items": []})
    table.update_item = Mock(return_value={"Attributes": {"status": "active"}})
    table.scan = Mock(return_value={"Items": []})
    return table


@pytest.fixture
def svc(mock_table):
    with patch("app.services.subscription_service.SubscriptionService.__init__", lambda self: None):
        service = SubscriptionService()
        service.table = mock_table
        service.ddb = Mock()
        service.ddb.meta.client.exceptions.ConditionalCheckFailedException = type(
            "ConditionalCheckFailedException", (Exception,), {}
        )
        return service


# ── Payment Methods ──

class TestPaymentMethods:
    def test_nigeria_methods(self, svc):
        methods = svc.get_payment_methods("NG")
        ids = [m["id"] for m in methods]
        assert "paystack" in ids
        assert "flutterwave" in ids
        assert "ussd" in ids

    def test_kenya_methods(self, svc):
        methods = svc.get_payment_methods("KE")
        ids = [m["id"] for m in methods]
        assert "mobile_money" in ids
        assert "flutterwave" in ids
        assert "paystack" not in ids

    def test_uk_methods(self, svc):
        methods = svc.get_payment_methods("GB")
        ids = [m["id"] for m in methods]
        assert "stripe" in ids
        assert "paystack" not in ids

    def test_unknown_country_gets_default(self, svc):
        methods = svc.get_payment_methods("XX")
        ids = [m["id"] for m in methods]
        assert "stripe" in ids
        assert "flutterwave" in ids

    def test_case_insensitive(self, svc):
        methods = svc.get_payment_methods("ng")
        ids = [m["id"] for m in methods]
        assert "paystack" in ids

    def test_methods_have_labels(self, svc):
        methods = svc.get_payment_methods("NG")
        for m in methods:
            assert "label" in m
            assert len(m["label"]) > 0


# ── Pricing ──

class TestPricing:
    def test_ngn_pricing(self, svc):
        tiers = svc.get_pricing("NGN")
        assert len(tiers) == 4
        starter = next(t for t in tiers if t["tier"] == "starter")
        assert starter["monthly"] == 0
        assert starter["monthly_display"] == "Free"

    def test_usd_pricing(self, svc):
        tiers = svc.get_pricing("USD")
        growth = next(t for t in tiers if t["tier"] == "growth")
        assert growth["monthly"] == 9.50
        assert "$" in growth["monthly_display"]

    def test_annual_discount(self, svc):
        tiers = svc.get_pricing("NGN")
        growth = next(t for t in tiers if t["tier"] == "growth")
        # Annual = monthly * 10 (not 12), saving ~17%
        assert growth["annual"] == growth["monthly"] * 10

    def test_starter_always_free(self, svc):
        for currency in ["NGN", "USD"]:
            tiers = svc.get_pricing(currency)
            starter = next(t for t in tiers if t["tier"] == "starter")
            assert starter["monthly"] == 0
            assert starter["annual"] == 0


# ── Subscription Lifecycle ──

class TestSubscriptionLifecycle:
    def test_create_subscription(self, svc, mock_table):
        result = svc.create_subscription("org_123", "growth", "paystack", "monthly", "NGN")
        assert result["org_id"] == "org_123"
        assert result["tier"] == "growth"
        assert result["status"] == "pending"
        assert result["payment_method"] == "paystack"
        mock_table.put_item.assert_called_once()

    def test_create_annual_subscription(self, svc, mock_table):
        result = svc.create_subscription("org_123", "business", "stripe", "annual", "USD")
        assert result["billing_cycle"] == "annual"
        assert float(result["amount"]) == TIER_PRICES_USD["business"] * 10

    def test_activate_subscription(self, svc, mock_table):
        mock_table.update_item.return_value = {
            "Attributes": {"status": "active", "payment_provider_ref": "ref_123"}
        }
        result = svc.activate_subscription("org_123", "sub_123", "ref_123")
        assert result["status"] == "active"

    def test_activate_idempotent(self, svc, mock_table):
        """Activating an already-active subscription returns existing record."""
        exc_class = svc.ddb.meta.client.exceptions.ConditionalCheckFailedException
        mock_table.update_item.side_effect = exc_class("Already active")
        mock_table.query.return_value = {"Items": [{"status": "active", "subscription_id": "sub_123"}]}
        result = svc.activate_subscription("org_123", "sub_123", "ref_123")
        assert result["status"] == "active"

    def test_cancel_subscription(self, svc, mock_table):
        mock_table.update_item.return_value = {
            "Attributes": {"status": "cancelled", "cancelled_at": "2025-01-01"}
        }
        result = svc.cancel_subscription("org_123", "sub_123")
        assert result["status"] == "cancelled"

    def test_get_subscription_empty(self, svc, mock_table):
        mock_table.query.return_value = {"Items": []}
        result = svc.get_subscription("org_123")
        assert result is None

    def test_get_subscription_returns_latest(self, svc, mock_table):
        mock_table.query.return_value = {"Items": [{"subscription_id": "sub_latest"}]}
        result = svc.get_subscription("org_123")
        assert result["subscription_id"] == "sub_latest"

    def test_list_all_subscriptions(self, svc, mock_table):
        mock_table.scan.return_value = {"Items": [{"sub": 1}, {"sub": 2}]}
        result = svc.list_all_subscriptions()
        assert len(result) == 2
