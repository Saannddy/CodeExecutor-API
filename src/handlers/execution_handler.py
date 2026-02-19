from flask import request, jsonify
from services import ExecutionService
from core import execute_custom_code

class ExecutionHandler:
    def __init__(self):
        self.execution_service = ExecutionService()

    def execute_problem_code(self, problem_id):
        """Execute code against stored test cases for a problem."""
        lang = request.args.get('lang')
        if not lang or not request.is_json:
            return jsonify(status="error", message="Missing 'lang' or invalid body"), 400
        
        data = request.get_json()
        code = data.get('code')
        if not code:
            return jsonify(status="error", message="Missing 'code'"), 400

        res = self.execution_service.run_problem_code(problem_id, code, lang)
        return jsonify(res), (500 if res.get("status") == "error" else 200)

    def custom_code_executor(self):
        """Execute arbitrary code without test cases."""
        lang = request.args.get('lang')
        if not lang or not request.is_json:
            return jsonify(status="error", message="Missing lang or invalid body"), 400

        data = request.get_json()
        code = data.get('code')
        if not code:
            return jsonify(status="error", message="Missing code"), 400

        res = execute_custom_code(code, lang)
        return jsonify(res), (500 if res.get("status") == "error" else 200)
