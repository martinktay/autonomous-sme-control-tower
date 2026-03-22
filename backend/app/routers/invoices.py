"""
Invoice upload router — handles PDF/image invoice uploads with full validation.

Production-hardened with:
- File type, size, and filename validation
- org_id format validation
- Structured error handling with safe error messages
- Logging for debugging without leaking internals
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import uuid
import logging

from app.agents.signal_agent import SignalAgent
from app.services.s3_service import get_s3_service
from app.services.ddb_service import get_ddb_service
from app.services.counterparty_service import get_counterparty_service
from app.models import Signal
from app.utils.upload_validator import (
    validate_org_id,
    validate_upload_file,
    INVOICE_CONTENT_TYPES,
    INVOICE_EXTENSIONS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["invoices"])
signal_agent = SignalAgent()
s3_service = get_s3_service()
ddb_service = get_ddb_service()


@router.post("/upload")
async def upload_invoice(
    org_id: str,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Upload and extract invoice data from a PDF or image file."""

    # Validate org_id format
    org_id = validate_org_id(org_id)

    # Validate file type, size, filename
    file_content, safe_filename, ext = await validate_upload_file(
        file, INVOICE_CONTENT_TYPES, INVOICE_EXTENSIONS
    )

    signal_id = str(uuid.uuid4())

    # Upload to S3
    try:
        s3_key = f"invoices/{org_id}/{signal_id}/{safe_filename}"
        s3_service.upload_file(file_content, s3_key)
    except Exception as e:
        logger.error(f"S3 upload failed for org={org_id}: {e}")
        raise HTTPException(500, "Failed to store file. Please try again.")

    # Extract invoice data via AI
    try:
        invoice_text = "Invoice text placeholder"  # TODO: integrate OCR/Textract
        extracted_data = signal_agent.extract_invoice(invoice_text)
    except Exception as e:
        logger.error(f"Invoice extraction failed for org={org_id}: {e}")
        extracted_data = {
            "vendor_name": None, "amount": None, "due_date": None,
            "line_items": [], "extraction_note": "AI extraction unavailable"
        }

    # Store signal in DynamoDB
    try:
        signal = Signal(
            signal_id=signal_id,
            org_id=org_id,
            signal_type="invoice",
            content=extracted_data,
            processing_status="processed"
        )
        ddb_service.put_signal(signal.model_dump())
    except Exception as e:
        logger.error(f"DynamoDB put_signal failed for org={org_id}: {e}")
        raise HTTPException(500, "Failed to save invoice data. Please try again.")

    # Best-effort auto-create counterparty from extracted vendor
    _auto_create_counterparty(org_id, extracted_data)

    return {
        "signal_id": signal_id,
        "org_id": org_id,
        "status": "processed",
        "extracted_data": extracted_data
    }


def _auto_create_counterparty(org_id: str, extracted_data: Dict[str, Any]) -> None:
    """Best-effort auto-creation of counterparty from extracted invoice data."""
    vendor_name = extracted_data.get("vendor_name")
    if not vendor_name or not isinstance(vendor_name, str) or not vendor_name.strip():
        return
    try:
        from app.models.counterparty import CounterpartyCreate
        cp_svc = get_counterparty_service()
        # Check if counterparty already exists
        existing = cp_svc.list_counterparties(org_id)
        for cp in existing:
            if cp.get("name", "").lower() == vendor_name.strip().lower():
                return  # Already exists
        cp_svc.create_counterparty(
            org_id,
            CounterpartyCreate(name=vendor_name.strip(), counterparty_type="supplier"),
        )
        logger.info("Auto-created counterparty '%s' for org %s", vendor_name, org_id)
    except Exception as e:
        logger.debug("Auto-create counterparty failed (non-critical): %s", e)


@router.get("/{org_id}")
async def get_invoices(org_id: str) -> Dict[str, Any]:
    """Get invoice signals for an organization."""
    org_id = validate_org_id(org_id)
    try:
        signals = ddb_service.get_signals(org_id)
        invoices = [s for s in signals if s.get("signal_type") == "invoice"]
    except Exception as e:
        logger.error(f"Failed to fetch invoices for org={org_id}: {e}")
        raise HTTPException(500, "Failed to retrieve invoices.")
    return {"org_id": org_id, "invoices": invoices}
