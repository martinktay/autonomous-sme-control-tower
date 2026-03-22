"""
Inventory Prediction Agent — AI-powered demand forecasting.

Uses Nova Lite to analyse historical sales data, predict future demand,
detect seasonal patterns, and generate reorder suggestions.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class PredictionAgent:
    """Forecasts inventory demand and generates reorder suggestions."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def predict_demand(
        self,
        sales_data: List[Dict[str, Any]],
        inventory_data: List[Dict[str, Any]],
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Analyse sales history and predict demand for inventory items."""
        prompt = load_prompt("inventory-prediction", {
            "sales_data": json.dumps(sales_data[:100]),
            "inventory_data": json.dumps(inventory_data[:50]),
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=3000, temperature=0.3)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_prediction_agent() -> PredictionAgent:
    return PredictionAgent()
