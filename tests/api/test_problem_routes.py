"""
Unit tests for Problem API routes.

Tests for:
  - GET /problem/ - List all problems
  - GET /problem/<id> - Get problem details
  - GET /problem/random - Get random problem
  - POST /problem/<id>/testcases - Add test cases
  - POST /problem/<id>/testcases/import - Import test cases from ZIP
  - PATCH /problem/<id>/title - Update problem title
"""

from unittest.mock import patch, MagicMock
import json

# Handler service path for patching
PROBLEM_HANDLER = "api.routes.problem_routes.problem_handler"


class TestGetAllProblems:
    """Tests for GET /problem/"""

    ENDPOINT = "/problem/"

    def test_get_all_problems_success(self, client):
        """Should return all problems with status 200."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
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

    def test_get_all_problems_empty(self, client):
        """Should return empty list when no problems exist."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.list_all_problems.return_value = []
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"] == []

    def test_get_problems_with_category_filter(self, client):
        """Should filter problems by category query parameter."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.list_problems_by_category.return_value = [
                {"id": "3", "title": "Binary Search", "difficulty": "easy"},
            ]
            
            response = client.get(f"{self.ENDPOINT}?category=searching")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]) == 1
        mock_svc.list_problems_by_category.assert_called_once_with("searching")

    def test_get_problems_with_tag_filter(self, client):
        """Should filter problems by tag query parameter."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.list_problems_by_tag.return_value = [
                {"id": "4", "title": "Reverse String", "difficulty": "easy"},
            ]
            
            response = client.get(f"{self.ENDPOINT}?tag=string")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]) == 1
        mock_svc.list_problems_by_tag.assert_called_once_with("string")


class TestGetProblemById:
    """Tests for GET /problem/<id>"""

    def test_get_problem_by_id_success(self, client):
        """Should return problem details."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.get_problem_details.return_value = {
                "id": "abc-123",
                "title": "Two Sum",
                "description": "Find two numbers that add up to target",
                "difficulty": "easy",
                "test_cases": []
            }
            
            response = client.get("/problem/abc-123")

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["data"]["title"] == "Two Sum"
        mock_svc.get_problem_details.assert_called_once_with("abc-123")

    def test_get_problem_by_id_not_found(self, client):
        """Should return 404 when problem doesn't exist."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.get_problem_details.return_value = None
            
            response = client.get("/problem/nonexistent")

        assert response.status_code == 404
        body = response.get_json()
        assert body["status"] == "error"

    def test_get_problem_with_test_cases(self, client):
        """Should return problem with associated test cases."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.get_problem_details.return_value = {
                "id": "p1",
                "title": "Test Problem",
                "test_cases": [
                    {"input": "1", "expected_output": "2"},
                    {"input": "2", "expected_output": "4"},
                ]
            }
            
            response = client.get("/problem/p1")

        assert response.status_code == 200
        body = response.get_json()
        assert len(body["data"]["test_cases"]) == 2


class TestGetRandomProblem:
    """Tests for GET /problem/random"""

    ENDPOINT = "/problem/random"

    def test_get_random_problem_success(self, client):
        """Should return a random problem."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.get_random_problem.return_value = {
                "id": "random-1",
                "title": "Random Problem",
                "difficulty": "medium"
            }
            
            response = client.get(self.ENDPOINT)

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert "id" in body["data"]

    def test_get_random_problem_no_problems(self, client):
        """Should handle case when no problems exist."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.get_random_problem.return_value = None
            
            response = client.get(self.ENDPOINT)

        assert response.status_code in [404, 200]  # Depends on implementation


class TestAddTestCases:
    """Tests for POST /problem/<id>/testcases"""

    def test_add_test_cases_success(self, client):
        """Should add test cases to a problem."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.add_test_cases.return_value = {
                "status": "success",
                "message": "Test cases added",
                "count": 2
            }
            
            test_cases = [
                {"input": "1", "expected_output": "2"},
                {"input": "2", "expected_output": "4"},
            ]
            
            response = client.post(
                "/problem/p1/testcases",
                data=json.dumps({"test_cases": test_cases}),
                content_type="application/json"
            )

        assert response.status_code in [200, 201]
        body = response.get_json()
        assert body["status"] == "success"

    def test_add_test_cases_invalid_json(self, client):
        """Should return 400 for invalid JSON."""
        response = client.post("/problem/p1/testcases")

        assert response.status_code == 400

    def test_add_test_cases_empty(self, client):
        """Should handle empty test cases."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.add_test_cases.return_value = {
                "status": "success",
                "count": 0
            }
            
            response = client.post(
                "/problem/p1/testcases",
                data=json.dumps({"test_cases": []}),
                content_type="application/json"
            )

        assert response.status_code in [200, 201]


class TestImportTestCases:
    """Tests for POST /problem/<id>/testcases/import"""

    def test_import_test_cases_success(self, client):
        """Should import test cases from ZIP file."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.import_test_cases.return_value = {
                "status": "success",
                "imported": 5
            }
            
            response = client.post(
                "/problem/p1/testcases/import",
                data={"file": (b"fake zip content", "testcases.zip")},
                content_type="multipart/form-data"
            )

        assert response.status_code in [200, 201]

    def test_import_test_cases_no_file(self, client):
        """Should return error when file is missing."""
        response = client.post("/problem/p1/testcases/import")

        assert response.status_code in [400, 415]


class TestUpdateProblemTitle:
    """Tests for PATCH /problem/<id>/title"""

    def test_update_problem_title_success(self, client):
        """Should update problem title."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.update_problem_title.return_value = {
                "status": "success",
                "data": {"id": "p1", "title": "New Title"}
            }
            
            response = client.patch(
                "/problem/p1/title",
                data=json.dumps({"title": "New Title"}),
                content_type="application/json"
            )

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"

    def test_update_problem_title_missing_title(self, client):
        """Should return error when title is missing."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.update_problem_title.return_value = {
                "status": "error",
                "message": "Title is required"
            }
            
            response = client.patch(
                "/problem/p1/title",
                data=json.dumps({}),
                content_type="application/json"
            )

        assert response.status_code in [400, 400]

    def test_update_problem_title_not_found(self, client):
        """Should return 404 when problem doesn't exist."""
        with patch(f"{PROBLEM_HANDLER}.problem_service") as mock_svc:
            mock_svc.update_problem_title.return_value = None
            
            response = client.patch(
                "/problem/nonexistent/title",
                data=json.dumps({"title": "New Title"}),
                content_type="application/json"
            )

        assert response.status_code in [404, 404]
