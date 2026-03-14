from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Evaluation(BaseModel):
    """Post-action evaluation data model"""
    
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    org_id: str = Field(..., description="Organization identifier")
    execution_id: str = Field(..., description="Reference to action execution")
    old_nsi: float = Field(..., ge=0, le=100, description="NSI before action execution")
    new_nsi: float = Field(..., ge=0, le=100, description="NSI after action execution")
    predicted_improvement: float = Field(..., description="Predicted NSI improvement from strategy")
    actual_improvement: float = Field(..., description="Actual NSI improvement (new_nsi - old_nsi)")
    prediction_accuracy: float = Field(..., ge=0, le=1, description="Prediction accuracy score between 0 and 1")
    timestamp: datetime = Field(default_factory=_utc_now, description="Evaluation timestamp")
    
    @field_validator('actual_improvement')
    @classmethod
    def validate_actual_improvement(cls, v: float, info) -> float:
        """Validate actual improvement matches NSI difference"""
        if 'new_nsi' in info.data and 'old_nsi' in info.data:
            expected = info.data['new_nsi'] - info.data['old_nsi']
            if abs(v - expected) > 0.01:  # Allow small floating point differences
                raise ValueError(f'Actual improvement {v} does not match NSI difference {expected}')
        return v
