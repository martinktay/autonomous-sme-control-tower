# Agent Template

Use this structure when creating a new backend agent.

## File location

```
backend/app/agents/<agent_name>.py
```

## Agent responsibilities

- One core responsibility only
- Accept structured input
- Call Bedrock or infrastructure services if needed
- Validate output
- Return normalized structured data

## Recommended pattern

1. Load prompt from prompts/v1 if needed
2. Inject runtime values
3. Call Bedrock through utils/bedrock_client.py
4. Parse with utils/json_guard.py
5. Validate with Pydantic model
6. Return result
7. Persist results through service layer if needed

## Avoid

- Direct Bedrock logic in routers
- Prompt text hardcoded inside router files
- Mixed concerns across agents
- Skipping validation for structured model output

## Example agent structure

```python
from app.utils.bedrock_client import invoke_nova_model
from app.utils.json_guard import parse_json_safely
from app.models.signal import Signal
from app.services.ddb_service import store_signal
import logging

logger = logging.getLogger(__name__)

class SignalAgent:
    """Agent responsible for processing operational signals"""
    
    def __init__(self):
        self.prompt_path = "prompts/v1/signal_invoice.md"
    
    async def process_invoice(self, org_id: str, file_content: bytes, filename: str) -> Signal:
        """
        Extract structured data from invoice document
        
        Args:
            org_id: Organization identifier
            file_content: Raw invoice file bytes
            filename: Original filename
            
        Returns:
            Signal: Validated signal object
        """
        try:
            # 1. Load prompt template
            with open(self.prompt_path, 'r') as f:
                prompt_template = f.read()
            
            # 2. Inject runtime values
            prompt = prompt_template.format(
                invoice_content=file_content.decode('utf-8'),
                filename=filename
            )
            
            # 3. Call Bedrock
            response = await invoke_nova_model(
                model_id="amazon.nova-lite-v1",
                prompt=prompt,
                max_tokens=2000
            )
            
            # 4. Parse JSON safely
            parsed_data = parse_json_safely(response)
            
            # 5. Validate with Pydantic
            signal = Signal(
                org_id=org_id,
                signal_type="invoice",
                content=parsed_data,
                processing_status="processed"
            )
            
            # 6. Persist through service layer
            await store_signal(signal)
            
            # 7. Return validated result
            return signal
            
        except Exception as e:
            logger.error(f"Invoice processing failed: {str(e)}", exc_info=True)
            raise
```
