"""
Memory / semantic search router — store and retrieve embeddings.

Uses Nova embeddings for semantic similarity search across business data.

Endpoints:
  POST /api/memory/search — semantic search across stored embeddings
  POST /api/memory/store  — store content with its embedding vector
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.agents.memory_agent import MemoryAgent
from app.middleware.org_isolation import validate_org_id_from_body

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memory", tags=["memory"])
memory_agent = MemoryAgent()


class SearchQuery(BaseModel):
    """Payload for semantic search."""
    query: str
    org_id: str
    limit: int = 10


class StoreRequest(BaseModel):
    """Payload for storing content with embeddings."""
    org_id: str
    content: str
    metadata: Dict[str, Any] = {}


@router.post("/search")
async def search_memory(query: SearchQuery, req: Request) -> Dict[str, Any]:
    """Semantic search using Nova embeddings."""
    validate_org_id_from_body(req, query.org_id)
    try:
        stored_embeddings: list = []
        results = memory_agent.search_similar(query.query, stored_embeddings, query.limit)
        return {"query": query.query, "results": results}
    except Exception as e:
        logger.error("Memory search failed for org %s: %s", query.org_id, e)
        raise HTTPException(500, "Semantic search failed.")


@router.post("/store")
async def store_memory(request: StoreRequest, req: Request) -> Dict[str, Any]:
    """Store content with its embedding vector."""
    validate_org_id_from_body(req, request.org_id)
    try:
        result = memory_agent.store_with_embedding(request.content, request.metadata)
        return {"status": "stored", "org_id": request.org_id}
    except Exception as e:
        logger.error("Memory store failed for org %s: %s", request.org_id, e)
        raise HTTPException(500, "Failed to store content.")
