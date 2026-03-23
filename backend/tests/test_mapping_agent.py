"""Unit tests for Mapping Agent."""

import pytest
from unittest.mock import Mock, patch


class TestMapColumns:
    """Tests for MappingAgent.map_columns."""

    @patch("app.agents.mapping_agent.load_prompt", return_value="Map columns")
    @patch("app.agents.mapping_agent.get_bedrock_client")
    def test_map_columns_returns_mappings(self, mock_bedrock, mock_prompt):
        from app.agents.mapping_agent import MappingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"mappings": {"Date": "date", "Amount": "amount", "Description": "description"}, "unmapped_columns": [], "suggested_record_type": "transaction"}'
        mock_bedrock.return_value = mock_client

        agent = MappingAgent()
        result = agent.map_columns(
            columns=["Date", "Amount", "Description"],
            sample_rows=[["2025-01-01", "5000", "Sold rice"]],
        )

        assert result["mappings"]["Date"] == "date"
        assert result["suggested_record_type"] == "transaction"

    @patch("app.agents.mapping_agent.load_prompt", return_value="Map columns")
    @patch("app.agents.mapping_agent.get_bedrock_client")
    def test_map_columns_uses_low_temperature(self, mock_bedrock, mock_prompt):
        from app.agents.mapping_agent import MappingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"mappings": {}}'
        mock_bedrock.return_value = mock_client

        agent = MappingAgent()
        agent.map_columns(["Col1"], [["val1"]])

        call_kwargs = mock_client.invoke_nova_lite.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.2 or call_kwargs[1].get("temperature") == 0.2

    @patch("app.agents.mapping_agent.load_prompt", return_value="Map columns")
    @patch("app.agents.mapping_agent.get_bedrock_client")
    def test_map_columns_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.mapping_agent import MappingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = MappingAgent()
        with pytest.raises(ValueError):
            agent.map_columns(["A"], [["1"]])

    @patch("app.agents.mapping_agent.load_prompt", return_value="Map columns")
    @patch("app.agents.mapping_agent.get_bedrock_client")
    def test_map_columns_passes_locale_context(self, mock_bedrock, mock_prompt):
        from app.agents.mapping_agent import MappingAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"mappings": {}}'
        mock_bedrock.return_value = mock_client

        agent = MappingAgent()
        agent.map_columns(["Wahala", "Owo"], [["x", "y"]], business_type="kiosk", country="Nigeria")

        call_args = mock_prompt.call_args
        variables = call_args[0][1]
        assert variables["business_type"] == "kiosk"
        assert variables["country"] == "Nigeria"
