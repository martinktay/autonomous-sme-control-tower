from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models import Strategy
from app.agents.strategy_agent import StrategyAgent
from app.services.ddb_service import get_ddb_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/strategy", tags=["strategy"])
strategy_agent = StrategyAgent()
ddb_service = get_ddb_service()


class SimulateRequest(BaseModel):
    org_id: str


@router.post("/simulate")
async def simulate_strategies(request: SimulateRequest) -> Strategy:
    """Generate strategy options based on current NSI"""
    
    nsi_data = ddb_service.get_latest_nsi(request.org_id)
    
    if not nsi_data:
        raise HTTPException(404, "No NSI score found. Calculate NSI first.")
    
    current_nsi = nsi_data["nova_stability_index"]
    top_risks = nsi_data.get("top_risks", [])
    
    strategy = strategy_agent.simulate_strategies(
        org_id=request.org_id,
        current_nsi=current_nsi,
        top_risks=top_risks,
        context={}
    )
    
    ddb_service.put_strategy(strategy.model_dump())
    
    return strategy


@router.post("/select")
async def select_strategy(
    org_id: str,
    strategy_id: str
) -> Dict[str, Any]:
    """Select a strategy for execution"""
    
    # TODO: Update strategy record with selection
    
    return {
        "org_id": org_id,
        "strategy_id": strategy_id,
        "status": "selected"
    }
