"""Cross-Branch Optimisation endpoints — multi-branch intelligence."""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from app.agents.branch_agent import get_branch_agent
from app.services.business_service import get_business_service
from app.services.inventory_service import get_inventory_service
from app.services.transaction_service import get_transaction_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/branches", tags=["branch-optimisation"])


@router.get("/{org_id}/optimise", response_model=Dict[str, Any])
async def optimise_branches(
    org_id: str,
    business_name: str = "",
    business_type: str = "supermarket",
):
    """Generate AI cross-branch optimisation report."""
    try:
        biz_svc = get_business_service()
        inv_svc = get_inventory_service()
        tx_svc = get_transaction_service()

        # Get branches for this business
        branches = biz_svc.list_branches(org_id)
        if len(branches) < 2:
            return {
                "org_id": org_id,
                "message": "Cross-branch optimisation requires at least 2 branches.",
                "branch_count": len(branches),
            }

        # Gather inventory and sales per branch
        branch_inventory: Dict[str, list] = {}
        branch_sales: Dict[str, list] = {}
        for branch in branches:
            bid = branch.get("branch_id", "")
            bname = branch.get("branch_name", bid)
            # For now, all inventory/transactions are at org level
            # In future, filter by branch_id
            branch_inventory[bname] = inv_svc.list_items(org_id, limit=50)
            branch_sales[bname] = tx_svc.list_transactions(org_id, limit=50)

        agent = get_branch_agent()
        result = agent.optimise(
            branch_data=branches,
            branch_inventory=branch_inventory,
            branch_sales=branch_sales,
            business_type=business_type,
            business_name=business_name,
        )
        result["org_id"] = org_id
        return result

    except Exception as e:
        logger.error("Branch optimisation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate branch optimisation")


@router.get("/{org_id}/benchmarks", response_model=Dict[str, Any])
async def get_branch_benchmarks(org_id: str):
    """Quick branch performance benchmarks without full AI analysis."""
    try:
        biz_svc = get_business_service()
        branches = biz_svc.list_branches(org_id)

        benchmarks = []
        for branch in branches:
            benchmarks.append({
                "branch_name": branch.get("branch_name", "Unknown"),
                "branch_id": branch.get("branch_id", ""),
                "address": branch.get("address", ""),
                "status": "active",
            })

        return {
            "org_id": org_id,
            "total_branches": len(benchmarks),
            "branches": benchmarks,
        }

    except Exception as e:
        logger.error("Branch benchmarks failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get branch benchmarks")
