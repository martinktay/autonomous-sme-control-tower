"""
Bank Reconciliation Agent — AI-powered bank statement matching.

Uses Nova Lite to match bank statement entries against existing
business transactions and finance documents.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class BankAgent:
    """Reconciles bank statements against business records."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def reconcile(
        self,
        bank_entries: List[Dict[str, Any]],
        business_transactions: List[Dict[str, Any]],
        finance_documents: List[Dict[str, Any]] | None = None,
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Match bank entries to existing transactions."""
        prompt = load_prompt("bank-reconciliation", {
            "bank_entries": json.dumps(bank_entries[:100]),
            "business_transactions": json.dumps(business_transactions[:100]),
            "finance_documents": json.dumps(finance_documents[:50]) if finance_documents else "[]",
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=4000, temperature=0.2)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_bank_agent() -> BankAgent:
    return BankAgent()
