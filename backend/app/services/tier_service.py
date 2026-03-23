"""Pricing tier definitions and enforcement logic."""

import logging
from typing import Any, Dict, List, Optional

from app.models.business import PricingTier

logger = logging.getLogger(__name__)

TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    PricingTier.STARTER: {
        "uploads_per_month": 20,
        "branches": 1,
        "alerts_per_week": 5,
        "features": [
            "manual_upload", "basic_dashboard", "weekly_summary",
            "data_export", "single_branch", "transaction_tracking",
            "basic_pnl", "receipt_capture", "tax_compliance",
        ],
    },
    PricingTier.GROWTH: {
        "uploads_per_month": -1,
        "branches": 1,
        "alerts_per_week": -1,
        "features": [
            "manual_upload", "basic_dashboard", "daily_alerts",
            "cashflow_insights", "inventory_risk", "supplier_tracking",
            "whatsapp_summary", "data_export", "single_branch",
            "transaction_tracking", "basic_pnl", "receipt_capture",
            "expense_tracking", "payment_reminders", "tax_tracking",
            "invoice_management", "email_ingestion",
            "tax_compliance",
        ],
    },
    PricingTier.BUSINESS: {
        "uploads_per_month": -1,
        "branches": 10,
        "alerts_per_week": -1,
        "features": [
            "manual_upload", "basic_dashboard", "daily_alerts",
            "cashflow_insights", "inventory_risk", "supplier_tracking",
            "whatsapp_summary", "data_export", "multi_branch",
            "auto_sync", "advanced_forecasting", "staff_analytics",
            "transaction_tracking", "basic_pnl", "receipt_capture",
            "expense_tracking", "payment_reminders", "tax_tracking",
            "invoice_management", "email_ingestion",
            "marketing_analytics", "business_analytics",
            "bank_reconciliation", "profit_loss_reports",
            "customer_segmentation", "sales_forecasting",
            "tax_compliance",
        ],
    },
    PricingTier.ENTERPRISE: {
        "uploads_per_month": -1,
        "branches": -1,
        "alerts_per_week": -1,
        "features": [
            "manual_upload", "basic_dashboard", "daily_alerts",
            "cashflow_insights", "inventory_risk", "supplier_tracking",
            "whatsapp_summary", "data_export", "multi_branch",
            "auto_sync", "advanced_forecasting", "staff_analytics",
            "realtime_pos", "ai_pricing", "supplier_intelligence",
            "executive_dashboard", "dedicated_onboarding",
            "transaction_tracking", "basic_pnl", "receipt_capture",
            "expense_tracking", "payment_reminders", "tax_tracking",
            "invoice_management", "email_ingestion",
            "marketing_analytics", "business_analytics",
            "bank_reconciliation", "profit_loss_reports",
            "customer_segmentation", "sales_forecasting",
            "marketing_roi", "custom_reports", "api_access",
            "tax_compliance",
        ],
    },
}

TIER_PRICING_NGN = {
    PricingTier.STARTER: {"price": 0, "label": "Free"},
    PricingTier.GROWTH: {"price": 14900, "label": "₦14,900/mo"},
    PricingTier.BUSINESS: {"price": 39900, "label": "₦39,900/mo"},
    PricingTier.ENTERPRISE: {"price": 0, "label": "Contact Us"},
}


class TierService:
    """Checks feature access and usage limits against pricing tier."""

    def get_tier_limits(self, tier: PricingTier) -> Dict[str, Any]:
        """Return limits for a given tier."""
        return TIER_LIMITS.get(tier, TIER_LIMITS[PricingTier.STARTER])

    def has_feature(self, tier: PricingTier, feature: str) -> bool:
        """Check if a tier includes a specific feature."""
        limits = self.get_tier_limits(tier)
        return feature in limits["features"]

    def max_branches(self, tier: PricingTier) -> int:
        """Return max branches allowed (-1 = unlimited)."""
        return self.get_tier_limits(tier)["branches"]

    def max_uploads_per_month(self, tier: PricingTier) -> int:
        """Return max uploads per month (-1 = unlimited)."""
        return self.get_tier_limits(tier)["uploads_per_month"]

    def get_all_tiers(self) -> List[Dict[str, Any]]:
        """Return all tier definitions with pricing for the pricing page."""
        result = []
        for tier in PricingTier:
            limits = TIER_LIMITS[tier]
            pricing = TIER_PRICING_NGN[tier]
            result.append({
                "tier": tier.value,
                "pricing": pricing,
                "limits": {
                    "uploads_per_month": limits["uploads_per_month"],
                    "branches": limits["branches"],
                    "alerts_per_week": limits["alerts_per_week"],
                },
                "features": limits["features"],
            })
        return result

    def check_upload_allowed(self, tier: PricingTier, current_month_uploads: int) -> bool:
        """Check if another upload is allowed this month."""
        limit = self.max_uploads_per_month(tier)
        if limit == -1:
            return True
        return current_month_uploads < limit

    def check_branch_allowed(self, tier: PricingTier, current_branches: int) -> bool:
        """Check if another branch can be created."""
        limit = self.max_branches(tier)
        if limit == -1:
            return True
        return current_branches < limit

    def check_feature(self, business_id: str, feature: str) -> bool:
        """Check if a business's tier includes a specific feature.

        Looks up the business tier from DynamoDB and checks against TIER_LIMITS.
        Returns True if the feature is allowed or if the lookup fails (fail-open).
        """
        try:
            from app.services.business_service import get_business_service
            biz_svc = get_business_service()
            business = biz_svc.get_business(business_id)
            if not business:
                return True  # fail-open if business not found
            tier = business.get("pricing_tier", PricingTier.STARTER)
            return self.has_feature(tier, feature)
        except Exception as e:
            logger.warning("check_feature lookup failed for %s: %s", business_id, e)
            return True  # fail-open on error


def get_tier_service() -> TierService:
    """Return a TierService instance."""
    return TierService()
