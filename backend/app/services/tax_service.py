"""Tax computation service — generates country-aware annual reports from transaction data."""

import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.models.tax_report import AnnualTaxReport, TaxLineItem
from app.services.transaction_service import get_transaction_service
from app.services.country_tax_config import (
    get_country_config, compute_cit, compute_vat, compute_paye,
)
from app.utils.id_generator import generate_id

logger = logging.getLogger(__name__)
settings = get_settings()


class TaxService:
    """Computes tax obligations from platform transaction data using country-specific rules."""

    def __init__(self):
        self.txn_service = get_transaction_service()

    def generate_annual_report(
        self,
        business_id: str,
        fiscal_year: int,
        business_name: str = "",
        tin: Optional[str] = None,
        vat_registered: bool = False,
        has_employees: bool = False,
        monthly_staff_cost: float = 0.0,
        country_code: str = "NG",
    ) -> AnnualTaxReport:
        """Generate a complete annual tax report from transaction data."""

        country = get_country_config(country_code)
        period_start = f"{fiscal_year}-01-01"
        period_end = f"{fiscal_year}-12-31"

        # Fetch all transactions for the year
        all_txns = self.txn_service.list_transactions(business_id, limit=5000)
        year_txns = [
            t for t in all_txns
            if str(t.get("date", ""))[:4] == str(fiscal_year)
        ]

        # Categorise
        revenue_by_cat: Dict[str, float] = {}
        expense_by_cat: Dict[str, float] = {}
        total_revenue = 0.0
        total_expenses = 0.0
        supplier_payments = 0.0

        for txn in year_txns:
            amount = float(txn.get("amount", 0))
            if amount < 0:
                amount = 0.0  # guard against negative amounts
            txn_type = txn.get("transaction_type", "")
            category = txn.get("category", "uncategorised") or "uncategorised"

            if txn_type == "revenue":
                total_revenue += amount
                revenue_by_cat[category] = revenue_by_cat.get(category, 0) + amount
            elif txn_type in ("expense", "payment"):
                total_expenses += amount
                expense_by_cat[category] = expense_by_cat.get(category, 0) + amount
                if category in ("services", "contractors", "professional_fees", "consulting"):
                    supplier_payments += amount

        gross_profit = total_revenue - total_expenses
        net_profit = max(gross_profit, 0)

        # --- CIT Calculation (country-aware) ---
        cit_amount, cit_rate, cit_note = compute_cit(net_profit, total_revenue, country_code)
        cit_applicable = cit_rate > 0

        # --- VAT Calculation (country-aware) ---
        vat_collected, vat_on_purchases, vat_payable = compute_vat(
            total_revenue, total_expenses, vat_registered, country_code
        )
        vatable_revenue = total_revenue if vat_registered else 0.0

        # --- WHT Calculation (country-aware) ---
        wht_rate = country.get("wht_rate_services", 0.05)
        wht_deducted = round(supplier_payments * wht_rate, 2)

        # --- PAYE Estimate (country-aware) ---
        annual_staff_cost = monthly_staff_cost * 12
        paye_estimate = compute_paye(annual_staff_cost, has_employees, country_code)

        # --- Total liability ---
        total_tax_liability = round(cit_amount + vat_payable + wht_deducted + paye_estimate, 2)

        # Filing info
        filing_deadline_text = country.get("filing_deadline_cit", "")
        # For CIT, compute actual deadline year
        filing_deadline = f"{fiscal_year + 1} — {filing_deadline_text}"
        penalties = (
            f"Late filing: {country.get('late_filing_penalty', 'varies')}. "
            f"Late payment: {country.get('late_payment_penalty', 'varies')}."
        )

        report = AnnualTaxReport(
            report_id=generate_id("document"),
            business_id=business_id,
            business_name=business_name,
            tin=tin,
            fiscal_year=fiscal_year,
            period_start=period_start,
            period_end=period_end,
            total_revenue=round(total_revenue, 2),
            total_expenses=round(total_expenses, 2),
            gross_profit=round(gross_profit, 2),
            net_profit=round(net_profit, 2),
            cit_turnover_threshold=25_000_000 if country_code == "NG" else 0,
            cit_applicable=cit_applicable,
            cit_rate=cit_rate,
            cit_amount=cit_amount,
            cit_note=cit_note,
            vat_rate=country.get("vat_rate", 0.075),
            vatable_revenue=round(vatable_revenue, 2),
            vat_collected=vat_collected,
            vat_on_purchases=vat_on_purchases,
            vat_payable=vat_payable,
            wht_payments=round(supplier_payments, 2),
            wht_rate=wht_rate,
            wht_deducted=wht_deducted,
            total_staff_costs=round(annual_staff_cost, 2),
            paye_estimate=paye_estimate,
            total_tax_liability=total_tax_liability,
            filing_deadline=filing_deadline,
            penalties_if_late=penalties,
            revenue_by_category=revenue_by_cat,
            expense_by_category=expense_by_cat,
        )

        logger.info(
            "Generated tax report %s for %s FY%d [%s]: revenue=%.2f liability=%.2f",
            report.report_id, business_id, fiscal_year, country_code,
            total_revenue, total_tax_liability,
        )
        return report

    def get_quarterly_vat_summary(
        self, business_id: str, fiscal_year: int, quarter: int,
        country_code: str = "NG",
    ) -> Dict[str, Any]:
        """VAT summary for a specific quarter."""
        country = get_country_config(country_code)
        vat_rate = country.get("vat_rate", 0.075)

        q_months = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}
        start_m, end_m = q_months.get(quarter, (1, 3))

        all_txns = self.txn_service.list_transactions(business_id, limit=5000)
        q_txns = []
        for t in all_txns:
            date_str = str(t.get("date", ""))
            if date_str[:4] == str(fiscal_year):
                month = int(date_str[5:7]) if len(date_str) >= 7 else 0
                if start_m <= month <= end_m:
                    q_txns.append(t)

        revenue = sum(float(t.get("amount", 0)) for t in q_txns if t.get("transaction_type") == "revenue")
        expenses = sum(float(t.get("amount", 0)) for t in q_txns if t.get("transaction_type") in ("expense", "payment"))

        vat_output = round(revenue * vat_rate, 2)
        vat_input = round(expenses * vat_rate * 0.3, 2)

        return {
            "fiscal_year": fiscal_year,
            "quarter": quarter,
            "period": f"Q{quarter} {fiscal_year} ({start_m:02d}-{end_m:02d})",
            "country": country_code,
            "vat_rate": vat_rate,
            "total_revenue": round(revenue, 2),
            "total_expenses": round(expenses, 2),
            "vat_output": vat_output,
            "vat_input_credit": vat_input,
            "vat_payable": round(max(vat_output - vat_input, 0), 2),
            "transaction_count": len(q_txns),
        }


def get_tax_service() -> TaxService:
    return TaxService()
