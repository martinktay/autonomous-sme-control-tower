"""
Mapping Agent — AI-powered field mapping for uploaded CSV/Excel files.

Uses Nova Lite to map source columns to standard platform fields,
handling informal African business naming conventions.
"""

import json
import logging
from typing import Any, Dict, List

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class MappingAgent:
    """Maps uploaded file columns to standard platform fields using AI."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def map_columns(
        self,
        columns: List[str],
        sample_rows: List[List[str]],
        business_type: str = "general",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Map source columns to standard fields.

        Args:
            columns: List of column header names from the uploaded file.
            sample_rows: First few rows of data for context.
            business_type: The business segment (e.g. supermarket, artisan).
            country: Country for locale-aware mapping.

        Returns:
            Dict with mappings, unmapped_columns, and suggested_record_type.
        """
        prompt = load_prompt("field-mapping", {
            "columns": json.dumps(columns),
            "sample_rows": json.dumps(sample_rows[:3]),
            "business_type": business_type,
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, temperature=0.2)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_mapping_agent() -> MappingAgent:
    return MappingAgent()
