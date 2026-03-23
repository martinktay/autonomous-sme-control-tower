"""Unit tests for Categorisation Agent."""

import pytest
from unittest.mock import Mock, patch


class TestCategoriseTransaction:
    """Tests for CategorisationAgent.categorise_transaction."""

    @patch("app.agents.categorisation_agent.load_prompt", return_value="Categorise transaction")
    @patch("app.agents.categorisation_agent.get_bedrock_client")
    def test_categorise_returns_parsed_output(self, mock_bedrock, mock_prompt):
        from app.agents.categorisation_agent import CategorisationAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"transaction_type": "expense", "category": "supplies", "confidence": 0.92, "subcategory": "office", "tags": ["stationery"]}'
        mock_bedrock.return_value = mock_client

        agent = CategorisationAgent()
        result = agent.categorise_transaction("Bought pens and paper", 5000.0)

        assert result["transaction_type"] == "expense"
        assert result["category"] == "supplies"
        assert result["confidence"] == 0.92

    @patch("app.agents.categorisation_agent.load_prompt", return_value="Categorise transaction")
    @patch("app.agents.categorisation_agent.get_bedrock_client")
    def test_categorise_uses_low_temperature(self, mock_bedrock, mock_prompt):
        from app.agents.categorisation_agent import CategorisationAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"transaction_type": "revenue", "category": "sales"}'
        mock_bedrock.return_value = mock_client

        agent = CategorisationAgent()
        agent.categorise_transaction("Sold goods", 10000.0)

        call_kwargs = mock_client.invoke_nova_lite.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.2 or call_kwargs[1].get("temperature") == 0.2

    @patch("app.agents.categorisation_agent.load_prompt", return_value="Categorise transaction")
    @patch("app.agents.categorisation_agent.get_bedrock_client")
    def test_categorise_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.categorisation_agent import CategorisationAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not valid json"
        mock_bedrock.return_value = mock_client

        agent = CategorisationAgent()
        with pytest.raises(ValueError):
            agent.categorise_transaction("test", 100.0)

    @patch("app.agents.categorisation_agent.load_prompt", return_value="Categorise transaction")
    @patch("app.agents.categorisation_agent.get_bedrock_client")
    def test_categorise_passes_context_to_prompt(self, mock_bedrock, mock_prompt):
        from app.agents.categorisation_agent import CategorisationAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"transaction_type": "expense", "category": "food"}'
        mock_bedrock.return_value = mock_client

        agent = CategorisationAgent()
        agent.categorise_transaction(
            description="Bought garri and rice",
            amount=15000.0,
            counterparty="Mama Nkechi",
            date="2025-03-15",
            business_type="supermarket",
            country="Nigeria",
        )

        call_args = mock_prompt.call_args
        assert call_args[0][0] == "transaction-categorisation"
        variables = call_args[0][1]
        assert variables["description"] == "Bought garri and rice"
        assert variables["country"] == "Nigeria"

    @patch("app.agents.categorisation_agent.load_prompt", return_value="Categorise transaction")
    @patch("app.agents.categorisation_agent.get_bedrock_client")
    def test_categorise_handles_markdown_wrapped_json(self, mock_bedrock, mock_prompt):
        from app.agents.categorisation_agent import CategorisationAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '```json\n{"transaction_type": "revenue", "category": "sales", "confidence": 0.85}\n```'
        mock_bedrock.return_value = mock_client

        agent = CategorisationAgent()
        result = agent.categorise_transaction("Customer payment", 25000.0)

        assert result["transaction_type"] == "revenue"


class TestGetCategorisationAgent:
    def test_returns_instance(self):
        with patch("app.agents.categorisation_agent.get_bedrock_client"):
            from app.agents.categorisation_agent import get_categorisation_agent
            assert get_categorisation_agent() is not None
