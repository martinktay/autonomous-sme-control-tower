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
from typing import Any, Optional, TypeVar, Type
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
