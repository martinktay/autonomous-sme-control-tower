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
    strategy_description: str
    execution_steps: list
    predicted_improvement: float


@router.post("/execute")
async def execute_action(request: ExecuteRequest) -> Action:
    """Execute selected strategy via Nova Act"""
    
    action = action_agent.execute_strategy(
        org_id=request.org_id,
        strategy_id=request.strategy_id,
        strategy_description=request.strategy_description,
        execution_steps=request.execution_steps,
        predicted_improvement=request.predicted_improvement
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
    
    # TODO: Implement single action retrieval
    
    raise HTTPException(501, "Not implemented")
