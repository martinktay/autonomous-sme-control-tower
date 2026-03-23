"""Unit tests for Inventory Agent."""

import pytest
from unittest.mock import Mock, patch


class TestAnalyseInventory:
    """Tests for InventoryAgent.analyse_inventory."""

    @patch("app.agents.inventory_agent.load_prompt", return_value="Analyse inventory")
    @patch("app.agents.inventory_agent.get_bedrock_client")
    def test_analyse_returns_parsed_output(self, mock_bedrock, mock_prompt):
        from app.agents.inventory_agent import InventoryAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"alerts": [{"item": "Rice", "type": "low_stock", "severity": "high"}], "summary": "1 item low"}'
        mock_bedrock.return_value = mock_client

        agent = InventoryAgent()
        result = agent.analyse_inventory([{"item_name": "Rice", "quantity": 2}])

        assert "alerts" in result
        assert result["alerts"][0]["item"] == "Rice"

    @patch("app.agents.inventory_agent.load_prompt", return_value="Analyse inventory")
    @patch("app.agents.inventory_agent.get_bedrock_client")
    def test_analyse_with_sales_data(self, mock_bedrock, mock_prompt):
        from app.agents.inventory_agent import InventoryAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"alerts": [], "summary": "Stock levels OK"}'
        mock_bedrock.return_value = mock_client

        agent = InventoryAgent()
        result = agent.analyse_inventory(
            [{"item_name": "Flour", "quantity": 50}],
            sales_data=[{"item": "Flour", "quantity_sold": 5}],
            business_type="bakery",
        )

        assert result["summary"] == "Stock levels OK"

    @patch("app.agents.inventory_agent.load_prompt", return_value="Analyse inventory")
    @patch("app.agents.inventory_agent.get_bedrock_client")
    def test_analyse_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.inventory_agent import InventoryAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = InventoryAgent()
        with pytest.raises(ValueError):
            agent.analyse_inventory([])

    @patch("app.agents.inventory_agent.load_prompt", return_value="Analyse inventory")
    @patch("app.agents.inventory_agent.get_bedrock_client")
    def test_analyse_uses_low_temperature(self, mock_bedrock, mock_prompt):
        from app.agents.inventory_agent import InventoryAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"alerts": []}'
        mock_bedrock.return_value = mock_client

        agent = InventoryAgent()
        agent.analyse_inventory([])

        call_kwargs = mock_client.invoke_nova_lite.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.3 or call_kwargs[1].get("temperature") == 0.3
