"""Unit tests for Supplier Intelligence Agent."""

import pytest
from unittest.mock import Mock, patch


class TestAnalyseSuppliers:
    @patch("app.agents.supplier_agent.load_prompt", return_value="Analyse suppliers")
    @patch("app.agents.supplier_agent.get_bedrock_client")
    def test_analyse_returns_scored_suppliers(self, mock_bedrock, mock_prompt):
        from app.agents.supplier_agent import SupplierAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"suppliers": [{"name": "Dangote", "score": 85, "risk": "low"}], "concentration_risk": false, "summary": "Healthy supplier base"}'
        mock_bedrock.return_value = mock_client

        agent = SupplierAgent()
        result = agent.analyse_suppliers(
            supplier_data=[{"name": "Dangote", "total_spend": 500000}],
        )

        assert result["suppliers"][0]["score"] == 85

    @patch("app.agents.supplier_agent.load_prompt", return_value="Analyse suppliers")
    @patch("app.agents.supplier_agent.get_bedrock_client")
    def test_analyse_with_transaction_and_inventory(self, mock_bedrock, mock_prompt):
        from app.agents.supplier_agent import SupplierAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"suppliers": [], "summary": "No data"}'
        mock_bedrock.return_value = mock_client

        agent = SupplierAgent()
        result = agent.analyse_suppliers(
            supplier_data=[],
            transaction_data=[{"amount": 1000}],
            inventory_data=[{"item": "Flour"}],
            business_type="bakery",
            country="Kenya",
        )

        assert isinstance(result, dict)

    @patch("app.agents.supplier_agent.load_prompt", return_value="Analyse suppliers")
    @patch("app.agents.supplier_agent.get_bedrock_client")
    def test_analyse_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.supplier_agent import SupplierAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = SupplierAgent()
        with pytest.raises(ValueError):
            agent.analyse_suppliers([])

    @patch("app.agents.supplier_agent.load_prompt", return_value="Analyse suppliers")
    @patch("app.agents.supplier_agent.get_bedrock_client")
    def test_analyse_uses_correct_temperature(self, mock_bedrock, mock_prompt):
        from app.agents.supplier_agent import SupplierAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"suppliers": []}'
        mock_bedrock.return_value = mock_client

        agent = SupplierAgent()
        agent.analyse_suppliers([])

        call_kwargs = mock_client.invoke_nova_lite.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.3 or call_kwargs[1].get("temperature") == 0.3
