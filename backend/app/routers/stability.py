from fastapi import APIRouter
from typing import Dict, Any
from app.models import NSIScore
from app.agents.risk_agent import RiskAgent
from app.services.ddb_service import get_ddb_service

router = APIRouter(prefix="/api/stability", tags=["stability"])
risk_agent = RiskAgent()
ddb_service = get_ddb_service()


@router.post("/calculate")
async def calculate_nsi(org_id: str) -> NSIScore:
    """Calculate NSI for organization"""
    
    signals = ddb_service.get_signals(org_id)
    context = {}  # TODO: Add business context
    
    nsi_score = risk_agent.calculate_nsi(org_id, signals, context)
    ddb_service.put_nsi_score(nsi_score.model_dump())
    
    return nsi_score


@router.get("/{org_id}")
async def get_nsi(org_id: str) -> Dict[str, Any]:
    """Get latest NSI score"""
    
    nsi_data = ddb_service.get_latest_nsi(org_id)
    
    return {
        "org_id": org_id,
        "nsi": nsi_data
    }


@router.get("/{org_id}/history")
async def get_nsi_history(org_id: str, limit: int = 30) -> Dict[str, Any]:
    """Get NSI history"""
    
    # TODO: Implement historical query
    
    return {
        "org_id": org_id,
        "history": []
    }
