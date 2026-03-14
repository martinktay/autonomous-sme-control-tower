"""Task model for admin/knowledge-based tasks extracted from emails and other sources."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskEntity(BaseModel):
    """Entities related to a task."""
    people: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)
    invoice_refs: List[str] = Field(default_factory=list)


class Task(BaseModel):
    """Administrative or knowledge-based task."""

    task_id: str = Field(..., description="Unique task identifier")
    org_id: str = Field(..., description="Organization identifier")
    title: str = Field(..., description="Short task title")
    description: str = Field(default="", description="What needs to be done")
    task_type: str = Field(..., description="Type of task")
    priority: str = Field(default="medium", description="Priority: high, medium, low")
    status: str = Field(default="pending", description="Task status")
    source_type: str = Field(default="manual", description="Where the task came from")
    source_id: Optional[str] = Field(None, description="ID of source signal/email")
    due_date: Optional[str] = Field(None, description="Due date hint from source")
    assigned_to: Optional[str] = Field(None, description="Assignee")
    related_entities: Optional[TaskEntity] = Field(None, description="Related entities")
    result: Optional[str] = Field(None, description="Outcome after completion")
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)

    @field_validator("task_type")
    @classmethod
    def validate_task_type(cls, v: str) -> str:
        valid = {
            "reply_email", "schedule_followup", "update_invoice",
            "send_payment", "review_document", "create_report",
            "contact_vendor", "contact_client", "internal_action", "other",
        }
        if v not in valid:
            raise ValueError(f"task_type must be one of: {valid}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        if v not in {"high", "medium", "low"}:
            raise ValueError("priority must be high, medium, or low")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid = {"pending", "in_progress", "completed", "cancelled"}
        if v not in valid:
            raise ValueError(f"status must be one of: {valid}")
        return v

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        valid = {"email", "invoice", "finance_document", "manual", "system"}
        if v not in valid:
            raise ValueError(f"source_type must be one of: {valid}")
        return v
