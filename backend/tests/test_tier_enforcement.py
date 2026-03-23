"""Unit tests for Tier Enforcement Middleware."""

import pytest
from unittest.mock import patch, Mock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.tier_enforcement import TierEnforcementMiddleware, TIER_GATED_ROUTES


def _build_app(check_feature_return=True) -> FastAPI:
    """Build a test app with tier enforcement and a fake auth layer."""
    app = FastAPI()

    # Fake auth middleware that sets request.state.org_id
    class FakeAuth(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            request.state.org_id = "org-test-123"
            return await call_next(request)

    app.add_middleware(TierEnforcementMiddleware)
    app.add_middleware(FakeAuth)

    @app.get("/api/inventory/analytics")
    def inventory_analytics():
        return {"data": "analytics"}

    @app.get("/api/counterparties")
    def counterparties():
        return {"data": "counterparties"}

    @app.get("/api/other")
    def other():
        return {"data": "other"}

    return app


class TestTierEnforcement:
    @patch("app.middleware.tier_enforcement.get_tier_service")
    def test_non_gated_route_passes(self, mock_tier):
        client = TestClient(_build_app())
        resp = client.get("/api/other")
        assert resp.status_code == 200
        mock_tier.assert_not_called()

    @patch("app.middleware.tier_enforcement.get_tier_service")
    def test_gated_route_allowed_when_feature_available(self, mock_tier):
        mock_svc = Mock()
        mock_svc.check_feature.return_value = True
        mock_tier.return_value = mock_svc

        client = TestClient(_build_app())
        resp = client.get("/api/inventory/analytics")
        assert resp.status_code == 200

    @patch("app.middleware.tier_enforcement.get_tier_service")
    def test_gated_route_blocked_when_feature_unavailable(self, mock_tier):
        mock_svc = Mock()
        mock_svc.check_feature.return_value = False
        mock_tier.return_value = mock_svc

        client = TestClient(_build_app())
        resp = client.get("/api/inventory/analytics")
        assert resp.status_code == 403
        assert "upgrade" in resp.json()["detail"].lower()

    @patch("app.middleware.tier_enforcement.get_tier_service")
    def test_tier_service_error_fails_open(self, mock_tier):
        mock_svc = Mock()
        mock_svc.check_feature.side_effect = Exception("DB down")
        mock_tier.return_value = mock_svc

        client = TestClient(_build_app())
        resp = client.get("/api/counterparties")
        assert resp.status_code == 200  # fail-open


class TestTierGatedRoutes:
    def test_gated_routes_defined(self):
        assert len(TIER_GATED_ROUTES) > 0

    def test_inventory_analytics_gated(self):
        assert "/api/inventory/analytics" in TIER_GATED_ROUTES

    def test_counterparties_gated(self):
        assert "/api/counterparties" in TIER_GATED_ROUTES
