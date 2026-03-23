"""Unit tests for WhatsApp Agent."""

import pytest
from unittest.mock import Mock, patch


class TestExtractMessage:
    """Tests for WhatsAppAgent.extract_message."""

    @patch("app.agents.whatsapp_agent.load_prompt", return_value="Extract from WhatsApp message: {message_text}")
    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_extract_returns_parsed_output(self, mock_bedrock, mock_prompt):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"message_type": "receipt", "vendor_name": "Mama Nkechi", "amount": 5000, "currency": "NGN", "items": ["garri", "rice"]}'
        mock_bedrock.return_value = mock_client

        agent = WhatsAppAgent()
        result = agent.extract_message("Bought garri and rice from Mama Nkechi for 5000 naira")

        assert result["message_type"] == "receipt"
        assert result["amount"] == 5000

    @patch("app.agents.whatsapp_agent.load_prompt", return_value="Extract from WhatsApp")
    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_extract_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = WhatsAppAgent()
        with pytest.raises(ValueError):
            agent.extract_message("random text")

    @patch("app.agents.whatsapp_agent.load_prompt", return_value="Extract from WhatsApp")
    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_extract_appends_message_when_not_in_prompt(self, mock_bedrock, mock_prompt):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"message_type": "text"}'
        mock_bedrock.return_value = mock_client

        agent = WhatsAppAgent()
        agent.extract_message("Hello world")

        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert "Hello world" in prompt_arg


class TestGenerateInsightSummary:
    """Tests for WhatsAppAgent.generate_insight_summary."""

    @patch("app.agents.whatsapp_agent.load_prompt", return_value="Generate WhatsApp summary")
    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_summary_returns_structured_output(self, mock_bedrock, mock_prompt):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"greeting": "Good morning!", "health_score": "75/100", "highlights": ["Sales up 10%"], "alerts": ["Low stock on rice"], "tip": "Reorder rice today", "sign_off": "Your AI assistant"}'
        mock_bedrock.return_value = mock_client

        agent = WhatsAppAgent()
        result = agent.generate_insight_summary(
            business_name="Mama Shop",
            nsi_score=75.0,
            top_risks=["Late payments"],
        )

        assert result["greeting"] == "Good morning!"
        assert "health_score" in result

    @patch("app.agents.whatsapp_agent.load_prompt", return_value="Generate WhatsApp summary")
    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_summary_includes_context(self, mock_bedrock, mock_prompt):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"greeting": "Hi"}'
        mock_bedrock.return_value = mock_client

        agent = WhatsAppAgent()
        agent.generate_insight_summary(
            business_name="Test Biz",
            nsi_score=60.0,
            top_risks=["Risk A", "Risk B"],
            transaction_summary={"total_revenue": 100000, "total_expenses": 80000},
            stock_alerts=[{"item": "flour"}],
        )

        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert "Test Biz" in prompt_arg
        assert "60.0" in prompt_arg


class TestFormatSummaryForWhatsapp:
    """Tests for WhatsAppAgent.format_summary_for_whatsapp."""

    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_format_full_summary(self, mock_bedrock):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_bedrock.return_value = Mock()
        agent = WhatsAppAgent()

        summary = {
            "greeting": "Good morning!",
            "health_score": "Score: 75/100",
            "highlights": ["Sales up", "New customer"],
            "alerts": ["Low stock"],
            "tip": "Reorder flour",
            "sign_off": "— Your AI",
        }
        text = agent.format_summary_for_whatsapp(summary)

        assert "Good morning!" in text
        assert "- Sales up" in text
        assert "! Low stock" in text
        assert "Tip: Reorder flour" in text

    @patch("app.agents.whatsapp_agent.get_bedrock_client")
    def test_format_empty_summary(self, mock_bedrock):
        from app.agents.whatsapp_agent import WhatsAppAgent

        mock_bedrock.return_value = Mock()
        agent = WhatsAppAgent()

        text = agent.format_summary_for_whatsapp({})
        assert isinstance(text, str)
