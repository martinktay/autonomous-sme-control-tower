"""
Tests for admin router — super_admin endpoints.

Covers role enforcement, user management, stats, subscriptions,
and platform config endpoints.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.services.auth_service import create_access_token


# Tokens for different roles
def _make_token(role="super_admin", tier="enterprise"):
    return create_access_token({
        "sub": "user-admin-test",
        "email": "admin@test.com",
        "org_id": "org_admin",
        "role": role,
        "tier": tier,
    })


_ADMIN_TOKEN = _make_token("super_admin")
_OWNER_TOKEN = _make_token("owner")
_ADMIN_HEADERS = {"Authorization": f"Bearer {_ADMIN_TOKEN}"}
_OWNER_HEADERS = {"Authorization": f"Bearer {_OWNER_TOKEN}"}


@pytest.fixture(autouse=True)
def _patch_aws(monkeypatch):
    """Prevent real AWS connections."""
    mock_ddb = Mock()
    mock_ddb.get_signals.return_value = []
    mock_ddb.get_actions.return_value = []
    mock_ddb.get_latest_bsi.return_value = None
    monkeypatch.setattr("app.routers.invoices.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.invoices.s3_service", Mock())
    monkeypatch.setattr("app.routers.signals.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.stability.ddb_service", mock_ddb)


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestAdminRoleEnforcement:
    """Non-super_admin users should get 403 on all admin endpoints."""

    def test_list_users_requires_super_admin(self, client):
        resp = client.get("/api/admin/users", headers=_OWNER_HEADERS)
        assert resp.status_code == 403

    def test_stats_requires_super_admin(self, client):
        resp = client.get("/api/admin/stats", headers=_OWNER_HEADERS)
        assert resp.status_code == 403

    def test_no_auth_returns_401_or_403(self, client):
        resp = client.get("/api/admin/users")
        assert resp.status_code in (401, 403)

    def test_delete_requires_super_admin(self, client):
        resp = client.request(
            "DELETE", "/api/admin/users",
            json={"email": "test@example.com"},
            headers=_OWNER_HEADERS,
        )
        assert resp.status_code == 403

    def test_reactivate_requires_super_admin(self, client):
        resp = client.put(
            "/api/admin/users/reactivate",
            json={"email": "test@example.com"},
            headers=_OWNER_HEADERS,
        )
        assert resp.status_code == 403

    def test_subscriptions_requires_super_admin(self, client):
        resp = client.get("/api/admin/subscriptions", headers=_OWNER_HEADERS)
        assert resp.status_code == 403

    def test_config_requires_super_admin(self, client):
        resp = client.get("/api/admin/config/platform", headers=_OWNER_HEADERS)
        assert resp.status_code == 403


class TestAdminEndpoints:
    """Test admin endpoints with proper super_admin auth."""

    @patch("app.routers.admin.get_auth_service")
    def test_list_users(self, mock_get_svc, client):
        mock_svc = AsyncMock()
        mock_svc.list_users.return_value = [
            {"email": "a@test.com", "role": "owner"},
            {"email": "b@test.com", "role": "member"},
        ]
        mock_get_svc.return_value = mock_svc
        resp = client.get("/api/admin/users", headers=_ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 2

    @patch("app.routers.admin.get_auth_service")
    def test_update_role(self, mock_get_svc, client):
        mock_svc = AsyncMock()
        mock_svc.update_user_role.return_value = {"message": "updated"}
        mock_get_svc.return_value = mock_svc
        resp = client.put(
            "/api/admin/users/role",
            json={"email": "user@test.com", "role": "admin"},
            headers=_ADMIN_HEADERS,
        )
        assert resp.status_code == 200

    @patch("app.routers.admin.get_auth_service")
    def test_update_tier(self, mock_get_svc, client):
        mock_svc = AsyncMock()
        mock_svc.update_user_tier.return_value = {"message": "updated"}
        mock_get_svc.return_value = mock_svc
        resp = client.put(
            "/api/admin/users/tier",
            json={"email": "user@test.com", "tier": "growth"},
            headers=_ADMIN_HEADERS,
        )
        assert resp.status_code == 200

    def test_platform_config(self, client):
        resp = client.get("/api/admin/config/platform", headers=_ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "region" in data
        assert "models" in data
        assert "tables" in data

    def test_invalid_role_rejected(self, client):
        resp = client.put(
            "/api/admin/users/role",
            json={"email": "user@test.com", "role": "hacker"},
            headers=_ADMIN_HEADERS,
        )
        assert resp.status_code == 422  # Pydantic validation
