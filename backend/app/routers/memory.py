from fastapi import APIRouter
from typing import Dict, Any, List
from app.agents.memory_agent import MemoryAgent
from pydantic import BaseModel

router = APIRouter(prefix="/api/memory", tags=["memory"])
memory_agent = MemoryAgent()


class SearchQuery(BaseModel):
    query: str
    org_id: str
    limit: int = 10


@router.post("/search")
async def search_memory(query: SearchQuery) -> Dict[str, Any]:
    """Semantic search using embeddings"""
    
    # TODO: Retrieve stored embeddings and search
    stored_embeddings = []
    results = memory_agent.search_similar(query.query, stored_embeddings, query.limit)
    
    return {
        "query": query.query,
        "results": results
    }


@router.post("/store")
async def store_memory(
    org_id: str,
    content: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Store content with embeddings"""
    
    result = memory_agent.store_with_embedding(content, metadata)
    
    # TODO: Store in DynamoDB
    
    return {
        "status": "stored",
        "org_id": org_id
    }
