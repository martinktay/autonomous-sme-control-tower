"""Inventory management service — CRUD, stock alerts, analytics."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.inventory_item import InventoryItem, InventoryItemCreate, InventoryItemUpdate
from app.services.ddb_service import get_ddb_service
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()


class InventoryService:
    """Manages inventory items, stock alerts, and basic analytics."""

    def __init__(self):
        self.ddb = get_ddb_service()
        self.table = settings.inventory_table

    def create_item(self, business_id: str, data: InventoryItemCreate) -> InventoryItem:
        """Add a new inventory item."""
        now = datetime.now(timezone.utc)
        item = InventoryItem(
            item_id=generate_id("inventory_item"),
            business_id=business_id,
            branch_id=data.branch_id,
            name=data.name,
            sku=data.sku,
            quantity_on_hand=data.quantity_on_hand,
            unit=data.unit,
            unit_cost=data.unit_cost,
            selling_price=data.selling_price,
            reorder_point=data.reorder_point,
            category=data.category,
            extension_attrs=data.extension_attrs,
            last_updated=now,
            created_at=now,
        )
        self.ddb.put_item(self.table, {
            "business_id": item.business_id,
            "item_id": item.item_id,
            **item.model_dump(mode="json"),
        })
        logger.info("Created inventory item %s for business %s", item.item_id, business_id)
        return item

    def get_item(self, business_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single inventory item."""
        return self.ddb.get_item(self.table, {
            "business_id": {"S": business_id},
            "item_id": {"S": item_id},
        })

    def list_items(self, business_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List inventory items for a business."""
        return self.ddb.query_items(
            table_name=self.table,
            key_condition="org_id = :bid",
            expression_values={":bid": business_id},
            limit=limit,
        )

    def update_item(self, business_id: str, item_id: str, data: InventoryItemUpdate) -> Optional[Dict[str, Any]]:
        """Update inventory item fields."""
        updates = data.model_dump(exclude_none=True)
        if not updates:
            return self.get_item(business_id, item_id)

        updates["last_updated"] = datetime.now(timezone.utc).isoformat()

        expr_parts = []
        expr_values = {}
        expr_names = {}
        for i, (key, value) in enumerate(updates.items()):
            attr_name = f"#a{i}"
            attr_val = f":v{i}"
            expr_parts.append(f"{attr_name} = {attr_val}")
            expr_names[attr_name] = key
            expr_values[attr_val] = self.ddb._convert_to_dynamodb_format({attr_val: value})[attr_val]

        try:
            self.ddb.client.update_item(
                TableName=self.table,
                Key={
                    "business_id": {"S": business_id},
                    "item_id": {"S": item_id},
                },
                UpdateExpression="SET " + ", ".join(expr_parts),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
            )
            return self.get_item(business_id, item_id)
        except Exception as e:
            logger.error("Failed to update inventory item %s: %s", item_id, e)
            raise

    def get_low_stock_alerts(self, business_id: str) -> List[Dict[str, Any]]:
        """Return items where quantity_on_hand <= reorder_point."""
        items = self.list_items(business_id, limit=500)
        alerts = []
        for item in items:
            reorder = item.get("reorder_point")
            qty = item.get("quantity_on_hand", 0)
            if reorder is not None and float(qty) <= float(reorder):
                alerts.append({
                    "item_id": item.get("item_id"),
                    "name": item.get("name"),
                    "quantity_on_hand": qty,
                    "reorder_point": reorder,
                    "severity": "critical" if float(qty) == 0 else "warning",
                })
        return alerts

    def get_analytics(self, business_id: str) -> Dict[str, Any]:
        """Basic inventory analytics — total items, low stock count, total value."""
        items = self.list_items(business_id, limit=500)
        total_items = len(items)
        low_stock = 0
        total_value = 0.0

        for item in items:
            qty = float(item.get("quantity_on_hand", 0))
            cost = float(item.get("unit_cost", 0) or 0)
            total_value += qty * cost

            reorder = item.get("reorder_point")
            if reorder is not None and qty <= float(reorder):
                low_stock += 1

        return {
            "total_items": total_items,
            "low_stock_count": low_stock,
            "estimated_stock_value": round(total_value, 2),
        }


def get_inventory_service() -> InventoryService:
    return InventoryService()
