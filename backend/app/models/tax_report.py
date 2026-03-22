"""Tax report models for Nigerian SME FIRS compliance."""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaxLineItem(BaseModel):
    """Single line in a tax computation."""
    label: str
    amount: float = 0.0
    rate: Optional[float] = None
    tax_due: float = 0.0
    note: Optional[str] = None


class AnnualTaxReport(BaseModel):
    """FIRS-ready annual tax computation for an SME."""

    report_id: str
    business_id: str
    business_name: str = ""
    tin: Optional[str] = Field(None, description="Tax Identification Number")
    fiscal_year: int
    period_start: str  # YYYY-MM-DD
    period_end: str

    # Revenue & expense totals
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    gross_profit: float = 0.0
    net_profit: float = 0.0

    # CIT (Companies Income Tax)
    cit_turnover_threshold: float = 25_000_000.0
    cit_applicable: bool = False
    cit_rate: float = 0.0
    cit_amount: float = 0.0
    cit_note: str = ""

    # VAT (Value Added Tax — 7.5%)
    vat_rate: float = 0.075
    vatable_revenue: float = 0.0
    vat_collected: float = 0.0
    vat_on_purchases: float = 0.0
    vat_payable: float = 0.0

    # WHT (Withholding Tax)
    wht_payments: float = 0.0
    wht_rate: float = 0.05
    wht_deducted: float = 0.0

    # PAYE (Pay As You Earn) — staff salaries
    total_staff_costs: float = 0.0
    paye_estimate: float = 0.0

    # Summary
    total_tax_liability: float = 0.0
    filing_deadline: str = ""
    penalties_if_late: str = ""

    # AI-generated guidance
    ai_summary: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)

    # Breakdown tables
    revenue_by_category: Dict[str, float] = Field(default_factory=dict)
    expense_by_category: Dict[str, float] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=_utc_now)


class TaxSettings(BaseModel):
    """Per-business tax configuration."""
    tin: Optional[str] = None
    vat_registered: bool = False
    has_employees: bool = False
    monthly_staff_cost: float = 0.0
    business_type: str = "sole_proprietorship"  # sole_proprietorship | llc | partnership
