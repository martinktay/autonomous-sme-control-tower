"""Unit tests for Subscription and SubscriptionCreate models."""

import pytest
from pydantic import ValidationError
from app.models.subscription import Subscription, SubscriptionCreate


class TestSubscriptionModel:
    def test_valid_subscription(self):
        sub = Subscription(
            subscription_id="sub-1", org_id="org-1", tier="growth",
            payment_method="paystack", status="active", currency="NGN", amount=14900,
        )
        assert sub.tier == "growth"
        assert sub.amount == 14900

    def test_invalid_payment_method(self):
        with pytest.raises(ValidationError):
            Subscription(
                subscription_id="sub-1", org_id="org-1",
                payment_method="bitcoin",
            )

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            Subscription(
                subscription_id="sub-1", org_id="org-1",
                status="deleted",
            )

    def test_invalid_tier(self):
        with pytest.raises(ValidationError):
            Subscription(
                subscription_id="sub-1", org_id="org-1",
                tier="premium",
            )

    def test_negative_amount_rejected(self):
        with pytest.raises(ValidationError):
            Subscription(
                subscription_id="sub-1", org_id="org-1",
                amount=-100,
            )

    def test_all_valid_payment_methods(self):
        for method in ["paystack", "flutterwave", "bank_transfer", "ussd", "mobile_money", "stripe", "free"]:
            sub = Subscription(subscription_id="s", org_id="o", payment_method=method)
            assert sub.payment_method == method

    def test_all_valid_statuses(self):
        for status in ["active", "cancelled", "expired", "past_due", "trialing", "pending"]:
            sub = Subscription(subscription_id="s", org_id="o", status=status)
            assert sub.status == status


class TestSubscriptionCreateModel:
    def test_valid_create(self):
        sc = SubscriptionCreate(tier="growth", payment_method="paystack")
        assert sc.billing_cycle == "monthly"

    def test_starter_tier_rejected(self):
        with pytest.raises(ValidationError):
            SubscriptionCreate(tier="starter", payment_method="free")

    def test_annual_billing(self):
        sc = SubscriptionCreate(tier="business", payment_method="stripe", billing_cycle="annual", currency="USD")
        assert sc.billing_cycle == "annual"
        assert sc.currency == "USD"

    def test_invalid_payment_method(self):
        with pytest.raises(ValidationError):
            SubscriptionCreate(tier="growth", payment_method="cash")
