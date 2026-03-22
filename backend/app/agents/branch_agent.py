"""
Cross-Branch Optimisation Agent — Multi-branch intelligence.

Uses Nova Lite to compare branch performance, recommend stock transfers,
and generate consolidated multi-branch reports.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class BranchAgent:
    """Optimises operations across multiple branches."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def optimise(
        self,
        branch_data: List[Dict[str, Any]],
        branch_inventory: Dict[str, List[Dict[str, Any]]],
        branch_sales: Dict[str, List[Dict[str, Any]]],
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Analyse branches and generate optimisation recommendations."""
        prompt = load_prompt("cross-branch-optimisation", {
            "branch_data": json.dumps(branch_data[:20]),
            "branch_inventory": json.dumps(
                {k: v[:30] for k, v in list(branch_inventory.items())[:10]}
            ),
            "branch_sales": json.dumps(
                {k: v[:30] for k, v in list(branch_sales.items())[:10]}
            ),
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=3000, temperature=0.3)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_branch_agent() -> BranchAgent:
    return BranchAgent()
