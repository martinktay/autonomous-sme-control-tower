"""Counterparty (supplier/customer) management endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header, Request
from app.models.counterparty import CounterpartyCreate
from app.services.counterparty_service import get_counterparty_service
from app.middleware.auth import require_role

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/counterparties", tags=["counterparties"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_counterparties(x_org_id: str = Header(..., alias="X-Org-ID")):
    """List suppliers and customers for the business."""
    svc = get_counterparty_service()
    return svc.list_counterparties(x_org_id)


@router.post("", response_model=Dict[str, Any])
async def create_counterparty(request: Request, data: CounterpartyCreate, x_org_id: str = Header(..., alias="X-Org-ID")):
    """Create a new supplier or customer (member+ only)."""
    require_role(request, "member")
    try:
        svc = get_counterparty_service()
        cp = svc.create_counterparty(x_org_id, data)
        return cp.model_dump(mode="json")
    except Exception as e:
        logger.error("Counterparty creation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create counterparty")


@router.get("/{counterparty_id}/balance", response_model=Dict[str, Any])
async def get_balance(counterparty_id: str, x_org_id: str = Header(..., alias="X-Org-ID")):
    """Get balance summary for a counterparty."""
    svc = get_counterparty_service()
    result = svc.get_balance_summary(x_org_id, counterparty_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
