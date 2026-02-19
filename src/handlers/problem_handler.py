from flask import request, jsonify
from services import ProblemService

class ProblemHandler:
    def __init__(self):
        self.problem_service = ProblemService()

    def get_problems(self):
        """List problems with optional category/tag filtering."""
        category = request.args.get('category')
        tag = request.args.get('tag')

        if category:
            problems = self.problem_service.list_problems_by_category(category)
        elif tag:
            problems = self.problem_service.list_problems_by_tag(tag)
        else:
            problems = self.problem_service.list_all_problems()

        return jsonify(status="success", data=problems), 200

    def get_problem(self, problem_id):
        """Retrieve detailed information for a single problem."""
        problem = self.problem_service.get_problem_details(problem_id)
        if not problem:
            return jsonify(status="error", message="Problem not found"), 404
        return jsonify(status="success", data=problem), 200

    def get_random_problem(self):
        """Fetch a random problem, optionally filtered by category or tag."""
        category = request.args.get('category')
        tag = request.args.get('tag')
        limit = request.args.get('limit', 1, type=int)

        # Prefer category filter, then tag, otherwise random across all
        if category:
            problem = self.problem_service.get_random_problem(category_name=category, limit=limit)
        elif tag:
            problem = self.problem_service.get_random_problem(tag_name=tag, limit=limit)
        else:
            problem = self.problem_service.get_random_problem(category_name=None, limit=limit)

        if not problem:
            return jsonify(status="error", message="No problems found"), 404
        return jsonify(status="success", data=problem), 200

    def add_test_cases(self, problem_id):
        """ Add multiple test case  """
        if not request.is_json:
            return jsonify(status='error', message='Request must be JSON'), 400
        
        data = request.get_json()
        testcases = data.get('testcases')

        if not testcases or not isinstance(testcases, list):
            return jsonify(status='error', message='Testcases must be a list'), 400
        
        result = self.problem_service.add_test_cases(problem_id, testcases)

        if result['status'] == 'error':
            return jsonify(status='error', message=result.get('message')), 400
        return jsonify(status='success', data=result.get('data')), 201
