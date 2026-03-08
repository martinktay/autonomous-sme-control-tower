from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import uuid

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/upload")
async def upload_invoice(
    org_id: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Upload and extract invoice data"""
    
    if not file.content_type or "pdf" not in file.content_type.lower():
        if not file.content_type or "image" not in file.content_type.lower():
            raise HTTPException(400, "Only PDF and image files supported")
    
    signal_id = str(uuid.uuid4())
    
    # TODO: Implement signal agent extraction
    
    return {
        "signal_id": signal_id,
        "org_id": org_id,
        "status": "processing",
        "message": "Invoice uploaded successfully"
    }


@router.get("/{org_id}")
async def get_invoices(org_id: str) -> Dict[str, Any]:
    """Get invoice signals for organization"""
    
    # TODO: Retrieve from DynamoDB
    
    return {
        "org_id": org_id,
        "invoices": []
    }
