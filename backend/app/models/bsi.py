from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SubIndices(BaseModel):
    liquidity_index: float = Field(default=50.0, ge=0, le=100)
    revenue_stability_index: float = Field(default=50.0, ge=0, le=100)
    operational_latency_index: float = Field(default=50.0, ge=0, le=100)
    vendor_risk_index: float = Field(default=50.0, ge=0, le=100)


class BSIScore(BaseModel):
    org_id: str = Field(..., description='Organization identifier')
    sub_indices: SubIndices = Field(default_factory=SubIndices)
    business_stability_index: float = Field(default=50.0, ge=0, le=100)
    top_risks: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str = Field(default='')
    signal_count: int = Field(default=0)
    timestamp: datetime = Field(default_factory=_utc_now)
    confidence: str = Field(default='medium')

    @field_validator('top_risks', mode='before')
    @classmethod
    def normalize_top_risks(cls, v: Any) -> List[Dict[str, Any]]:
        """Normalize top_risks: Bedrock may return plain strings instead of dicts."""
        if not isinstance(v, list):
            return []
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(item)
            elif isinstance(item, str):
                result.append({"risk": item, "severity": "medium"})
        return result

    @field_validator('confidence')
    @classmethod
    def validate_bsi_confidence(cls, v: str) -> str:
        valid = {'high', 'medium', 'low'}
        if v not in valid:
            raise ValueError(f'Confidence must be one of: {valid}')
        return v


class BSISnapshot(BaseModel):
    """Business Stability Index snapshot model for business health tracking"""
    bsi_id: str = Field(..., description="Unique BSI snapshot identifier")
    org_id: str = Field(..., description="Organization identifier")
    bsi_score: float = Field(default=50.0, ge=0, le=100)
    liquidity_index: float = Field(default=50.0, ge=0, le=100)
    revenue_stability_index: float = Field(default=50.0, ge=0, le=100)
    operational_latency_index: float = Field(default=50.0, ge=0, le=100)
    vendor_risk_index: float = Field(default=50.0, ge=0, le=100)
    confidence: str = Field(default="medium")
    reasoning: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_utc_now)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        valid_levels = {'high', 'medium', 'low'}
        if v not in valid_levels:
            raise ValueError(f'Confidence must be one of: {valid_levels}')
        return v
