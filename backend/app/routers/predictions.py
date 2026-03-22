"""Inventory Prediction endpoints — demand forecasting and reorder suggestions."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Header
from app.agents.prediction_agent import get_prediction_agent
from app.services.inventory_service import get_inventory_service
from app.services.transaction_service import get_transaction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/{org_id}/demand", response_model=Dict[str, Any])
async def get_demand_forecast(
    org_id: str,
    business_name: str = "",
    business_type: str = "supermarket",
):
    """Generate AI demand forecast with reorder suggestions."""
    try:
        inv_svc = get_inventory_service()
        tx_svc = get_transaction_service()

        inventory = inv_svc.list_items(org_id, limit=100)
        transactions = tx_svc.list_transactions(org_id, limit=300)

        # Filter to revenue transactions (sales) for demand signal
        sales = [t for t in transactions if t.get("transaction_type") == "revenue"]

        agent = get_prediction_agent()
        forecast = agent.predict_demand(
            sales_data=sales,
            inventory_data=inventory,
            business_type=business_type,
            business_name=business_name,
        )
        forecast["org_id"] = org_id
        return forecast

    except Exception as e:
        logger.error("Demand prediction failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate demand forecast")


@router.get("/{org_id}/reorder", response_model=Dict[str, Any])
async def get_reorder_suggestions(org_id: str):
    """Get quick reorder suggestions based on stock levels and sales velocity."""
    try:
        inv_svc = get_inventory_service()
        tx_svc = get_transaction_service()

        inventory = inv_svc.list_items(org_id, limit=200)
        transactions = tx_svc.list_transactions(org_id, limit=200)
        sales = [t for t in transactions if t.get("transaction_type") == "revenue"]

        suggestions = []
        for item in inventory:
            qty = float(item.get("quantity_on_hand", 0))
            reorder_pt = float(item.get("reorder_point", 0) or 0)
            name = item.get("name", "Unknown")
            item_id = item.get("item_id", "")

            # Count sales mentioning this item
            sale_count = sum(
                1 for s in sales
                if name.lower() in s.get("description", "").lower()
            )
            avg_daily = sale_count / 30 if sale_count > 0 else 0
            days_remaining = qty / avg_daily if avg_daily > 0 else 999

            if days_remaining < 14 or qty <= reorder_pt:
                urgency = "immediate" if days_remaining < 3 or qty == 0 else "soon" if days_remaining < 7 else "routine"
                suggested_qty = max(int(avg_daily * 14 - qty), int(reorder_pt * 2))
                suggestions.append({
                    "item_name": name,
                    "item_id": item_id,
                    "current_stock": qty,
                    "avg_daily_sales": round(avg_daily, 1),
                    "days_remaining": round(days_remaining, 1),
                    "suggested_quantity": max(suggested_qty, 1),
                    "urgency": urgency,
                })

        suggestions.sort(key=lambda x: x["days_remaining"])
        return {"org_id": org_id, "suggestions": suggestions}

    except Exception as e:
        logger.error("Reorder suggestions failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate reorder suggestions")
