"""Tax guidance agent — uses Nova to explain tax obligations in plain language."""

import logging
from typing import Any, Dict

from app.models.tax_report import AnnualTaxReport
from app.utils.bedrock_client import get_bedrock_client
from app.utils.json_guard import safe_parse
from app.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class TaxAgent:
    """Generates AI-powered tax guidance from annual report data."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    async def generate_guidance(self, report: AnnualTaxReport) -> Dict[str, Any]:
        """Generate plain-English tax guidance from a computed report."""
        try:
            prompt = load_prompt(
                "tax-report-summary",
                business_name=report.business_name or "Your Business",
                fiscal_year=str(report.fiscal_year),
                total_revenue=f"{report.total_revenue:,.2f}",
                total_expenses=f"{report.total_expenses:,.2f}",
                net_profit=f"{report.net_profit:,.2f}",
                cit_note=report.cit_note,
                cit_amount=f"{report.cit_amount:,.2f}",
                vat_payable=f"{report.vat_payable:,.2f}",
                wht_deducted=f"{report.wht_deducted:,.2f}",
                paye_estimate=f"{report.paye_estimate:,.2f}",
                total_tax_liability=f"{report.total_tax_liability:,.2f}",
                filing_deadline=report.filing_deadline,
            )

            response = self.bedrock.invoke_model(prompt)
            parsed = safe_parse(response)

            return {
                "summary": parsed.get("summary", ""),
                "deadlines": parsed.get("deadlines", []),
                "recommendations": parsed.get("recommendations", []),
                "warnings": parsed.get("warnings", []),
                "confidence": parsed.get("confidence", "medium"),
            }
        except Exception as exc:
            logger.error("Tax agent guidance failed: %s", exc)
            return {
                "summary": "Unable to generate AI guidance at this time. Please review the numbers above.",
                "deadlines": [f"CIT filing deadline: {report.filing_deadline}"],
                "recommendations": [],
                "warnings": [],
                "confidence": "low",
            }


def get_tax_agent() -> TaxAgent:
    return TaxAgent()
