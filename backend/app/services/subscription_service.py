"""
Subscription service — manages payment subscriptions for organisations.

Handles subscription creation, payment method selection, status updates,
and integration hooks for Paystack, Flutterwave, bank transfer, USSD,
mobile money, and Stripe.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from functools import lru_cache

from app.config import get_settings
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()

# Pricing in NGN (monthly)
TIER_PRICES_NGN = {
    "starter": 0,
    "growth": 14_900,
    "business": 39_900,
    "enterprise": 99_900,
}

# Annual discount: ~17% off (10 months for 12)
ANNUAL_MULTIPLIER = 10

# Approximate USD equivalents
TIER_PRICES_USD = {
    "starter": 0,
    "growth": 9.50,
    "business": 25.00,
    "enterprise": 63.00,
}

# Payment methods available per region
PAYMENT_METHODS_BY_REGION = {
    "NG": ["paystack", "flutterwave", "bank_transfer", "ussd"],
    "GH": ["paystack", "flutterwave", "mobile_money", "bank_transfer"],
    "KE": ["flutterwave", "mobile_money", "bank_transfer"],
    "ZA": ["paystack", "flutterwave", "bank_transfer"],
    "RW": ["flutterwave", "mobile_money", "bank_transfer"],
    "TZ": ["flutterwave", "mobile_money", "bank_transfer"],
    "UG": ["flutterwave", "mobile_money", "bank_transfer"],
    "GB": ["stripe", "bank_transfer"],
    "US": ["stripe", "bank_transfer"],
    "DEFAULT": ["stripe", "flutterwave", "bank_transfer"],
}

PAYMENT_METHOD_LABELS = {
    "paystack": "Paystack (Card, Bank Transfer, USSD)",
    "flutterwave": "Flutterwave (Card, Mobile Money, Bank)",
    "bank_transfer": "Direct Bank Transfer",
    "ussd": "USSD (Feature Phone)",
    "mobile_money": "Mobile Money (M-Pesa, MTN MoMo, Airtel Money)",
    "stripe": "Stripe (International Card)",
    "free": "Free Plan",
}


class SubscriptionService:
    """Service for managing subscriptions."""

    def __init__(self):
        import boto3
        self.ddb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id or None,
            aws_secret_access_key=settings.aws_secret_access_key or None,
        )
        table_name = getattr(settings, "subscriptions_table", "autonomous-sme-subscriptions")
        self.table = self.ddb.Table(table_name)

    def get_payment_methods(self, country_code: str = "NG") -> List[Dict[str, str]]:
        """Return available payment methods for a country."""
        methods = PAYMENT_METHODS_BY_REGION.get(
            country_code.upper(), PAYMENT_METHODS_BY_REGION["DEFAULT"]
        )
        return [
            {"id": m, "label": PAYMENT_METHOD_LABELS.get(m, m)}
            for m in methods
        ]

    def get_pricing(self, currency: str = "NGN") -> List[Dict[str, Any]]:
        """Return pricing tiers with amounts in the requested currency."""
        prices = TIER_PRICES_NGN if currency.upper() == "NGN" else TIER_PRICES_USD
        symbol = "\u20A6" if currency.upper() == "NGN" else "$"
        tiers = []
        for tier, monthly in prices.items():
            annual = monthly * ANNUAL_MULTIPLIER if monthly > 0 else 0
            tiers.append({
                "tier": tier,
                "monthly": monthly,
                "annual": annual,
                "monthly_display": f"{symbol}{monthly:,.0f}/mo" if monthly > 0 else "Free",
                "annual_display": f"{symbol}{annual:,.0f}/yr" if annual > 0 else "Free",
                "currency": currency.upper(),
            })
        return tiers

    def create_subscription(self, org_id: str, tier: str, payment_method: str,
                            billing_cycle: str = "monthly", currency: str = "NGN") -> Dict[str, Any]:
        """Create a new subscription record."""
        now = datetime.now(timezone.utc)
        prices = TIER_PRICES_NGN if currency.upper() == "NGN" else TIER_PRICES_USD
        monthly_amount = prices.get(tier, 0)

        if billing_cycle == "annual":
            amount = monthly_amount * ANNUAL_MULTIPLIER
            period_end = now + timedelta(days=365)
        else:
            amount = monthly_amount
            period_end = now + timedelta(days=30)

        sub_id = generate_id("subscription")
        item = {
            "org_id": org_id,
            "subscription_id": sub_id,
            "tier": tier,
            "payment_method": payment_method,
            "payment_provider_ref": "",
            "status": "pending",
            "currency": currency.upper(),
            "amount": str(amount),
            "billing_cycle": billing_cycle,
            "current_period_start": now.isoformat(),
            "current_period_end": period_end.isoformat(),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        self.table.put_item(Item=item)
        logger.info("Created subscription %s for org %s (tier=%s, method=%s)",
                     sub_id, org_id, tier, payment_method)
        return item

    def get_subscription(self, org_id: str) -> Optional[Dict[str, Any]]:
        """Get the current active subscription for an org."""
        try:
            resp = self.table.query(
                KeyConditionExpression="org_id = :oid",
                ExpressionAttributeValues={":oid": org_id},
                ScanIndexForward=False,
                Limit=1,
            )
            items = resp.get("Items", [])
            return items[0] if items else None
        except Exception as e:
            logger.error("Failed to get subscription for org %s: %s", org_id, e)
            return None

    def activate_subscription(self, org_id: str, subscription_id: str,
                              provider_ref: str = "") -> Optional[Dict[str, Any]]:
        """Mark a subscription as active after payment confirmation.

        Uses a conditional update to ensure idempotency — only activates
        subscriptions that are currently in 'pending' status.  If the
        subscription is already active the existing record is returned
        unchanged (no duplicate activation).
        """
        now = datetime.now(timezone.utc).isoformat()
        try:
            resp = self.table.update_item(
                Key={"org_id": org_id, "subscription_id": subscription_id},
                UpdateExpression="SET #s = :status, payment_provider_ref = :ref, updated_at = :now",
                ConditionExpression="#s = :pending",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":status": "active",
                    ":ref": provider_ref,
                    ":now": now,
                    ":pending": "pending",
                },
                ReturnValues="ALL_NEW",
            )
            return resp.get("Attributes")
        except self.ddb.meta.client.exceptions.ConditionalCheckFailedException:
            # Already activated — return current record (idempotent)
            logger.info("Subscription %s already activated (idempotent no-op)", subscription_id)
            existing = self.get_subscription(org_id)
            return existing
        except Exception as e:
            logger.error("Failed to activate subscription %s: %s", subscription_id, e)
            return None

    def cancel_subscription(self, org_id: str, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a subscription."""
        now = datetime.now(timezone.utc).isoformat()
        try:
            resp = self.table.update_item(
                Key={"org_id": org_id, "subscription_id": subscription_id},
                UpdateExpression="SET #s = :status, cancelled_at = :now, updated_at = :now",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":status": "cancelled", ":now": now},
                ReturnValues="ALL_NEW",
            )
            return resp.get("Attributes")
        except Exception as e:
            logger.error("Failed to cancel subscription %s: %s", subscription_id, e)
            return None

    def list_all_subscriptions(self) -> List[Dict[str, Any]]:
        """List all subscriptions (admin use)."""
        try:
            resp = self.table.scan(Limit=500)
            return resp.get("Items", [])
        except Exception as e:
            logger.error("Failed to list subscriptions: %s", e)
            return []


@lru_cache()
def get_subscription_service() -> SubscriptionService:
    return SubscriptionService()
