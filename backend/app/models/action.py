from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ActionExecution(BaseModel):
    """Action execution record"""
    execution_id: str = Field(..., description="Unique execution identifier")
    org_id: str = Field(..., description="Organization identifier")
    strategy_id: str = Field(..., description="Reference to strategy")
    action_type: str = Field(..., description="Type of workflow executed")
    target_entity: str = Field(..., description="Entity affected by action")
    execution_status: str = Field(..., description="Status: success, failed, pending")
    error_reason: Optional[str] = Field(None, description="Failure reason if applicable")
    timestamp: datetime = Field(default_factory=_utc_now)
    
    @field_validator('execution_status')
    @classmethod
    def validate_execution_status(cls, v: str) -> str:
        """Validate execution status"""
        valid_statuses = {'success', 'failed', 'pending'}
        if v not in valid_statuses:
            raise ValueError(f'Execution status must be one of: {valid_statuses}')
        return v
