"""
WhatsApp integration router — webhook for incoming messages and insight delivery.

Endpoints:
- POST /api/whatsapp/webhook     — Receive incoming WhatsApp messages (webhook)
- POST /api/whatsapp/ingest      — Manual message ingestion (for testing)
- POST /api/whatsapp/summary     — Generate and return a WhatsApp insight summary
- GET  /api/whatsapp/{org_id}/messages — List processed WhatsApp messages
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.whatsapp_agent import WhatsAppAgent
from app.services.ddb_service import get_ddb_service
from app.models import Signal
from app.utils.upload_validator import validate_org_id
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])
whatsapp_agent = WhatsAppAgent()
ddb_service = get_ddb_service()


# --- Request models ---

class WhatsAppWebhookPayload(BaseModel):
    """Simplified WhatsApp Business API webhook payload."""
    phone_number: str
    message_text: str
    org_id: str
    sender_name: Optional[str] = None
    media_url: Optional[str] = None
    timestamp: Optional[str] = None


class IngestMessageRequest(BaseModel):
    """Manual message ingestion for testing."""
    org_id: str
    message_text: str
    sender_name: Optional[str] = None
    sender_phone: Optional[str] = None


class SummaryRequest(BaseModel):
    """Request for WhatsApp insight summary."""
    org_id: str
    business_name: Optional[str] = "Your Business"


# --- Webhook endpoint ---

@router.post("/webhook")
async def whatsapp_webhook(payload: WhatsAppWebhookPayload) -> Dict[str, Any]:
    """Receive and process an incoming WhatsApp message.

    This endpoint would be called by the WhatsApp Business API webhook.
    It extracts business data from the message and stores it as a signal.
    """
    org_id = validate_org_id(payload.org_id)
    signal_id = generate_id("signal")

    try:
        extracted = whatsapp_agent.extract_message(payload.message_text)
    except Exception as e:
        logger.error("WhatsApp extraction failed for org=%s: %s", org_id, e)
        extracted = {
            "message_type": "other",
            "description": payload.message_text[:200],
            "confidence": 0.0,
        }

    # Store as signal
    content = {
        **extracted,
        "sender_phone": payload.phone_number,
        "sender_name": payload.sender_name,
        "raw_message": payload.message_text[:1000],
        "media_url": payload.media_url,
    }

    signal = Signal(
        signal_id=signal_id,
        org_id=org_id,
        signal_type="whatsapp",
        content=content,
        processing_status="processed",
    )

    try:
        ddb_service.put_signal(signal.model_dump())
    except Exception as e:
        logger.error("Failed to store WhatsApp signal for org=%s: %s", org_id, e)
        raise HTTPException(500, "Failed to save message.")

    # Auto-create counterparty if vendor/customer name extracted
    _auto_create_counterparty_from_whatsapp(org_id, extracted)

    return {
        "signal_id": signal_id,
        "org_id": org_id,
        "message_type": extracted.get("message_type", "other"),
        "extracted_data": extracted,
    }


# --- Manual ingestion (testing) ---

@router.post("/ingest")
async def ingest_message(request: IngestMessageRequest) -> Dict[str, Any]:
    """Manually ingest a WhatsApp message for testing purposes."""
    org_id = validate_org_id(request.org_id)
    signal_id = generate_id("signal")

    try:
        extracted = whatsapp_agent.extract_message(request.message_text)
    except Exception as e:
        logger.error("WhatsApp extraction failed for org=%s: %s", org_id, e)
        extracted = {
            "message_type": "other",
            "description": request.message_text[:200],
            "confidence": 0.0,
        }

    content = {
        **extracted,
        "sender_phone": request.sender_phone,
        "sender_name": request.sender_name,
        "raw_message": request.message_text[:1000],
    }

    signal = Signal(
        signal_id=signal_id,
        org_id=org_id,
        signal_type="whatsapp",
        content=content,
        processing_status="processed",
    )

    try:
        ddb_service.put_signal(signal.model_dump())
    except Exception as e:
        logger.error("Failed to store WhatsApp signal for org=%s: %s", org_id, e)
        raise HTTPException(500, "Failed to save message.")

    return {
        "signal_id": signal_id,
        "org_id": org_id,
        "message_type": extracted.get("message_type", "other"),
        "extracted_data": extracted,
    }


# --- Insight summary ---

@router.post("/summary")
async def generate_summary(request: SummaryRequest) -> Dict[str, Any]:
    """Generate a WhatsApp-friendly business insight summary."""
    org_id = validate_org_id(request.org_id)

    # Gather context
    nsi_score = None
    top_risks = []
    txn_summary = None
    stock_alerts = None

    try:
        from app.services.ddb_service import get_ddb_service
        ddb = get_ddb_service()
        # Get latest NSI
        signals = ddb.get_signals(org_id)
        nsi_signals = [s for s in signals if s.get("signal_type") == "nsi_snapshot"]
        if nsi_signals:
            latest = nsi_signals[-1]
            nsi_score = latest.get("content", {}).get("nsi_score")
            top_risks = latest.get("content", {}).get("top_risks", [])
    except Exception:
        logger.debug("Could not fetch NSI for WhatsApp summary")

    try:
        from app.services.transaction_service import get_transaction_service
        txn_summary = get_transaction_service().get_summary(org_id)
    except Exception:
        logger.debug("Could not fetch transaction summary for WhatsApp")

    try:
        from app.services.inventory_service import get_inventory_service
        alerts = get_inventory_service().get_low_stock_alerts(org_id)
        if alerts:
            stock_alerts = alerts[:5]
    except Exception:
        logger.debug("Could not fetch stock alerts for WhatsApp")

    try:
        summary = whatsapp_agent.generate_insight_summary(
            business_name=request.business_name or "Your Business",
            nsi_score=nsi_score,
            top_risks=top_risks,
            transaction_summary=txn_summary,
            stock_alerts=stock_alerts,
        )
        formatted = whatsapp_agent.format_summary_for_whatsapp(summary)
    except Exception as e:
        logger.error("WhatsApp summary generation failed for org=%s: %s", org_id, e)
        raise HTTPException(500, "Failed to generate summary.")

    return {
        "org_id": org_id,
        "summary": summary,
        "formatted_text": formatted,
    }


# --- Message history ---

@router.get("/{org_id}/messages")
async def get_whatsapp_messages(org_id: str) -> Dict[str, Any]:
    """List processed WhatsApp messages for an organization."""
    org_id = validate_org_id(org_id)
    try:
        signals = ddb_service.get_signals(org_id)
        messages = [s for s in signals if s.get("signal_type") == "whatsapp"]
    except Exception as e:
        logger.error("Failed to fetch WhatsApp messages for org=%s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve messages.")
    return {"org_id": org_id, "messages": messages, "count": len(messages)}


# --- Helpers ---

def _auto_create_counterparty_from_whatsapp(org_id: str, extracted: Dict[str, Any]) -> None:
    """Best-effort auto-creation of counterparty from WhatsApp message data."""
    name = extracted.get("vendor_name") or extracted.get("customer_name")
    if not name or not isinstance(name, str) or not name.strip():
        return
    try:
        from app.models.counterparty import CounterpartyCreate
        from app.services.counterparty_service import get_counterparty_service
        cp_svc = get_counterparty_service()
        existing = cp_svc.list_counterparties(org_id)
        for cp in existing:
            if cp.get("name", "").lower() == name.strip().lower():
                return
        cp_type = "customer" if extracted.get("customer_name") else "supplier"
        cp_svc.create_counterparty(
            org_id,
            CounterpartyCreate(name=name.strip(), counterparty_type=cp_type),
        )
        logger.info("Auto-created counterparty '%s' from WhatsApp for org %s", name, org_id)
    except Exception as e:
        logger.debug("Auto-create counterparty from WhatsApp failed (non-critical): %s", e)
