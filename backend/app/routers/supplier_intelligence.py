"""Supplier Intelligence endpoints — scoring, risk analysis, recommendations."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Header
from app.agents.supplier_agent import get_supplier_agent
from app.services.counterparty_service import get_counterparty_service
from app.services.transaction_service import get_transaction_service
from app.services.inventory_service import get_inventory_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/supplier-intelligence", tags=["supplier-intelligence"])


@router.get("/{org_id}/report", response_model=Dict[str, Any])
async def get_supplier_report(
    org_id: str,
    business_name: str = "",
    business_type: str = "supermarket",
):
    """Generate AI supplier intelligence report with scores and recommendations."""
    try:
        cp_svc = get_counterparty_service()
        tx_svc = get_transaction_service()
        inv_svc = get_inventory_service()

        suppliers = cp_svc.list_counterparties(org_id)
        # Filter to suppliers only
        supplier_list = [s for s in suppliers if s.get("counterparty_type") == "supplier"]

        transactions = tx_svc.list_transactions(org_id, limit=200)
        inventory = inv_svc.list_items(org_id, limit=100)

        agent = get_supplier_agent()
        report = agent.analyse_suppliers(
            supplier_data=supplier_list,
            transaction_data=transactions,
            inventory_data=inventory,
            business_type=business_type,
            business_name=business_name,
        )
        report["org_id"] = org_id
        return report

    except Exception as e:
        logger.error("Supplier intelligence failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate supplier report")


@router.get("/{org_id}/scores", response_model=List[Dict[str, Any]])
async def get_supplier_scores(org_id: str):
    """Get supplier reliability scores (lightweight — from cached report or quick calc)."""
    try:
        cp_svc = get_counterparty_service()
        tx_svc = get_transaction_service()

        suppliers = cp_svc.list_counterparties(org_id)
        supplier_list = [s for s in suppliers if s.get("counterparty_type") == "supplier"]
        transactions = tx_svc.list_transactions(org_id, limit=200)

        # Quick heuristic scoring without full AI call
        scores = []
        for supplier in supplier_list:
            sid = supplier.get("counterparty_id", "")
            name = supplier.get("name", "Unknown")
            tx_count = sum(
                1 for t in transactions
                if t.get("counterparty_id") == sid or name.lower() in t.get("description", "").lower()
            )
            score = min(100, 40 + tx_count * 10)  # Base 40 + 10 per transaction
            scores.append({
                "supplier_id": sid,
                "supplier_name": name,
                "reliability_score": score,
                "transaction_count": tx_count,
            })

        return sorted(scores, key=lambda x: x["reliability_score"], reverse=True)

    except Exception as e:
        logger.error("Supplier scores failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to calculate supplier scores")
