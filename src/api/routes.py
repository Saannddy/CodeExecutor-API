from flask import Blueprint, request, jsonify, send_from_directory, current_app
from services import ProblemService, ExecutionService, QuestionService, RiddleService
from core import execute_custom_code

api_bp = Blueprint('api', __name__)
problem_service = ProblemService()
execution_service = ExecutionService()
question_service = QuestionService()
riddle_service = RiddleService()

@api_bp.route('/openapi.yaml')
def serve_openapi():
    """Serve the OpenAPI specification file."""
    return send_from_directory(current_app.root_path, 'openapi.yaml')

@api_bp.route('/docs')
def scalar_docs():
    """Serve interactive API documentation via Scalar."""
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
    """List problems with optional category/tag filtering."""
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
    """Retrieve detailed information for a single problem."""
    problem = problem_service.get_problem_details(problem_id)
    if not problem:
        return jsonify(status="error", message="Problem not found"), 404
    return jsonify(status="success", data=problem), 200

@api_bp.post('/code/<problem_id>')
def execute_problem_code(problem_id):
    """Execute code against stored test cases for a problem."""
    lang = request.args.get('lang')
    if not lang or not request.is_json:
        return jsonify(status="error", message="Missing 'lang' or invalid body"), 400
    
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify(status="error", message="Missing 'code'"), 400

    res = execution_service.run_problem_code(problem_id, code, lang)
    return jsonify(res), (500 if res.get("status") == "error" else 200)

@api_bp.post('/run')
def custom_code_executor():
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

# --- Question & Choice Management ---

@api_bp.get('/questions')
def get_questions():
    """List all questions with pagination."""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    pagination_data = question_service.list_all_questions(page=page, page_size=page_size)
    return jsonify(status="success", data=pagination_data), 200

@api_bp.get('/question/<question_id>')
def get_question(question_id):
    """Retrieve question details with choices."""
    question = question_service.get_question_details(question_id)
    if not question:
        return jsonify(status="error", message="Question not found"), 404
    return jsonify(status="success", data=question), 200

@api_bp.post('/question')
def add_question():
    """Create a new question."""
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400
    data = request.get_json()
    if not data.get('title') or not data.get('question_text'):
        return jsonify(status="error", message="Missing title or question_text"), 400
    
    question = question_service.add_question(data)
    return jsonify(status="success", data=question), 201

@api_bp.patch('/question/<question_id>')
def update_question(question_id):
    """Update an existing question."""
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400
    data = request.get_json()
    
    question = question_service.update_question(question_id, data)
    if not question:
        return jsonify(status="error", message="Question not found"), 404
    return jsonify(status="success", data=question), 200

@api_bp.post('/question/<question_id>/choice')
def add_choice(question_id):
    """Add a choice to a question (Limit: 4)."""
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400
    data = request.get_json()
    if not data.get('choice_text'):
        return jsonify(status="error", message="Missing choice_text"), 400
        
    res = question_service.add_choice(question_id, data)
    return jsonify(res), (400 if res.get("status") == "error" else 201)

@api_bp.patch('/choice/<choice_id>')
def update_choice(choice_id):
    """Update an existing choice."""
    if not request.is_json:
        return jsonify(status="error", message="Request must be JSON"), 400
    data = request.get_json()
    
    choice = question_service.update_choice(choice_id, data)
    if not choice:
        return jsonify(status="error", message="Choice not found"), 404
    return jsonify(status="success", data=choice), 200

@api_bp.get('/questions/random')
def get_random_questions():
    """Get random questions by tag."""
    tag = request.args.get('tag')
    amount = request.args.get('amount', 1, type=int)
    
    if not tag:
        return jsonify(status="error", message="Missing 'tag' parameter"), 400
        
    questions = question_service.get_random_questions(tag, amount)
    return jsonify(status="success", data=questions), 200

# --- Riddle Management ---

@api_bp.get('/riddles')
def get_riddles():
    """List all riddles with pagination."""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    
    pagination_data = riddle_service.list_all_riddles(page=page, page_size=page_size)
    return jsonify(status="success", data=pagination_data), 200

@api_bp.get('/riddles/group')
def get_riddles_group():
    """Get a random group of riddles (1 per index) and their solution."""
    amount = request.args.get('amount', 5, type=int)
    res = riddle_service.get_random_riddles_group(amount)
    if res['status'] == "error":
        return jsonify(res), 400
    return jsonify(res), 200

@api_bp.get('/riddle/<riddle_id>')
def get_riddle(riddle_id):
    """Retrieve single riddle details."""
    riddle = riddle_service.get_riddle_details(riddle_id)
    if not riddle:
        return jsonify(status="error", message="Riddle not found"), 404
    return jsonify(status="success", data=riddle), 200

@api_bp.post('/riddle')
def create_riddle():
    """Add a new riddle."""
    try:
        data = request.get_json()
        required = ['riddle_text', 'refer_char', 'refer_index']
        if not all(k in data for k in required):
            return jsonify(status="error", message=f"Missing required fields: {required}"), 400
        
        new_riddle = riddle_service.add_riddle(data)
        return jsonify(status="success", data=new_riddle), 201
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

@api_bp.patch('/riddle/<riddle_id>')
def update_riddle(riddle_id):
    """Update an existing riddle."""
    try:
        data = request.get_json()
        updated_riddle = riddle_service.update_riddle(riddle_id, data)
        if not updated_riddle:
            return jsonify(status="error", message="Riddle not found"), 404
        return jsonify(status="success", data=updated_riddle), 200
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500
