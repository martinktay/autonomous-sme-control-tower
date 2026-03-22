"""
Desktop Sync Agent — AI-powered POS file extraction and processing.

Uses Nova Lite to parse POS exports, sales files, and receipt dumps
uploaded by a desktop companion agent watching designated folders.
"""

import json
import logging
from typing import Any, Dict

from app.utils.bedrock_client import get_bedrock_client
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely, clean_model_output

logger = logging.getLogger(__name__)


class DesktopSyncAgent:
    """Extracts structured data from POS export files."""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def extract_file_data(
        self,
        file_content: str,
        filename: str = "",
        file_type: str = "unknown",
        business_type: str = "supermarket",
        business_name: str = "",
        country: str = "Nigeria",
    ) -> Dict[str, Any]:
        """Parse a POS export file and extract structured records."""
        prompt = load_prompt("desktop-sync-extraction", {
            "file_content": file_content[:5000],
            "filename": filename,
            "file_type": file_type,
            "business_type": business_type,
            "business_name": business_name or "SME Business",
            "country": country,
        })

        response = self.bedrock.invoke_nova_lite(prompt, max_tokens=4000, temperature=0.2)
        parsed = parse_json_safely(response)
        return clean_model_output(parsed)


def get_desktop_sync_agent() -> DesktopSyncAgent:
    return DesktopSyncAgent()
