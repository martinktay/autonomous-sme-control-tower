"""
Inventory Agent — AI-powered stock analysis and alert generation.

Uses Nova Lite to analyse inventory data, detect risks (low stock,
slow movers, expiry), and generate actionable recommendations for
African SME retail businesses.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class InventoryAgent:
    """Analyses inventory and generates stock intelligence alerts."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def analyse_inventory(
        self,
        inventory_data: List[Dict[str, Any]],
        sales_data: List[Dict[str, Any]] | None = None,
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Analyse inventory and generate alerts.

        Args:
            inventory_data: List of inventory item dicts.
            sales_data: Optional recent sales/transaction data.
            business_type: Business segment.
            business_name: Name of the business.
            country: Country for locale context.

        Returns:
            Dict with alerts list and summary.
        """
        prompt = load_prompt("inventory-analysis", {
            "inventory_data": json.dumps(inventory_data[:50]),
            "sales_data": json.dumps(sales_data[:30]) if sales_data else "No sales data available",
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=3000, temperature=0.3)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_inventory_agent() -> InventoryAgent:
    return InventoryAgent()
