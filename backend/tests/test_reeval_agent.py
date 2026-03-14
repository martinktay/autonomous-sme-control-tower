"""
Unit tests for Re-evaluation Agent

Tests Requirements 7.1-7.5 (Post-action NSI recalculation and prediction accuracy)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.reeval_agent import ReevalAgent
from app.models import Evaluation


class TestOutcomeEvaluation:
    """Test suite for outcome evaluation"""

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_evaluate_outcome_returns_evaluation(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"assessment": "positive"}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        result = agent.evaluate_outcome(
            org_id="org_123",
            execution_id="exec_001",
            predicted_improvement=10.0,
            actual_nsi_before=60.0,
            actual_nsi_after=68.0,
            strategy_description="Collect invoices",
            execution_log={"status": "success"},
        )

        assert isinstance(result, Evaluation)
        assert result.org_id == "org_123"
        assert result.execution_id == "exec_001"
        assert result.old_nsi == 60.0
        assert result.new_nsi == 68.0
        assert result.actual_improvement == 8.0

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_prediction_accuracy_perfect(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        result = agent.evaluate_outcome(
            org_id="org_1",
            execution_id="exec_1",
            predicted_improvement=10.0,
            actual_nsi_before=50.0,
            actual_nsi_after=60.0,
            strategy_description="test",
            execution_log={},
        )

        assert result.prediction_accuracy == pytest.approx(1.0)

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_prediction_accuracy_partial(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        result = agent.evaluate_outcome(
            org_id="org_1",
            execution_id="exec_1",
            predicted_improvement=10.0,
            actual_nsi_before=50.0,
            actual_nsi_after=55.0,
            strategy_description="test",
            execution_log={},
        )

        assert result.prediction_accuracy == pytest.approx(0.5)

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_prediction_accuracy_clamped_to_zero(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        result = agent.evaluate_outcome(
            org_id="org_1",
            execution_id="exec_1",
            predicted_improvement=5.0,
            actual_nsi_before=50.0,
            actual_nsi_after=40.0,
            strategy_description="test",
            execution_log={},
        )

        assert result.prediction_accuracy == 0.0

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_prediction_accuracy_clamped_to_one(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        result = agent.evaluate_outcome(
            org_id="org_1",
            execution_id="exec_1",
            predicted_improvement=5.0,
            actual_nsi_before=50.0,
            actual_nsi_after=55.0,
            strategy_description="test",
            execution_log={},
        )

        assert 0.0 <= result.prediction_accuracy <= 1.0

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_prediction_accuracy_zero_predicted(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        result = agent.evaluate_outcome(
            org_id="org_1",
            execution_id="exec_1",
            predicted_improvement=0.0,
            actual_nsi_before=50.0,
            actual_nsi_after=55.0,
            strategy_description="test",
            execution_log={},
        )

        assert result.prediction_accuracy == 0.0

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome as JSON")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_evaluate_generates_unique_id(self, mock_bedrock, mock_load):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{}'
        mock_bedrock.return_value = mock_client

        agent = ReevalAgent()
        r1 = agent.evaluate_outcome("o", "e1", 5.0, 50.0, 55.0, "d", {})
        r2 = agent.evaluate_outcome("o", "e2", 5.0, 50.0, 55.0, "d", {})

        assert r1.evaluation_id != r2.evaluation_id
