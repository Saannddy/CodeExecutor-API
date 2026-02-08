from flask import Flask, request, jsonify
from executor import execute_code, execute_custom_code
from db import init_db

app = Flask(__name__, static_folder='html')

init_db()

@app.post('/run')
def custom_code_executor():
    """Endpoint to run the specific code with given lang"""
    lang = request.args.get('lang')
    if not lang:
        return jsonify(status="error", message="Missing 'lang' query parameter"), 400

    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400

    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify(status="error", message="Missing 'code' in request body"), 400

    res = execute_custom_code(code, lang)
    return jsonify(res), (500 if res.get("status") == "error" else 200)

@app.get('/problems')
def get_problems():
    """Endpoint to list all problems."""
    from db import list_problems
    problems = list_problems()
    return jsonify(status="success", data=problems), 200

@app.get('/problem/<problem_id>')
def get_problem(problem_id):
    """Endpoint to fetch problem details by ID."""
    from db import get_problem_details, get_public_test_cases
    problem = get_problem_details(problem_id)
    if not problem:
        return jsonify(status="error", message="Problem not found"), 404
    
    # Construct an ordered result for better readability
    response_data = {
        "id": problem.get("id"),
        "title": problem.get("title"),
        "difficulty": problem.get("difficulty"),
        "description": problem.get("description"),
        "categories": problem.get("categories"),
        "tags": problem.get("tags"),
        "config": problem.get("config"),
        "test_cases": get_public_test_cases(problem_id)
    }
    
    return jsonify(status="success", data=response_data), 200

@app.post('/code/<question_id>')
def code_executor(question_id):
    """Endpoint to execute code for a given question ID."""
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400

    data = request.get_json()
    code, lang = data.get('code'), data.get('language')
    if not code or not lang:
        return jsonify(status="error", message="Missing 'code' or 'language'"), 400

    res = execute_code(code, lang, question_id)
    return jsonify(res), (500 if res.get("status") == "error" else 200)

@app.route('/')
def home():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors by serving a custom page."""
    return app.send_static_file('404.html'), 404
