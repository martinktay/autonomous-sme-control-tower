"""
Voice interaction router — briefings, summaries, and free-form Q&A.

Supports two frontend interaction modes:
- Text mode: returns JSON text answers only (no audio generation).
- Voice mode: same JSON text answers; the frontend uses browser
  SpeechSynthesis (Web Speech API) for TTS playback.

Endpoints:
  POST /api/voice/brief            — generate a text briefing
  GET  /api/voice/{org_id}/summary — text-only operational briefing
  POST /api/voice/{org_id}/ask     — answer any business question
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.agents.voice_agent import VoiceAgent
from app.services.ddb_service import get_ddb_service
from app.middleware.org_isolation import validate_org_id_from_body

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])
voice_agent = VoiceAgent()
ddb_service = get_ddb_service()


class VoiceBriefRequest(BaseModel):
    """Request body for generating a briefing."""
    org_id: str


class VoiceQueryRequest(BaseModel):
    """Request body for asking a business question."""
    org_id: str
    question: str
    mode: str = "text"


@router.post("/brief")
async def generate_voice_brief(request: VoiceBriefRequest, req: Request) -> Dict[str, Any]:
    """Generate a text briefing from NSI + actions."""
    validate_org_id_from_body(req, request.org_id)
    try:
        nsi_data = ddb_service.get_latest_nsi(request.org_id)
        actions = ddb_service.get_actions(request.org_id, limit=5)
    except Exception as exc:
        logger.error("Failed to fetch briefing data for org %s: %s", request.org_id, exc)
        return {"org_id": request.org_id, "briefing": "Unable to load business data.", "nsi_score": 0}

    nsi_score = (
        nsi_data.get("nova_stability_index", nsi_data.get("nsi_score", 0))
        if nsi_data else 0
    )
    top_risks = nsi_data.get("top_risks", []) if nsi_data else []

    text = voice_agent.generate_briefing_text(
        nsi_score=nsi_score,
        top_risks=top_risks,
        recent_actions=actions,
        trend="stable",
    )
    return {"org_id": request.org_id, "briefing": text, "nsi_score": nsi_score}


@router.get("/{org_id}/summary")
async def get_voice_summary(org_id: str) -> Dict[str, Any]:
    """Return a text-only operational briefing."""
    try:
        nsi_data = ddb_service.get_latest_nsi(org_id)
        actions = ddb_service.get_actions(org_id, limit=5)
    except Exception as exc:
        logger.error("Failed to fetch summary data for org %s: %s", org_id, exc)
        return {"org_id": org_id, "summary": "Unable to load business data."}

    nsi_score = (
        nsi_data.get("nova_stability_index", nsi_data.get("nsi_score", 0))
        if nsi_data else 0
    )
    top_risks = nsi_data.get("top_risks", []) if nsi_data else []

    text = voice_agent.generate_briefing_text(
        nsi_score=nsi_score,
        top_risks=top_risks,
        recent_actions=actions,
        trend="stable",
    )
    return {"org_id": org_id, "summary": text}


@router.post("/{org_id}/ask")
async def ask_business_question(org_id: str, request: VoiceQueryRequest, req: Request) -> Dict[str, Any]:
    """Answer a free-form business question using AI with full context."""
    validate_org_id_from_body(req, request.org_id)
    question = (request.question or "").strip()
    if not question:
        return {"org_id": org_id, "answer": "Please ask a question.", "source": "system"}

    try:
        nsi_data = ddb_service.get_latest_nsi(org_id)
    except Exception:
        nsi_data = None

    try:
        signals = ddb_service.get_signals(org_id)
    except Exception:
        signals = []

    risks = nsi_data.get("top_risks", []) if nsi_data else []

    pnl = None
    try:
        from app.services.finance_service import get_finance_service
        finance_svc = get_finance_service()
        pnl = finance_svc.get_pnl(org_id)
    except Exception:
        pass

    result = voice_agent.answer_business_query(
        question=question,
        nsi_data=nsi_data,
        signals=signals,
        risks=risks,
        pnl=pnl,
    )
    return {"org_id": org_id, "mode": request.mode, **result}
