from fastapi import APIRouter, Response
from typing import Dict, Any
from app.agents.voice_agent import VoiceAgent
from app.services.ddb_service import get_ddb_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/voice", tags=["voice"])
voice_agent = VoiceAgent()
ddb_service = get_ddb_service()


class VoiceBriefRequest(BaseModel):
    org_id: str


@router.post("/brief")
async def generate_voice_brief(request: VoiceBriefRequest) -> Response:
    """Generate voice briefing using Nova Sonic"""
    
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
    """Get text summary for voice briefing"""
    
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
