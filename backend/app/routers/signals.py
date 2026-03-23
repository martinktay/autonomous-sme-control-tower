"""
Signal retrieval router — list and fetch business signals.

Signals are the raw data events ingested from invoices, emails, WhatsApp,
POS exports, and other sources. They feed into the NSI risk engine.

Endpoints:
  GET /api/signals/{org_id}            — list all signals for an org
  GET /api/signals/{org_id}/{signal_id} — get a specific signal
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from app.services.ddb_service import get_ddb_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signals", tags=["signals"])
ddb_service = get_ddb_service()


@router.get("/{org_id}")
async def get_signals(org_id: str) -> Dict[str, Any]:
    """List all signals for an organisation."""
    try:
        signals = ddb_service.get_signals(org_id)
        return {"org_id": org_id, "signals": signals}
    except Exception as e:
        logger.error("Failed to fetch signals for org %s: %s", org_id, e)
        raise HTTPException(500, "Failed to retrieve signals.")


@router.get("/{org_id}/{signal_id}")
async def get_signal(org_id: str, signal_id: str) -> Dict[str, Any]:
    """Get a specific signal by ID."""
    try:
        signal = ddb_service.get_signal(org_id, signal_id)
        if not signal:
            raise HTTPException(404, f"Signal {signal_id} not found")
        return signal
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch signal %s for org %s: %s", signal_id, org_id, e)
        raise HTTPException(500, "Failed to retrieve signal.")
