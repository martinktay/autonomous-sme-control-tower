"""Unit tests for POS Connector Agent."""

import pytest
from unittest.mock import Mock, patch


class TestExtractPosData:
    @patch("app.agents.pos_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.pos_agent.get_bedrock_client")
    def test_extract_returns_structured_transactions(self, mock_bedrock, mock_prompt):
        from app.agents.pos_agent import PosAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"transactions": [{"date": "2025-03-01", "amount": 2500, "item": "Rice 5kg"}], "pos_system_detected": "generic", "record_count": 1}'
        mock_bedrock.return_value = mock_client

        agent = PosAgent()
        result = agent.extract_pos_data("Item: Rice 5kg, Qty: 1, Price: 2500")

        assert result["record_count"] == 1
        assert result["transactions"][0]["amount"] == 2500

    @patch("app.agents.pos_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.pos_agent.get_bedrock_client")
    def test_extract_passes_pos_system(self, mock_bedrock, mock_prompt):
        from app.agents.pos_agent import PosAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"transactions": []}'
        mock_bedrock.return_value = mock_client

        agent = PosAgent()
        agent.extract_pos_data("data", pos_system="palmpay", country="Nigeria")

        call_args = mock_prompt.call_args[0][1]
        assert call_args["pos_system"] == "palmpay"
        assert call_args["country"] == "Nigeria"

    @patch("app.agents.pos_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.pos_agent.get_bedrock_client")
    def test_extract_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.pos_agent import PosAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "garbage"
        mock_bedrock.return_value = mock_client

        agent = PosAgent()
        with pytest.raises(ValueError):
            agent.extract_pos_data("bad data")

    @patch("app.agents.pos_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.pos_agent.get_bedrock_client")
    def test_extract_truncates_large_input(self, mock_bedrock, mock_prompt):
        from app.agents.pos_agent import PosAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"transactions": []}'
        mock_bedrock.return_value = mock_client

        agent = PosAgent()
        agent.extract_pos_data("x" * 10000)

        call_args = mock_prompt.call_args[0][1]
        assert len(call_args["pos_data"]) <= 5000
