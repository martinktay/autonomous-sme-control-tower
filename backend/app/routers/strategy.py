from fastapi import APIRouter
from typing import Dict, Any
from app.models import Strategy
from pydantic import BaseModel

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


class SimulateRequest(BaseModel):
    org_id: str


@router.post("/simulate")
async def simulate_strategies(request: SimulateRequest) -> Strategy:
    """Generate strategy options based on current NSI"""
    
    # TODO: Implement strategy agent simulation
    
    raise NotImplementedError()


@router.post("/select")
async def select_strategy(
    org_id: str,
    strategy_id: str
) -> Dict[str, Any]:
    """Select a strategy for execution"""
    
    # TODO: Mark strategy as selected
    
    return {
        "org_id": org_id,
        "strategy_id": strategy_id,
        "status": "selected"
    }
