from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models import Action
from app.agents.action_agent import ActionAgent
from app.services.ddb_service import get_ddb_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/actions", tags=["actions"])
action_agent = ActionAgent()
ddb_service = get_ddb_service()


class ExecuteRequest(BaseModel):
    org_id: str
    strategy_id: str
    strategy_description: str = ""
    action_type: str = "workflow_execution"


@router.post("/execute")
async def execute_action(request: ExecuteRequest) -> Action:
    """Execute selected strategy via Nova Act"""
    
    action = action_agent.execute_strategy(
        org_id=request.org_id,
        strategy_id=request.strategy_id,
        strategy_description=request.strategy_description,
        action_type=request.action_type
    )
    
    ddb_service.put_action(action.model_dump())
    
    return action


@router.get("/{org_id}")
async def get_actions(org_id: str) -> Dict[str, Any]:
    """Get action history"""
    
    actions = ddb_service.get_actions(org_id)
    
    return {
        "org_id": org_id,
        "actions": actions
    }


@router.get("/{org_id}/{action_id}")
async def get_action(org_id: str, action_id: str) -> Dict[str, Any]:
    """Get specific action details"""
    
    action = ddb_service.get_action(org_id, action_id)
    if not action:
        raise HTTPException(404, f"Action {action_id} not found")
    return action
