"""Unit tests for Email Agent."""

import pytest
from unittest.mock import Mock, patch


class TestClassifyEmail:
    """Tests for EmailAgent.classify_email."""

    @patch("app.agents.email_agent.load_prompt", return_value="Classify this email")
    @patch("app.agents.email_agent.get_bedrock_client")
    def test_classify_returns_parsed_output(self, mock_bedrock, mock_prompt):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"category": "payment_reminder", "priority": "high", "action_required": true, "summary": "Payment overdue"}'
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        result = agent.classify_email("Payment Due", "Your invoice is overdue", "vendor@test.com")

        assert result["category"] == "payment_reminder"
        assert result["priority"] == "high"

    @patch("app.agents.email_agent.load_prompt", return_value="Classify this email")
    @patch("app.agents.email_agent.get_bedrock_client")
    def test_classify_includes_email_fields_in_prompt(self, mock_bedrock, mock_prompt):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"category": "inquiry"}'
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        agent.classify_email("Order Status", "Where is my order?", "customer@shop.ng")

        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert "Order Status" in prompt_arg
        assert "customer@shop.ng" in prompt_arg

    @patch("app.agents.email_agent.load_prompt", return_value="Classify this email")
    @patch("app.agents.email_agent.get_bedrock_client")
    def test_classify_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        with pytest.raises(ValueError):
            agent.classify_email("Test", "Body", "a@b.com")


class TestExtractTasks:
    """Tests for EmailAgent.extract_tasks."""

    @patch("app.agents.email_agent.load_prompt", return_value="Extract tasks from {email_content}")
    @patch("app.agents.email_agent.get_bedrock_client")
    def test_extract_tasks_returns_task_list(self, mock_bedrock, mock_prompt):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"tasks": [{"title": "Pay invoice", "deadline": "2025-04-01"}], "email_summary": "Payment request", "sentiment": "neutral"}'
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        result = agent.extract_tasks("Invoice #123", "Please pay by April 1", "vendor@test.com")

        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Pay invoice"

    @patch("app.agents.email_agent.load_prompt", return_value="Extract tasks from {email_content}")
    @patch("app.agents.email_agent.get_bedrock_client")
    def test_extract_tasks_raises_on_bad_json(self, mock_bedrock, mock_prompt):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "garbage"
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        with pytest.raises(ValueError):
            agent.extract_tasks("Test", "Body", "a@b.com")


class TestGenerateReplyDraft:
    """Tests for EmailAgent.generate_reply_draft."""

    @patch("app.agents.email_agent.get_bedrock_client")
    def test_generate_reply_returns_string(self, mock_bedrock):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "Thank you for your email. We will process your payment shortly."
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        result = agent.generate_reply_draft("Invoice", "Please pay", "vendor@test.com")

        assert isinstance(result, str)
        assert "payment" in result.lower()

    @patch("app.agents.email_agent.get_bedrock_client")
    def test_generate_reply_uses_tone(self, mock_bedrock):
        from app.agents.email_agent import EmailAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "Hi there! Thanks for reaching out."
        mock_bedrock.return_value = mock_client

        agent = EmailAgent()
        agent.generate_reply_draft("Hello", "Question", "a@b.com", tone="friendly")

        prompt_arg = mock_client.invoke_nova_lite.call_args[0][0]
        assert "friendly" in prompt_arg
