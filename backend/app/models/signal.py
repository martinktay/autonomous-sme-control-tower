import re
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any

_ORG_ID_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{1,64}$")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Signal(BaseModel):
    """Business signal data model"""
    
    signal_id: str = Field(..., description="Unique signal identifier")
    org_id: str = Field(..., description="Organization identifier")
    signal_type: str = Field(..., description="Signal type: invoice, email")
    content: Dict[str, Any] = Field(..., description="Structured signal content")
    embedding_ref: Optional[str] = Field(None, description="Reference to embedding vector")
    created_at: datetime = Field(default_factory=_utc_now, description="Record creation timestamp")
    processing_status: str = Field(default="processed", description="Processing status: processed, failed, pending")
    
    @field_validator('org_id')
    @classmethod
    def validate_org_id(cls, v: str) -> str:
        """Validate org_id format (must start with a letter, followed by 1-64 alphanumeric/dash/underscore chars)"""
        if not _ORG_ID_PATTERN.match(v):
            raise ValueError("org_id must start with a letter and contain only alphanumeric, dash, or underscore characters (max 65 chars)")
        return v
    
    @field_validator('signal_type')
    @classmethod
    def validate_signal_type(cls, v: str) -> str:
        """Validate signal type"""
        valid_types = {'invoice', 'email', 'finance_document', 'whatsapp'}
        if v not in valid_types:
            raise ValueError(f'Signal type must be one of: {valid_types}')
        return v
    
    @field_validator('processing_status')
    @classmethod
    def validate_processing_status(cls, v: str) -> str:
        """Validate processing status"""
        valid_statuses = {'processed', 'failed', 'pending'}
        if v not in valid_statuses:
            raise ValueError(f'Processing status must be one of: {valid_statuses}')
        return v
