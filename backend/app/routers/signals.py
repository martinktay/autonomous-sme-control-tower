from fastapi import APIRouter
from typing import Dict, Any, List
from app.models import Signal
from app.services.ddb_service import get_ddb_service

router = APIRouter(prefix="/api/signals", tags=["signals"])
ddb_service = get_ddb_service()


@router.get("/{org_id}")
async def get_signals(org_id: str) -> Dict[str, Any]:
    """Get all signals for organization"""
    
    signals = ddb_service.get_signals(org_id)
    
    return {
        "org_id": org_id,
        "signals": signals
    }


@router.get("/{org_id}/{signal_id}")
async def get_signal(org_id: str, signal_id: str) -> Dict[str, Any]:
    """Get specific signal"""
    
    # TODO: Implement single signal retrieval
    
    return {
        "signal_id": signal_id,
        "org_id": org_id
    }
