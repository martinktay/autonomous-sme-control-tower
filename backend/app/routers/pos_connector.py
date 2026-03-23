"""POS Connector endpoints — POS system integration and data extraction."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query
from app.agents.pos_agent import get_pos_agent
from app.services.transaction_service import get_transaction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pos", tags=["pos-connector"])


@router.post("/import", response_model=Dict[str, Any])
async def import_pos_data(
    file: UploadFile = File(...),
    x_org_id: str = Header(..., alias="X-Org-ID"),
    pos_system: str = Query("unknown", description="POS system name"),
    business_name: str = Query("", description="Business name"),
):
    """Import and parse a POS system export file."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="replace")

        agent = get_pos_agent()
        result = agent.extract_pos_data(
            pos_data=text_content,
            pos_system=pos_system,
            business_name=business_name,
        )

        # Auto-create transactions from POS data
        tx_svc = get_transaction_service()
        created = 0
        for tx in result.get("transactions", []):
            try:
                from app.models.transaction import TransactionCreate
                tx_data = TransactionCreate(
                    description=f"POS sale - {tx.get('receipt_number', 'N/A')}",
                    amount=float(tx.get("total_amount", 0)),
                    transaction_type="revenue",
                    category="pos_sale",
                    date=tx.get("date"),
                )
                tx_svc.create_transaction(x_org_id, tx_data)
                created += 1
            except Exception as e:
                logger.warning("Skipped POS transaction: %s", e)

        result["transactions_created"] = created
        result["org_id"] = x_org_id
        return result

    except Exception as e:
        logger.error("POS import failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="POS import failed. Please try again.")


@router.get("/systems", response_model=Dict[str, Any])
async def list_supported_systems():
    """List supported POS systems for Nigerian SMEs."""
    return {
        "supported_systems": [
            {"name": "Generic CSV", "id": "generic_csv", "status": "available"},
            {"name": "Moniepoint POS", "id": "moniepoint", "status": "available"},
            {"name": "Opay POS", "id": "opay", "status": "available"},
            {"name": "Palmpay POS", "id": "palmpay", "status": "available"},
            {"name": "Kudi POS", "id": "kudi", "status": "coming_soon"},
            {"name": "Nomba POS", "id": "nomba", "status": "coming_soon"},
        ],
        "note": "Upload any CSV/Excel export from your POS system. Our AI will auto-detect the format.",
    }
