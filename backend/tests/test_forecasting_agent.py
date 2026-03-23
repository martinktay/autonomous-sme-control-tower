"""Unit tests for Forecasting Agent."""

import pytest
from unittest.mock import Mock, patch


class TestForecast:
    @patch("app.agents.forecasting_agent.load_prompt", return_value="Generate forecast")
    @patch("app.agents.forecasting_agent.get_bedrock_client")
    def test_forecast_returns_projections(self, mock_bedrock, mock_prompt):
        from app.agents.forecasting_agent import ForecastingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"revenue_forecast": [{"month": "2025-04", "amount": 500000}], "expense_forecast": [{"month": "2025-04", "amount": 300000}], "cash_runway_months": 6, "summary": "Healthy outlook"}'
        mock_bedrock.return_value = mock_client

        agent = ForecastingAgent()
        result = agent.forecast(
            revenue_data=[{"month": "2025-01", "amount": 400000}],
            expense_data=[{"month": "2025-01", "amount": 250000}],
        )

        assert "revenue_forecast" in result
        assert result["cash_runway_months"] == 6

    @patch("app.agents.forecasting_agent.load_prompt", return_value="Generate forecast")
    @patch("app.agents.forecasting_agent.get_bedrock_client")
    def test_forecast_with_cash_position(self, mock_bedrock, mock_prompt):
        from app.agents.forecasting_agent import ForecastingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"revenue_forecast": [], "summary": "OK"}'
        mock_bedrock.return_value = mock_client

        agent = ForecastingAgent()
        agent.forecast([], [], cash_position={"balance": 1000000, "currency": "NGN"})

        call_args = mock_prompt.call_args[0][1]
        assert "1000000" in call_args["cash_position"]

    @patch("app.agents.forecasting_agent.load_prompt", return_value="Generate forecast")
    @patch("app.agents.forecasting_agent.get_bedrock_client")
    def test_forecast_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.forecasting_agent import ForecastingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = ForecastingAgent()
        with pytest.raises(ValueError):
            agent.forecast([], [])
