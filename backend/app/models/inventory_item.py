"""Inventory item model with extension attributes for business-type-specific fields."""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InventoryItem(BaseModel):
    """Inventory item tracked per business/branch."""

    item_id: str = Field(..., description="Unique item identifier")
    business_id: str = Field(..., description="Business identifier")
    branch_id: Optional[str] = None
    product_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=300)
    sku: Optional[str] = None
    quantity_on_hand: float = Field(default=0, ge=0)
    unit: str = Field(default="units", max_length=30)
    unit_cost: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    reorder_point: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None
    extension_attrs: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=_utc_now)
    created_at: datetime = Field(default_factory=_utc_now)


class InventoryItemCreate(BaseModel):
    """Request body for adding an inventory item."""

    branch_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=300)
    sku: Optional[str] = None
    quantity_on_hand: float = 0
    unit: str = "units"
    unit_cost: Optional[float] = None
    selling_price: Optional[float] = None
    reorder_point: Optional[float] = None
    category: Optional[str] = None
    extension_attrs: Dict[str, Any] = Field(default_factory=dict)


class InventoryItemUpdate(BaseModel):
    """Request body for updating an inventory item."""

    name: Optional[str] = None
    quantity_on_hand: Optional[float] = None
    unit_cost: Optional[float] = None
    selling_price: Optional[float] = None
    reorder_point: Optional[float] = None
    category: Optional[str] = None
    extension_attrs: Optional[Dict[str, Any]] = None
