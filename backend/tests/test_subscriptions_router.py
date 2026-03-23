"""
Tests for subscriptions router — endpoints and webhook security.
"""

import hashlib
import hmac
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from app.services.auth_service import create_access_token


_TEST_TOKEN = create_access_token({
    "sub": "user-sub-test",
    "email": "sub@test.com",
    "org_id": "org_sub_test",
    "role": "owner",
    "tier": "starter",
})
_AUTH_HEADERS = {"Authorization": f"Bearer {_TEST_TOKEN}"}


@pytest.fixture(autouse=True)
def _patch_aws(monkeypatch):
    mock_ddb = Mock()
    mock_ddb.get_signals.return_value = []
    mock_ddb.get_actions.return_value = []
    mock_ddb.get_latest_nsi.return_value = None
    monkeypatch.setattr("app.routers.invoices.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.invoices.s3_service", Mock())
    monkeypatch.setattr("app.routers.signals.ddb_service", mock_ddb)
    monkeypatch.setattr("app.routers.stability.ddb_service", mock_ddb)


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


class TestPublicEndpoints:
    """Payment methods and pricing don't require auth."""

    def test_get_payment_methods_default(self, client):
        resp = client.get("/api/subscriptions/payment-methods")
        assert resp.status_code == 200
        data = resp.json()
        assert "payment_methods" in data
        assert len(data["payment_methods"]) > 0

    def test_get_payment_methods_by_country(self, client):
        resp = client.get("/api/subscriptions/payment-methods?country_code=KE")
        assert resp.status_code == 200
        ids = [m["id"] for m in resp.json()["payment_methods"]]
        assert "mobile_money" in ids

    def test_get_pricing_ngn(self, client):
        resp = client.get("/api/subscriptions/pricing?currency=NGN")
        assert resp.status_code == 200
        tiers = resp.json()["tiers"]
        assert len(tiers) == 4

    def test_get_pricing_usd(self, client):
        resp = client.get("/api/subscriptions/pricing?currency=USD")
        assert resp.status_code == 200
        assert resp.json()["currency"] == "USD"


class TestAuthenticatedEndpoints:
    """Subscription CRUD requires auth."""

    @patch("app.routers.subscriptions.get_subscription_service")
    def test_create_subscription(self, mock_get_svc, client):
        mock_svc = Mock()
        mock_svc.create_subscription.return_value = {
            "subscription_id": "sub_123",
            "tier": "growth",
            "status": "pending",
        }
        mock_get_svc.return_value = mock_svc
        resp = client.post(
            "/api/subscriptions",
            json={"tier": "growth", "payment_method": "paystack", "billing_cycle": "monthly", "currency": "NGN"},
            headers=_AUTH_HEADERS,
        )
        assert resp.status_code == 200
        assert resp.json()["subscription"]["tier"] == "growth"

    def test_create_subscription_no_auth(self, client):
        resp = client.post(
            "/api/subscriptions",
            json={"tier": "growth", "payment_method": "paystack"},
        )
        assert resp.status_code in (401, 403)

    @patch("app.routers.subscriptions.get_subscription_service")
    def test_get_current_no_subscription(self, mock_get_svc, client):
        mock_svc = Mock()
        mock_svc.get_subscription.return_value = None
        mock_get_svc.return_value = mock_svc
        resp = client.get("/api/subscriptions/current", headers=_AUTH_HEADERS)
        assert resp.status_code == 200
        assert resp.json()["tier"] == "starter"

    @patch("app.routers.subscriptions.get_subscription_service")
    def test_cancel_not_found(self, mock_get_svc, client):
        mock_svc = Mock()
        mock_svc.cancel_subscription.return_value = None
        mock_get_svc.return_value = mock_svc
        resp = client.post(
            "/api/subscriptions/cancel",
            json={"subscription_id": "sub_nonexistent"},
            headers=_AUTH_HEADERS,
        )
        assert resp.status_code == 404


class TestWebhookSecurity:
    """Webhook endpoints should validate signatures when secrets are set."""

    @patch("app.routers.subscriptions.settings")
    @patch("app.routers.subscriptions.get_subscription_service")
    def test_paystack_webhook_valid_signature(self, mock_get_svc, mock_settings, client):
        mock_settings.paystack_secret_key = "test_secret"
        mock_svc = Mock()
        mock_svc.activate_subscription.return_value = {"status": "active"}
        mock_get_svc.return_value = mock_svc

        body = json.dumps({
            "event": "charge.success",
            "data": {"reference": "ref_123", "metadata": {"org_id": "org_1", "subscription_id": "sub_1"}},
        })
        sig = hmac.new("test_secret".encode(), body.encode(), hashlib.sha512).hexdigest()
        resp = client.post(
            "/api/subscriptions/webhook/paystack",
            content=body,
            headers={"Content-Type": "application/json", "x-paystack-signature": sig},
        )
        assert resp.status_code == 200

    @patch("app.routers.subscriptions.settings")
    def test_paystack_webhook_invalid_signature(self, mock_settings, client):
        mock_settings.paystack_secret_key = "test_secret"
        body = json.dumps({"event": "charge.success", "data": {}})
        resp = client.post(
            "/api/subscriptions/webhook/paystack",
            content=body,
            headers={"Content-Type": "application/json", "x-paystack-signature": "bad_sig"},
        )
        assert resp.status_code == 400

    @patch("app.routers.subscriptions.settings")
    @patch("app.routers.subscriptions.get_subscription_service")
    def test_flutterwave_webhook_valid(self, mock_get_svc, mock_settings, client):
        mock_settings.flutterwave_secret_hash = "fw_hash"
        mock_svc = Mock()
        mock_svc.activate_subscription.return_value = {"status": "active"}
        mock_get_svc.return_value = mock_svc

        body = json.dumps({
            "event": "charge.completed",
            "data": {"status": "successful", "id": 12345, "meta": {"org_id": "org_1", "subscription_id": "sub_1"}},
        })
        resp = client.post(
            "/api/subscriptions/webhook/flutterwave",
            content=body,
            headers={"Content-Type": "application/json", "verif-hash": "fw_hash"},
        )
        assert resp.status_code == 200

    @patch("app.routers.subscriptions.settings")
    def test_flutterwave_webhook_invalid(self, mock_settings, client):
        mock_settings.flutterwave_secret_hash = "fw_hash"
        body = json.dumps({"event": "charge.completed", "data": {}})
        resp = client.post(
            "/api/subscriptions/webhook/flutterwave",
            content=body,
            headers={"Content-Type": "application/json", "verif-hash": "wrong"},
        )
        assert resp.status_code == 400
