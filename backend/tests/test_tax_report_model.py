"""Unit tests for Tax Report models."""

import pytest
from pydantic import ValidationError
from app.models.tax_report import AnnualTaxReport, TaxLineItem, TaxSettings


class TestAnnualTaxReport:
    def test_valid_report(self):
        report = AnnualTaxReport(
            report_id="doc-1", business_id="biz-1", fiscal_year=2024,
            period_start="2024-01-01", period_end="2024-12-31",
            total_revenue=1000000, total_expenses=700000,
            gross_profit=300000, net_profit=300000,
        )
        assert report.fiscal_year == 2024
        assert report.net_profit == 300000

    def test_defaults(self):
        report = AnnualTaxReport(
            report_id="doc-1", business_id="biz-1", fiscal_year=2024,
            period_start="2024-01-01", period_end="2024-12-31",
        )
        assert report.total_revenue == 0.0
        assert report.cit_applicable is False
        assert report.vat_rate == 0.075
        assert report.recommendations == []

    def test_revenue_by_category(self):
        report = AnnualTaxReport(
            report_id="doc-1", business_id="biz-1", fiscal_year=2024,
            period_start="2024-01-01", period_end="2024-12-31",
            revenue_by_category={"sales": 800000, "services": 200000},
        )
        assert report.revenue_by_category["sales"] == 800000

    def test_ai_summary_optional(self):
        report = AnnualTaxReport(
            report_id="doc-1", business_id="biz-1", fiscal_year=2024,
            period_start="2024-01-01", period_end="2024-12-31",
            ai_summary="Your tax liability is low.",
        )
        assert "low" in report.ai_summary


class TestTaxLineItem:
    def test_valid_line_item(self):
        item = TaxLineItem(label="CIT", amount=1000000, rate=0.30, tax_due=300000)
        assert item.tax_due == 300000

    def test_defaults(self):
        item = TaxLineItem(label="WHT")
        assert item.amount == 0.0
        assert item.tax_due == 0.0
        assert item.rate is None


class TestTaxSettings:
    def test_defaults(self):
        settings = TaxSettings()
        assert settings.vat_registered is False
        assert settings.has_employees is False
        assert settings.monthly_staff_cost == 0.0

    def test_custom_settings(self):
        settings = TaxSettings(
            tin="12345678", vat_registered=True,
            has_employees=True, monthly_staff_cost=500000,
            business_type="llc",
        )
        assert settings.tin == "12345678"
        assert settings.business_type == "llc"
