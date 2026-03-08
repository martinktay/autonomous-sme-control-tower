import json
import re
from typing import Any, Optional


def safe_json_parse(text: str) -> Optional[dict]:
    """Safely parse JSON from model output"""
    
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object in text
    json_obj_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(json_obj_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    return None


def extract_json_field(data: dict, field: str, default: Any = None) -> Any:
    """Safely extract field from parsed JSON"""
    return data.get(field, default)
