from datetime import datetime, timezone
from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client
from app.models import ActionExecution
from app.utils.id_generator import generate_id


class ActionAgent:
    """Agent for action execution via Nova Lite"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def execute_strategy(
        self,
        org_id: str,
        strategy_id: str,
        strategy_description: str,
        action_type: str = "workflow_execution"
    ) -> ActionExecution:
        """Execute strategy using Nova Lite to plan and simulate the action"""
        
        execution_id = generate_id("action")
        
        prompt = f"""You are an autonomous business operations agent. Execute the following strategy and return the result as JSON.

Strategy: {strategy_description}
Organization ID: {org_id}

Return ONLY valid JSON with these fields:
- "target": the entity or area affected (e.g. "accounts_payable", "vendor_management")
- "actions_taken": list of specific actions performed
- "status": "success"
- "summary": brief description of what was done

JSON:"""
        
        try:
            response = self.bedrock.invoke_nova_lite(prompt, temperature=0.3)
            
            # Try to parse the response as JSON for the target field
            from app.utils.json_guard import parse_json_safely, clean_model_output
            parsed = clean_model_output(parse_json_safely(response))
            target = parsed.get("target", "business_operations") if isinstance(parsed, dict) else "business_operations"
            
            action = ActionExecution(
                execution_id=execution_id,
                org_id=org_id,
                strategy_id=strategy_id,
                action_type=action_type,
                target_entity=target,
                execution_status="success",
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            action = ActionExecution(
                execution_id=execution_id,
                org_id=org_id,
                strategy_id=strategy_id,
                action_type=action_type,
                target_entity="unknown",
                execution_status="failed",
                error_reason=str(e),
                timestamp=datetime.now(timezone.utc)
            )
        
        return action
