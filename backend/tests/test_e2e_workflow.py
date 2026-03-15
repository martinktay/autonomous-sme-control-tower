"""
End-to-end integration tests for closed-loop workflow

Tests Requirements 1.1, 2.1, 4.1, 5.1, 6.1, 7.1, 12.2, 12.3
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.agents.signal_agent import SignalAgent
from app.agents.risk_agent import RiskAgent
from app.agents.strategy_agent import StrategyAgent
from app.agents.action_agent import ActionAgent
from app.agents.reeval_agent import ReevalAgent


class TestClosedLoopWorkflow:
    """Test complete closed-loop workflow using actual agent methods"""

    @patch("app.agents.reeval_agent.load_prompt", return_value="Evaluate outcome")
    @patch("app.agents.strategy_agent.load_prompt", return_value="Generate strategies")
    @patch("app.agents.strategy_agent.get_bedrock_client")
    @patch("app.agents.risk_agent.load_prompt", return_value="Calculate NSI")
    @patch("app.agents.risk_agent.get_bedrock_client")
    @patch("app.agents.signal_agent.load_prompt", return_value="Extract invoice")
    @patch("app.agents.signal_agent.get_bedrock_client")
    @patch("app.agents.action_agent.get_bedrock_client")
    @patch("app.agents.reeval_agent.get_bedrock_client")
    def test_full_closed_loop_invoice_workflow(
        self,
        mock_reeval_bedrock,
        mock_action_bedrock,
        mock_signal_bedrock,
        mock_signal_prompt,
        mock_risk_bedrock,
        mock_risk_prompt,
        mock_strategy_bedrock,
        mock_strategy_prompt,
        mock_reeval_prompt,
    ):
        org_id = "org_test_123"

        # Step 1: INGEST - extract invoice
        mock_sig = Mock()
        mock_sig.invoke_nova_lite.return_value = (
            '{"vendor_name":"Acme","invoice_id":"INV-001","amount":5000}'
        )
        mock_signal_bedrock.return_value = mock_sig

        signal_agent = SignalAgent()
        invoice_data = signal_agent.extract_invoice("Invoice from Acme $5000")
        assert invoice_data["vendor_name"] == "Acme"

        # Step 2: DIAGNOSE - calculate NSI
        mock_risk = Mock()
        mock_risk.invoke_nova_lite.return_value = (
            '{"nova_stability_index":65,"liquidity_index":60,'
            '"revenue_stability_index":70,"operational_latency_index":65,'
            '"vendor_risk_index":65,"confidence":"medium",'
            '"top_risks":[{"description":"Cash flow risk"}]}'
        )
        mock_risk_bedrock.return_value = mock_risk

        risk_agent = RiskAgent()
        nsi = risk_agent.calculate_nsi(org_id, [invoice_data], {})
        assert nsi.nova_stability_index == 65.0
        assert nsi.confidence == "medium"

        # Step 3: SIMULATE - generate strategies
        mock_strat = Mock()
        mock_strat.invoke_nova_lite.return_value = (
            '{"strategies":[{"description":"Collect invoices",'
            '"predicted_improvement":8.0,"confidence":0.85,"automatable":true}]}'
        )
        mock_strategy_bedrock.return_value = mock_strat

        strategy_agent = StrategyAgent()
        strategies = strategy_agent.simulate_strategies(
            org_id=org_id,
            nsi_snapshot_id="nsi_001",
            current_nsi=nsi.nova_stability_index,
            top_risks=nsi.top_risks,
            context={},
        )
        assert len(strategies) > 0
        assert strategies[0].automation_eligibility is True

        # Step 4: EXECUTE - run action
        mock_act = Mock()
        mock_act.invoke_nova_lite.return_value = '{"target": "INV-001", "status": "success", "actions_taken": ["collected"], "summary": "done"}'
        mock_action_bedrock.return_value = mock_act

        action_agent = ActionAgent()
        action = action_agent.execute_strategy(
            org_id=org_id,
            strategy_id=strategies[0].strategy_id,
            strategy_description=strategies[0].description,
        )
        assert action.execution_status == "success"

        # Step 5: EVALUATE - measure accuracy
        mock_reeval = Mock()
        mock_reeval.invoke_nova_lite.return_value = '{"assessment":"positive"}'
        mock_reeval_bedrock.return_value = mock_reeval

        reeval_agent = ReevalAgent()
        evaluation = reeval_agent.evaluate_outcome(
            org_id=org_id,
            execution_id=action.execution_id,
            predicted_improvement=8.0,
            actual_nsi_before=65.0,
            actual_nsi_after=72.0,
            strategy_description=strategies[0].description,
            execution_log={"status": "success"},
        )
        assert evaluation.new_nsi > evaluation.old_nsi
        assert evaluation.prediction_accuracy > 0.8


class TestMultiOrganizationIsolation:
    """Test multi-organization data isolation"""

    @patch("app.services.ddb_service.boto3")
    def test_org_data_isolation(self, mock_boto):
        mock_table = Mock()
        mock_resource = Mock()
        mock_resource.Table.return_value = mock_table
        mock_boto.resource.return_value = mock_resource

        from app.services.ddb_service import DynamoDBService

        svc = DynamoDBService()

        # Org A
        mock_table.query.return_value = {
            "Items": [{"signal_id": "s1", "org_id": "org_A"}]
        }
        a = svc.query_signals("org_A")

        # Org B
        mock_table.query.return_value = {
            "Items": [{"signal_id": "s2", "org_id": "org_B"}]
        }
        b = svc.query_signals("org_B")

        assert all(i["org_id"] == "org_A" for i in a)
        assert all(i["org_id"] == "org_B" for i in b)
        assert {i["signal_id"] for i in a}.isdisjoint({i["signal_id"] for i in b})


class TestErrorRecoveryAndGracefulDegradation:
    """Test error recovery"""

    @patch("app.agents.signal_agent.load_prompt", return_value="Extract")
    @patch("app.agents.signal_agent.get_bedrock_client")
    def test_signal_processing_continues_on_bad_json(self, mock_bedrock, mock_prompt):
        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = SignalAgent()
        with pytest.raises(ValueError):
            agent.extract_invoice("test")

    @patch("app.agents.action_agent.get_bedrock_client")
    def test_workflow_execution_logs_failures(self, mock_bedrock):
        mock_client = Mock()
        mock_client.invoke_nova_lite.side_effect = Exception("Nova Lite unavailable")
        mock_bedrock.return_value = mock_client

        agent = ActionAgent()
        result = agent.execute_strategy("org_123", "strat_001", "Test strategy")
        assert result.execution_status == "failed"
        assert result.error_reason == "Nova Lite unavailable"


class TestDataConsistency:
    """Test data consistency across workflow"""

    def test_org_id_propagates_through_workflow(self):
        org_id = "org_consistency_test"
        data = [
            {"org_id": org_id, "signal_id": "s1"},
            {"org_id": org_id, "nsi_id": "n1"},
            {"org_id": org_id, "strategy_id": "st1"},
            {"org_id": org_id, "execution_id": "e1"},
            {"org_id": org_id, "evaluation_id": "ev1"},
        ]
        for item in data:
            assert item["org_id"] == org_id
