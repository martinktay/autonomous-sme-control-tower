"""
Unit tests for Action Agent (workflow execution)

Tests Requirements 6.1-6.5 (Workflow execution and failure handling)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.action_agent import ActionAgent
from app.models import ActionExecution


class TestWorkflowExecution:
    """Test suite for workflow execution"""

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_success(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_act.return_value = {
            "status": "success",
            "target": "INV-001",
        }
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        result = agent.execute_strategy(
            org_id="org_123",
            strategy_id="strat_001",
            strategy_description="Collect overdue invoices",
        )

        assert isinstance(result, ActionExecution)
        assert result.execution_status == "success"
        assert result.org_id == "org_123"
        assert result.strategy_id == "strat_001"
        assert result.target_entity == "INV-001"

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_failure_captured(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_act.side_effect = Exception("Nova Act unavailable")
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        result = agent.execute_strategy(
            org_id="org_123",
            strategy_id="strat_001",
            strategy_description="Test strategy",
        )

        assert result.execution_status == "failed"
        assert result.error_reason == "Nova Act unavailable"
        assert result.target_entity == "unknown"

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_generates_unique_id(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_act.return_value = {"target": "X"}
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        r1 = agent.execute_strategy("org_1", "s1", "desc1")
        r2 = agent.execute_strategy("org_1", "s1", "desc1")

        assert r1.execution_id != r2.execution_id

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_default_action_type(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_act.return_value = {"target": "X"}
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        result = agent.execute_strategy("org_1", "s1", "desc")

        assert result.action_type == "workflow_execution"

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_custom_action_type(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_act.return_value = {"target": "X"}
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        result = agent.execute_strategy(
            "org_1", "s1", "desc", action_type="update_invoice_status"
        )

        assert result.action_type == "update_invoice_status"

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_includes_org_in_task(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_act.return_value = {"target": "X"}
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        agent.execute_strategy("org_test_99", "s1", "Collect invoices")

        task_arg = mock_client.invoke_nova_act.call_args[0][0]
        assert "org_test_99" in task_arg
        assert "Collect invoices" in task_arg

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_execute_strategy_failure_does_not_raise(self, mock_bedrock):
        """Failures should be captured, not raised"""
        mock_client = Mock()
        mock_client.invoke_nova_act.side_effect = RuntimeError("boom")
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        # Should NOT raise
        result = agent.execute_strategy("org_1", "s1", "desc")
        assert result.execution_status == "failed"
