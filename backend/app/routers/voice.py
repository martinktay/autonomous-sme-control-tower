"""
Voice interaction router — briefings, summaries, and free-form Q&A.

Provides three endpoints:
- /brief  — generate an audio briefing (MP3) from current NSI + actions
- /{org_id}/summary — text-only version of the briefing
- /{org_id}/ask — answer any business question using AI with full context
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
from app.agents.voice_agent import VoiceAgent
from app.services.ddb_service import get_ddb_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/voice", tags=["voice"])
voice_agent = VoiceAgent()
ddb_service = get_ddb_service()


class VoiceBriefRequest(BaseModel):
    """Request body for generating a voice briefing."""

    org_id: str


class VoiceQueryRequest(BaseModel):
    """Request body for asking a free-form business question."""

    org_id: str
    question: str


@router.post("/brief")
async def generate_voice_brief(request: VoiceBriefRequest) -> Response:
    """Generate an audio briefing (MP3) summarising NSI score, risks, and recent actions."""
    
    nsi_data = ddb_service.get_latest_nsi(request.org_id)
    actions = ddb_service.get_actions(request.org_id, limit=5)
    
    nsi_score = nsi_data.get("nova_stability_index", 0) if nsi_data else 0
    top_risks = nsi_data.get("top_risks", []) if nsi_data else []
    
    text = voice_agent.generate_briefing_text(
        nsi_score=nsi_score,
        top_risks=top_risks,
        recent_actions=actions,
        trend="stable"
    )
    
    audio = voice_agent.generate_audio(text)
    
    return Response(
        content=audio,
        media_type="audio/mpeg"
    )


@router.get("/{org_id}/summary")
async def get_voice_summary(org_id: str) -> Dict[str, Any]:
    """Return a text-only operational briefing (same content as /brief, no audio)."""
    
    nsi_data = ddb_service.get_latest_nsi(org_id)
    actions = ddb_service.get_actions(org_id, limit=5)
    
    nsi_score = nsi_data.get("nova_stability_index", 0) if nsi_data else 0
    top_risks = nsi_data.get("top_risks", []) if nsi_data else []
    
    text = voice_agent.generate_briefing_text(
        nsi_score=nsi_score,
        top_risks=top_risks,
        recent_actions=actions,
        trend="stable"
    )
    
    return {
        "org_id": org_id,
        "summary": text
    }

@router.post("/{org_id}/ask")
async def ask_business_question(org_id: str, request: VoiceQueryRequest) -> Dict[str, Any]:
    """Answer a free-form business question using AI with full business context (NSI, signals, P&L)."""
    question = (request.question or "").strip()
    if not question:
        return {"org_id": org_id, "answer": "Please ask a question.", "source": "system"}

    nsi_data = ddb_service.get_latest_nsi(org_id)
    signals = ddb_service.get_signals(org_id)
    risks = nsi_data.get("top_risks", []) if nsi_data else []

    # Optionally enrich context with P&L data for financial questions
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
    return {"org_id": org_id, **result}
