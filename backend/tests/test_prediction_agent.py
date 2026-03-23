"""Unit tests for Inventory Prediction Agent."""

import pytest
from unittest.mock import Mock, patch


class TestPredictDemand:
    @patch("app.agents.prediction_agent.load_prompt", return_value="Predict demand")
    @patch("app.agents.prediction_agent.get_bedrock_client")
    def test_predict_returns_forecasts(self, mock_bedrock, mock_prompt):
        from app.agents.prediction_agent import PredictionAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"predictions": [{"item": "Rice", "predicted_demand": 200, "reorder_point": 50}], "seasonal_patterns": ["Ramadan spike"], "summary": "Reorder rice soon"}'
        mock_bedrock.return_value = mock_client

        agent = PredictionAgent()
        result = agent.predict_demand(
            sales_data=[{"item": "Rice", "quantity": 150, "date": "2025-02"}],
            inventory_data=[{"item": "Rice", "quantity": 30}],
        )

        assert result["predictions"][0]["item"] == "Rice"
        assert result["predictions"][0]["predicted_demand"] == 200

    @patch("app.agents.prediction_agent.load_prompt", return_value="Predict demand")
    @patch("app.agents.prediction_agent.get_bedrock_client")
    def test_predict_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.prediction_agent import PredictionAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = PredictionAgent()
        with pytest.raises(ValueError):
            agent.predict_demand([], [])

    @patch("app.agents.prediction_agent.load_prompt", return_value="Predict demand")
    @patch("app.agents.prediction_agent.get_bedrock_client")
    def test_predict_passes_business_context(self, mock_bedrock, mock_prompt):
        from app.agents.prediction_agent import PredictionAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"predictions": []}'
        mock_bedrock.return_value = mock_client

        agent = PredictionAgent()
        agent.predict_demand([], [], business_type="bakery", business_name="Mama Bakery", country="Ghana")

        call_args = mock_prompt.call_args[0][1]
        assert call_args["business_type"] == "bakery"
        assert call_args["country"] == "Ghana"
