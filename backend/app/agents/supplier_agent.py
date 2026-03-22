"""
Supplier Intelligence Agent — AI-powered supplier scoring and risk analysis.

Uses Nova Lite to evaluate supplier reliability, detect single-source
dependencies, compare pricing, and recommend alternatives.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class SupplierAgent:
    """Analyses supplier data and generates intelligence reports."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def analyse_suppliers(
        self,
        supplier_data: List[Dict[str, Any]],
        transaction_data: List[Dict[str, Any]] | None = None,
        inventory_data: List[Dict[str, Any]] | None = None,
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Score suppliers and generate intelligence report."""
        prompt = load_prompt("supplier-intelligence", {
            "supplier_data": json.dumps(supplier_data[:50]),
            "transaction_data": json.dumps(transaction_data[:50]) if transaction_data else "[]",
            "inventory_data": json.dumps(inventory_data[:30]) if inventory_data else "[]",
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=3000, temperature=0.3)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_supplier_agent() -> SupplierAgent:
    return SupplierAgent()
