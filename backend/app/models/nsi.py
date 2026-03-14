from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Dict, Any, List, Optional


class SubIndices(BaseModel):
    liquidity_index: float = Field(default=50.0, ge=0, le=100)
    revenue_stability_index: float = Field(default=50.0, ge=0, le=100)
    operational_latency_index: float = Field(default=50.0, ge=0, le=100)
    vendor_risk_index: float = Field(default=50.0, ge=0, le=100)


class NSIScore(BaseModel):
    org_id: str = Field(..., description='Organization identifier')
    sub_indices: SubIndices = Field(default_factory=SubIndices)
    nova_stability_index: float = Field(default=50.0, ge=0, le=100)
    top_risks: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str = Field(default='')
    signal_count: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: str = Field(default='medium')

    @field_validator('confidence')
    @classmethod
    def validate_nsi_confidence(cls, v: str) -> str:
        valid = {'high', 'medium', 'low'}
        if v not in valid:
            raise ValueError(f'Confidence must be one of: {valid}')
        return v


class NSISnapshot(BaseModel):
    nsi_id: str = Field(..., description='Unique NSI snapshot identifier')
    org_id: str = Field(..., description='Organization identifier')
    nsi_score: float = Field(..., ge=0, le=100)
    liquidity_index: float = Field(..., ge=0, le=100)
    revenue_stability_index: float = Field(..., ge=0, le=100)
    operational_latency_index: float = Field(..., ge=0, le=100)
    vendor_risk_index: float = Field(..., ge=0, le=100)
    confidence: str = Field(...)
    reasoning: Dict[str, Any] = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: str) -> str:
        valid_levels = {'high', 'medium', 'low'}
        if v not in valid_levels:
            raise ValueError(f'Confidence must be one of: {valid_levels}')
        return v
