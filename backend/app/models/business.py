"""Business and pricing tier models for multi-tenant SME platform."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BusinessType(str, Enum):
    SUPERMARKET = "supermarket"
    MINI_MART = "mini_mart"
    KIOSK = "kiosk"
    ARTISAN = "artisan"
    SALON = "salon"
    FOOD_VENDOR = "food_vendor"
    AGRICULTURE = "agriculture"
    PROFESSIONAL_SERVICE = "professional_service"
    PHARMACY = "pharmacy"
    RESTAURANT = "restaurant"
    BAR_LOUNGE = "bar_lounge"
    HOTEL_GUESTHOUSE = "hotel_guesthouse"
    LOGISTICS = "logistics"
    FASHION_TEXTILE = "fashion_textile"
    ELECTRONICS = "electronics"
    CONSTRUCTION = "construction"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    AUTO_MECHANIC = "auto_mechanic"
    LAUNDRY_CLEANING = "laundry_cleaning"
    OTHER = "other"


class PricingTier(str, Enum):
    STARTER = "starter"
    GROWTH = "growth"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"


class Business(BaseModel):
    """Core business entity — replaces bare org_id with rich metadata."""

    business_id: str = Field(..., description="Unique business identifier (also used as org_id)")
    business_name: str = Field(..., min_length=1, max_length=200)
    business_type: BusinessType = Field(default=BusinessType.OTHER)
    country: str = Field(default="NG", max_length=3)
    state_region: Optional[str] = Field(None, max_length=100)
    currency: str = Field(default="NGN", max_length=3)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=200)
    pricing_tier: PricingTier = Field(default=PricingTier.STARTER)
    onboarding_complete: bool = Field(default=False)
    modules_enabled: List[str] = Field(default_factory=list)
    extension_attrs: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3 or not v.isupper():
            raise ValueError("Currency must be a 3-letter uppercase ISO 4217 code")
        return v


class BusinessCreate(BaseModel):
    """Request body for creating a new business."""

    business_name: str = Field(..., min_length=1, max_length=200)
    business_type: BusinessType = Field(default=BusinessType.OTHER)
    country: str = Field(default="NG", max_length=3)
    state_region: Optional[str] = None
    currency: str = Field(default="NGN", max_length=3)
    phone: Optional[str] = None
    email: Optional[str] = None


class BusinessUpdate(BaseModel):
    """Request body for updating a business."""

    business_name: Optional[str] = None
    business_type: Optional[BusinessType] = None
    state_region: Optional[str] = None
    currency: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    modules_enabled: Optional[List[str]] = None
    extension_attrs: Optional[Dict[str, Any]] = None
