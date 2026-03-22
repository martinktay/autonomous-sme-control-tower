"""
Alert Agent — Proactive business alert generation using AI.

Uses Nova Lite to analyse business signals (transactions, inventory,
counterparties) and generate actionable alerts for SME owners.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class AlertAgent:
    """Generates proactive business alerts from operational signals."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def generate_alerts(
        self,
        signals_data: Dict[str, Any],
        business_type: str = "general",
        business_name: str = "",
        country: str = "Nigeria",
        tier: str = "starter",
    ) -> Dict[str, Any]:
        """Generate alerts from business signals.

        Args:
            signals_data: Dict containing transactions, inventory, counterparties, etc.
            business_type: Business segment.
            business_name: Name of the business.
            country: Country for locale context.
            tier: Pricing tier (affects alert limits).

        Returns:
            Dict with alerts list and summary string.
        """
        prompt = load_prompt("alert-generation", {
            "signals_data": json.dumps(signals_data),
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
            "tier": tier,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=3000, temperature=0.3)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_alert_agent() -> AlertAgent:
    return AlertAgent()
