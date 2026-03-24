"""
BSI stability router — calculate and retrieve Business Stability Index scores.

The BSI is the core health metric for each business, combining liquidity,
revenue stability, operational latency, and vendor risk sub-indices.

Endpoints:
  POST /api/stability/calculate    — recalculate BSI from current signals
  GET  /api/stability/{org_id}     — get the latest BSI score
  GET  /api/stability/{org_id}/history — get historical BSI scores
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from app.models import BSIScore
from app.agents.risk_agent import RiskAgent
from app.services.ddb_service import get_ddb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stability", tags=["stability"])
risk_agent = RiskAgent()
ddb_service = get_ddb_service()


@router.post("/calculate")
async def calculate_bsi(org_id: str) -> BSIScore:
    """Recalculate the Business Stability Index from current signals."""
    try:
        signals = ddb_service.get_signals(org_id)
        context = {}
        bsi_score = risk_agent.calculate_bsi(org_id, signals, context)
        ddb_service.put_bsi_score(bsi_score.model_dump())
        return bsi_score
    except Exception as e:
        logger.error("BSI calculation failed for org %s: %s", org_id, e, exc_info=True)
        raise HTTPException(500, "BSI calculation failed. Check server logs.")


@router.get("/{org_id}")
async def get_bsi(org_id: str) -> Dict[str, Any]:
    """Get the latest BSI score for an organisation."""
    try:
        bsi_data = ddb_service.get_latest_bsi(org_id)
        return {"org_id": org_id, "bsi": bsi_data}
    except Exception as e:
        logger.error("Failed to fetch BSI for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve BSI score.")


@router.get("/{org_id}/history")
async def get_bsi_history(org_id: str, limit: int = 30) -> Dict[str, Any]:
    """Get historical BSI scores for trend analysis."""
    try:
        history = ddb_service.query_bsi_scores(org_id, limit=limit)
        return {"org_id": org_id, "history": history}
    except Exception as e:
        logger.error("Failed to fetch BSI history for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve BSI history.")
