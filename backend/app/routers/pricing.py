"""Pricing tier information endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from app.services.tier_service import get_tier_service
from app.services.business_service import get_business_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pricing", tags=["pricing"])


@router.get("/tiers", response_model=List[Dict[str, Any]])
async def get_tiers():
    """Return all pricing tier definitions for the pricing page."""
    svc = get_tier_service()
    return svc.get_all_tiers()


@router.get("/current/{business_id}", response_model=Dict[str, Any])
async def get_current_tier(business_id: str):
    """Return current tier and usage for a business."""
    try:
        biz_svc = get_business_service()
        tier_svc = get_tier_service()

        business = biz_svc.get_business(business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        tier = business.get("pricing_tier", "starter")
        limits = tier_svc.get_tier_limits(tier)
        branches = biz_svc.list_branches(business_id)

        return {
            "business_id": business_id,
            "tier": tier,
            "limits": limits,
            "usage": {
                "branches": len(branches),
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get current tier: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve tier info")
