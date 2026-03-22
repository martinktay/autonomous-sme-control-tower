"""Upload job model for batch document ingestion tracking."""

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UploadJobStatus(str, Enum):
    """Valid statuses for an upload job."""
    pending = "pending"
    mapping = "mapping"
    processing = "processing"
    complete = "complete"
    failed = "failed"


class UploadJob(BaseModel):
    """Tracks a batch document ingestion session."""

    job_id: str = Field(..., description="Unique job identifier")
    business_id: str = Field(..., description="Business identifier")
    branch_id: Optional[str] = None
    filename: str = Field(default="", description="Original filename")
    file_type: str = Field(default="", description="File MIME type or extension")
    file_size_bytes: int = Field(default=0, ge=0)
    source_channel: str = Field(default="manual_upload")
    file_count: int = Field(default=1, ge=1)
    file_names: List[str] = Field(default_factory=list)
    status: str = Field(default="pending", description="pending | mapping | processing | complete | failed")
    total_records: int = Field(default=0, ge=0)
    processed_records: int = Field(default=0, ge=0)
    failed_records: int = Field(default=0, ge=0)
    field_mappings: Optional[Dict[str, str]] = None
    unmapped_fields: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)
    completed_at: Optional[datetime] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"pending", "mapping", "processing", "complete", "failed"}
        if v not in valid:
            raise ValueError(f"status must be one of: {valid}")
        return v
