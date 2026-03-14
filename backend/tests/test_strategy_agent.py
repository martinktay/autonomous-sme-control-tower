"""
Unit tests for Strategy Agent

Tests Requirements 5.1-5.5 (Strategy generation and simulation)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.strategy_agent import StrategyAgent
from app.models import Strategy


class TestStrategyGeneration:
    """Test suite for strategy generation"""

    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies as JSON")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    def test_simulate_returns_strategies(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '''{
            "strategies": [
                {
                    "description": "Accelerate invoice collections",
                    "predicted_improvement": 8.0,
                    "confidence": 0.85,
                    "automatable": true,
                    "reasoning": "Historical data supports this"
                },
                {
                    "description": "Renegotiate vendor terms",
                    "predicted_improvement": 5.0,
                    "confidence": 0.6,
                    "automatable": false,
                    "reasoning": "Moderate confidence"
                }
            ]
        }'''
        mock_bedrock.return_value = mock_client

        agent = StrategyAgent()
        results = agent.simulate_strategies(
            org_id="org_123",
            nsi_snapshot_id="nsi_001",
            current_nsi=55.0,
            top_risks=[{"description": "Cash flow risk"}],
            context={},
        )

        assert len(results) == 2
        assert all(isinstance(s, Strategy) for s in results)
        assert results[0].description == "Accelerate invoice collections"
        assert results[0].predicted_nsi_improvement == 8.0
        assert results[0].automation_eligibility is True
        assert results[0].org_id == "org_123"

    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies as JSON")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    def test_simulate_sets_correct_org_and_snapshot(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"strategies": [{"description": "Test", "predicted_improvement": 3.0, "confidence": 0.5}]}'
        mock_bedrock.return_value = mock_client

        agent = StrategyAgent()
        results = agent.simulate_strategies(
            org_id="org_abc",
            nsi_snapshot_id="nsi_xyz",
            current_nsi=60.0,
            top_risks=[],
            context={},
        )

        assert results[0].org_id == "org_abc"
        assert results[0].nsi_snapshot_id == "nsi_xyz"

    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies as JSON")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    def test_simulate_raises_on_missing_strategies_key(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"result": "no strategies"}'
        mock_bedrock.return_value = mock_client

        agent = StrategyAgent()
        with pytest.raises(ValueError, match="Failed to simulate"):
            agent.simulate_strategies(
                org_id="org_1",
                nsi_snapshot_id="nsi_1",
                current_nsi=50.0,
                top_risks=[],
                context={},
            )

    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies as JSON")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    def test_simulate_raises_on_invalid_json(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = StrategyAgent()
        with pytest.raises(ValueError):
            agent.simulate_strategies(
                org_id="org_1",
                nsi_snapshot_id="nsi_1",
                current_nsi=50.0,
                top_risks=[],
                context={},
            )

    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies as JSON")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    def test_simulate_generates_unique_strategy_ids(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"strategies": [{"description": "A", "predicted_improvement": 1.0, "confidence": 0.5}, {"description": "B", "predicted_improvement": 2.0, "confidence": 0.7}]}'
        mock_bedrock.return_value = mock_client

        agent = StrategyAgent()
        results = agent.simulate_strategies(
            org_id="org_1", nsi_snapshot_id="nsi_1",
            current_nsi=50.0, top_risks=[], context={},
        )

        ids = [s.strategy_id for s in results]
        assert len(set(ids)) == len(ids)  # All unique

    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies as JSON")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    def test_simulate_uses_higher_temperature(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"strategies": [{"description": "X", "predicted_improvement": 1.0, "confidence": 0.5}]}'
        mock_bedrock.return_value = mock_client

        agent = StrategyAgent()
        agent.simulate_strategies(
            org_id="org_1", nsi_snapshot_id="nsi_1",
            current_nsi=50.0, top_risks=[], context={},
        )

        call_args = mock_client.invoke_nova_lite.call_args
        assert call_args.kwargs.get("temperature") == 0.7 or call_args[1].get("temperature") == 0.7
