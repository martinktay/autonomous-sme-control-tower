"""
AI Forecasting Agent — Revenue, expense, and cash runway projections.

Uses Nova Lite to analyse historical financial data and generate
forward-looking projections for African SME businesses.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class ForecastingAgent:
    """Generates revenue, expense, and cash runway forecasts."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def forecast(
        self,
        revenue_data: List[Dict[str, Any]],
        expense_data: List[Dict[str, Any]],
        cash_position: Dict[str, Any] | None = None,
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Generate financial forecasts from historical data."""
        prompt = load_prompt("revenue-forecasting", {
            "revenue_data": json.dumps(revenue_data[:200]),
            "expense_data": json.dumps(expense_data[:200]),
            "cash_position": json.dumps(cash_position) if cash_position else '{"balance": "unknown"}',
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=3000, temperature=0.3)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_forecasting_agent() -> ForecastingAgent:
    return ForecastingAgent()
