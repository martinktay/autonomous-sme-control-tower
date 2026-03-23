"""Unit tests for Bank Reconciliation Agent."""

import pytest
from unittest.mock import Mock, patch


class TestReconcile:
    @patch("app.agents.bank_agent.load_prompt", return_value="Reconcile bank entries")
    @patch("app.agents.bank_agent.get_bedrock_client")
    def test_reconcile_returns_matches(self, mock_bedrock, mock_prompt):
        from app.agents.bank_agent import BankAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"matched": [{"bank_entry": "TXN-1", "business_txn": "INV-1", "confidence": 0.95}], "unmatched": [], "summary": "1 matched"}'
        mock_bedrock.return_value = mock_client

        agent = BankAgent()
        result = agent.reconcile(
            bank_entries=[{"id": "TXN-1", "amount": 5000}],
            business_transactions=[{"id": "INV-1", "amount": 5000}],
        )

        assert "matched" in result
        assert result["matched"][0]["confidence"] == 0.95

    @patch("app.agents.bank_agent.load_prompt", return_value="Reconcile bank entries")
    @patch("app.agents.bank_agent.get_bedrock_client")
    def test_reconcile_with_finance_documents(self, mock_bedrock, mock_prompt):
        from app.agents.bank_agent import BankAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"matched": [], "unmatched": ["TXN-2"]}'
        mock_bedrock.return_value = mock_client

        agent = BankAgent()
        result = agent.reconcile(
            bank_entries=[{"id": "TXN-2", "amount": 3000}],
            business_transactions=[],
            finance_documents=[{"doc_id": "DOC-1", "amount": 3000}],
            business_name="Test Shop",
            country="Kenya",
        )

        assert isinstance(result, dict)

    @patch("app.agents.bank_agent.load_prompt", return_value="Reconcile")
    @patch("app.agents.bank_agent.get_bedrock_client")
    def test_reconcile_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.bank_agent import BankAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = BankAgent()
        with pytest.raises(ValueError):
            agent.reconcile([], [])

    @patch("app.agents.bank_agent.load_prompt", return_value="Reconcile")
    @patch("app.agents.bank_agent.get_bedrock_client")
    def test_reconcile_uses_low_temperature(self, mock_bedrock, mock_prompt):
        from app.agents.bank_agent import BankAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"matched": []}'
        mock_bedrock.return_value = mock_client

        agent = BankAgent()
        agent.reconcile([], [])

        call_kwargs = mock_client.invoke_nova_lite.call_args
        assert call_kwargs.kwargs.get("temperature") == 0.2 or call_kwargs[1].get("temperature") == 0.2
