from datetime import datetime
from typing import Dict, Any
from app.utils.bedrock_client import get_bedrock_client
from app.models import Action, ActionStatus


class ActionAgent:
    """Agent for action execution via Nova Act"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
    
    def execute_strategy(
        self,
        org_id: str,
        strategy_id: str,
        strategy_description: str,
        execution_steps: list,
        predicted_improvement: float
    ) -> Action:
        """Execute strategy using Nova Act"""
        
        action_id = f"action_{datetime.utcnow().timestamp()}"
        
        task = f"""
Execute the following business strategy:
{strategy_description}

Steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(execution_steps))}
"""
        
        action = Action(
            action_id=action_id,
            org_id=org_id,
            strategy_id=strategy_id,
            predicted_nsi_improvement=predicted_improvement,
            status=ActionStatus.IN_PROGRESS,
            started_at=datetime.utcnow()
        )
        
        try:
            result = self.bedrock.invoke_nova_act(task, {"org_id": org_id})
            
            action.status = ActionStatus.COMPLETED
            action.completed_at = datetime.utcnow()
            action.execution_log = result
            
        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            action.completed_at = datetime.utcnow()
        
        return action
