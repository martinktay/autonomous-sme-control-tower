"""Unit tests for Branch Optimisation Agent."""

import pytest
from unittest.mock import Mock, patch


class TestOptimise:
    @patch("app.agents.branch_agent.load_prompt", return_value="Optimise branches")
    @patch("app.agents.branch_agent.get_bedrock_client")
    def test_optimise_returns_recommendations(self, mock_bedrock, mock_prompt):
        from app.agents.branch_agent import BranchAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"recommendations": [{"type": "stock_transfer", "from": "Branch A", "to": "Branch B", "item": "Rice"}], "summary": "Transfer rice"}'
        mock_bedrock.return_value = mock_client

        agent = BranchAgent()
        result = agent.optimise(
            branch_data=[{"branch_id": "b1", "name": "Branch A"}, {"branch_id": "b2", "name": "Branch B"}],
            branch_inventory={"b1": [{"item": "Rice", "qty": 100}], "b2": [{"item": "Rice", "qty": 5}]},
            branch_sales={"b1": [], "b2": []},
        )

        assert "recommendations" in result

    @patch("app.agents.branch_agent.load_prompt", return_value="Optimise branches")
    @patch("app.agents.branch_agent.get_bedrock_client")
    def test_optimise_raises_on_invalid_json(self, mock_bedrock, mock_prompt):
        from app.agents.branch_agent import BranchAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = "not json"
        mock_bedrock.return_value = mock_client

        agent = BranchAgent()
        with pytest.raises(ValueError):
            agent.optimise([], {}, {})

    @patch("app.agents.branch_agent.load_prompt", return_value="Optimise branches")
    @patch("app.agents.branch_agent.get_bedrock_client")
    def test_optimise_passes_business_context(self, mock_bedrock, mock_prompt):
        from app.agents.branch_agent import BranchAgent

        mock_client = Mock()
        mock_client.invoke_nova_lite.return_value = '{"recommendations": []}'
        mock_bedrock.return_value = mock_client

        agent = BranchAgent()
        agent.optimise([], {}, {}, business_type="supermarket", business_name="ShopRite", country="Nigeria")

        call_args = mock_prompt.call_args[0][1]
        assert call_args["business_type"] == "supermarket"
        assert call_args["country"] == "Nigeria"
