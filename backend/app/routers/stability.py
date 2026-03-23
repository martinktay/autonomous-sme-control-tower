"""
NSI stability router — calculate and retrieve Nova Stability Index scores.

The NSI is the core health metric for each business, combining liquidity,
revenue stability, operational latency, and vendor risk sub-indices.

Endpoints:
  POST /api/stability/calculate    — recalculate NSI from current signals
  GET  /api/stability/{org_id}     — get the latest NSI score
  GET  /api/stability/{org_id}/history — get historical NSI scores
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from app.models import NSIScore
from app.agents.risk_agent import RiskAgent
from app.services.ddb_service import get_ddb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stability", tags=["stability"])
risk_agent = RiskAgent()
ddb_service = get_ddb_service()


@router.post("/calculate")
async def calculate_nsi(org_id: str) -> NSIScore:
    """Recalculate the Nova Stability Index from current signals."""
    try:
        signals = ddb_service.get_signals(org_id)
        context = {}
        nsi_score = risk_agent.calculate_nsi(org_id, signals, context)
        ddb_service.put_nsi_score(nsi_score.model_dump())
        return nsi_score
    except Exception as e:
        logger.error("NSI calculation failed for org %s: %s", org_id, e, exc_info=True)
        raise HTTPException(500, "NSI calculation failed. Check server logs.")


@router.get("/{org_id}")
async def get_nsi(org_id: str) -> Dict[str, Any]:
    """Get the latest NSI score for an organisation."""
    try:
        nsi_data = ddb_service.get_latest_nsi(org_id)
        return {"org_id": org_id, "nsi": nsi_data}
    except Exception as e:
        logger.error("Failed to fetch NSI for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve NSI score.")


@router.get("/{org_id}/history")
async def get_nsi_history(org_id: str, limit: int = 30) -> Dict[str, Any]:
    """Get historical NSI scores for trend analysis."""
    try:
        history = ddb_service.query_nsi_scores(org_id, limit=limit)
        return {"org_id": org_id, "history": history}
    except Exception as e:
        logger.error("Failed to fetch NSI history for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve NSI history.")
