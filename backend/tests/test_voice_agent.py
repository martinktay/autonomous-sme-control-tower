"""
Unit tests for Voice Agent

Tests Requirements 9.1-9.5 (Voice queries, responses, and error handling)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.voice_agent import VoiceAgent, get_voice_agent


class TestTranscription:
    """Test suite for voice transcription"""

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_transcribe_query_success(self, mock_bedrock):
        mock_client = Mock()
        mock_client.transcribe_audio.return_value = "How stable is my business?"
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.transcribe_query(b"fake_audio_data")

        assert result == "How stable is my business?"

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_transcribe_query_empty_result(self, mock_bedrock):
        mock_client = Mock()
        mock_client.transcribe_audio.return_value = ""
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.transcribe_query(b"audio")

        assert result is None

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_transcribe_query_failure_returns_none(self, mock_bedrock):
        mock_client = Mock()
        mock_client.transcribe_audio.side_effect = Exception("Sonic unavailable")
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.transcribe_query(b"audio")

        assert result is None


class TestTextQueryProcessing:
    """Test suite for text query processing"""

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_stability_query(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        result = agent.process_text_query(
            "How stable is my business?", 75.0, [], []
        )

        assert "stable" in result.lower()
        assert "75.0" in result

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_bsi_query(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        result = agent.process_text_query(
            "What is my BSI score?", 45.0, [], []
        )

        assert "45.0" in result

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_overdue_invoices_query_none(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        result = agent.process_text_query(
            "Which invoices are overdue?", 70.0, [], []
        )

        assert "no overdue" in result.lower()

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_overdue_invoices_query_with_overdue(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        signals = [
            {"signal_type": "invoice", "status": "overdue"},
            {"signal_type": "invoice", "status": "overdue"},
            {"signal_type": "invoice", "status": "paid"},
        ]

        result = agent.process_text_query(
            "Which invoices are overdue?", 70.0, signals, []
        )

        assert "2 overdue" in result

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_risks_query(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        risks = [
            {"description": "Cash flow risk", "severity": "high"},
            {"description": "Vendor risk", "severity": "medium"},
        ]

        result = agent.process_text_query("What are my top risks?", 60.0, [], risks)

        assert "2 operational risks" in result
        assert "Cash flow risk" in result

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_unknown_query_fallback(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        result = agent.process_text_query("Tell me a joke", 70.0, [], [])

        assert "help you" in result.lower()

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_stability_levels(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        agent = VoiceAgent()

        high = agent.process_text_query("stability?", 85.0, [], [])
        assert "stable" in high.lower()

        mid = agent.process_text_query("stability?", 55.0, [], [])
        assert "moderately" in mid.lower()

        low = agent.process_text_query("stability?", 25.0, [], [])
        assert "unstable" in low.lower()


class TestVoiceResponse:
    """Test suite for voice response generation"""

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_generate_voice_response_success(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_sonic.return_value = b"audio_bytes"
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.generate_voice_response(
            "How stable?", 70.0, [], []
        )

        assert result["success"] is True
        assert result["audio_data"] == b"audio_bytes"
        assert "stable" in result["response_text"].lower()

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_generate_voice_response_failure(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_sonic.side_effect = Exception("Sonic down")
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.generate_voice_response("test", 70.0, [], [])

        assert result["success"] is False
        assert result["audio_data"] is None
        assert "error" in result


class TestBriefingGeneration:
    """Test suite for briefing text generation"""

    @patch("app.agents.voice_agent.load_prompt")
    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_generate_briefing_text(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "Your business is doing well."
        mock_bedrock.return_value = mock_client
        mock_prompt.return_value = "Generate a briefing."

        agent = VoiceAgent()
        result = agent.generate_briefing_text(
            bsi_score=75.0,
            top_risks=["Cash flow"],
            recent_actions=[{"id": "a1"}],
            trend="improving",
        )

        assert result == "Your business is doing well."

    @patch("app.agents.voice_agent.load_prompt")
    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_generate_briefing_fallback_on_error(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.side_effect = Exception("API error")
        mock_bedrock.return_value = mock_client
        mock_prompt.return_value = "Generate a briefing."

        agent = VoiceAgent()
        result = agent.generate_briefing_text(
            bsi_score=65.0, top_risks=[], recent_actions=[], trend="stable"
        )

        assert "65.0" in result
        assert "Stable" in result


class TestAudioGeneration:
    """Test suite for audio generation"""

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_generate_audio_success(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_sonic.return_value = b"audio_data"
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.generate_audio("Hello world")

        assert result == b"audio_data"

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_generate_audio_failure_returns_none(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_sonic.side_effect = Exception("fail")
        mock_bedrock.return_value = mock_client

        agent = VoiceAgent()
        result = agent.generate_audio("Hello")

        assert result is None


class TestSingleton:
    """Test singleton pattern"""

    @patch("app.agents.voice_agent.get_bedrock_client")
    def test_get_voice_agent_returns_instance(self, mock_bedrock):
        mock_bedrock.return_value = Mock()
        # Reset singleton
        import app.agents.voice_agent as va
        va._voice_agent = None

        agent = get_voice_agent()
        assert isinstance(agent, VoiceAgent)
