"""Transaction management endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header
from app.models.transaction import TransactionCreate
from app.services.transaction_service import get_transaction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_transactions(x_org_id: str = Header(..., alias="X-Org-ID")):
    """List transactions for the business."""
    svc = get_transaction_service()
    return svc.list_transactions(x_org_id)


@router.post("", response_model=Dict[str, Any])
async def create_transaction(data: TransactionCreate, x_org_id: str = Header(..., alias="X-Org-ID")):
    """Create a new transaction."""
    try:
        svc = get_transaction_service()
        txn = svc.create_transaction(x_org_id, data)
        return txn.model_dump(mode="json")
    except Exception as e:
        logger.error("Transaction creation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create transaction")


@router.get("/summary", response_model=Dict[str, Any])
async def get_summary(x_org_id: str = Header(..., alias="X-Org-ID")):
    """Revenue vs expense summary."""
    svc = get_transaction_service()
    return svc.get_summary(x_org_id)


@router.get("/cashflow", response_model=List[Dict[str, Any]])
async def get_cashflow(x_org_id: str = Header(..., alias="X-Org-ID")):
    """Cashflow data for charting (money in vs money out by day)."""
    svc = get_transaction_service()
    return svc.get_cashflow(x_org_id)
