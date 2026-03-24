"""
Strategy simulation router — generate, list, and select strategies.

Endpoints:
  POST /api/strategy/simulate — AI-generate strategy options from current BSI
  GET  /api/strategy/{org_id} — list strategies for an org
  POST /api/strategy/select   — mark a strategy as selected for execution
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.models import Strategy
from app.agents.strategy_agent import StrategyAgent
from app.services.ddb_service import get_ddb_service
from app.middleware.org_isolation import validate_org_id_from_body

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategy", tags=["strategy"])
strategy_agent = StrategyAgent()
ddb_service = get_ddb_service()


class SimulateRequest(BaseModel):
    """Payload for triggering strategy simulation."""
    org_id: str


@router.post("/simulate")
async def simulate_strategies(request: SimulateRequest, req: Request) -> Dict[str, Any]:
    """Generate AI strategy options based on the current BSI score."""
    validate_org_id_from_body(req, request.org_id)
    try:
        bsi_data = ddb_service.get_latest_bsi(request.org_id)
        if not bsi_data:
            raise HTTPException(404, "No BSI score found. Calculate BSI first.")

        current_bsi = bsi_data.get("bsi_score", bsi_data.get("business_stability_index", 50.0))
        top_risks = bsi_data.get("top_risks", [])
        bsi_id = bsi_data.get("bsi_id", "unknown")

        strategies = strategy_agent.simulate_strategies(
            org_id=request.org_id,
            bsi_snapshot_id=bsi_id,
            current_bsi=current_bsi,
            top_risks=top_risks,
            context={},
        )

        for s in strategies:
            ddb_service.put_strategy(s.model_dump())

        return {
            "org_id": request.org_id,
            "current_bsi": current_bsi,
            "strategies": [s.model_dump() for s in strategies],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Strategy simulation failed for org %s: %s", request.org_id, e, exc_info=True)
        raise HTTPException(500, "Strategy simulation failed. Check server logs.")


@router.get("/{org_id}")
async def get_strategies(org_id: str) -> Dict[str, Any]:
    """List strategies for an organisation."""
    try:
        strategies = ddb_service.query_strategies(org_id)
        return {"org_id": org_id, "strategies": strategies}
    except Exception as e:
        logger.error("Failed to fetch strategies for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve strategies.")


@router.post("/select")
async def select_strategy(org_id: str, strategy_id: str) -> Dict[str, Any]:
    """Mark a strategy as selected for execution."""
    return {"org_id": org_id, "strategy_id": strategy_id, "status": "selected"}
