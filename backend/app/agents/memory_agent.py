"""
Memory Agent - Manages embeddings-based contextual memory

Uses Nova Multimodal Embeddings for vector generation and
cosine similarity for semantic search.
"""

import logging
import math
from typing import List, Dict, Any
from app.utils.bedrock_client import get_bedrock_client

logger = logging.getLogger(__name__)


class MemoryAgent:
    """Agent for embeddings-based memory"""

    def __init__(self):
        self.bedrock = get_bedrock_client()

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Nova embeddings"""
        try:
            embedding = self.bedrock.generate_embeddings(text)
            if not embedding:
                logger.warning("Empty embedding returned")
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}", exc_info=True)
            return []

    def search_similar(
        self,
        query: str,
        stored_embeddings: List[Dict[str, Any]],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for similar content using cosine similarity"""
        if not stored_embeddings:
            return []

        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []

        results = []
        for item in stored_embeddings:
            vec = item.get("embedding", [])
            score = self._cosine_similarity(query_embedding, vec)
            results.append({
                **{k: v for k, v in item.items() if k != "embedding"},
                "similarity_score": score,
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:limit]

    def store_with_embedding(
        self, content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store content with its embedding"""
        embedding = self.generate_embedding(content)
        return {
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
        }

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        try:
            dot = sum(a * b for a, b in zip(vec1, vec2))
            mag1 = math.sqrt(sum(a * a for a in vec1))
            mag2 = math.sqrt(sum(b * b for b in vec2))
            if mag1 == 0 or mag2 == 0:
                return 0.0
            return dot / (mag1 * mag2)
        except Exception:
            return 0.0
