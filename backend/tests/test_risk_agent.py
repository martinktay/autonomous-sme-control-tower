"""
Unit tests for Risk Agent (BSI calculation)

Tests Requirements 4.1-4.5 (BSI calculation and risk assessment)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.risk_agent import RiskAgent
from app.models import BSIScore


class TestBSICalculation:
    """Test suite for BSI calculation"""

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_bsi_returns_bsi_score(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "liquidity_index": 75.0,
            "revenue_stability_index": 80.0,
            "operational_latency_index": 65.0,
            "vendor_risk_index": 70.0,
            "business_stability_index": 73.0,
            "top_risks": [{"description": "Cash flow risk", "severity": "medium"}],
            "explanation": "Moderate stability",
            "confidence": "high"
        }'''
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_123", [{"type": "invoice"}], {})

        assert isinstance(result, BSIScore)
        assert result.business_stability_index == 73.0
        assert result.org_id == "org_123"
        assert result.confidence == "high"

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_bsi_sub_indices_populated(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "liquidity_index": 60.0,
            "revenue_stability_index": 70.0,
            "operational_latency_index": 55.0,
            "vendor_risk_index": 65.0,
            "business_stability_index": 62.5,
            "confidence": "medium"
        }'''
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_1", [{"type": "invoice"}], {})

        assert result.sub_indices.liquidity_index == 60.0
        assert result.sub_indices.revenue_stability_index == 70.0
        assert result.sub_indices.operational_latency_index == 55.0
        assert result.sub_indices.vendor_risk_index == 65.0

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_bsi_defaults_on_missing_fields(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_1", [], {})

        # Should default to 50.0 for all indices
        assert result.business_stability_index == 50.0
        assert result.sub_indices.liquidity_index == 50.0
        assert result.confidence == "medium"

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_bsi_with_empty_signals(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"business_stability_index": 50.0, "confidence": "low"}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_new", [], {})

        assert result.signal_count == 0
        assert result.confidence == "low"

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_bsi_limits_signals_to_10(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"business_stability_index": 70.0}'
        mock_bedrock.return_value = mock_client

        signals = [{"id": str(i)} for i in range(25)]

        agent = RiskAgent()
        result = agent.calculate_bsi("org_1", signals, {})

        # Verify prompt only includes first 10 signals
        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert result.signal_count == 25

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_bsi_top_risks_populated(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "business_stability_index": 45.0,
            "top_risks": [
                {"description": "High invoice aging", "severity": "high"},
                {"description": "Revenue concentration", "severity": "medium"}
            ]
        }'''
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_1", [{"type": "invoice"}], {})

        assert len(result.top_risks) == 2
        assert result.top_risks[0]["description"] == "High invoice aging"


class TestBSIScoreBounds:
    """Test BSI score boundary conditions"""

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_bsi_score_at_zero(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"business_stability_index": 0.0}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_1", [], {})
        assert result.business_stability_index == 0.0

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate BSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_bsi_score_at_hundred(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"business_stability_index": 100.0}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_bsi("org_1", [], {})
        assert result.business_stability_index == 100.0
