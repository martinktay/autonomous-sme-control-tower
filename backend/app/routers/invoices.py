from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime
from app.agents.signal_agent import SignalAgent
from app.services.s3_service import get_s3_service
from app.services.ddb_service import get_ddb_service
from app.models import Signal, SignalType

router = APIRouter(prefix="/api/invoices", tags=["invoices"])
signal_agent = SignalAgent()
s3_service = get_s3_service()
ddb_service = get_ddb_service()


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
    file_content = await file.read()
    
    # Upload to S3
    s3_key = f"invoices/{org_id}/{signal_id}/{file.filename}"
    s3_service.upload_file(file_content, s3_key)
    
    # Extract invoice data (placeholder for OCR + extraction)
    invoice_text = "Invoice text placeholder"  # TODO: Add OCR
    extracted_data = signal_agent.extract_invoice(invoice_text)
    
    # Store signal
    signal = Signal(
        signal_id=signal_id,
        org_id=org_id,
        signal_type=SignalType.INVOICE,
        s3_key=s3_key,
        extracted_data=extracted_data,
        processed=True
    )
    
    ddb_service.put_signal(signal.model_dump())
    
    return {
        "signal_id": signal_id,
        "org_id": org_id,
        "status": "processed",
        "extracted_data": extracted_data
    }


@router.get("/{org_id}")
async def get_invoices(org_id: str) -> Dict[str, Any]:
    """Get invoice signals for organization"""
    
    signals = ddb_service.get_signals(org_id)
    invoices = [s for s in signals if s.get("signal_type") == "invoice"]
    
    return {
        "org_id": org_id,
        "invoices": invoices
    }
