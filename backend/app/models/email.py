from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Email(BaseModel):
    """Email data model for operational signals"""
    
    email_id: str = Field(..., description="Unique email identifier")
    org_id: str = Field(..., description="Organization identifier")
    sender: str = Field(..., description="Email sender address")
    subject: str = Field(..., description="Email subject line")
    classification: str = Field(..., description="Email classification: payment_reminder, customer_inquiry, operational_message, other")
    content: str = Field(..., description="Email body content")
    created_at: datetime = Field(default_factory=_utc_now, description="Record creation timestamp")
    
    @field_validator('classification')
    @classmethod
    def validate_classification(cls, v: str) -> str:
        """Validate email classification"""
        valid_classifications = {'payment_reminder', 'customer_inquiry', 'operational_message', 'other'}
        if v not in valid_classifications:
            raise ValueError(f'Classification must be one of: {valid_classifications}')
        return v
