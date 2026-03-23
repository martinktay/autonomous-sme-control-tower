"""Unit tests for Rate Limiter Middleware."""

import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.rate_limiter import RateLimiterMiddleware


def _build_app(rpm: int = 5) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RateLimiterMiddleware, rpm=rpm)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/test")
    def test_endpoint():
        return {"data": "ok"}

    @app.post("/api/auth/login")
    def login():
        return {"token": "abc"}

    @app.post("/api/invoices/upload")
    def upload():
        return {"uploaded": True}

    return app


class TestRateLimiter:
    def test_exempt_paths_not_limited(self):
        client = TestClient(_build_app(rpm=1))
        for _ in range(10):
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_general_rate_limit_enforced(self):
        client = TestClient(_build_app(rpm=3))
        for i in range(3):
            resp = client.get("/api/test")
            assert resp.status_code == 200

        resp = client.get("/api/test")
        assert resp.status_code == 429
        assert "Retry-After" in resp.headers

    def test_auth_strict_limit(self):
        app = _build_app(rpm=100)
        # Auth limit is 10 by default, but we'll test it hits 429 before general
        client = TestClient(app)
        for i in range(10):
            resp = client.post("/api/auth/login")
            assert resp.status_code == 200

        resp = client.post("/api/auth/login")
        assert resp.status_code == 429
        assert "login" in resp.json()["detail"].lower()

    def test_upload_separate_limit(self):
        app = _build_app(rpm=100)
        client = TestClient(app)
        for i in range(20):
            resp = client.post("/api/invoices/upload")
            assert resp.status_code == 200

        resp = client.post("/api/invoices/upload")
        assert resp.status_code == 429

    def test_429_includes_retry_after(self):
        client = TestClient(_build_app(rpm=1))
        client.get("/api/test")
        resp = client.get("/api/test")
        assert resp.status_code == 429
        assert resp.headers["Retry-After"] == "60"
