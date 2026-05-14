"""
Unit tests for Chunk API routes.

Tests for:
  - GET /chunk/ - List all chunks
  - GET /chunk/random - Get random chunks
  - GET /chunk/<id> - Get chunk details
"""

from unittest.mock import patch, MagicMock
import json
from uuid import uuid4

# Handler service path for patching
CHUNK_HANDLER = "api.routes.chunk_routes.handler"


class TestGetAllChunks:
    """Tests for GET /chunk/"""

    ENDPOINT = "/chunk/"

    def test_get_all_chunks_success(self, client):
        """Should return paginated list of chunks."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_all_chunks.return_value = [
                {"id": str(uuid4()), "title": "Chunk 1", "language": "python"},
                {"id": str(uuid4()), "title": "Chunk 2", "language": "java"}
            ]
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert len(body["data"]) == 2

    def test_get_all_chunks_with_pagination(self, client):
        """Should support pagination parameters."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_all_chunks.return_value = [
                {"id": str(uuid4()), "title": "Chunk 1"}
            ]
            
            response = client.get(f"{self.ENDPOINT}?page=2&limit=5")

        assert response.status_code == 200
        mock_svc.get_all_chunks.assert_called_once_with(page=2, limit=5, lang=None)

    def test_get_all_chunks_with_language_filter(self, client):
        """Should filter chunks by language."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_all_chunks.return_value = [
                {"id": str(uuid4()), "title": "Python Chunk", "language": "python"}
            ]
            
            response = client.get(f"{self.ENDPOINT}?lang=python")

        assert response.status_code == 200
        mock_svc.get_all_chunks.assert_called_once_with(page=1, limit=10, lang="python")

    def test_get_all_chunks_empty(self, client):
        """Should return empty list when no chunks exist."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_all_chunks.return_value = []
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["data"] == []

    def test_get_all_chunks_default_pagination(self, client):
        """Should use default page and limit values."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_all_chunks.return_value = []
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        mock_svc.get_all_chunks.assert_called_once_with(page=1, limit=10, lang=None)


class TestGetRandomChunks:
    """Tests for GET /chunk/random"""

    ENDPOINT = "/chunk/random"

    def test_get_random_chunks_success(self, client):
        """Should return random chunks."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            chunk_id = str(uuid4())
            mock_svc.get_random_chunks.return_value = [
                {"id": chunk_id, "title": "Random Chunk", "language": "python"}
            ]
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert len(body["data"]) >= 1

    def test_get_random_chunks_with_limit(self, client):
        """Should support limit parameter."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_random_chunks.return_value = [
                {"id": str(uuid4()), "title": "Chunk 1"},
                {"id": str(uuid4()), "title": "Chunk 2"},
                {"id": str(uuid4()), "title": "Chunk 3"}
            ]
            
            response = client.get(f"{self.ENDPOINT}?limit=3")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]) == 3
        mock_svc.get_random_chunks.assert_called_once_with(limit=3, lang=None, tags=None)

    def test_get_random_chunks_with_language_filter(self, client):
        """Should filter random chunks by language."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_random_chunks.return_value = [
                {"id": str(uuid4()), "title": "Java Chunk", "language": "java"}
            ]
            
            response = client.get(f"{self.ENDPOINT}?lang=java&limit=1")

        assert response.status_code == 200
        mock_svc.get_random_chunks.assert_called_once_with(limit=1, lang="java", tags=None)

    def test_get_random_chunks_with_tags(self, client):
        """Should filter random chunks by tags."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_random_chunks.return_value = [
                {"id": str(uuid4()), "title": "Loop Chunk", "tags": ["loops", "iteration"]}
            ]
            
            response = client.get(f"{self.ENDPOINT}?tags=loops,iteration")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        # Verify tags were parsed and passed correctly
        call_args = mock_svc.get_random_chunks.call_args
        assert call_args[1]["tags"] == ["loops", "iteration"]

    def test_get_random_chunks_multiple_tags_comma_separated(self, client):
        """Should parse comma-separated tags correctly."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_random_chunks.return_value = []
            
            response = client.get(f"{self.ENDPOINT}?tags=string,array,sorting")

        assert response.status_code == 200
        call_args = mock_svc.get_random_chunks.call_args
        assert call_args[1]["tags"] == ["string", "array", "sorting"]

    def test_get_random_chunks_default_limit(self, client):
        """Should use default limit value."""
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_random_chunks.return_value = []
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        mock_svc.get_random_chunks.assert_called_once_with(limit=1, lang=None, tags=None)


class TestGetChunkById:
    """Tests for GET /chunk/<id>"""

    def test_get_chunk_by_id_success(self, client):
        """Should return chunk details."""
        chunk_id = str(uuid4())
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_chunk.return_value = {
                "id": chunk_id,
                "title": "Sample Chunk",
                "description": "A sample chunk",
                "language": "python",
                "template": "def solution():\n    pass",
                "test_cases": []
            }
            
            response = client.get(f"/chunk/{chunk_id}")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"]["title"] == "Sample Chunk"

    def test_get_chunk_by_id_not_found(self, client):
        """Should return 404 when chunk doesn't exist."""
        chunk_id = str(uuid4())
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_chunk.return_value = None
            
            response = client.get(f"/chunk/{chunk_id}")

        assert response.status_code == 404
        body = response.get_json()
        assert body["status"] == "error"
        assert body["message"] == "Chunk not found"

    def test_get_chunk_with_language_filter(self, client):
        """Should filter chunk result by language."""
        chunk_id = str(uuid4())
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_chunk.return_value = {
                "id": chunk_id,
                "title": "Multi-language Chunk",
                "languages": {
                    "python": {"template": "# Python"},
                    "java": {"template": "// Java"}
                }
            }
            
            response = client.get(f"/chunk/{chunk_id}?lang=python")

        assert response.status_code == 200
        mock_svc.get_chunk.assert_called_once_with(chunk_id, lang="python")

    def test_get_chunk_includes_test_cases(self, client):
        """Should include test cases for the chunk."""
        chunk_id = str(uuid4())
        with patch(f"{CHUNK_HANDLER}.service") as mock_svc:
            mock_svc.get_chunk.return_value = {
                "id": chunk_id,
                "title": "Chunk with Tests",
                "test_cases": [
                    {"input": "test1", "expected": "output1"},
                    {"input": "test2", "expected": "output2"}
                ]
            }
            
            response = client.get(f"/chunk/{chunk_id}")

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert len(data["test_cases"]) == 2

    def test_get_chunk_invalid_uuid_format(self, client):
        """Should handle invalid UUID formats gracefully."""
        # Flask will handle UUID validation through the converter
        response = client.get("/chunk/not-a-uuid")

        # Should return 404 due to invalid UUID format
        assert response.status_code == 404
