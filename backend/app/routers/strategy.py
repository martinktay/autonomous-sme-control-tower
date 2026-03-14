from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
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
async def simulate_strategies(request: SimulateRequest) -> Dict[str, Any]:
    """Generate strategy options based on current NSI"""

    nsi_data = ddb_service.get_latest_nsi(request.org_id)

    if not nsi_data:
        raise HTTPException(404, "No NSI score found. Calculate NSI first.")

    current_nsi = nsi_data.get("nsi_score", nsi_data.get("nova_stability_index", 50.0))
    top_risks = nsi_data.get("top_risks", [])
    nsi_id = nsi_data.get("nsi_id", "unknown")

    strategies = strategy_agent.simulate_strategies(
        org_id=request.org_id,
        nsi_snapshot_id=nsi_id,
        current_nsi=current_nsi,
        top_risks=top_risks,
        context={},
    )

    for s in strategies:
        ddb_service.put_strategy(s.model_dump())

    return {
        "org_id": request.org_id,
        "current_nsi": current_nsi,
        "strategies": [s.model_dump() for s in strategies],
    }


@router.get("/{org_id}")
async def get_strategies(org_id: str) -> Dict[str, Any]:
    """Get strategies for organization"""
    strategies = ddb_service.query_strategies(org_id)
    return {"org_id": org_id, "strategies": strategies}


@router.post("/select")
async def select_strategy(org_id: str, strategy_id: str) -> Dict[str, Any]:
    """Select a strategy for execution"""
    return {"org_id": org_id, "strategy_id": strategy_id, "status": "selected"}
