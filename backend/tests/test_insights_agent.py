"""Unit tests for Insights Agent — both general and finance fallback paths."""

import pytest
from unittest.mock import Mock, patch
from app.agents.insights_agent import InsightsAgent


class TestGenerateInsightsFallback:
    """Tests for the rule-based fallback path (no Bedrock)."""

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_fallback_no_bsi_data(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        # Force fallback by making _generate_with_bedrock raise
        agent._generate_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        result = agent.generate_insights("org-1", None, [], [], [])

        assert result["confidence"] == "low"
        assert "don't have enough data" in result["summary"]

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_fallback_healthy_score(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        bsi = {"bsi_score": 75, "liquidity_index": 80, "revenue_stability_index": 72,
               "operational_latency_index": 65, "vendor_risk_index": 60}
        result = agent.generate_insights("org-1", bsi, [], [], [])

        assert "healthy" in result["summary"].lower()
        assert result["confidence"] == "medium"

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_fallback_at_risk_score(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        bsi = {"bsi_score": 30, "liquidity_index": 25, "revenue_stability_index": 35,
               "operational_latency_index": 40, "vendor_risk_index": 30}
        result = agent.generate_insights("org-1", bsi, [], [], [])

        assert "at-risk" in result["summary"].lower()

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_fallback_includes_risk_highlight(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        bsi = {"bsi_score": 50, "liquidity_index": 50, "revenue_stability_index": 50,
               "operational_latency_index": 50, "vendor_risk_index": 50}
        risks = [{"description": "Late supplier payments", "severity": "high"}]
        result = agent.generate_insights("org-1", bsi, risks, [], [])

        risk_highlights = [h for h in result["highlights"] if h["title"] == "Top risk identified"]
        assert len(risk_highlights) == 1

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_fallback_includes_action_highlight(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        bsi = {"bsi_score": 60, "liquidity_index": 60, "revenue_stability_index": 60,
               "operational_latency_index": 60, "vendor_risk_index": 60}
        actions = [{"execution_status": "success"}, {"execution_status": "success"}]
        result = agent.generate_insights("org-1", bsi, [], actions, [])

        action_highlights = [h for h in result["highlights"] if "completed" in h["title"].lower()]
        assert len(action_highlights) == 1


class TestGenerateInsightsBedrock:
    """Tests for the Bedrock-powered path."""

    @patch("app.agents.insights_agent.load_prompt", return_value="Generate insights")
    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_bedrock_path_returns_structured_output(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"summary": "Business is healthy", "highlights": ["Good cash flow"], "next_steps": ["Keep it up"], "confidence": "high"}'
        mock_bedrock.return_value = mock_client

        agent = InsightsAgent()
        bsi = {"bsi_score": 80, "liquidity_index": 75, "revenue_stability_index": 70,
               "operational_latency_index": 65, "vendor_risk_index": 60, "confidence": 0.9}
        result = agent.generate_insights("org-1", bsi, [], [], [])

        assert result["summary"] == "Business is healthy"
        assert result["confidence"] == "high"


class TestFinanceInsightsFallback:
    """Tests for finance-specific fallback insights."""

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_finance_fallback_no_documents(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_finance_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        pnl = {"total_revenue": 0, "total_expenses": 0, "net_profit": 0,
               "vat_summary": {}, "tax_summary": {}, "by_vendor": {}}
        result = agent.generate_finance_insights("org-1", pnl, [], {"total_documents": 0, "pending_review": 0})

        assert "No financial documents" in result["summary"]

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_finance_fallback_profitable(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_finance_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        pnl = {"total_revenue": 1000000, "total_expenses": 700000, "net_profit": 300000,
               "vat_summary": {"total_vat_collected": 75000, "total_vat_paid": 52500},
               "tax_summary": {"withholding_tax": 0, "corporate_income_tax": 0, "paye_payroll": 0, "customs_levy": 0, "total_tax_burden": 0},
               "by_vendor": {}}
        result = agent.generate_finance_insights("org-1", pnl, [], {"total_documents": 10, "pending_review": 0})

        assert "revenue" in result["summary"].lower()
        assert result["confidence"] == "medium"

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_finance_fallback_loss_making(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_finance_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        pnl = {"total_revenue": 500000, "total_expenses": 800000, "net_profit": -300000,
               "vat_summary": {"total_vat_collected": 0, "total_vat_paid": 0},
               "tax_summary": {"withholding_tax": 0, "corporate_income_tax": 0, "paye_payroll": 0, "customs_levy": 0, "total_tax_burden": 0},
               "by_vendor": {}}
        result = agent.generate_finance_insights("org-1", pnl, [], {"total_documents": 5, "pending_review": 0})

        assert "loss" in result["summary"].lower()

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_finance_fallback_vat_liability(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_finance_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        pnl = {"total_revenue": 1000000, "total_expenses": 600000, "net_profit": 400000,
               "vat_summary": {"total_vat_collected": 75000, "total_vat_paid": 30000},
               "tax_summary": {"withholding_tax": 5000, "corporate_income_tax": 0, "paye_payroll": 10000, "customs_levy": 0, "total_tax_burden": 15000},
               "by_vendor": {"Supplier A": {"expenses": 400000}}}
        result = agent.generate_finance_insights("org-1", pnl,
            [{"revenue": 500000, "expenses": 300000}, {"revenue": 400000, "expenses": 350000}],
            {"total_documents": 20, "pending_review": 3})

        assert result["tax_insights"]["estimated_vat_liability"] == 45000.0
        assert result["tax_insights"]["paye_position"] != ""
        assert len(result["next_steps"]) > 0

    @patch("app.agents.insights_agent.get_bedrock_client")
    def test_finance_fallback_cashflow_declining(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = InsightsAgent()
        agent._generate_finance_with_bedrock = Mock(side_effect=Exception("no bedrock"))

        pnl = {"total_revenue": 800000, "total_expenses": 600000, "net_profit": 200000,
               "vat_summary": {"total_vat_collected": 0, "total_vat_paid": 0},
               "tax_summary": {"withholding_tax": 0, "corporate_income_tax": 0, "paye_payroll": 0, "customs_levy": 0, "total_tax_burden": 0},
               "by_vendor": {}}
        cashflow = [{"revenue": 500000, "expenses": 200000}, {"revenue": 300000, "expenses": 400000}]
        result = agent.generate_finance_insights("org-1", pnl, cashflow, {"total_documents": 10, "pending_review": 0})

        assert "declining" in result["cashflow_analysis"].lower()
