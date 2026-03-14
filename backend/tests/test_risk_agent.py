"""
Unit tests for Risk Agent (NSI calculation)

Tests Requirements 4.1-4.5 (NSI calculation and risk assessment)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.risk_agent import RiskAgent
from app.models import NSIScore


class TestNSICalculation:
    """Test suite for NSI calculation"""

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_nsi_returns_nsi_score(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "liquidity_index": 75.0,
            "revenue_stability_index": 80.0,
            "operational_latency_index": 65.0,
            "vendor_risk_index": 70.0,
            "nova_stability_index": 73.0,
            "top_risks": [{"description": "Cash flow risk", "severity": "medium"}],
            "explanation": "Moderate stability",
            "confidence": "high"
        }'''
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_123", [{"type": "invoice"}], {})

        assert isinstance(result, NSIScore)
        assert result.nova_stability_index == 73.0
        assert result.org_id == "org_123"
        assert result.confidence == "high"

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_nsi_sub_indices_populated(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "liquidity_index": 60.0,
            "revenue_stability_index": 70.0,
            "operational_latency_index": 55.0,
            "vendor_risk_index": 65.0,
            "nova_stability_index": 62.5,
            "confidence": "medium"
        }'''
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_1", [{"type": "invoice"}], {})

        assert result.sub_indices.liquidity_index == 60.0
        assert result.sub_indices.revenue_stability_index == 70.0
        assert result.sub_indices.operational_latency_index == 55.0
        assert result.sub_indices.vendor_risk_index == 65.0

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_nsi_defaults_on_missing_fields(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_1", [], {})

        # Should default to 50.0 for all indices
        assert result.nova_stability_index == 50.0
        assert result.sub_indices.liquidity_index == 50.0
        assert result.confidence == "medium"

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_nsi_with_empty_signals(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"nova_stability_index": 50.0, "confidence": "low"}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_new", [], {})

        assert result.signal_count == 0
        assert result.confidence == "low"

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_nsi_limits_signals_to_10(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"nova_stability_index": 70.0}'
        mock_bedrock.return_value = mock_client

        signals = [{"id": str(i)} for i in range(25)]

        agent = RiskAgent()
        result = agent.calculate_nsi("org_1", signals, {})

        # Verify prompt only includes first 10 signals
        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert result.signal_count == 25

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_calculate_nsi_top_risks_populated(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "nova_stability_index": 45.0,
            "top_risks": [
                {"description": "High invoice aging", "severity": "high"},
                {"description": "Revenue concentration", "severity": "medium"}
            ]
        }'''
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_1", [{"type": "invoice"}], {})

        assert len(result.top_risks) == 2
        assert result.top_risks[0]["description"] == "High invoice aging"


class TestNSIScoreBounds:
    """Test NSI score boundary conditions"""

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_nsi_score_at_zero(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"nova_stability_index": 0.0}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_1", [], {})
        assert result.nova_stability_index == 0.0

    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI as JSON")
    @patch("app.agents.risk_agent.get_bedrock_client")
    def test_nsi_score_at_hundred(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"nova_stability_index": 100.0}'
        mock_bedrock.return_value = mock_client

        agent = RiskAgent()
        result = agent.calculate_nsi("org_1", [], {})
        assert result.nova_stability_index == 100.0
