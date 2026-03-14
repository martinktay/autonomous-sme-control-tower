"""
Integration tests for API routers

Tests Requirements 12.2, 12.3, 14.1, 14.2:
- Test each endpoint with valid and invalid inputs
- Test org_id isolation across endpoints
- Test error responses and validation
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock


# Patch DDB and S3 at module level before importing app
# This prevents real AWS connections during test collection
@pytest.fixture(autouse=True)
def _patch_aws(monkeypatch):
    """Prevent real AWS connections in all router tests"""
    mock_ddb = Mock()
    mock_ddb.get_signals.return_value = []
    mock_ddb.get_actions.return_value = []
    mock_ddb.get_latest_nsi.return_value = None
    mock_ddb.query_signals.return_value = []
    mock_ddb.query_strategies.return_value = []
    mock_ddb.query_actions.return_value = []
    mock_ddb.put_signal.return_value = None
    mock_ddb.put_nsi_score.return_value = None
    mock_ddb.put_strategy.return_value = None
    mock_ddb.put_action.return_value = None

    mock_s3 = Mock()
    mock_s3.upload_file.return_value = None

    monkeypatch.setattr("app.routers.invoices.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.invoices.s3_service", mock_s3)
    monkeypatch.setattr("app.routers.signals.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.stability.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.strategy.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.actions.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.orchestration.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.voice.ddb_service", mock_ddb)

    return mock_ddb, mock_s3


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Test basic health endpoints"""

    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "status" in resp.json() or "message" in resp.json()

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "degraded")
        assert "checks" in data
        assert data["checks"]["api"] == "ok"


class TestInvoiceRouter:
    """Test Invoice Router endpoints"""

    @patch("app.routers.invoices.signal_agent")
    def test_upload_invoice_success(self, mock_agent, client, _patch_aws):
        mock_ddb, mock_s3 = _patch_aws
        mock_agent.extract_invoice.return_value = {
            "vendor_name": "Acme Corp",
            "invoice_id": "INV-001",
            "amount": 1500.00,
        }

        resp = client.post(
            "/api/invoices/upload?org_id=org_123",
            files={"file": ("invoice.pdf", b"fake pdf", "application/pdf")},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"
        assert data["status"] == "processed"

    def test_get_invoices(self, client, _patch_aws):
        mock_ddb, _ = _patch_aws
        mock_ddb.get_signals.return_value = [
            {"signal_id": "s1", "org_id": "org_123", "signal_type": "invoice"},
        ]

        resp = client.get("/api/invoices/org_123", headers={"X-Org-ID": "org_123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"


class TestSignalRouter:
    """Test Signal Router endpoints"""

    def test_get_signals(self, client, _patch_aws):
        mock_ddb, _ = _patch_aws
        mock_ddb.get_signals.return_value = [
            {"signal_id": "s1", "org_id": "org_123", "signal_type": "email"},
        ]

        resp = client.get("/api/signals/org_123", headers={"X-Org-ID": "org_123"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"


class TestStabilityRouter:
    """Test Stability Router endpoints"""

    def test_get_nsi_returns_data(self, client, _patch_aws):
        mock_ddb, _ = _patch_aws
        mock_ddb.get_latest_nsi.return_value = {
            "nsi_id": "nsi_1",
            "org_id": "org_123",
            "nsi_score": 72.0,
        }

        resp = client.get(
            "/api/stability/org_123", headers={"X-Org-ID": "org_123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"

    def test_get_nsi_history(self, client, _patch_aws):
        resp = client.get(
            "/api/stability/org_123/history", headers={"X-Org-ID": "org_123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"


class TestStrategyRouter:
    """Test Strategy Router endpoints"""

    def test_get_strategies(self, client, _patch_aws):
        mock_ddb, _ = _patch_aws
        mock_ddb.query_strategies.return_value = []

        resp = client.get(
            "/api/strategy/org_123", headers={"X-Org-ID": "org_123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"


class TestActionRouter:
    """Test Action Router endpoints"""

    @patch("app.routers.actions.action_agent")
    def test_execute_action_success(self, mock_agent, client, _patch_aws):
        from app.models import ActionExecution

        mock_agent.execute_strategy.return_value = ActionExecution(
            execution_id="exec_001",
            org_id="org_123",
            strategy_id="strat_001",
            action_type="workflow_execution",
            target_entity="INV-001",
            execution_status="success",
        )

        resp = client.post(
            "/api/actions/execute",
            json={
                "org_id": "org_123",
                "strategy_id": "strat_001",
                "strategy_description": "Collect invoices",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["execution_status"] == "success"

    def test_get_actions(self, client, _patch_aws):
        mock_ddb, _ = _patch_aws
        mock_ddb.get_actions.return_value = [
            {"execution_id": "e1", "org_id": "org_123"},
        ]

        resp = client.get(
            "/api/actions/org_123", headers={"X-Org-ID": "org_123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["org_id"] == "org_123"


class TestMemoryRouter:
    """Test Memory Router endpoints"""

    @patch("app.routers.memory.memory_agent")
    def test_semantic_search(self, mock_agent, client):
        mock_agent.search_similar.return_value = []

        resp = client.post(
            "/api/memory/search",
            json={"query": "overdue invoices", "org_id": "org_123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data


class TestCrossOrganizationIsolation:
    """Test cross-org isolation via middleware"""

    def test_mismatched_org_blocked(self, client):
        resp = client.get(
            "/api/stability/org_456",
            headers={"X-Org-ID": "org_123"},
        )
        assert resp.status_code == 403


class TestErrorHandling:
    """Test error handling"""

    def test_execute_action_missing_fields(self, client):
        resp = client.post(
            "/api/actions/execute",
            json={},
        )
        assert resp.status_code == 422
