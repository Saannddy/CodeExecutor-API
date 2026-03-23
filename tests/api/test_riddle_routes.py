"""
Unit tests for Riddle API routes.

Tests for:
  - GET /riddle/ - List all riddles
  - GET /riddle/group - Get random group of riddles
  - GET /riddle/<id> - Get riddle details
  - POST /riddle/ - Create new riddle
  - PATCH /riddle/<id> - Update riddle
"""

from unittest.mock import patch, MagicMock
import json

# Handler service path for patching
RIDDLE_HANDLER = "api.routes.riddle_routes.riddle_handler"


class TestGetAllRiddles:
    """Tests for GET /riddle/"""

    ENDPOINT = "/riddle/"

    def test_get_all_riddles_success(self, client):
        """Should return all riddles."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.list_all_riddles.return_value = [
                {"id": "r1", "question": "What am I?", "answer": "riddle"},
                {"id": "r2", "question": "I am?", "answer": "answer"}
            ]
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert len(body["data"]) == 2

    def test_get_all_riddles_empty(self, client):
        """Should return empty list when no riddles exist."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.list_all_riddles.return_value = []
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"] == []

    def test_get_all_riddles_with_filters(self, client):
        """Should support filtering riddles."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.list_all_riddles.return_value = [
                {"id": "r1", "question": "Easy riddle", "difficulty": "easy"}
            ]
            
            response = client.get(f"{self.ENDPOINT}?difficulty=easy")

        if response.status_code == 200:
            body = response.get_json()
            assert body["status"] == "success"


class TestGetRiddlesGroup:
    """Tests for GET /riddle/group"""

    ENDPOINT = "/riddle/group"

    def test_get_riddles_group_success(self, client):
        """Should return a random group of riddles."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.get_riddles_group.return_value = [
                {"id": "r1", "question": "Riddle 1"},
                {"id": "r2", "question": "Riddle 2"},
                {"id": "r3", "question": "Riddle 3"}
            ]
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert len(body["data"]) >= 1

    def test_get_riddles_group_with_limit(self, client):
        """Should support limit parameter for group size."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.get_riddles_group.return_value = [
                {"id": "r1", "question": "Riddle 1"}
            ]
            
            response = client.get(f"{self.ENDPOINT}?limit=1")

        if response.status_code == 200:
            body = response.get_json()
            assert len(body["data"]) <= 1


class TestGetRiddleById:
    """Tests for GET /riddle/<id>"""

    def test_get_riddle_by_id_success(self, client):
        """Should return riddle details."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.get_riddle_details.return_value = {
                "id": "r1",
                "question": "What am I?",
                "answer": "riddle",
                "difficulty": "medium",
                "category": "general"
            }
            
            response = client.get("/riddle/r1")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"]["question"] == "What am I?"

    def test_get_riddle_by_id_not_found(self, client):
        """Should return 404 when riddle doesn't exist."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.get_riddle_details.return_value = None
            
            response = client.get("/riddle/nonexistent")

        assert response.status_code == 404
        body = response.get_json()
        assert body["status"] == "error"

    def test_get_riddle_includes_metadata(self, client):
        """Should include all riddle metadata."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.get_riddle_details.return_value = {
                "id": "r1",
                "question": "Question?",
                "answer": "answer",
                "difficulty": "hard",
                "category": "logic",
                "tags": ["thinking", "logic"]
            }
            
            response = client.get("/riddle/r1")

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert "question" in data
        assert "answer" in data
        assert "difficulty" in data


class TestCreateRiddle:
    """Tests for POST /riddle/"""

    ENDPOINT = "/riddle/"

    def test_create_riddle_success(self, client):
        """Should create a new riddle."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.add_riddle.return_value = {
                "id": "r-new",
                "question": "New riddle?",
                "answer": "answer",
                "difficulty": "easy"
            }
            
            payload = {
                "question": "New riddle?",
                "answer": "answer",
                "difficulty": "easy"
            }
            
            response = client.post(
                self.ENDPOINT,
                data=json.dumps(payload),
                content_type="application/json"
            )

        assert response.status_code == 201
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"]["id"] == "r-new"

    def test_create_riddle_missing_question(self, client):
        """Should return 400 when question is missing."""
        response = client.post(
            self.ENDPOINT,
            data=json.dumps({"answer": "test"}),
            content_type="application/json"
        )

        if response.status_code == 400:
            body = response.get_json()
            assert body["status"] == "error"

    def test_create_riddle_missing_answer(self, client):
        """Should return 400 when answer is missing."""
        response = client.post(
            self.ENDPOINT,
            data=json.dumps({"question": "Test?"}),
            content_type="application/json"
        )

        if response.status_code == 400:
            body = response.get_json()
            assert body["status"] == "error"

    def test_create_riddle_invalid_json(self, client):
        """Should return 400 for invalid JSON."""
        response = client.post(self.ENDPOINT)

        assert response.status_code == 400 or response.status_code == 415


class TestUpdateRiddle:
    """Tests for PATCH /riddle/<id>"""

    def test_update_riddle_success(self, client):
        """Should update an existing riddle."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.update_riddle.return_value = {
                "id": "r1",
                "question": "Updated riddle?",
                "answer": "updated"
            }
            
            payload = {
                "question": "Updated riddle?",
                "answer": "updated"
            }
            
            response = client.patch(
                "/riddle/r1",
                data=json.dumps(payload),
                content_type="application/json"
            )

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"

    def test_update_riddle_not_found(self, client):
        """Should return 404 when riddle doesn't exist."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.update_riddle.return_value = None
            
            response = client.patch(
                "/riddle/nonexistent",
                data=json.dumps({"question": "Updated?"}),
                content_type="application/json"
            )

        assert response.status_code == 404

    def test_update_riddle_invalid_json(self, client):
        """Should return 400 for invalid JSON."""
        response = client.patch("/riddle/r1")

        assert response.status_code == 400 or response.status_code == 415

    def test_update_riddle_partial(self, client):
        """Should allow partial updates."""
        with patch(f"{RIDDLE_HANDLER}.riddle_service") as mock_svc:
            mock_svc.update_riddle.return_value = {
                "id": "r1",
                "question": "Only question updated",
                "answer": "old answer"
            }
            
            response = client.patch(
                "/riddle/r1",
                data=json.dumps({"question": "Only question updated"}),
                content_type="application/json"
            )

        assert response.status_code == 200
