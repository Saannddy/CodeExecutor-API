from flask import request, jsonify
from services import QuestionService

class QuestionHandler:
    def __init__(self):
        self.question_service = QuestionService()

    def get_questions(self):
        """List all questions with pagination."""
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        pagination_data = self.question_service.list_all_questions(page=page, page_size=page_size)
        return jsonify(status="success", data=pagination_data), 200

    def get_question(self, question_id):
        """Retrieve question details with choices."""
        question = self.question_service.get_question_details(question_id)
        if not question:
            return jsonify(status="error", message="Question not found"), 404
        return jsonify(status="success", data=question), 200

    def add_question(self):
        """Create a new question."""
        if not request.is_json:
            return jsonify(status="error", message="Request must be JSON"), 400
        data = request.get_json()
        if not data.get('title') or not data.get('question_text'):
            return jsonify(status="error", message="Missing title or question_text"), 400
        
        question = self.question_service.add_question(data)
        return jsonify(status="success", data=question), 201

    def update_question(self, question_id):
        """Update an existing question."""
        if not request.is_json:
            return jsonify(status="error", message="Request must be JSON"), 400
        data = request.get_json()
        
        question = self.question_service.update_question(question_id, data)
        if not question:
            return jsonify(status="error", message="Question not found"), 404
        return jsonify(status="success", data=question), 200

    def add_choice(self, question_id):
        """Add a choice to a question (Limit: 4)."""
        if not request.is_json:
            return jsonify(status="error", message="Request must be JSON"), 400
        data = request.get_json()
        if not data.get('choice_text'):
            return jsonify(status="error", message="Missing choice_text"), 400
            
        res = self.question_service.add_choice(question_id, data)
        return jsonify(res), (400 if res.get("status") == "error" else 201)

    def update_choice(self, choice_id):
        """Update an existing choice."""
        if not request.is_json:
            return jsonify(status="error", message="Request must be JSON"), 400
        data = request.get_json()
        
        choice = self.question_service.update_choice(choice_id, data)
        if not choice:
            return jsonify(status="error", message="Choice not found"), 404
        return jsonify(status="success", data=choice), 200

    def get_random_questions(self):
        """Get random questions by tag."""
        tag = request.args.get('tag')
        amount = request.args.get('amount', 1, type=int)
        
        if not tag:
            return jsonify(status="error", message="Missing 'tag' parameter"), 400
            
        questions = self.question_service.get_random_questions(tag, amount)
        return jsonify(status="success", data=questions), 200
