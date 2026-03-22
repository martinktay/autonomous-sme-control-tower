"""Alert management endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Header
from app.services.alert_service import get_alert_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_alerts(x_org_id: str = Header(..., alias="X-Org-ID")):
    """List alerts for the business."""
    svc = get_alert_service()
    return svc.list_alerts(x_org_id)


@router.put("/{alert_id}/read")
async def mark_alert_read(alert_id: str, x_org_id: str = Header(..., alias="X-Org-ID")):
    """Mark an alert as read."""
    svc = get_alert_service()
    svc.mark_read(x_org_id, alert_id)
    return {"status": "ok"}
