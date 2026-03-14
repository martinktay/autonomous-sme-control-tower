"""
Unit tests for Signal Agent

Tests Requirements 1.1-1.5 (Invoice processing) and 2.1-2.5 (Email processing)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agents.signal_agent import SignalAgent


class TestInvoiceExtraction:
    """Test suite for invoice extraction"""

    @patch("app.agents.signal_agent.load_prompt", return_value="Extract invoice data as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_extract_invoice_returns_parsed_data(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "Acme Corp", "invoice_id": "INV-100", "amount": 2500.00, "currency": "USD", "due_date": "2025-06-30", "description": "Consulting"}'
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        result = agent.extract_invoice("Invoice from Acme Corp for $2500")

        assert result["vendor_name"] == "Acme Corp"
        assert result["amount"] == 2500.00
        assert result["currency"] == "USD"

    @patch("app.agents.signal_agent.load_prompt", return_value="Extract invoice data as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_extract_invoice_handles_json_in_markdown(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '```json\n{"vendor_name": "Test", "invoice_id": "INV-1", "amount": 100.0}\n```'
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        result = agent.extract_invoice("test invoice")

        assert result["vendor_name"] == "Test"

    @patch("app.agents.signal_agent.load_prompt", return_value="Extract invoice data as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_extract_invoice_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "This is not JSON at all"
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            agent.extract_invoice("bad invoice")

    @patch("app.agents.signal_agent.load_prompt", return_value="Extract invoice data as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_extract_invoice_calls_nova_lite_with_low_temp(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "X"}'
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        agent.extract_invoice("test")

        call_args = mock_client.invoke_nova_lite.call_args
        assert call_args.kwargs.get("temperature") == 0.3 or call_args[1].get("temperature") == 0.3


class TestEmailClassification:
    """Test suite for email classification"""

    @patch("app.agents.signal_agent.load_prompt", return_value="Classify email as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_classify_email_payment_reminder(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"classification": "payment_reminder", "urgency": "high", "sender": "vendor@example.com", "subject": "Payment overdue"}'
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        result = agent.classify_email(
            subject="Payment overdue",
            body="Your invoice is past due",
            sender="vendor@example.com",
        )

        assert result["classification"] == "payment_reminder"

    @patch("app.agents.signal_agent.load_prompt", return_value="Classify email as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_classify_email_customer_inquiry(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"classification": "customer_inquiry", "urgency": "medium"}'
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        result = agent.classify_email(
            subject="Question about order",
            body="When will my order ship?",
            sender="customer@example.com",
        )

        assert result["classification"] == "customer_inquiry"

    @patch("app.agents.signal_agent.load_prompt", return_value="Classify email as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_classify_email_raises_on_bad_response(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        with pytest.raises(ValueError):
            agent.classify_email(subject="Test", body="Test", sender="a@b.com")

    @patch("app.agents.signal_agent.load_prompt", return_value="Classify email as JSON")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_classify_email_includes_all_fields_in_prompt(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"classification": "other"}'
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        agent.classify_email(
            subject="Hello",
            body="World",
            sender="test@test.com",
        )

        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert "Hello" in prompt_arg
        assert "World" in prompt_arg
        assert "test@test.com" in prompt_arg
