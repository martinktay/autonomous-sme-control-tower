"""
Categorisation Agent — AI transaction categorisation for SME records.

Uses Nova Lite to classify transactions as revenue or expense and assign
appropriate categories, handling informal African business terminology.
"""

import logging
from typing import Any, Dict, Optional

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class CategorisationAgent:
    """Categorises transactions using AI."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def categorise_transaction(
        self,
        description: str,
        amount: float,
        counterparty: str = "",
        date: str = "",
        business_type: str = "general",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Categorise a single transaction.

        Args:
            description: Transaction description text.
            amount: Transaction amount.
            counterparty: Supplier or customer name.
            date: Transaction date string.
            business_type: Business segment for context.
            country: Country for locale-aware categorisation.

        Returns:
            Dict with transaction_type, category, confidence, subcategory, tags.
        """
        prompt = load_prompt("transaction-categorisation", {
            "description": description,
            "amount": str(amount),
            "counterparty": counterparty or "unknown",
            "date": date or "not specified",
            "business_type": business_type,
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.2)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_categorisation_agent() -> CategorisationAgent:
    return CategorisationAgent()
