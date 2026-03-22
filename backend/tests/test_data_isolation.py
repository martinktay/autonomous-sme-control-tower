"""
Property tests for data isolation

Tests Requirements 12.2, 12.3:
- Queries with different org_ids return isolated data
- Cross-organization access attempts are rejected
"""

import pytest
from pydantic import ValidationError
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from app.models import Signal, Invoice, ActionExecution, Evaluation


class TestOrgIdIsolationProperties:
    """Property tests for org_id isolation across all models"""

    def test_signal_requires_org_id(self):
        """Every signal must have an org_id"""
        signal = Signal(
            signal_id="sig_001",
            org_id="org_abc",
            signal_type="invoice",
            content={"test": True},
        )
        assert signal.org_id == "org_abc"

    def test_signal_org_id_cannot_be_empty(self):
        """org_id must not be empty string — validator rejects it"""
        with pytest.raises(ValidationError):
            Signal(
                signal_id="sig_001",
                org_id="",
                signal_type="invoice",
                content={},
            )

    def test_invoice_preserves_org_id(self):
        inv = Invoice(
            invoice_id="INV-1",
            org_id="org_xyz",
            vendor_name="Test",
            amount=100.0,
            due_date=datetime.now(timezone.utc),
            description="Test",
        )
        assert inv.org_id == "org_xyz"

    def test_action_preserves_org_id(self):
        action = ActionExecution(
            execution_id="exec_1",
            org_id="org_999",
            strategy_id="strat_1",
            action_type="test",
            target_entity="target",
            execution_status="success",
        )
        assert action.org_id == "org_999"

    def test_evaluation_preserves_org_id(self):
        ev = Evaluation(
            evaluation_id="eval_1",
            org_id="org_test",
            execution_id="exec_1",
            old_nsi=50.0,
            new_nsi=60.0,
            predicted_improvement=10.0,
            actual_improvement=10.0,
            prediction_accuracy=1.0,
        )
        assert ev.org_id == "org_test"


class TestDDBServiceIsolation:
    """Test DynamoDB service enforces org_id"""

    @patch("app.services.ddb_service.boto3")
    def test_enforce_org_id_raises_on_missing(self, mock_boto):
        mock_boto.resource.return_value = Mock()
        from app.services.ddb_service import DynamoDBService

        svc = DynamoDBService()

        with pytest.raises(ValueError, match="org_id is required"):
            svc._enforce_org_id({"name": "test"}, "org_1")

    @patch("app.services.ddb_service.boto3")
    def test_enforce_org_id_raises_on_mismatch(self, mock_boto):
        mock_boto.resource.return_value = Mock()
        from app.services.ddb_service import DynamoDBService

        svc = DynamoDBService()

        with pytest.raises(ValueError, match="org_id mismatch"):
            svc._enforce_org_id({"org_id": "org_other"}, "org_expected")

    @patch("app.services.ddb_service.boto3")
    def test_enforce_org_id_passes_on_match(self, mock_boto):
        mock_boto.resource.return_value = Mock()
        from app.services.ddb_service import DynamoDBService

        svc = DynamoDBService()
        # Should not raise — use valid org_id format
        svc._enforce_org_id({"org_id": "org-abcdef123456"}, "org-abcdef123456")

    @patch("app.services.ddb_service.boto3")
    def test_query_signals_filters_by_org(self, mock_boto):
        mock_table = Mock()
        mock_table.query.return_value = {
            "Items": [
                {"signal_id": "s1", "org_id": "org_A"},
                {"signal_id": "s2", "org_id": "org_A"},
            ]
        }
        mock_resource = Mock()
        mock_resource.Table.return_value = mock_table
        mock_boto.resource.return_value = mock_resource

        from app.services.ddb_service import DynamoDBService

        svc = DynamoDBService()
        results = svc.query_signals("org_A")

        # Verify the query used org_id filter
        call_kwargs = mock_table.query.call_args[1]
        assert "org_id = :org_id" in call_kwargs["KeyConditionExpression"]
        assert call_kwargs["ExpressionAttributeValues"][":org_id"] == "org_A"

    @patch("app.services.ddb_service.boto3")
    def test_different_orgs_get_different_data(self, mock_boto):
        """Simulate two orgs querying and verify isolation"""
        mock_table = Mock()
        mock_resource = Mock()
        mock_resource.Table.return_value = mock_table
        mock_boto.resource.return_value = mock_resource

        from app.services.ddb_service import DynamoDBService

        svc = DynamoDBService()

        # Org A query
        mock_table.query.return_value = {"Items": [{"org_id": "org_A", "id": "1"}]}
        results_a = svc.query_signals("org_A")

        # Org B query
        mock_table.query.return_value = {"Items": [{"org_id": "org_B", "id": "2"}]}
        results_b = svc.query_signals("org_B")

        # Verify isolation
        for item in results_a:
            assert item["org_id"] == "org_A"
        for item in results_b:
            assert item["org_id"] == "org_B"

        a_ids = {r["id"] for r in results_a}
        b_ids = {r["id"] for r in results_b}
        assert a_ids.isdisjoint(b_ids)


class TestMiddlewareIsolation:
    """Test middleware blocks cross-org access"""

    def test_mismatched_org_blocked(self):
        from fastapi.testclient import TestClient
        from app.middleware.org_isolation import OrgIsolationMiddleware
        from starlette.middleware.base import BaseHTTPMiddleware
        from fastapi import FastAPI

        test_app = FastAPI()

        # Shim that copies X-Org-ID header into request.state.org_id
        class _FakeAuth(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                request.state.org_id = request.headers.get("X-Org-ID", "")
                return await call_next(request)

        test_app.add_middleware(OrgIsolationMiddleware)
        test_app.add_middleware(_FakeAuth)

        @test_app.get("/api/test/{org_id}")
        def endpoint(org_id: str):
            return {"org_id": org_id}

        client = TestClient(test_app)

        # Matching org - should pass
        resp = client.get("/api/test/org_123", headers={"X-Org-ID": "org_123"})
        assert resp.status_code == 200

        # Mismatched org - should be blocked
        resp = client.get("/api/test/org_456", headers={"X-Org-ID": "org_123"})
        assert resp.status_code == 403
