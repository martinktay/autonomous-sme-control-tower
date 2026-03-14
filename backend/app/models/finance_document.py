from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DocumentFlag(BaseModel):
    """Flag attached to a finance document for anomaly/duplicate/review reasons"""

    flag_type: str = Field(..., description="Type of flag: duplicate, anomaly, low_confidence, extraction_failure, missing_currency")
    flag_reason: str = Field(..., description="Human-readable reason for the flag")


class FinanceDocument(BaseModel):
    """Processed financial document model"""

    document_id: str = Field(..., description="Unique document identifier (UUID)")
    org_id: str = Field(..., description="Organization identifier")
    vendor_name: str = Field(..., description="Vendor or supplier name")
    amount: float = Field(..., gt=0, description="Document amount (must be positive)")
    currency: str = Field(..., description="3-letter uppercase ISO 4217 currency code")
    vat_amount: Optional[float] = Field(None, description="VAT amount (non-negative)")
    vat_rate: Optional[float] = Field(None, description="VAT rate as percentage (non-negative)")
    wht_amount: Optional[float] = Field(None, description="Withholding Tax amount (non-negative)")
    wht_rate: Optional[float] = Field(None, description="Withholding Tax rate as percentage")
    cit_amount: Optional[float] = Field(None, description="Corporate Income Tax amount (non-negative)")
    paye_amount: Optional[float] = Field(None, description="PAYE / Payroll tax amount (non-negative)")
    customs_levy: Optional[float] = Field(None, description="Customs duty or import levy amount (non-negative)")
    document_date: datetime = Field(..., description="Date of the document")
    description: str = Field(..., description="Document description or purpose")
    category: str = Field(..., description="Category: revenue or expense")
    confidence_score: float = Field(..., description="Classification confidence score (0.0 to 1.0)")
    processing_status: str = Field(default="processed", description="Processing status")
    s3_key: str = Field(..., description="S3 object key for the uploaded document")
    created_at: datetime = Field(default_factory=_utc_now, description="Record creation timestamp")
    flags: Optional[List[DocumentFlag]] = Field(None, description="List of flags for anomalies, duplicates, etc.")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency is a 3-letter uppercase ISO 4217 code"""
        if len(v) != 3 or not v.isalpha() or not v.isupper():
            raise ValueError('Currency must be a 3-letter uppercase ISO 4217 code')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is revenue or expense"""
        valid_categories = {'revenue', 'expense'}
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v

    @field_validator('processing_status')
    @classmethod
    def validate_processing_status(cls, v: str) -> str:
        """Validate processing status"""
        valid_statuses = {'processed', 'needs_review', 'approved', 'rejected', 'failed'}
        if v not in valid_statuses:
            raise ValueError(f'Processing status must be one of: {valid_statuses}')
        return v

    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v: float) -> float:
        """Validate confidence score is between 0.0 and 1.0 inclusive"""
        if v < 0.0 or v > 1.0:
            raise ValueError('Confidence score must be between 0.0 and 1.0 inclusive')
        return v

    @field_validator('vat_amount')
    @classmethod
    def validate_vat_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate VAT amount is non-negative when provided"""
        if v is not None and v < 0:
            raise ValueError('VAT amount must be non-negative')
        return v

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate VAT rate is non-negative when provided"""
        if v is not None and v < 0:
            raise ValueError('VAT rate must be non-negative')
        return v

    @field_validator('wht_amount', 'cit_amount', 'paye_amount', 'customs_levy')
    @classmethod
    def validate_tax_amounts(cls, v: Optional[float]) -> Optional[float]:
        """Validate tax amounts are non-negative when provided"""
        if v is not None and v < 0:
            raise ValueError('Tax amount must be non-negative')
        return v
