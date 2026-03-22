"""Branch model for multi-location business support."""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Branch(BaseModel):
    """A physical location belonging to a business."""

    branch_id: str = Field(..., description="Unique branch identifier")
    business_id: str = Field(..., description="Parent business identifier")
    branch_name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    is_primary: bool = Field(default=True)
    extension_attrs: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)


class BranchCreate(BaseModel):
    """Request body for creating a branch."""

    branch_name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None
    is_primary: bool = False
