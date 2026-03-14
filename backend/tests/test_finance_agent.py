"""
Unit tests for Finance Document Agent

Tests Requirements 2.1-2.6, 3.1-3.5, 5.1-5.5, 6.1-6.6, 14.4-14.6
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.finance_agent import FinanceDocumentAgent


class TestExtractDocument:
    """Test suite for document extraction"""

    @patch("app.agents.finance_agent.load_prompt", return_value="Extract finance data as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_extract_document_returns_parsed_fields(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = (
            '{"vendor_name": "Tesco PLC", "amount": 150.00, "currency": "GBP",'
            ' "document_date": "2025-01-15", "description": "Groceries",'
            ' "vat_amount": 25.0, "vat_rate": 20.0}'
        )
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        result = agent.extract_document("Invoice from Tesco for £150")

        assert result["vendor_name"] == "Tesco PLC"
        assert result["amount"] == 150.00
        assert result["currency"] == "GBP"
        assert result["vat_amount"] == 25.0
        assert result["vat_rate"] == 20.0

    @patch("app.agents.finance_agent.load_prompt", return_value="Extract finance data as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_extract_document_with_currency_hint(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "Shop", "amount": 50.0, "currency": "GBP"}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.extract_document("Some receipt text", currency_hint="GBP")

        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert "Extract finance data as JSON" in prompt_arg

    @patch("app.agents.finance_agent.load_prompt", return_value="Extract finance data as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_extract_document_calls_nova_lite_with_low_temp(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "X"}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.extract_document("test")

        call_args = mock_client.invoke_nova_lite.call_args
        assert call_args.kwargs.get("temperature") == 0.3 or call_args[1].get("temperature") == 0.3

    @patch("app.agents.finance_agent.load_prompt", return_value="Extract finance data as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_extract_document_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "This is not JSON"
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            agent.extract_document("bad document")

    @patch("app.agents.finance_agent.load_prompt")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_extract_document_loads_correct_prompt(self, mock_bedrock, mock_prompt):
        mock_prompt.return_value = "prompt content"
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "X"}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.extract_document("some text")

        mock_prompt.assert_called_once_with(
            "finance-document-extraction",
            variables={"document_text": "some text"},
        )


class TestClassifyDocument:
    """Test suite for document classification"""

    @patch("app.agents.finance_agent.load_prompt", return_value="Classify document as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_classify_document_returns_category_and_score(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"category": "expense", "confidence_score": 0.92}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        result = agent.classify_document({
            "vendor_name": "Tesco PLC",
            "amount": 150.00,
            "currency": "GBP",
            "document_date": "2025-01-15",
            "description": "Groceries",
        })

        assert result["category"] == "expense"
        assert result["confidence_score"] == 0.92

    @patch("app.agents.finance_agent.load_prompt", return_value="Classify document as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_classify_document_calls_nova_lite_with_low_temp(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"category": "revenue", "confidence_score": 0.8}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.classify_document({"vendor_name": "Client A", "amount": 1000, "currency": "GBP", "document_date": "2025-01-01", "description": "Payment"})

        call_args = mock_client.invoke_nova_lite.call_args
        assert call_args.kwargs.get("temperature") == 0.3 or call_args[1].get("temperature") == 0.3

    @patch("app.agents.finance_agent.load_prompt")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_classify_document_loads_correct_prompt_with_fields(self, mock_bedrock, mock_prompt):
        mock_prompt.return_value = "prompt content"
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"category": "expense", "confidence_score": 0.9}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.classify_document({
            "vendor_name": "Acme",
            "amount": 500,
            "currency": "USD",
            "document_date": "2025-03-01",
            "description": "Office supplies",
        })

        mock_prompt.assert_called_once_with(
            "finance-document-classification",
            variables={
                "vendor_name": "Acme",
                "amount": 500,
                "currency": "USD",
                "document_date": "2025-03-01",
                "description": "Office supplies",
            },
        )

    @patch("app.agents.finance_agent.load_prompt", return_value="Classify document as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_classify_document_handles_missing_fields_gracefully(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"category": "expense", "confidence_score": 0.5}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        result = agent.classify_document({})

        assert result["category"] == "expense"

    @patch("app.agents.finance_agent.load_prompt", return_value="Classify document as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_classify_document_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        with pytest.raises(ValueError):
            agent.classify_document({"vendor_name": "X", "amount": 1, "currency": "GBP", "document_date": "2025-01-01", "description": "test"})


class TestParseInformalReceipt:
    """Test suite for informal receipt parsing"""

    @patch("app.agents.finance_agent.load_prompt", return_value="Parse informal receipt as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_parse_informal_receipt_returns_ngn_fields(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = (
            '{"vendor_name": "Mama Put", "amount": 3500.0, "currency": "NGN",'
            ' "document_date": "2025-02-10", "description": "Food purchase",'
            ' "vat_amount": null, "vat_rate": null}'
        )
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        result = agent.parse_informal_receipt("POS slip from Mama Put N3500")

        assert result["vendor_name"] == "Mama Put"
        assert result["amount"] == 3500.0
        assert result["currency"] == "NGN"
        assert result["vat_amount"] is None
        assert result["vat_rate"] is None

    @patch("app.agents.finance_agent.load_prompt", return_value="Parse informal receipt as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_parse_informal_receipt_calls_nova_lite_with_low_temp(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "X", "amount": 100, "currency": "NGN"}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.parse_informal_receipt("test receipt")

        call_args = mock_client.invoke_nova_lite.call_args
        assert call_args.kwargs.get("temperature") == 0.3 or call_args[1].get("temperature") == 0.3

    @patch("app.agents.finance_agent.load_prompt")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_parse_informal_receipt_loads_correct_prompt(self, mock_bedrock, mock_prompt):
        mock_prompt.return_value = "prompt content"
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"vendor_name": "X"}'
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        agent.parse_informal_receipt("receipt text here")

        mock_prompt.assert_called_once_with(
            "finance-informal-receipt",
            variables={"document_text": "receipt text here"},
        )

    @patch("app.agents.finance_agent.load_prompt", return_value="Parse informal receipt as JSON")
    @patch("app.agents.finance_agent.get_bedrock_client")
    def test_parse_informal_receipt_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "garbage output"
        mock_bedrock.return_value = mock_client

        agent = FinanceDocumentAgent()
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            agent.parse_informal_receipt("bad receipt")
