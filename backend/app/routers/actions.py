"""
Action execution router — execute strategies and retrieve action history.

Endpoints:
  POST /api/actions/execute       — execute a strategy via Nova Act agent
  GET  /api/actions/{org_id}      — list action history for an org
  GET  /api/actions/{org_id}/{id} — get a specific action's details
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.models import Action
from app.agents.action_agent import ActionAgent
from app.services.ddb_service import get_ddb_service
from app.middleware.org_isolation import validate_org_id_from_body

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/actions", tags=["actions"])
action_agent = ActionAgent()
ddb_service = get_ddb_service()


class ExecuteRequest(BaseModel):
    """Payload for executing a strategy as an autonomous action."""
    org_id: str
    strategy_id: str
    strategy_description: str = ""
    action_type: str = "workflow_execution"


@router.post("/execute")
async def execute_action(request: ExecuteRequest, req: Request) -> Action:
    """Execute a selected strategy via the Nova Act agent."""
    # Validate body org_id matches JWT org_id
    validate_org_id_from_body(req, request.org_id)
    try:
        action = action_agent.execute_strategy(
            org_id=request.org_id,
            strategy_id=request.strategy_id,
            strategy_description=request.strategy_description,
            action_type=request.action_type,
        )
        ddb_service.put_action(action.model_dump())
        return action
    except Exception as e:
        logger.error("Action execution failed for org %s: %s", request.org_id, e, exc_info=True)
        raise HTTPException(500, "Action execution failed. Check server logs.")


@router.get("/{org_id}")
async def get_actions(org_id: str) -> Dict[str, Any]:
    """List action history for an organisation."""
    try:
        actions = ddb_service.get_actions(org_id)
        return {"org_id": org_id, "actions": actions}
    except Exception as e:
        logger.error("Failed to fetch actions for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve actions.")


@router.get("/{org_id}/{action_id}")
async def get_action(org_id: str, action_id: str) -> Dict[str, Any]:
    """Get details for a specific action execution."""
    action = ddb_service.get_action(org_id, action_id)
    if not action:
        raise HTTPException(404, f"Action {action_id} not found")
    return action
