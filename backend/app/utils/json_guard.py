"""
JSON parsing safety utilities for handling model output.

Provides progressively aggressive JSON extraction strategies:
1. Direct json.loads
2. Extract from markdown code blocks
3. Regex search for JSON objects in free text

Also supports Pydantic schema validation (Requirement 13.3).
"""

import json
import re
import logging
from typing import Any, Optional, TypeVar, Type, Union
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def safe_json_parse(text: str) -> Optional[dict]:
    """Safely extract and parse JSON from raw model output.

    Tries three strategies in order:
    1. Direct json.loads on the full text
    2. Extract JSON from ```json ... ``` code blocks
    3. Regex search for the first { ... } object

    Args:
        text: Raw text that may contain JSON.

    Returns:
        Parsed dict, or None if all strategies fail.
    """
    if not text:
        return None
    
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object in text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    logger.error(f"Failed to parse JSON from text: {text[:200]}...")
    return None


def parse_json_safely(response: str) -> dict:
    """Parse JSON from model response; raises ValueError on failure.

    Thin wrapper around safe_json_parse that converts None to a ValueError
    so callers get a clear exception rather than a silent None.

    Args:
        response: Model response text.

    Returns:
        Parsed dict.

    Raises:
        ValueError: If JSON cannot be extracted from the response.
    """
    parsed = safe_json_parse(response)
    if parsed is None:
        logger.error(f"JSON parsing failed. Raw output: {response}")
        raise ValueError("Failed to parse JSON from model response")
    return parsed


def validate_with_schema(
    response: str,
    schema: Type[T],
    log_raw_on_error: bool = True
) -> T:
    """
    Parse JSON and validate against Pydantic schema
    
    This function enforces strict JSON output validation as required by
    Requirement 13.3: "WHEN a prompt is used, THE NovaSME_System SHALL 
    enforce strict JSON output validation against Pydantic schemas"
    
    Args:
        response: Model response text containing JSON
        schema: Pydantic model class to validate against
        log_raw_on_error: Whether to log raw output on parsing/validation failure
        
    Returns:
        Validated Pydantic model instance
        
    Raises:
        ValueError: If JSON cannot be parsed
        ValidationError: If JSON doesn't match schema
    """
    # First, parse the JSON
    try:
        parsed_data = safe_json_parse(response)
        if parsed_data is None:
            if log_raw_on_error:
                logger.error(f"JSON parsing failed. Raw output: {response}")
            raise ValueError("Failed to parse JSON from model response")
    except Exception as e:
        if log_raw_on_error:
            logger.error(f"JSON parsing error. Raw output: {response}")
        raise ValueError(f"Failed to parse JSON: {str(e)}")
    
    # Then, validate against Pydantic schema
    try:
        validated_model = schema(**parsed_data)
        logger.info(f"Successfully validated response against {schema.__name__} schema")
        return validated_model
    except ValidationError as e:
        if log_raw_on_error:
            logger.error(
                f"Schema validation failed for {schema.__name__}. "
                f"Raw output: {response}\n"
                f"Validation errors: {e.errors()}"
            )
        # Re-raise the original ValidationError
        raise


def parse_and_validate(
    response: str,
    schema: Type[T]
) -> T:
    """
    Convenience function to parse and validate in one call
    
    Implements Requirement 13.4: "IF prompt output parsing fails, 
    THEN THE NovaSME_System SHALL log the raw output and return a parsing error"
    
    Args:
        response: Model response text
        schema: Pydantic model class to validate against
        
    Returns:
        Validated Pydantic model instance
        
    Raises:
        ValueError: If parsing or validation fails
    """
    return validate_with_schema(response, schema, log_raw_on_error=True)


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text for clean display.

    Strips bold, italic, headers, bullet markers, and code fences
    so AI-generated text appears as clean plain text to end users.

    Args:
        text: Raw text that may contain markdown formatting.

    Returns:
        Clean plain text with markdown artifacts removed.
    """
    if not text:
        return text
    # Remove bold/italic markers: **text**, __text__, *text*, _text_
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text)
    # Remove markdown headers: # ## ### etc.
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove code fences
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Replace bullet markers (* or -) with clean dash
    text = re.sub(r'^\s*[\*\-]\s+', '- ', text, flags=re.MULTILINE)
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def clean_model_output(data: Union[dict, list, str]) -> Union[dict, list, str]:
    """Recursively strip markdown from all string values in a dict/list.

    Walks through nested dicts and lists, applying strip_markdown to every
    string value. Non-string leaves are returned unchanged.

    Args:
        data: A dict, list, or string from parsed model output.

    Returns:
        The same structure with all string values cleaned.
    """
    if isinstance(data, str):
        return strip_markdown(data)
    if isinstance(data, dict):
        return {k: clean_model_output(v) for k, v in data.items()}
    if isinstance(data, list):
        return [clean_model_output(item) for item in data]
    return data
