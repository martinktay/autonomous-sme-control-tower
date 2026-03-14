"""
Unit tests for Memory Agent

Tests Requirements 3.1-3.4 (Embedding generation and semantic search)
"""

import pytest
from unittest.mock import Mock, patch
from app.agents.memory_agent import MemoryAgent


class TestEmbeddingGeneration:
    """Test suite for embedding generation"""

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_generate_embedding_returns_vector(self, mock_bedrock):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = [0.1, 0.2, 0.3, 0.4]
        mock_bedrock.return_value = mock_client

        agent = MemoryAgent()
        result = agent.generate_embedding("test text")

        assert result == [0.1, 0.2, 0.3, 0.4]
        mock_client.generate_embeddings.assert_called_once_with("test text")

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_generate_embedding_returns_empty_on_failure(self, mock_bedrock):
        mock_client = Mock()
        mock_client.generate_embeddings.side_effect = Exception("API error")
        mock_bedrock.return_value = mock_client

        agent = MemoryAgent()
        result = agent.generate_embedding("test")

        assert result == []

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_generate_embedding_handles_empty_response(self, mock_bedrock):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = []
        mock_bedrock.return_value = mock_client

        agent = MemoryAgent()
        result = agent.generate_embedding("test")

        assert result == []


class TestSemanticSearch:
    """Test suite for semantic search"""

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_search_similar_returns_ranked_results(self, mock_bedrock):
        mock_client = Mock()
        # Query embedding
        mock_client.generate_embeddings.return_value = [1.0, 0.0, 0.0]
        mock_bedrock.return_value = mock_client

        stored = [
            {"id": "a", "embedding": [1.0, 0.0, 0.0]},  # Perfect match
            {"id": "b", "embedding": [0.0, 1.0, 0.0]},  # Orthogonal
            {"id": "c", "embedding": [0.7, 0.7, 0.0]},  # Partial match
        ]

        agent = MemoryAgent()
        results = agent.search_similar("test query", stored, limit=3)

        assert len(results) == 3
        assert results[0]["id"] == "a"
        assert results[0]["similarity_score"] == pytest.approx(1.0, abs=0.01)
        assert results[1]["id"] == "c"
        assert results[2]["id"] == "b"

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_search_similar_respects_limit(self, mock_bedrock):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = [1.0, 0.0]
        mock_bedrock.return_value = mock_client

        stored = [
            {"id": str(i), "embedding": [1.0, 0.0]} for i in range(20)
        ]

        agent = MemoryAgent()
        results = agent.search_similar("test", stored, limit=5)

        assert len(results) == 5

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_search_similar_empty_stored(self, mock_bedrock):
        mock_client = Mock()
        mock_bedrock.return_value = mock_client

        agent = MemoryAgent()
        results = agent.search_similar("test", [], limit=10)

        assert results == []

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_search_similar_excludes_embedding_from_results(self, mock_bedrock):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = [1.0]
        mock_bedrock.return_value = mock_client

        stored = [{"id": "a", "content": "hello", "embedding": [1.0]}]

        agent = MemoryAgent()
        results = agent.search_similar("test", stored, limit=1)

        assert "embedding" not in results[0]
        assert results[0]["content"] == "hello"


class TestStoreWithEmbedding:
    """Test suite for store_with_embedding"""

    @patch("app.agents.memory_agent.get_bedrock_client")
    def test_store_returns_content_and_embedding(self, mock_bedrock):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = [0.5, 0.5]
        mock_bedrock.return_value = mock_client

        agent = MemoryAgent()
        result = agent.store_with_embedding("hello world", {"org_id": "org1"})

        assert result["content"] == "hello world"
        assert result["embedding"] == [0.5, 0.5]
        assert result["metadata"]["org_id"] == "org1"


class TestCosineSimilarity:
    """Test cosine similarity edge cases"""

    def test_identical_vectors(self):
        assert MemoryAgent._cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert MemoryAgent._cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        assert MemoryAgent._cosine_similarity([1, 0], [-1, 0]) == pytest.approx(-1.0)

    def test_empty_vectors(self):
        assert MemoryAgent._cosine_similarity([], []) == 0.0

    def test_mismatched_lengths(self):
        assert MemoryAgent._cosine_similarity([1, 0], [1, 0, 0]) == 0.0

    def test_zero_vector(self):
        assert MemoryAgent._cosine_similarity([0, 0], [1, 0]) == 0.0
