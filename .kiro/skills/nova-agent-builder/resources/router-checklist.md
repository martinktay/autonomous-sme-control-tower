# Router Checklist

When adding or updating a router:

- Define request/response schema
- Validate inputs
- Call the correct agent/service
- Return predictable structured JSON
- Avoid embedding business logic in router
- Avoid embedding long prompts in router
- Log errors clearly
- Keep route names aligned with domain

## Expected router locations

```
backend/app/routers/
```

## Router structure example

```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.invoice import Invoice, InvoiceUploadRequest
from app.agents.signal_agent import SignalAgent
from app.utils.auth import get_current_org_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

@router.post("/upload", response_model=Invoice)
async def upload_invoice(
    request: InvoiceUploadRequest,
    org_id: str = Depends(get_current_org_id)
):
    """
    Upload and process invoice document
    
    Args:
        request: Invoice upload request with file content
        org_id: Organization identifier from auth context
        
    Returns:
        Invoice: Processed invoice with extracted data
    """
    try:
        # Delegate to agent
        agent = SignalAgent()
        signal = await agent.process_invoice(
            org_id=org_id,
            file_content=request.file_content,
            filename=request.filename
        )
        
        # Return structured response
        return Invoice(**signal.content)
        
    except Exception as e:
        logger.error(f"Invoice upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Invoice processing failed")

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: str,
    org_id: str = Depends(get_current_org_id)
):
    """Retrieve invoice by ID"""
    # Implementation here
    pass

@router.get("/", response_model=list[Invoice])
async def list_invoices(
    org_id: str = Depends(get_current_org_id),
    limit: int = 50
):
    """List invoices for organization"""
    # Implementation here
    pass
```

## Key principles

1. **Thin routers**: Business logic belongs in agents/services
2. **Clear contracts**: Use Pydantic models for request/response
3. **Error handling**: Catch exceptions and return appropriate HTTP status codes
4. **Data isolation**: Always filter by org_id from auth context
5. **Logging**: Log errors with context for debugging
