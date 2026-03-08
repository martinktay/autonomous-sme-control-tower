from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any


class SignalType(str, Enum):
    INVOICE = "invoice"
    EMAIL = "email"
    DOCUMENT = "document"


class Signal(BaseModel):
    """Business signal data model"""
    
    signal_id: str = Field(..., description="Unique signal identifier")
    org_id: str = Field(..., description="Organization identifier")
    signal_type: SignalType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Raw data
    raw_content: Optional[str] = None
    s3_key: Optional[str] = None
    
    # Extracted structured data
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Classification
    category: Optional[str] = None
    priority: Optional[str] = None
    action_required: bool = False
    
    # Metadata
    processed: bool = False
    processing_error: Optional[str] = None
