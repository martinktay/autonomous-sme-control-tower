"""Alert model for proactive business notifications."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(BaseModel):
    """Proactive alert generated from business signals."""

    alert_id: str = Field(..., description="Unique alert identifier")
    business_id: str = Field(..., description="Business identifier")
    branch_id: Optional[str] = None
    alert_type: str = Field(..., description="low_stock | overdue_payment | cashflow_warning | expense_spike | supplier_issue")
    severity: str = Field(..., description="critical | warning | info")
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(..., description="Plain-language alert description")
    recommended_action: Optional[str] = None
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=_utc_now)

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        valid = {"critical", "warning", "info"}
        if v not in valid:
            raise ValueError(f"severity must be one of: {valid}")
        return v

    @field_validator("alert_type")
    @classmethod
    def validate_alert_type(cls, v: str) -> str:
        valid = {"low_stock", "overdue_payment", "cashflow_warning", "expense_spike", "supplier_issue"}
        if v not in valid:
            raise ValueError(f"alert_type must be one of: {valid}")
        return v
