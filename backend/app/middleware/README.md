# Organization Isolation Middleware

## Overview

The `OrgIsolationMiddleware` enforces multi-tenancy by validating `org_id` from request context and preventing cross-organization data access.

## Features

- ✅ Validates `org_id` from request headers (X-Org-ID)
- ✅ Extracts `org_id` from path parameters and query strings
- ✅ Prevents cross-organization access attempts
- ✅ Logs security events for access violations
- ✅ Returns HTTP 403 for unauthorized access attempts
- ✅ Supports body-based org_id validation in route handlers

## How It Works

### 1. Path/Query Parameter Validation

The middleware automatically validates `org_id` from:
- Path parameters: `/api/invoices/{org_id}`
- Query parameters: `/api/invoices?org_id=org123`

If the authenticated `org_id` (from `X-Org-ID` header) doesn't match the requested `org_id`, the request is blocked with HTTP 403.

### 2. Request Body Validation

For POST/PUT/PATCH requests where `org_id` is in the request body, route handlers must explicitly validate using the `validate_org_id_from_body()` helper function.

## Usage in Route Handlers

### Path Parameter Example

```python
from fastapi import APIRouter, Request
from app.middleware import get_org_id_from_request

router = APIRouter()

@router.get("/api/invoices/{org_id}")
async def get_invoices(org_id: str, request: Request):
    # Middleware already validated org_id from path
    # Get the validated org_id from request state
    validated_org_id = get_org_id_from_request(request)
    
    # Query DynamoDB with org_id
    invoices = await ddb_service.query_invoices(validated_org_id)
    return invoices
```

### Request Body Example

```python
from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.middleware import validate_org_id_from_body

router = APIRouter()

class InvoiceCreate(BaseModel):
    org_id: str
    vendor_name: str
    amount: float

@router.post("/api/invoices")
async def create_invoice(request: Request, invoice: InvoiceCreate):
    # Validate org_id from request body
    validate_org_id_from_body(request, invoice.org_id)
    
    # Proceed with invoice creation
    result = await ddb_service.create_invoice(invoice)
    return result
```

## Security Events

The middleware logs security events in structured JSON format:

### Access Violation Event

```json
{
  "event_type": "access_violation",
  "timestamp": "2024-03-09T12:34:56.789Z",
  "severity": "high",
  "authenticated_org_id": "org123",
  "requested_org_id": "org456",
  "path": "/api/invoices/org456",
  "method": "GET",
  "client_ip": "192.168.1.1",
  "message": "Organization org123 attempted to access data for organization org456"
}
```

### Missing Org ID Event

```json
{
  "event_type": "missing_org_id",
  "timestamp": "2024-03-09T12:34:56.789Z",
  "severity": "medium",
  "path": "/api/invoices",
  "method": "GET",
  "client_ip": "192.168.1.1",
  "message": "Request missing required org_id"
}
```

## Exempt Paths

The following paths are exempt from org_id validation:
- `/` - Root endpoint
- `/health` - Health check
- `/docs` - API documentation
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

## Testing

Run the test suite:

```bash
cd backend
PYTHONPATH=$PWD pytest tests/test_org_isolation.py -v
```

## Production Considerations

Currently, the middleware allows requests without the `X-Org-ID` header for development purposes. In production:

1. Implement proper authentication (JWT tokens, OAuth, etc.)
2. Extract `org_id` from authenticated user session
3. Reject all requests without valid authentication
4. Consider rate limiting per organization
5. Monitor security event logs for suspicious patterns
