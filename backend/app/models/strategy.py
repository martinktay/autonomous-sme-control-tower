from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class Strategy(BaseModel):
    strategy_id: str = Field(..., description="Unique strategy identifier")
    org_id: str = Field(..., description="Organization identifier")
    nsi_snapshot_id: str = Field(..., description="Reference to NSI snapshot")
    description: str = Field(..., description="Strategy description")
    predicted_nsi_improvement: float = Field(..., description="Predicted NSI improvement")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    automation_eligibility: bool = Field(default=False, description="Whether strategy can be automated")
    reasoning: str = Field(default="", description="Reasoning for strategy recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    @field_validator("confidence_score")
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        if v < 0 or v > 1:
            raise ValueError("Confidence score must be between 0 and 1")
        return v
