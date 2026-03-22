"""
POS Connector Agent — AI-powered POS data extraction and normalisation.

Uses Nova Lite to parse raw POS system exports from popular Nigerian
POS systems and extract structured sales transactions.
"""

import json
import logging
from typing import Any, Dict

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class PosAgent:
    """Extracts structured data from POS system exports."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def extract_pos_data(
        self,
        pos_data: str,
        pos_system: str = "unknown",
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Parse raw POS data and extract structured transactions."""
        prompt = load_prompt("pos-data-extraction", {
            "pos_data": pos_data[:5000],
            "pos_system": pos_system,
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=4000, temperature=0.2)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_pos_agent() -> PosAgent:
    return PosAgent()
