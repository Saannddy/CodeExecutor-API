"""
Unit tests for the Problem endpoints.

Strategy:
  - Patch the ProblemService *instance* on the handler that is already
    created during blueprint registration.
  - Use the Flask test client to make real HTTP requests through the full
    Blueprint → Handler → (mocked) Service pipeline.
  - Assert status codes, JSON structure, and correct service delegation.
"""

from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Helper to get the handler's service instance via the blueprint module
# ---------------------------------------------------------------------------
HANDLER_SERVICE = "api.routes.problem_routes.problem_handler.problem_service"


# ── GET /problem/ ─────────────────────────────────────────────────────────────

class TestGetAllProblems:
    """Tests for GET /problem/ (list all problems)."""

    ENDPOINT = "/problem/"

    def test_returns_all_problems(self, client):
        """Should return 200 with a list of problems."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.list_all_problems.return_value = [
                {"id": "1", "title": "Two Sum", "difficulty": "easy"},
                {"id": "2", "title": "Add Two Numbers", "difficulty": "medium"},
            ]

            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert len(body["data"]) == 2
        assert body["data"][0]["title"] == "Two Sum"
        mock_svc.list_all_problems.assert_called_once()

    def test_returns_empty_list_when_no_problems(self, client):
        """Should return 200 with an empty list if the DB has no problems."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.list_all_problems.return_value = []

            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"] == []

    def test_filters_by_category(self, client):
        """Should delegate to list_problems_by_category when ?category= is given."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.list_problems_by_category.return_value = [
                {"id": "3", "title": "Binary Search", "difficulty": "easy"},
            ]

            response = client.get(f"{self.ENDPOINT}?category=searching")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]) == 1
        mock_svc.list_problems_by_category.assert_called_once_with("searching")

    def test_filters_by_tag(self, client):
        """Should delegate to list_problems_by_tag when ?tag= is given."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.list_problems_by_tag.return_value = [
                {"id": "4", "title": "Reverse String", "difficulty": "easy"},
            ]

            response = client.get(f"{self.ENDPOINT}?tag=string")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]) == 1
        mock_svc.list_problems_by_tag.assert_called_once_with("string")


# ── GET /problem/<id> ─────────────────────────────────────────────────────────

class TestGetProblemById:
    """Tests for GET /problem/<id>."""

    def test_returns_problem_details(self, client):
        """Should return 200 with full problem details."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.get_problem_details.return_value = {
                "id": "abc-123",
                "title": "Two Sum",
                "description": "Find two numbers...",
                "config": {"timeout": 5},
                "test_cases": [],
            }

            response = client.get("/problem/abc-123")

        assert response.status_code == 200
        body = response.get_json()
        assert body["data"]["title"] == "Two Sum"
        mock_svc.get_problem_details.assert_called_once_with("abc-123")

    def test_returns_404_when_not_found(self, client):
        """Should return 404 when problem does not exist."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.get_problem_details.return_value = None

            response = client.get("/problem/nonexistent-id")

        assert response.status_code == 404
        body = response.get_json()
        assert body["status"] == "error"


# ── GET /problem/random ───────────────────────────────────────────────────────

class TestGetRandomProblem:
    """Tests for GET /problem/random."""

    def test_returns_random_problem(self, client):
        """Should return 200 with a random problem."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.get_random_problem.return_value = [
                {"id": "rand-1", "title": "Random Problem", "difficulty": "hard"},
            ]

            response = client.get("/problem/random")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert len(body["data"]) == 1

    def test_returns_404_when_no_random_found(self, client):
        """Should return 404 when no problems match the filter."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.get_random_problem.return_value = []

            response = client.get("/problem/random")

        assert response.status_code == 404

    def test_accepts_limit_parameter(self, client):
        """Should pass the limit parameter to the service."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.get_random_problem.return_value = [
                {"id": "1", "title": "P1", "difficulty": "easy"},
                {"id": "2", "title": "P2", "difficulty": "medium"},
                {"id": "3", "title": "P3", "difficulty": "hard"},
            ]

            response = client.get("/problem/random?limit=3")

        assert response.status_code == 200
        mock_svc.get_random_problem.assert_called_once_with(category_name=None, limit=3)


# ── POST /problem/<id>/testcases ──────────────────────────────────────────────

class TestAddTestCases:
    """Tests for POST /problem/<id>/testcases."""

    def test_adds_testcases_successfully(self, client):
        """Should return 201 when test cases are created."""
        with patch(HANDLER_SERVICE) as mock_svc:
            mock_svc.add_test_cases.return_value = {
                "status": "success",
                "data": {"created_count": 1, "testcases": [{"id": "tc-1"}]},
            }

            response = client.post(
                "/problem/abc-123/testcases",
                json={"testcases": [{"input": "1 2", "output": "3"}]},
            )

        assert response.status_code == 201
        body = response.get_json()
        assert body["data"]["created_count"] == 1

    def test_rejects_non_json_request(self, client):
        """Should return 400 when Content-Type is not JSON."""
        response = client.post(
            "/problem/abc-123/testcases",
            data="not json",
            content_type="text/plain",
        )

        assert response.status_code == 400

    def test_rejects_invalid_testcases_field(self, client):
        """Should return 400 when testcases is not a list."""
        response = client.post(
            "/problem/abc-123/testcases",
            json={"testcases": "not a list"},
        )

        assert response.status_code == 400
