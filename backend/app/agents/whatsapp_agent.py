"""
WhatsApp Agent — Parses incoming WhatsApp messages and generates insight summaries.

Handles:
- Extracting business data from WhatsApp text/image messages
- Generating daily/weekly WhatsApp-friendly insight summaries

Uses prompt templates from /prompts/v1/ for Nova Lite model invocations.
"""

from typing import Dict, Any, List, Optional
from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output


class WhatsAppAgent:
    """AI agent for WhatsApp message processing and insight delivery."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def extract_message(self, message_text: str) -> Dict[str, Any]:
        """Extract business data from a WhatsApp message.

        Args:
            message_text: Raw WhatsApp message text or OCR from image.

        Returns:
            Dict with message_type, vendor_name, amount, currency, items, etc.
        """
        prompt = load_prompt(
            "whatsapp-message-extraction",
            variables={"message_text": message_text},
        )
        # If no variable substitution happened, append the message
        if message_text not in prompt:
            prompt = f"{prompt}\n\nWhatsApp message:\n{message_text}"

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
        return clean_model_output(parse_json_safely(response))

    def generate_insight_summary(
        self,
        business_name: str,
        nsi_score: Optional[float],
        top_risks: List[str],
        transaction_summary: Optional[Dict[str, Any]] = None,
        stock_alerts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate a WhatsApp-friendly business insight summary.

        Args:
            business_name: Name of the business.
            nsi_score: Current NSI score (0-100) or None.
            top_risks: List of top risk descriptions.
            transaction_summary: Optional transaction summary dict.
            stock_alerts: Optional list of stock alert dicts.

        Returns:
            Dict with greeting, health_score, highlights, alerts, tip, sign_off.
        """
        context_parts = [f"Business: {business_name}"]
        if nsi_score is not None:
            context_parts.append(f"NSI Score: {nsi_score:.1f}/100")
        if top_risks:
            context_parts.append(f"Top risks: {'; '.join(top_risks[:3])}")
        if transaction_summary:
            rev = transaction_summary.get("total_revenue", 0)
            exp = transaction_summary.get("total_expenses", 0)
            context_parts.append(f"Revenue: {rev:,.0f}, Expenses: {exp:,.0f}")
        if stock_alerts:
            context_parts.append(f"Stock alerts: {len(stock_alerts)} items low")

        context_block = "\n".join(context_parts)

        prompt = load_prompt("whatsapp-insight-summary")
        prompt = f"{prompt}\n\nBusiness context:\n{context_block}"

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.4)
        return clean_model_output(parse_json_safely(response))

    def format_summary_for_whatsapp(self, summary: Dict[str, Any]) -> str:
        """Format a structured summary into plain WhatsApp text.

        Args:
            summary: Dict from generate_insight_summary().

        Returns:
            Plain text string ready to send via WhatsApp.
        """
        lines = []
        if summary.get("greeting"):
            lines.append(summary["greeting"])
        lines.append("")
        if summary.get("health_score"):
            lines.append(summary["health_score"])
        if summary.get("highlights"):
            for h in summary["highlights"]:
                lines.append(f"- {h}")
        if summary.get("alerts"):
            lines.append("")
            lines.append("Needs attention:")
            for a in summary["alerts"]:
                lines.append(f"! {a}")
        if summary.get("tip"):
            lines.append("")
            lines.append(f"Tip: {summary['tip']}")
        if summary.get("sign_off"):
            lines.append("")
            lines.append(summary["sign_off"])
        return "\n".join(lines)
