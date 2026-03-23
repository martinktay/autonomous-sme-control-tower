"""Unit tests for Alert Agent."""

import pytest
from unittest.mock import Mock, patch


class TestAlertGeneration:
    """Tests for AlertAgent.generate_alerts."""

    @patch("app.agents.alert_agent.load_prompt", return_value="Generate alerts")
    @patch("app.agents.alert_agent.get_bedrock_client")
    def test_generate_alerts_returns_parsed_output(self, mock_bedrock, mock_prompt):
        from app.agents.alert_agent import AlertAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"alerts": [{"type": "low_stock", "title": "Rice running low"}], "summary": "1 alert"}'
        mock_bedrock.return_value = mock_client

        agent = AlertAgent()
        result = agent.generate_alerts({"transactions": []}, business_type="supermarket")

        assert "alerts" in result
        assert result["alerts"][0]["type"] == "low_stock"

    @patch("app.agents.alert_agent.load_prompt", return_value="Generate alerts")
    @patch("app.agents.alert_agent.get_bedrock_client")
    def test_generate_alerts_uses_low_temperature(self, mock_bedrock, mock_prompt):
        from app.agents.alert_agent import AlertAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"alerts": [], "summary": "none"}'
        mock_bedrock.return_value = mock_client

        agent = AlertAgent()
        agent.generate_alerts({})

        call_kwargs = mock_client.invoke_nova_lite.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.3 or call_kwargs[1].get("temperature") == 0.3

    @patch("app.agents.alert_agent.load_prompt", return_value="Generate alerts")
    @patch("app.agents.alert_agent.get_bedrock_client")
    def test_generate_alerts_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.alert_agent import AlertAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = AlertAgent()
        with pytest.raises(ValueError):
            agent.generate_alerts({})

    @patch("app.agents.alert_agent.load_prompt", return_value="Generate alerts")
    @patch("app.agents.alert_agent.get_bedrock_client")
    def test_generate_alerts_passes_business_context(self, mock_bedrock, mock_prompt):
        from app.agents.alert_agent import AlertAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"alerts": []}'
        mock_bedrock.return_value = mock_client

        agent = AlertAgent()
        agent.generate_alerts(
            {"transactions": [{"amount": 500}]},
            business_type="bakery",
            business_name="Test Bakery",
            country="Kenya",
            tier="growth",
        )

        mock_prompt.assert_called_once()
        call_args = mock_prompt.call_args
        assert call_args[0][0] == "alert-generation"
        assert "bakery" in str(call_args)


class TestGetAlertAgent:
    def test_get_alert_agent_returns_instance(self):
        with patch("app.agents.alert_agent.get_bedrock_client"):
            from app.agents.alert_agent import get_alert_agent
            agent = get_alert_agent()
            assert agent is not None
