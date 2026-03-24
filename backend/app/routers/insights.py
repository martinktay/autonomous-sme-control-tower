"""
Business Insights router — AI-generated plain-language business analysis.

Endpoints:
  GET /api/insights/{org_id} — generate AI insights from NSI, actions, and strategies
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from app.agents.insights_agent import InsightsAgent
from app.services.ddb_service import get_ddb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])

insights_agent = InsightsAgent()
ddb_service = get_ddb_service()


@router.get("/{org_id}")
async def get_business_insights(org_id: str) -> Dict[str, Any]:
    """Generate AI-powered business insights in plain language for SME owners."""
    try:
        nsi_data = ddb_service.get_latest_nsi(org_id)
        actions = ddb_service.get_actions(org_id, limit=5)
        strategies = ddb_service.query_strategies(org_id, limit=5)

        risks = []
        if nsi_data and "top_risks" in nsi_data:
            risks = nsi_data["top_risks"]

        insights = insights_agent.generate_insights(
            org_id=org_id,
            nsi_data=nsi_data,
            risks=risks,
            actions=actions,
            strategies=strategies,
        )

        return {"org_id": org_id, "insights": insights}

    except Exception as e:
        logger.error("Failed to generate insights for org %s: %s", org_id, e, exc_info=True)
        raise HTTPException(500, "Failed to generate insights. Check server logs for details.")
