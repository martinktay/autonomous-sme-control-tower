"""Unit tests for Tax Agent."""

import pytest
from unittest.mock import Mock, patch, AsyncMock

# Pre-import the module so @patch can resolve "app.agents.tax_agent.*"
# (the agents __init__.py doesn't re-export submodules)
import app.agents.tax_agent  # noqa: F401

from app.models.tax_report import AnnualTaxReport


def _make_report(**overrides):
    defaults = dict(
        report_id="doc-123", business_id="biz-1", business_name="Test Biz",
        tin="12345678", fiscal_year=2024, period_start="2024-01-01", period_end="2024-12-31",
        total_revenue=1000000, total_expenses=700000, gross_profit=300000, net_profit=300000,
        cit_turnover_threshold=25000000, cit_applicable=True, cit_rate=0.30, cit_amount=90000,
        cit_note="Standard CIT", vat_rate=0.075, vatable_revenue=1000000,
        vat_collected=75000, vat_on_purchases=52500, vat_payable=22500,
        wht_payments=100000, wht_rate=0.05, wht_deducted=5000,
        total_staff_costs=600000, paye_estimate=30000,
        total_tax_liability=147500, filing_deadline="2025 — June 30",
        penalties_if_late="Late filing: 25000 NGN",
        revenue_by_category={"sales": 1000000}, expense_by_category={"supplies": 700000},
    )
    defaults.update(overrides)
    return AnnualTaxReport(**defaults)


class TestGenerateGuidance:
    @pytest.mark.asyncio
    @patch("app.agents.tax_agent.load_prompt", return_value="Summarise tax report")
    @patch("app.agents.tax_agent.get_bedrock_client")
    async def test_guidance_returns_structured_output(self, mock_bedrock, mock_prompt):
        from app.agents.tax_agent import TaxAgent

        mock_client = Mock()
        mock_client.invoke_model.return_value = '{"summary": "Your tax liability is 147,500 NGN", "deadlines": ["CIT due June 30"], "recommendations": ["Set aside VAT monthly"], "warnings": [], "confidence": "high"}'
        mock_bedrock.return_value = mock_client

        agent = TaxAgent()
        result = await agent.generate_guidance(_make_report())

        assert "147,500" in result["summary"]
        assert result["confidence"] == "high"
        assert len(result["deadlines"]) >= 1

    @pytest.mark.asyncio
    @patch("app.agents.tax_agent.load_prompt", return_value="Summarise tax report")
    @patch("app.agents.tax_agent.get_bedrock_client")
    async def test_guidance_fallback_on_error(self, mock_bedrock, mock_prompt):
        from app.agents.tax_agent import TaxAgent

        mock_client = Mock()
        mock_client.invoke_model.side_effect = Exception("Bedrock down")
        mock_bedrock.return_value = mock_client

        agent = TaxAgent()
        report = _make_report()
        result = await agent.generate_guidance(report)

        assert result["confidence"] == "low"
        assert "Unable to generate" in result["summary"]
        assert report.filing_deadline in result["deadlines"][0]

    @pytest.mark.asyncio
    @patch("app.agents.tax_agent.load_prompt", return_value="Summarise tax report for {business_name}")
    @patch("app.agents.tax_agent.get_bedrock_client")
    async def test_guidance_passes_report_fields_to_prompt(self, mock_bedrock, mock_prompt):
        from app.agents.tax_agent import TaxAgent

        mock_client = Mock()
        mock_client.invoke_model.return_value = '{"summary": "OK", "deadlines": [], "recommendations": [], "warnings": [], "confidence": "medium"}'
        mock_bedrock.return_value = mock_client

        agent = TaxAgent()
        await agent.generate_guidance(_make_report(business_name="Mama Shop"))

        call_kwargs = mock_prompt.call_args
        assert call_kwargs.kwargs.get("business_name") == "Mama Shop" or "Mama Shop" in str(call_kwargs)
