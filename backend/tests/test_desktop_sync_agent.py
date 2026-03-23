"""Unit tests for Desktop Sync Agent."""

import pytest
from unittest.mock import Mock, patch


class TestExtractFileData:
    @patch("app.agents.desktop_sync_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.desktop_sync_agent.get_bedrock_client")
    def test_extract_returns_structured_records(self, mock_bedrock, mock_prompt):
        from app.agents.desktop_sync_agent import DesktopSyncAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"records": [{"date": "2025-03-01", "amount": 15000, "description": "Daily sales"}], "record_count": 1, "file_type_detected": "csv"}'
        mock_bedrock.return_value = mock_client

        agent = DesktopSyncAgent()
        result = agent.extract_file_data("date,amount\n2025-03-01,15000", filename="sales.csv", file_type="csv")

        assert result["record_count"] == 1

    @patch("app.agents.desktop_sync_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.desktop_sync_agent.get_bedrock_client")
    def test_extract_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.desktop_sync_agent import DesktopSyncAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = DesktopSyncAgent()
        with pytest.raises(ValueError):
            agent.extract_file_data("bad data")

    @patch("app.agents.desktop_sync_agent.load_prompt", return_value="Extract POS data")
    @patch("app.agents.desktop_sync_agent.get_bedrock_client")
    def test_extract_truncates_large_content(self, mock_bedrock, mock_prompt):
        from app.agents.desktop_sync_agent import DesktopSyncAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"records": []}'
        mock_bedrock.return_value = mock_client

        agent = DesktopSyncAgent()
        large_content = "x" * 10000
        agent.extract_file_data(large_content)

        call_args = mock_prompt.call_args[0][1]
        assert len(call_args["file_content"]) <= 5000
