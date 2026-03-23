"""Unit tests for Tier Service — pricing tier limits and feature checks."""

import pytest
from app.services.tier_service import TierService, TIER_LIMITS
from app.models.business import PricingTier


class TestGetTierLimits:
    def test_starter_limits(self):
        svc = TierService()
        limits = svc.get_tier_limits(PricingTier.STARTER)
        assert limits["uploads_per_month"] == 20
        assert limits["branches"] == 1

    def test_growth_unlimited_uploads(self):
        svc = TierService()
        limits = svc.get_tier_limits(PricingTier.GROWTH)
        assert limits["uploads_per_month"] == -1

    def test_business_multi_branch(self):
        svc = TierService()
        limits = svc.get_tier_limits(PricingTier.BUSINESS)
        assert limits["branches"] == 10

    def test_enterprise_unlimited_everything(self):
        svc = TierService()
        limits = svc.get_tier_limits(PricingTier.ENTERPRISE)
        assert limits["uploads_per_month"] == -1
        assert limits["branches"] == -1
        assert limits["alerts_per_week"] == -1


class TestHasFeature:
    def test_starter_has_basic_dashboard(self):
        svc = TierService()
        assert svc.has_feature(PricingTier.STARTER, "basic_dashboard") is True

    def test_starter_lacks_whatsapp(self):
        svc = TierService()
        assert svc.has_feature(PricingTier.STARTER, "whatsapp_summary") is False

    def test_growth_has_whatsapp(self):
        svc = TierService()
        assert svc.has_feature(PricingTier.GROWTH, "whatsapp_summary") is True

    def test_business_has_bank_reconciliation(self):
        svc = TierService()
        assert svc.has_feature(PricingTier.BUSINESS, "bank_reconciliation") is True

    def test_enterprise_has_api_access(self):
        svc = TierService()
        assert svc.has_feature(PricingTier.ENTERPRISE, "api_access") is True

    def test_growth_lacks_api_access(self):
        svc = TierService()
        assert svc.has_feature(PricingTier.GROWTH, "api_access") is False


class TestUploadAllowed:
    def test_starter_under_limit(self):
        svc = TierService()
        assert svc.check_upload_allowed(PricingTier.STARTER, 10) is True

    def test_starter_at_limit(self):
        svc = TierService()
        assert svc.check_upload_allowed(PricingTier.STARTER, 20) is False

    def test_growth_always_allowed(self):
        svc = TierService()
        assert svc.check_upload_allowed(PricingTier.GROWTH, 9999) is True


class TestBranchAllowed:
    def test_starter_single_branch(self):
        svc = TierService()
        assert svc.check_branch_allowed(PricingTier.STARTER, 0) is True
        assert svc.check_branch_allowed(PricingTier.STARTER, 1) is False

    def test_business_up_to_ten(self):
        svc = TierService()
        assert svc.check_branch_allowed(PricingTier.BUSINESS, 9) is True
        assert svc.check_branch_allowed(PricingTier.BUSINESS, 10) is False

    def test_enterprise_unlimited(self):
        svc = TierService()
        assert svc.check_branch_allowed(PricingTier.ENTERPRISE, 100) is True


class TestGetAllTiers:
    def test_returns_all_four_tiers(self):
        svc = TierService()
        tiers = svc.get_all_tiers()
        assert len(tiers) == 4
        tier_names = [t["tier"] for t in tiers]
        assert "starter" in tier_names
        assert "enterprise" in tier_names

    def test_each_tier_has_pricing(self):
        svc = TierService()
        for tier in svc.get_all_tiers():
            assert "pricing" in tier
            assert "price" in tier["pricing"]
