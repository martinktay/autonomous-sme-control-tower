"""
Unit tests for Memory Service

Tests Requirements 3.1-3.4 (Embedding generation, semantic search, error handling)
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.memory_service import MemoryService


class TestCosineSimlarity:
    """Test cosine similarity calculation"""

    def _svc(self):
        with patch("app.services.memory_service.get_bedrock_client"), \
             patch("app.services.memory_service.get_ddb_service"):
            return MemoryService()

    def test_identical_vectors(self):
        svc = self._svc()
        assert svc._cosine_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        svc = self._svc()
        assert svc._cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)

    def test_empty_vectors(self):
        svc = self._svc()
        assert svc._cosine_similarity([], []) == 0.0

    def test_different_lengths(self):
        svc = self._svc()
        assert svc._cosine_similarity([1], [1, 2]) == 0.0

    def test_zero_magnitude(self):
        svc = self._svc()
        assert svc._cosine_similarity([0, 0], [1, 1]) == 0.0


class TestEmbeddingGeneration:
    """Test embedding generation"""

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_generate_embedding_success(self, mock_bedrock, mock_ddb):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = [0.1, 0.2, 0.3]
        mock_bedrock.return_value = mock_client

        mock_ddb_inst = Mock()
        mock_ddb_inst.put_item = Mock()
        mock_ddb.return_value = mock_ddb_inst

        svc = MemoryService()
        result = await svc.generate_embedding("sig_1", "org_1", "invoice", "test content")

        assert result == "emb_sig_1"

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_generate_embedding_failure_returns_none(self, mock_bedrock, mock_ddb):
        mock_client = Mock()
        mock_client.generate_embeddings.side_effect = Exception("API error")
        mock_bedrock.return_value = mock_client
        mock_ddb.return_value = Mock()

        svc = MemoryService()
        result = await svc.generate_embedding("sig_1", "org_1", "invoice", "test")

        assert result is None

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_generate_embedding_empty_vector_returns_none(self, mock_bedrock, mock_ddb):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = []
        mock_bedrock.return_value = mock_client
        mock_ddb.return_value = Mock()

        svc = MemoryService()
        result = await svc.generate_embedding("sig_1", "org_1", "invoice", "test")

        assert result is None


class TestSemanticSearch:
    """Test semantic search"""

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_search_returns_ranked_results(self, mock_bedrock, mock_ddb):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = [1.0, 0.0]
        mock_bedrock.return_value = mock_client

        mock_ddb_inst = Mock()
        mock_ddb_inst.query_items.return_value = [
            {"signal_id": "s1", "signal_type": "invoice", "embedding_vector": [1.0, 0.0], "created_at": "2025-01-01", "content_preview": "A"},
            {"signal_id": "s2", "signal_type": "email", "embedding_vector": [0.0, 1.0], "created_at": "2025-01-02", "content_preview": "B"},
        ]
        mock_ddb.return_value = mock_ddb_inst

        svc = MemoryService()
        results = await svc.search_signals("org_1", "test query", limit=10)

        assert len(results) == 2
        assert results[0]["signal_id"] == "s1"
        assert results[0]["similarity_score"] > results[1]["similarity_score"]

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_search_empty_on_failure(self, mock_bedrock, mock_ddb):
        mock_client = Mock()
        mock_client.generate_embeddings.return_value = []
        mock_bedrock.return_value = mock_client
        mock_ddb.return_value = Mock()

        svc = MemoryService()
        results = await svc.search_signals("org_1", "test")

        assert results == []


class TestGetEmbedding:
    """Test embedding retrieval with org isolation"""

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_get_embedding_matching_org(self, mock_bedrock, mock_ddb):
        mock_bedrock.return_value = Mock()
        mock_ddb_inst = Mock()
        mock_ddb_inst.get_item.return_value = {"embedding_id": "emb_1", "org_id": "org_1"}
        mock_ddb.return_value = mock_ddb_inst

        svc = MemoryService()
        result = await svc.get_embedding("emb_1", "org_1")

        assert result is not None
        assert result["org_id"] == "org_1"

    @pytest.mark.asyncio
    @patch("app.services.memory_service.get_ddb_service")
    @patch("app.services.memory_service.get_bedrock_client")
    async def test_get_embedding_wrong_org_returns_none(self, mock_bedrock, mock_ddb):
        mock_bedrock.return_value = Mock()
        mock_ddb_inst = Mock()
        mock_ddb_inst.get_item.return_value = {"embedding_id": "emb_1", "org_id": "org_other"}
        mock_ddb.return_value = mock_ddb_inst

        svc = MemoryService()
        result = await svc.get_embedding("emb_1", "org_attacker")

        assert result is None
