"""Tax & Compliance router — FIRS annual report generation and VAT summaries."""

import logging
from typing import Optional

from fastapi import APIRouter, Header, Query
from pydantic import BaseModel

from app.services.tax_service import get_tax_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tax", tags=["tax"])


class TaxReportRequest(BaseModel):
    """Request body for generating an annual tax report."""
    fiscal_year: int
    business_name: str = ""
    tin: Optional[str] = None
    vat_registered: bool = False
    has_employees: bool = False
    monthly_staff_cost: float = 0.0
    country_code: str = "NG"


@router.post("/annual-report")
async def generate_annual_report(
    data: TaxReportRequest,
    x_org_id: str = Header(..., alias="X-Org-ID"),
):
    """Generate a FIRS-ready annual tax report from transaction data."""
    svc = get_tax_service()
    report = svc.generate_annual_report(
        business_id=x_org_id,
        fiscal_year=data.fiscal_year,
        business_name=data.business_name,
        tin=data.tin,
        vat_registered=data.vat_registered,
        has_employees=data.has_employees,
        monthly_staff_cost=data.monthly_staff_cost,
        country_code=data.country_code,
    )
    return report.model_dump(mode="json")


@router.get("/vat-summary")
async def get_vat_summary(
    x_org_id: str = Header(..., alias="X-Org-ID"),
    fiscal_year: int = Query(...),
    quarter: int = Query(..., ge=1, le=4),
    country_code: str = Query("NG"),
):
    """Get VAT summary for a specific quarter."""
    svc = get_tax_service()
    return svc.get_quarterly_vat_summary(x_org_id, fiscal_year, quarter, country_code)


@router.post("/ai-guidance")
async def get_ai_guidance(
    data: TaxReportRequest,
    x_org_id: str = Header(..., alias="X-Org-ID"),
):
    """Generate AI-powered tax guidance from annual report data."""
    from app.agents.tax_agent import get_tax_agent

    svc = get_tax_service()
    report = svc.generate_annual_report(
        business_id=x_org_id,
        fiscal_year=data.fiscal_year,
        business_name=data.business_name,
        tin=data.tin,
        vat_registered=data.vat_registered,
        has_employees=data.has_employees,
        monthly_staff_cost=data.monthly_staff_cost,
        country_code=data.country_code,
    )

    agent = get_tax_agent()
    guidance = await agent.generate_guidance(report)

    return {
        "report": report.model_dump(mode="json"),
        "guidance": guidance,
    }
