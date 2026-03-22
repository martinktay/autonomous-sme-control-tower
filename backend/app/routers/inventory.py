"""Inventory management endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header
from app.models.inventory_item import InventoryItemCreate, InventoryItemUpdate
from app.services.inventory_service import get_inventory_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_inventory(x_org_id: str = Header(..., alias="X-Org-ID")):
    """List inventory items for the business."""
    svc = get_inventory_service()
    return svc.list_items(x_org_id)


@router.post("", response_model=Dict[str, Any])
async def create_item(data: InventoryItemCreate, x_org_id: str = Header(..., alias="X-Org-ID")):
    """Add a new inventory item."""
    try:
        svc = get_inventory_service()
        item = svc.create_item(x_org_id, data)
        return item.model_dump(mode="json")
    except Exception as e:
        logger.error("Inventory item creation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create inventory item")


@router.put("/{item_id}", response_model=Dict[str, Any])
async def update_item(item_id: str, data: InventoryItemUpdate, x_org_id: str = Header(..., alias="X-Org-ID")):
    """Update an inventory item."""
    try:
        svc = get_inventory_service()
        result = svc.update_item(x_org_id, item_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Inventory update failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update inventory item")


@router.get("/alerts", response_model=List[Dict[str, Any]])
async def get_stock_alerts(x_org_id: str = Header(..., alias="X-Org-ID")):
    """Get low stock alerts for the business."""
    svc = get_inventory_service()
    return svc.get_low_stock_alerts(x_org_id)


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics(x_org_id: str = Header(..., alias="X-Org-ID")):
    """Get inventory analytics — total items, low stock count, stock value."""
    svc = get_inventory_service()
    return svc.get_analytics(x_org_id)
