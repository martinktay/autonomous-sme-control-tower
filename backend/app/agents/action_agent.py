import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client
from app.models import ActionExecution


class ActionAgent:
    """Agent for action execution via Nova Act"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def execute_strategy(
        self,
        org_id: str,
        strategy_id: str,
        strategy_description: str,
        action_type: str = "workflow_execution"
    ) -> ActionExecution:
        """Execute strategy using Nova Act"""
        
        execution_id = f"exec_{uuid.uuid4().hex[:12]}"
        
        task = f"""
Execute the following business strategy:
{strategy_description}

Organization ID: {org_id}
"""
        
        try:
            result = self.bedrock.invoke_nova_act(task, {"org_id": org_id})
            
            action = ActionExecution(
                execution_id=execution_id,
                org_id=org_id,
                strategy_id=strategy_id,
                action_type=action_type,
                target_entity=result.get("target", "unknown"),
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
