"""
Context Memory Service

This service provides semantic memory capabilities using Nova embeddings.
It generates embeddings for operational signals and enables semantic search.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json

from app.utils.bedrock_client import get_bedrock_client
from app.services.ddb_service import get_ddb_service
from app.config import get_settings

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing contextual memory with embeddings"""
    
    def __init__(self):
        self.bedrock = get_bedrock_client()
        self.ddb = get_ddb_service()
        self.embeddings_table = get_settings().embeddings_table
    
    async def generate_embedding(
        self,
        signal_id: str,
        org_id: str,
        signal_type: str,
        content: str
    ) -> Optional[str]:
        """
        Generate embedding for a signal
        
        Implements Requirement 3.1: Generate embedding vector using Nova embeddings
        
        Args:
            signal_id: Unique signal identifier
            org_id: Organization identifier
            signal_type: Type of signal (invoice, email)
            content: Text content to embed
            
        Returns:
            Embedding reference ID or None if generation fails
        """
        try:
            # Generate embedding using Nova embeddings model
            embedding_vector = self.bedrock.generate_embeddings(content)
            
            if not embedding_vector:
                logger.error(f"Failed to generate embedding for signal {signal_id}")
                return None
            
            # Store embedding metadata in DynamoDB
            embedding_id = f"emb_{signal_id}"
            embedding_record = {
                "embedding_id": embedding_id,
                "org_id": org_id,
                "signal_id": signal_id,
                "signal_type": signal_type,
                "embedding_vector": embedding_vector,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "content_preview": content[:200]  # Store preview for debugging
            }
            
            self.ddb.put_item(self.embeddings_table, embedding_record)
            
            logger.info(
                f"Generated embedding for signal {signal_id} "
                f"(org_id: {org_id}, type: {signal_type})"
            )
            
            return embedding_id
            
        except Exception as e:
            # Requirement 3.4: Log error and continue processing
            logger.error(
                f"Error generating embedding for signal {signal_id}: {e}",
                exc_info=True
            )
            return None
    
    async def search_signals(
        self,
        org_id: str,
        query: str,
        limit: int = 10,
        signal_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across signals
        
        Implements Requirement 3.3: Query embeddings by org_id for semantic similarity
        
        Args:
            org_id: Organization identifier
            query: Search query text
            limit: Maximum number of results
            signal_type: Optional filter by signal type
            
        Returns:
            List of matching signals ranked by similarity
        """
        try:
            # Generate embedding for query
            query_embedding = self.bedrock.generate_embeddings(query)
            
            if not query_embedding:
                logger.error("Failed to generate query embedding")
                return []
            
            # Query embeddings filtered by org_id
            filter_expression = "org_id = :org_id"
            expression_values = {":org_id": org_id}
            
            if signal_type:
                filter_expression += " AND signal_type = :signal_type"
                expression_values[":signal_type"] = signal_type
            
            # Get all embeddings for this org
            embeddings = self.ddb.query_items(
                self.embeddings_table,
                key_condition="org_id = :org_id",
                expression_values=expression_values
            )
            
            # Calculate similarity scores
            results = []
            for emb in embeddings:
                similarity = self._cosine_similarity(
                    query_embedding,
                    emb.get("embedding_vector", [])
                )
                
                results.append({
                    "signal_id": emb["signal_id"],
                    "signal_type": emb["signal_type"],
                    "similarity_score": similarity,
                    "content_preview": emb.get("content_preview", ""),
                    "created_at": emb["created_at"]
                })
            
            # Sort by similarity and limit results
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            results = results[:limit]
            
            logger.info(
                f"Semantic search for org {org_id} returned {len(results)} results"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search for org {org_id}: {e}", exc_info=True)
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between 0 and 1
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        try:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    async def get_embedding(self, embedding_id: str, org_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve embedding by ID
        
        Args:
            embedding_id: Embedding identifier
            org_id: Organization identifier (for access control)
            
        Returns:
            Embedding record or None
        """
        try:
            embedding = self.ddb.get_item(
                self.embeddings_table,
                {"embedding_id": embedding_id}
            )
            
            # Verify org_id matches (data isolation)
            if embedding and embedding.get("org_id") == org_id:
                return embedding
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving embedding {embedding_id}: {e}")
            return None


import threading

# Singleton instance
_memory_service: Optional[MemoryService] = None
_ms_lock = threading.Lock()


def get_memory_service() -> MemoryService:
    """Get singleton memory service instance (thread-safe)"""
    global _memory_service
    if _memory_service is None:
        with _ms_lock:
            if _memory_service is None:
                _memory_service = MemoryService()
    return _memory_service
