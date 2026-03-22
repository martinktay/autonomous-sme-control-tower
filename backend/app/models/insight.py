"""Insight model for AI-generated business intelligence."""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Insight(BaseModel):
    """AI-generated business insight."""

    insight_id: str = Field(..., description="Unique insight identifier")
    business_id: str = Field(..., description="Business identifier")
    insight_type: str = Field(..., description="sales_trend | profitable_product | cost_saving | seasonal_pattern | inventory_risk | cashflow | customer_segmentation | marketing_roi | sales_forecast | revenue_analysis | expense_analysis")
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., description="Plain-language insight")
    data: Dict[str, Any] = Field(default_factory=dict, description="Supporting metrics")
    created_at: datetime = Field(default_factory=_utc_now)
