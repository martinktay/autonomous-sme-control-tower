"""
Unit tests for organization data isolation middleware

Tests org_id validation, cross-organization access prevention,
and security event logging.
"""

import pytest
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware import OrgIsolationMiddleware, validate_org_id_from_body
import json
from pydantic import BaseModel


# ============================================================================
# Test App Setup - These are endpoint definitions, not test functions
# ============================================================================

app = FastAPI()


# Shim middleware that simulates AuthMiddleware by copying X-Org-ID header
# into request.state.org_id (the real AuthMiddleware reads it from the JWT).
class _FakeAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        org_id = request.headers.get("X-Org-ID", "")
        request.state.org_id = org_id
        return await call_next(request)


app.add_middleware(OrgIsolationMiddleware)
app.add_middleware(_FakeAuthMiddleware)


class ActionRequest(BaseModel):
    org_id: str
    action: str


@app.get("/api/test/{org_id}")
def get_test_endpoint(org_id: str):
    return {"org_id": org_id, "status": "success"}


@app.post("/api/test/action")
def post_test_endpoint(request: Request, data: ActionRequest):
    # Validate org_id from body
    validate_org_id_from_body(request, data.org_id)
    return {"org_id": data.org_id, "status": "success"}


@app.options("/api/test/{org_id}")
def options_test_endpoint(org_id: str):
    return {"status": "ok"}


@app.get("/health")
async def health_endpoint():
    return {"status": "healthy"}


# ============================================================================
# Test Client
# ============================================================================

client = TestClient(app)


# ============================================================================
# Test Cases
# ============================================================================


class TestOrgIsolationMiddleware:
    """Test suite for organization isolation middleware"""
    
    def test_exempt_paths_no_validation(self):
        """Test that exempt paths don't require org_id validation"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_request_without_auth_header_allowed(self):
        """Test that requests without X-Org-ID header are allowed (for now)"""
        response = client.get("/api/test/org123")
        assert response.status_code == 200
        assert response.json()["org_id"] == "org123"
    
    def test_matching_org_id_allowed(self):
        """Test that requests with matching org_id are allowed"""
        headers = {"X-Org-ID": "org123"}
        response = client.get("/api/test/org123", headers=headers)
        assert response.status_code == 200
        assert response.json()["org_id"] == "org123"
    
    def test_mismatched_org_id_blocked(self):
        """Test that cross-organization access is blocked with 403"""
        headers = {"X-Org-ID": "org123"}
        response = client.get("/api/test/org456", headers=headers)
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
        assert response.json()["error_code"] == "ORG_ACCESS_DENIED"
    
    def test_post_request_with_matching_org_id(self):
        """Test POST request with matching org_id in body"""
        headers = {"X-Org-ID": "org123"}
        response = client.post(
            "/api/test/action",
            headers=headers,
            json={"org_id": "org123", "action": "test"}
        )
        assert response.status_code == 200
        assert response.json()["org_id"] == "org123"
    
    def test_post_request_with_mismatched_org_id(self):
        """Test POST request with mismatched org_id is blocked"""
        headers = {"X-Org-ID": "org123"}
        response = client.post(
            "/api/test/action",
            headers=headers,
            json={"org_id": "org456", "action": "test"}
        )
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]
    
    def test_options_request_allowed(self):
        """Test that OPTIONS requests (CORS preflight) are allowed"""
        response = client.options("/api/test/org123")
        assert response.status_code == 200


class TestSecurityEventLogging:
    """Test suite for security event logging"""
    
    def test_access_violation_logged(self, caplog):
        """Test that cross-organization access attempts are logged"""
        headers = {"X-Org-ID": "org123"}
        
        with caplog.at_level("WARNING"):
            response = client.get("/api/test/org456", headers=headers)
        
        assert response.status_code == 403
        
        # Check that security event was logged
        log_records = [r for r in caplog.records if "SECURITY_EVENT" in r.message]
        assert len(log_records) > 0
        
        # Parse and validate log content
        log_message = log_records[0].message
        assert "access_violation" in log_message
        assert "org123" in log_message
        assert "org456" in log_message


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_org_id_in_path(self):
        """Test handling of empty org_id in path"""
        response = client.get("/api/test/")
        # Should return 404 (not found) rather than 403
        assert response.status_code == 404
    
    def test_special_characters_in_org_id(self):
        """Test org_id with special characters"""
        headers = {"X-Org-ID": "org-123_test"}
        response = client.get("/api/test/org-123_test", headers=headers)
        assert response.status_code == 200
    
    def test_case_sensitive_org_id(self):
        """Test that org_id comparison is case-sensitive"""
        headers = {"X-Org-ID": "ORG123"}
        response = client.get("/api/test/org123", headers=headers)
        # Should be blocked because case doesn't match
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
