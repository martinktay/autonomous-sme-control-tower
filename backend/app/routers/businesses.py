"""Business registration, onboarding, and management endpoints."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from app.models.business import BusinessCreate, BusinessUpdate
from app.models.branch import BranchCreate
from app.services.business_service import get_business_service
from app.services.tier_service import get_tier_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/businesses", tags=["businesses"])


@router.post("", response_model=Dict[str, Any])
async def create_business(data: BusinessCreate):
    """Register a new business. Creates default branch automatically."""
    try:
        svc = get_business_service()
        business = svc.create_business(data)
        return business.model_dump(mode="json")
    except Exception as e:
        logger.error("Business creation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create business")


@router.get("/{business_id}", response_model=Dict[str, Any])
async def get_business(business_id: str):
    """Retrieve business details."""
    svc = get_business_service()
    business = svc.get_business(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business


@router.put("/{business_id}", response_model=Dict[str, Any])
async def update_business(business_id: str, data: BusinessUpdate):
    """Update business fields."""
    try:
        svc = get_business_service()
        result = svc.update_business(business_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Business not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Business update failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update business")


@router.post("/{business_id}/onboarding/complete", response_model=Dict[str, Any])
async def complete_onboarding(business_id: str):
    """Mark onboarding as complete for a business."""
    try:
        svc = get_business_service()
        result = svc.complete_onboarding(business_id)
        if not result:
            raise HTTPException(status_code=404, detail="Business not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Onboarding completion failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to complete onboarding")


# --- Branch endpoints ---

@router.post("/{business_id}/branches", response_model=Dict[str, Any])
async def create_branch(business_id: str, data: BranchCreate):
    """Create a new branch for a business. Checks tier limits."""
    try:
        svc = get_business_service()
        tier_svc = get_tier_service()

        # Check business exists and get tier
        business = svc.get_business(business_id)
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")

        tier = business.get("pricing_tier", "starter")
        branches = svc.list_branches(business_id)

        if not tier_svc.check_branch_allowed(tier, len(branches)):
            raise HTTPException(
                status_code=403,
                detail=f"Branch limit reached for {tier} tier. Upgrade to add more branches.",
            )

        branch = svc.create_branch(business_id, data.branch_name, data.address)
        return branch.model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Branch creation failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create branch")


@router.get("/{business_id}/branches", response_model=List[Dict[str, Any]])
async def list_branches(business_id: str):
    """List all branches for a business."""
    svc = get_business_service()
    return svc.list_branches(business_id)
