"""
Unit tests for Execution API routes.

Tests for:
  - POST /code/<problem_id> - Execute problem code
  - POST /run - Custom code executor
  - POST /chunk/execute/<chunk_id> - Execute chunk code
"""

from unittest.mock import patch, MagicMock
import json

# Handler instance path for patching
EXECUTION_HANDLER = "api.routes.execution_routes.execution_handler"
EXECUTE_CUSTOM_CODE = "handlers.execution_handler.execute_custom_code"


class TestExecuteProblemCode:
    """Tests for POST /code/<problem_id>"""

    ENDPOINT = "/code/test-problem-123"

    def test_execute_problem_code_success(self, client):
        """Should execute code and return results."""
        with patch(f"{EXECUTION_HANDLER}.execution_service") as mock_svc:
            mock_svc.run_problem_code.return_value = {
                "status": "success",
                "passed": 3,
                "failed": 0,
                "results": [
                    {"input": "1,2,3", "expected": "6", "actual": "6", "passed": True}
                ]
            }
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({"code": "def sum_array(arr):\n    return sum(arr)"}),
                content_type="application/json"
            )

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["passed"] == 3
        assert body["failed"] == 0
        mock_svc.run_problem_code.assert_called_once_with(
            "test-problem-123",
            "def sum_array(arr):\n    return sum(arr)",
            "python"
        )

    def test_execute_problem_code_missing_lang(self, client):
        """Should return 400 if 'lang' parameter is missing."""
        response = client.post(
            self.ENDPOINT,
            data=json.dumps({"code": "print('hello')"}),
            content_type="application/json"
        )

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"
        assert "lang" in body["message"].lower()

    def test_execute_problem_code_invalid_json(self, client):
        """Should return 400 if body is not JSON."""
        response = client.post(f"{self.ENDPOINT}?lang=python")

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"

    def test_execute_problem_code_missing_code(self, client):
        """Should return 400 if 'code' field is missing."""
        response = client.post(
            f"{self.ENDPOINT}?lang=python",
            data=json.dumps({"description": "test"}),
            content_type="application/json"
        )

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"
        assert "code" in body["message"].lower()

    def test_execute_problem_code_execution_error(self, client):
        """Should return 500 if execution service returns an error."""
        with patch(f"{EXECUTION_HANDLER}.execution_service") as mock_svc:
            mock_svc.run_problem_code.return_value = {
                "status": "error",
                "message": "Problem not found"
            }
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({"code": "print('hello')"}),
                content_type="application/json"
            )

        assert response.status_code == 500
        body = response.get_json()
        assert body["status"] == "error"

    def test_execute_problem_code_with_different_languages(self, client):
        """Should accept different language parameters."""
        with patch(f"{EXECUTION_HANDLER}.execution_service") as mock_svc:
            mock_svc.run_problem_code.return_value = {"status": "success", "passed": 1, "failed": 0}
            
            for lang in ["python", "java", "javascript", "cpp"]:
                response = client.post(
                    f"{self.ENDPOINT}?lang={lang}",
                    data=json.dumps({"code": "int x = 5;"}),
                    content_type="application/json"
                )
                assert response.status_code == 200
                assert response.get_json()["status"] == "success"


class TestCustomCodeExecutor:
    """Tests for POST /run"""

    ENDPOINT = "/run"

    def test_custom_code_execution_success(self, client):
        """Should execute arbitrary code and return output."""
        with patch(EXECUTE_CUSTOM_CODE) as mock_exec:
            mock_exec.return_value = {
                "status": "success",
                "output": "Hello, World!"
            }
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({"code": "print('Hello, World!')"}),
                content_type="application/json"
            )

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        assert body["output"] == "Hello, World!"

    def test_custom_code_execution_missing_lang(self, client):
        """Should return 400 if 'lang' parameter is missing."""
        response = client.post(
            self.ENDPOINT,
            data=json.dumps({"code": "print('hello')"}),
            content_type="application/json"
        )

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"

    def test_custom_code_execution_invalid_json(self, client):
        """Should return 400 if body is not JSON."""
        response = client.post(f"{self.ENDPOINT}?lang=python")

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"

    def test_custom_code_execution_missing_code(self, client):
        """Should return 400 if 'code' field is missing."""
        response = client.post(
            f"{self.ENDPOINT}?lang=python",
            data=json.dumps({"description": "test"}),
            content_type="application/json"
        )

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"

    def test_custom_code_execution_with_syntax_error(self, client):
        """Should return 500 if code has syntax errors."""
        with patch(EXECUTE_CUSTOM_CODE) as mock_exec:
            mock_exec.return_value = {
                "status": "error",
                "message": "SyntaxError: invalid syntax"
            }
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({"code": "print('hello'"}),
                content_type="application/json"
            )

        assert response.status_code == 500

    def test_custom_code_execution_with_different_languages(self, client):
        """Should support multiple programming languages."""
        with patch(EXECUTE_CUSTOM_CODE) as mock_exec:
            mock_exec.return_value = {"status": "success", "output": "test"}
            
            for lang in ["python", "java", "javascript"]:
                response = client.post(
                    f"{self.ENDPOINT}?lang={lang}",
                    data=json.dumps({"code": "test code"}),
                    content_type="application/json"
                )
                assert response.status_code == 200


class TestExecuteChunkCode:
    """Tests for POST /chunk/execute/<chunk_id>"""

    ENDPOINT = "/chunk/execute/test-chunk-123"

    def test_execute_chunk_code_success(self, client):
        """Should execute chunk code and return results."""
        with patch(f"{EXECUTION_HANDLER}.execution_service") as mock_svc:
            mock_svc.run_chunk_code.return_value = {
                "status": "success",
                "passed": 2,
                "failed": 0,
                "results": []
            }
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({
                    "snippets": {
                        "solution": "def solve():\n    return 42"
                    }
                }),
                content_type="application/json"
            )

        assert response.status_code == 200
        body = response.get_json()
        assert body["status"] == "success"
        mock_svc.run_chunk_code.assert_called_once()

    def test_execute_chunk_code_missing_lang(self, client):
        """Should return 400 if 'lang' parameter is missing."""
        response = client.post(
            self.ENDPOINT,
            data=json.dumps({"snippets": {}}),
            content_type="application/json"
        )

        assert response.status_code == 400
        body = response.get_json()
        assert body["status"] == "error"

    def test_execute_chunk_code_invalid_json(self, client):
        """Should return 400 if body is not JSON."""
        response = client.post(f"{self.ENDPOINT}?lang=python")

        assert response.status_code == 400

    def test_execute_chunk_code_with_empty_snippets(self, client):
        """Should handle empty snippets gracefully."""
        with patch(f"{EXECUTION_HANDLER}.execution_service") as mock_svc:
            mock_svc.run_chunk_code.return_value = {"status": "success", "passed": 0, "failed": 0}
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({"snippets": {}}),
                content_type="application/json"
            )

        assert response.status_code == 200
        mock_svc.run_chunk_code.assert_called_once_with(
            "test-chunk-123",
            {},
            "python"
        )

    def test_execute_chunk_code_with_multiple_snippets(self, client):
        """Should handle multiple code snippets."""
        with patch(f"{EXECUTION_HANDLER}.execution_service") as mock_svc:
            mock_svc.run_chunk_code.return_value = {"status": "success", "passed": 1, "failed": 0}
            
            snippets = {
                "setup": "import math",
                "solution": "def calc(): return math.pi",
                "helper": "def helper(): pass"
            }
            
            response = client.post(
                f"{self.ENDPOINT}?lang=python",
                data=json.dumps({"snippets": snippets}),
                content_type="application/json"
            )

        assert response.status_code == 200
        mock_svc.run_chunk_code.assert_called_once_with(
            "test-chunk-123",
            snippets,
            "python"
        )
