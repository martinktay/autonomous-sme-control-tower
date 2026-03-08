from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class ActionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Action(BaseModel):
    """Action execution record"""
    
    action_id: str
    org_id: str
    strategy_id: str
    
    # Execution details
    status: ActionStatus = ActionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Predictions
    predicted_nsi_improvement: float
    
    # Results
    actual_nsi_before: Optional[float] = None
    actual_nsi_after: Optional[float] = None
    actual_improvement: Optional[float] = None
    prediction_accuracy: Optional[float] = None
    
    # Logs
    execution_log: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
