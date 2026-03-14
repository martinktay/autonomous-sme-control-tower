# Utilities Module

This module provides core utilities for the Autonomous SME Control Tower backend.

## Prompt Loader

The `prompt_loader.py` module provides functionality to load prompt templates from the `/prompts/v1/` directory with variable substitution support.

### Usage

```python
from app.utils.prompt_loader import load_prompt

# Load a prompt template without variables
prompt = load_prompt("signal-invoice")

# Load a prompt template with variable substitution
prompt = load_prompt("risk-diagnosis", variables={
    "org_id": "org_123",
    "signal_count": 42
})
```

### Features

- Loads prompt templates from `/prompts/v1/` directory
- Supports variable substitution using Python's `.format()` syntax
- Singleton pattern for efficient reuse
- Error handling for missing templates and variables
- Logging for debugging and monitoring

## JSON Guard

The `json_guard.py` module provides robust JSON parsing and Pydantic schema validation for model outputs.

### Usage

```python
from app.utils.json_guard import parse_and_validate
from app.models.invoice import Invoice

# Parse and validate model response against Pydantic schema
response = bedrock_client.invoke_nova_lite(prompt)
validated_invoice = parse_and_validate(response, Invoice)
```

### Features

- Extracts JSON from various formats (plain JSON, markdown code blocks, embedded JSON)
- Validates against Pydantic schemas
- Logs raw output when parsing fails (Requirement 13.4)
- Provides detailed error messages for debugging
- Type-safe with generic type hints

### Functions

- `safe_json_parse(text)` - Parse JSON with fallback strategies
- `parse_json_safely(response)` - Parse JSON with error logging
- `validate_with_schema(response, schema)` - Parse and validate against Pydantic model
- `parse_and_validate(response, schema)` - Convenience function with full logging

## Bedrock Client

The `bedrock_client.py` module provides a wrapper for AWS Bedrock Nova models with error handling and retry logic.

### Features

- Circuit breaker pattern for fault tolerance
- Exponential backoff retry logic
- Support for all Nova models (Lite, Act, Sonic, Embeddings)
- Singleton pattern for connection reuse
- Comprehensive error handling

### Usage

```python
from app.utils.bedrock_client import get_bedrock_client

bedrock = get_bedrock_client()

# Invoke Nova 2 Lite for text generation
response = bedrock.invoke_nova_lite(prompt, temperature=0.7)

# Generate embeddings
embedding = bedrock.generate_embeddings(text)

# Execute agentic actions
result = bedrock.invoke_nova_act(task, context)

# Generate voice output
audio = bedrock.invoke_nova_sonic(text)
```

## Requirements Mapping

This module implements the following requirements:

- **Requirement 13.1**: Store all prompt templates in `/prompts/v1/` directory
- **Requirement 13.2**: Load prompts from files at runtime, not hardcode them
- **Requirement 13.3**: Enforce strict JSON output validation against Pydantic schemas
- **Requirement 13.4**: Log raw output when parsing fails and return parsing error
