from flask import Blueprint, request, jsonify, send_from_directory, current_app
from services import ProblemService, ExecutionService
from core import execute_custom_code

api_bp = Blueprint('api', __name__)
problem_service = ProblemService()
execution_service = ExecutionService()

@api_bp.route('/openapi.yaml')
def serve_openapi():
    return send_from_directory(current_app.root_path, 'openapi.yaml')

@api_bp.route('/docs')
def scalar_docs():
    return f"""
    <!doctype html>
    <html>
      <head>
        <title>CodeExecutor-API Documentation</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>body {{ margin: 0; }}</style>
      </head>
      <body>
        <script id="api-reference" data-url="/openapi.yaml"></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>
    """, 200

@api_bp.get('/problems')
def get_problems():
    category = request.args.get('category')
    tag = request.args.get('tag')

    if category:
        problems = problem_service.list_problems_by_category(category)
    elif tag:
        problems = problem_service.list_problems_by_tag(tag)
    else:
        problems = problem_service.list_all_problems()

    return jsonify(status="success", data=problems), 200

@api_bp.get('/problem/<problem_id>')
def get_problem(problem_id):
    problem = problem_service.get_problem_details(problem_id)
    if not problem:
        return jsonify(status="error", message="Problem not found"), 404
    return jsonify(status="success", data=problem), 200

@api_bp.post('/code/<problem_id>')
def execute_problem_code(problem_id):
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400
    
    data = request.get_json()
    code, lang = data.get('code'), data.get('language')
    if not code or not lang:
        return jsonify(status="error", message="Missing 'code' or 'language'"), 400

    res = execution_service.run_problem_code(problem_id, code, lang)
    return jsonify(res), (500 if res.get("status") == "error" else 200)

@api_bp.post('/run')
def custom_code_executor():
    lang = request.args.get('lang')
    if not lang or not request.is_json:
        return jsonify(status="error", message="Missing lang or invalid body"), 400

    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify(status="error", message="Missing code"), 400

    res = execute_custom_code(code, lang)
    return jsonify(res), (500 if res.get("status") == "error" else 200)
