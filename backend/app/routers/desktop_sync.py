"""Desktop Sync endpoints — POS file upload and automated data extraction."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Query
from app.agents.desktop_sync_agent import get_desktop_sync_agent
from app.services.transaction_service import get_transaction_service
from app.services.ddb_service import get_ddb_service
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/desktop-sync", tags=["desktop-sync"])


@router.post("/upload", response_model=Dict[str, Any])
async def upload_sync_file(
    file: UploadFile = File(...),
    x_org_id: str = Header(..., alias="X-Org-ID"),
    business_name: str = Query("", description="Business name for context"),
    business_type: str = Query("supermarket", description="Business type"),
):
    """Upload a POS export file for AI extraction and ingestion."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8", errors="replace")

        agent = get_desktop_sync_agent()
        result = agent.extract_file_data(
            file_content=text_content,
            filename=file.filename or "unknown",
            file_type=file.content_type or "unknown",
            business_type=business_type,
            business_name=business_name,
        )

        # Auto-create transactions from extracted records
        records = result.get("records", [])
        tx_svc = get_transaction_service()
        created = 0
        for record in records:
            try:
                from app.models.transaction import TransactionCreate
                tx_data = TransactionCreate(
                    description=record.get("description", "POS import"),
                    amount=float(record.get("amount", 0)),
                    transaction_type=record.get("type", "revenue"),
                    category=record.get("category", "pos_import"),
                    date=record.get("date"),
                )
                tx_svc.create_transaction(x_org_id, tx_data)
                created += 1
            except Exception as e:
                logger.warning("Skipped record: %s", e)

        result["transactions_created"] = created
        result["org_id"] = x_org_id
        return result

    except Exception as e:
        logger.error("Desktop sync upload failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="File processing failed. Please try again.")


@router.get("/status", response_model=Dict[str, Any])
async def get_sync_status(x_org_id: str = Header(..., alias="X-Org-ID")):
    """Get desktop sync status — placeholder for companion app heartbeat."""
    return {
        "org_id": x_org_id,
        "sync_enabled": True,
        "last_sync": None,
        "watched_folders": [],
        "message": "Desktop sync agent ready. Install the companion app to enable automatic file watching.",
    }
