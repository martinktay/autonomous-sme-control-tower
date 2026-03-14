"""
Insights Agent - Generates plain-language business insights for SME owners

Uses Nova 2 Lite to translate raw NSI data, risks, and actions into
easy-to-understand summaries. Falls back to rule-based insights when
Bedrock is unavailable.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely

logger = logging.getLogger(__name__)


class InsightsAgent:
    """Generates AI-powered business insights in plain language.

    Supports two domains:
    - General business insights (NSI, risks, actions, strategies)
    - Finance-specific insights (P&L, cashflow, tax/VAT analysis)

    Each domain tries Bedrock first, then falls back to rule-based generation.
    """

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def generate_insights(
        self,
        org_id: str,
        nsi_data: Optional[Dict[str, Any]],
        risks: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        strategies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate general business insights from NSI data, risks, actions, and strategies.

        Args:
            org_id: Organisation identifier.
            nsi_data: Latest NSI score and sub-indices.
            risks: List of identified risk dicts.
            actions: List of recent action dicts.
            strategies: List of strategy dicts.

        Returns:
            Dict with summary, highlights, next_steps, and confidence level.
        """
        try:
            return self._generate_with_bedrock(org_id, nsi_data, risks, actions, strategies)
        except Exception as e:
            logger.warning(f"Bedrock insights failed, using fallback: {e}")
            return self._generate_fallback(nsi_data, risks, actions, strategies)

    def _generate_with_bedrock(
        self,
        org_id: str,
        nsi_data: Optional[Dict[str, Any]],
        risks: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        strategies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build a data block and send it to Nova Lite with the business-insights prompt."""
        prompt_template = load_prompt("business-insights")

        data_block = json.dumps(
            {
                "health_score": nsi_data.get("nsi_score") if nsi_data else None,
                "cash_flow": nsi_data.get("liquidity_index") if nsi_data else None,
                "revenue_stability": nsi_data.get("revenue_stability_index") if nsi_data else None,
                "operations_speed": nsi_data.get("operational_latency_index") if nsi_data else None,
                "vendor_risk": nsi_data.get("vendor_risk_index") if nsi_data else None,
                "confidence": nsi_data.get("confidence") if nsi_data else None,
                "top_risks": risks[:5],
                "recent_actions": [
                    {"type": a.get("action_type"), "status": a.get("execution_status"), "target": a.get("target_entity")}
                    for a in actions[:5]
                ],
                "strategies": [
                    {"description": s.get("description"), "predicted_improvement": s.get("predicted_nsi_improvement"), "automatable": s.get("automation_eligibility")}
                    for s in strategies[:5]
                ],
            },
            indent=2,
        )

        prompt = f"{prompt_template}\n\n## Current Business Data\n{data_block}"
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.6, max_tokens=1500)
        parsed = parse_json_safely(response)

        return {
            "summary": parsed.get("summary", "Analysis complete."),
            "highlights": parsed.get("highlights", []),
            "next_steps": parsed.get("next_steps", []),
            "confidence": parsed.get("confidence", "medium"),
        }

    def _generate_fallback(
        self,
        nsi_data: Optional[Dict[str, Any]],
        risks: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        strategies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Rule-based insights when Bedrock is unavailable.

        Generates highlights and next steps from NSI sub-indices using simple thresholds.
        """
        highlights = []
        next_steps = []

        if not nsi_data:
            return {
                "summary": "We don't have enough data to analyse your business yet. Upload some invoices and run an analysis to get started.",
                "highlights": [],
                "next_steps": [
                    "Upload your first invoice from the Upload page.",
                    "Run a full analysis from the Run Analysis page.",
                ],
                "confidence": "low",
            }

        score = nsi_data.get("nsi_score", 0)
        cash_flow = nsi_data.get("liquidity_index", 50)
        revenue = nsi_data.get("revenue_stability_index", 50)
        ops_speed = nsi_data.get("operational_latency_index", 50)
        vendor = nsi_data.get("vendor_risk_index", 50)

        # Build summary
        if score >= 70:
            summary = f"Your business health score is {score:.0f} out of 100 — that's in the healthy range. Things are looking good overall."
        elif score >= 40:
            summary = f"Your business health score is {score:.0f} out of 100 — there are some areas that need attention, but nothing critical yet."
        else:
            summary = f"Your business health score is {score:.0f} out of 100 — this is in the at-risk zone. Some immediate action is recommended."

        # Cash flow highlight
        if cash_flow < 40:
            highlights.append({"type": "critical", "title": "Cash flow is tight", "detail": f"Your cash flow score is {cash_flow:.0f}. This means you may have difficulty paying bills on time. Consider following up on overdue invoices."})
        elif cash_flow >= 70:
            highlights.append({"type": "positive", "title": "Cash flow is strong", "detail": f"Your cash flow score is {cash_flow:.0f}. You have good ability to cover your expenses."})

        # Revenue highlight
        if revenue < 40:
            highlights.append({"type": "warning", "title": "Revenue is inconsistent", "detail": f"Your revenue stability is {revenue:.0f}. Income has been unpredictable — try to diversify your customer base."})
        elif revenue >= 70:
            highlights.append({"type": "positive", "title": "Steady revenue", "detail": f"Your revenue stability is {revenue:.0f}. Your income has been consistent."})

        # Vendor risk highlight
        if vendor < 40:
            highlights.append({"type": "warning", "title": "Vendor risk is high", "detail": f"Your vendor risk score is {vendor:.0f}. Some of your suppliers may be unreliable. Consider finding backup vendors."})

        # Risks
        if risks:
            top_risk = risks[0] if isinstance(risks[0], dict) else {"description": str(risks[0]), "severity": "medium"}
            highlights.append({"type": "critical" if top_risk.get("severity", "").lower() in ["high", "critical"] else "warning", "title": "Top risk identified", "detail": top_risk.get("description", "A risk was detected in your operations.")})

        # Actions
        successful = [a for a in actions if a.get("execution_status", "").lower() == "success"]
        if successful:
            highlights.append({"type": "positive", "title": "Actions completed", "detail": f"{len(successful)} automated action(s) were successfully completed recently."})

        # Next steps
        if score < 70:
            next_steps.append("Run a full analysis to get updated recommendations.")
        if cash_flow < 50:
            next_steps.append("Follow up on any overdue invoices to improve cash flow.")
        if strategies:
            next_steps.append("Review the suggested strategies on the Strategy page.")
        if not actions:
            next_steps.append("Upload more invoices to give the system more data to work with.")
        if not next_steps:
            next_steps.append("Keep uploading invoices regularly to maintain an accurate health score.")

        return {
            "summary": summary,
            "highlights": highlights[:5],
            "next_steps": next_steps[:4],
            "confidence": "medium",
        }

    # ==================== Finance-Specific Insights ====================

    def generate_finance_insights(
        self,
        org_id: str,
        pnl: Dict[str, Any],
        cashflow: List[Dict[str, Any]],
        doc_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate financial insights with tax/VAT analysis.

        Args:
            org_id: Organisation identifier.
            pnl: P&L summary dict (revenue, expenses, tax breakdown).
            cashflow: List of period-aggregated cashflow dicts.
            doc_stats: Document statistics (total, pending review, currencies).

        Returns:
            Dict with summary, highlights, tax_insights, cashflow/profitability/vendor analysis.
        """
        try:
            return self._generate_finance_with_bedrock(org_id, pnl, cashflow, doc_stats)
        except Exception as e:
            logger.warning("Bedrock finance insights failed, using fallback: %s", e)
            return self._generate_finance_fallback(pnl, cashflow, doc_stats)

    def _generate_finance_with_bedrock(
        self,
        org_id: str,
        pnl: Dict[str, Any],
        cashflow: List[Dict[str, Any]],
        doc_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send P&L + cashflow data to Nova Lite with the finance-insights prompt."""
        prompt_template = load_prompt("finance-insights")

        data_block = json.dumps(
            {
                "pnl": pnl,
                "cashflow_periods": cashflow[-12:],
                "document_stats": doc_stats,
            },
            indent=2,
        )

        prompt = f"{prompt_template}\n\n## Current Financial Data\n{data_block}"
        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.5, max_tokens=2000)
        parsed = parse_json_safely(response)

        return {
            "summary": parsed.get("summary", "Financial analysis complete."),
            "highlights": parsed.get("highlights", []),
            "tax_insights": parsed.get("tax_insights", {}),
            "cashflow_analysis": parsed.get("cashflow_analysis", ""),
            "profitability_analysis": parsed.get("profitability_analysis", ""),
            "vendor_insights": parsed.get("vendor_insights", ""),
            "next_steps": parsed.get("next_steps", []),
            "confidence": parsed.get("confidence", "medium"),
        }

    def _generate_finance_fallback(
        self,
        pnl: Dict[str, Any],
        cashflow: List[Dict[str, Any]],
        doc_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Rule-based financial insights when Bedrock is unavailable.

        Covers profitability, VAT position, WHT, CIT, PAYE, customs, cashflow trends,
        vendor concentration, and actionable next steps.
        """
        highlights: List[Dict[str, Any]] = []
        next_steps: List[str] = []
        tax_tips: List[str] = []

        total_rev = pnl.get("total_revenue", 0)
        total_exp = pnl.get("total_expenses", 0)
        net_profit = pnl.get("net_profit", 0)
        vat_summary = pnl.get("vat_summary", {})
        tax_summary = pnl.get("tax_summary", {})
        vat_collected = vat_summary.get("total_vat_collected", 0)
        vat_paid = vat_summary.get("total_vat_paid", 0)
        net_vat = round(vat_collected - vat_paid, 2)
        wht = tax_summary.get("withholding_tax", 0)
        cit = tax_summary.get("corporate_income_tax", 0)
        paye = tax_summary.get("paye_payroll", 0)
        customs = tax_summary.get("customs_levy", 0)
        total_tax_burden = tax_summary.get("total_tax_burden", 0)
        by_vendor = pnl.get("by_vendor", {})

        total_docs = doc_stats.get("total_documents", 0)
        pending_review = doc_stats.get("pending_review", 0)

        # --- Summary ---
        if total_docs == 0:
            summary = "No financial documents have been processed yet. Upload invoices, receipts, or spreadsheets to get started with your financial analysis."
        elif net_profit >= 0:
            margin = (net_profit / total_rev * 100) if total_rev > 0 else 0
            summary = (
                f"Your business generated {total_rev:,.2f} in revenue against {total_exp:,.2f} in expenses, "
                f"giving you a net profit of {net_profit:,.2f} ({margin:.1f}% margin). "
                f"{'Solid profitability.' if margin >= 15 else 'Margins are thin — watch your costs.'}"
            )
        else:
            summary = (
                f"Your business is currently running at a loss: {total_rev:,.2f} in revenue vs {total_exp:,.2f} in expenses, "
                f"resulting in a net loss of {abs(net_profit):,.2f}. Immediate attention is needed."
            )

        # --- Profitability ---
        if net_profit < 0:
            highlights.append({"type": "critical", "title": "Business running at a loss", "detail": f"Net loss of {abs(net_profit):,.2f}. Review your largest expense categories and look for cost-cutting opportunities."})
        elif total_rev > 0:
            margin = net_profit / total_rev * 100
            if margin >= 20:
                highlights.append({"type": "positive", "title": "Healthy profit margins", "detail": f"Your profit margin is {margin:.1f}% — that's strong for an SME."})
            elif margin < 10:
                highlights.append({"type": "warning", "title": "Thin profit margins", "detail": f"Your profit margin is only {margin:.1f}%. Consider raising prices or reducing costs."})

        profitability_analysis = ""
        if total_rev > 0:
            margin = net_profit / total_rev * 100
            profitability_analysis = f"Profit margin is {margin:.1f}%. " + (
                "This is healthy for a small business." if margin >= 15
                else "This is below the typical 15% target for SMEs — focus on cost control." if margin >= 0
                else "The business is loss-making. Urgent cost review recommended."
            )

        # --- VAT ---
        vat_position = ""
        estimated_vat_liability = 0.0
        filing_reminder = None

        if vat_collected > 0 or vat_paid > 0:
            estimated_vat_liability = net_vat
            if net_vat > 0:
                vat_position = f"You collected {vat_collected:,.2f} in VAT from customers and paid {vat_paid:,.2f} on purchases. You owe approximately {net_vat:,.2f} to the tax authority."
                highlights.append({"type": "info", "title": "VAT liability due", "detail": f"Net VAT owed: {net_vat:,.2f}. Set this aside for your next filing."})
                tax_tips.append(f"Set aside {net_vat:,.2f} for your upcoming VAT payment to avoid penalties.")
            elif net_vat < 0:
                vat_position = f"You collected {vat_collected:,.2f} in VAT but paid {vat_paid:,.2f} — you may be eligible for a VAT refund of {abs(net_vat):,.2f}."
                highlights.append({"type": "positive", "title": "Potential VAT refund", "detail": f"You may be owed {abs(net_vat):,.2f} back from the tax authority."})
                tax_tips.append("Check if you can claim a VAT refund — you've paid more VAT than you collected.")
            else:
                vat_position = f"VAT collected ({vat_collected:,.2f}) and VAT paid ({vat_paid:,.2f}) are balanced."
        else:
            vat_position = "No VAT data recorded yet. If your business is VAT-registered, make sure VAT amounts are included on your invoices."
            tax_tips.append("If you're VAT-registered, ensure all uploaded documents include VAT amounts for accurate tracking.")

        # --- Withholding Tax (WHT) ---
        wht_position = ""
        if wht > 0:
            wht_position = f"Withholding tax of {wht:,.2f} has been deducted from your transactions. You can use these as tax credits when filing your annual return."
            highlights.append({"type": "info", "title": "WHT credits available", "detail": f"{wht:,.2f} in withholding tax can be claimed as credits on your tax return."})
            tax_tips.append(f"Collect WHT certificates for the {wht:,.2f} deducted — you'll need them to claim tax credits.")
        else:
            wht_position = "No withholding tax recorded. If clients deduct WHT from your payments, include those amounts when uploading documents."

        # --- Corporate Income Tax (CIT) ---
        cit_position = ""
        if cit > 0:
            cit_position = f"Corporate income tax of {cit:,.2f} has been recorded. Ensure this aligns with your expected CIT liability based on net profit."
            highlights.append({"type": "info", "title": "CIT recorded", "detail": f"{cit:,.2f} in corporate income tax recorded against your business."})
        elif net_profit > 0:
            estimated_cit = round(net_profit * 0.30, 2)
            cit_position = f"No CIT recorded yet, but based on your net profit of {net_profit:,.2f}, your estimated CIT exposure could be around {estimated_cit:,.2f} (at 30% rate). Consult your tax advisor for the exact rate."
            if estimated_cit > 0:
                tax_tips.append(f"Plan for approximately {estimated_cit:,.2f} in corporate income tax based on current profits.")
        else:
            cit_position = "No corporate income tax recorded. With a net loss, you may not owe CIT this period."

        # --- PAYE / Payroll ---
        paye_position = ""
        if paye > 0:
            paye_position = f"PAYE/payroll tax of {paye:,.2f} has been recorded. Remember to remit this to the tax authority monthly."
            highlights.append({"type": "info", "title": "PAYE obligations", "detail": f"{paye:,.2f} in payroll tax — ensure monthly remittance is up to date."})
            tax_tips.append("PAYE must be remitted monthly. Late remittance attracts penalties and interest.")
        else:
            paye_position = "No PAYE/payroll tax recorded. If you have employees, ensure payroll deductions are tracked."

        # --- Customs / Import Levy ---
        customs_position = ""
        if customs > 0:
            customs_pct = (customs / total_exp * 100) if total_exp > 0 else 0
            customs_position = f"Customs duties and import levies total {customs:,.2f} ({customs_pct:.1f}% of expenses)."
            if customs_pct > 15:
                highlights.append({"type": "warning", "title": "High import costs", "detail": f"Customs/levies are {customs_pct:.1f}% of expenses. Consider local sourcing alternatives."})
                tax_tips.append("Import duties are a significant cost. Explore local suppliers or duty-free trade agreements.")
        else:
            customs_position = "No customs duties or import levies recorded."

        # --- Total tax burden ---
        effective_tax_rate = round((total_tax_burden / total_rev * 100), 2) if total_rev > 0 else 0
        if total_tax_burden > 0 and net_profit > 0:
            tax_to_profit = round((total_tax_burden / net_profit * 100), 2)
            if tax_to_profit > 30:
                highlights.append({"type": "warning", "title": "High tax burden", "detail": f"Total taxes ({total_tax_burden:,.2f}) are {tax_to_profit:.0f}% of net profit. Review with a tax advisor."})

        # Filing reminder
        filing_parts = []
        if net_vat > 0:
            filing_parts.append("VAT return")
        if paye > 0:
            filing_parts.append("monthly PAYE remittance")
        if net_profit > 0:
            filing_parts.append("annual CIT filing")
        if wht > 0:
            filing_parts.append("WHT credit claims")
        if filing_parts:
            filing_reminder = f"Upcoming obligations: {', '.join(filing_parts)}. Stay on top of deadlines to avoid penalties."

        if total_exp > 0:
            tax_tips.append("Track all business expenses — they reduce your taxable profit and lower your tax bill.")
        tax_tips.append("Keep all tax receipts and certificates organised for at least 6 years.")

        tax_insights = {
            "vat_position": vat_position,
            "wht_position": wht_position,
            "cit_position": cit_position,
            "paye_position": paye_position,
            "customs_position": customs_position,
            "tax_tips": tax_tips[:4],
            "estimated_vat_liability": estimated_vat_liability,
            "total_tax_burden": total_tax_burden,
            "effective_tax_rate": effective_tax_rate,
            "filing_reminder": filing_reminder,
        }

        # --- Cashflow trend ---
        cashflow_analysis = ""
        if len(cashflow) >= 2:
            recent = cashflow[-1]
            previous = cashflow[-2]
            recent_net = recent.get("revenue", 0) - recent.get("expenses", 0)
            prev_net = previous.get("revenue", 0) - previous.get("expenses", 0)
            if recent_net > prev_net:
                cashflow_analysis = f"Cash flow is improving — net flow went from {prev_net:,.2f} to {recent_net:,.2f} in the most recent period."
            elif recent_net < prev_net:
                cashflow_analysis = f"Cash flow is declining — net flow dropped from {prev_net:,.2f} to {recent_net:,.2f}. Keep an eye on incoming payments."
                highlights.append({"type": "warning", "title": "Cash flow declining", "detail": f"Net cash flow dropped from {prev_net:,.2f} to {recent_net:,.2f}."})
            else:
                cashflow_analysis = "Cash flow is stable compared to the previous period."
        elif len(cashflow) == 1:
            net = cashflow[0].get("revenue", 0) - cashflow[0].get("expenses", 0)
            cashflow_analysis = f"Only one period of data so far (net: {net:,.2f}). Upload more documents to see trends."
        else:
            cashflow_analysis = "No cashflow data available yet."

        # --- Vendor concentration ---
        vendor_insights = ""
        if by_vendor and total_exp > 0:
            top_vendor = max(by_vendor.items(), key=lambda x: x[1].get("expenses", 0))
            top_vendor_pct = (top_vendor[1].get("expenses", 0) / total_exp * 100) if total_exp > 0 else 0
            if top_vendor_pct > 40:
                vendor_insights = f"'{top_vendor[0]}' accounts for {top_vendor_pct:.0f}% of your expenses — that's a concentration risk. Consider diversifying suppliers."
                highlights.append({"type": "warning", "title": "Vendor concentration risk", "detail": f"'{top_vendor[0]}' is {top_vendor_pct:.0f}% of your spending."})
            else:
                vendor_insights = f"Your spending is spread across {len(by_vendor)} vendors. Top vendor '{top_vendor[0]}' is {top_vendor_pct:.0f}% of expenses."

        # --- Pending reviews ---
        if pending_review > 0:
            highlights.append({"type": "info", "title": "Documents need review", "detail": f"{pending_review} document(s) are waiting for your review in the Review Queue."})
            next_steps.append(f"Review {pending_review} pending document(s) in the Review Queue.")

        # --- Next steps ---
        if net_profit < 0:
            next_steps.append("Identify your top 3 expense categories and look for savings.")
        if total_docs < 5:
            next_steps.append("Upload more financial documents to get a more accurate picture.")
        if net_vat > 0:
            next_steps.append(f"Set aside {net_vat:,.2f} for your next VAT payment.")
        if wht > 0:
            next_steps.append("Collect all WHT certificates for your annual tax credit claim.")
        if not next_steps:
            next_steps.append("Keep uploading invoices and receipts regularly for up-to-date insights.")

        return {
            "summary": summary,
            "highlights": highlights[:6],
            "tax_insights": tax_insights,
            "cashflow_analysis": cashflow_analysis,
            "profitability_analysis": profitability_analysis,
            "vendor_insights": vendor_insights,
            "next_steps": next_steps[:4],
            "confidence": "medium" if total_docs >= 5 else "low",
        }

