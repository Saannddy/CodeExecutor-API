from flask import request, jsonify
from services import RiddleService

class RiddleHandler:
    def __init__(self):
        self.riddle_service = RiddleService()

    def get_riddles(self):
        """List all riddles with pagination."""
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        
        pagination_data = self.riddle_service.list_all_riddles(page=page, page_size=page_size)
        return jsonify(status="success", data=pagination_data), 200

    def get_riddles_group(self):
        """Get a random group of riddles (1 per index) and their solution."""
        amount = request.args.get('amount', 5, type=int)
        res = self.riddle_service.get_random_riddles_group(amount)
        if res['status'] == "error":
            return jsonify(res), 400
        return jsonify(res), 200

    def get_riddle(self, riddle_id):
        """Retrieve single riddle details."""
        riddle = self.riddle_service.get_riddle_details(riddle_id)
        if not riddle:
            return jsonify(status="error", message="Riddle not found"), 404
        return jsonify(status="success", data=riddle), 200

    def create_riddle(self):
        """Add a new riddle."""
        try:
            data = request.get_json()
            required = ['riddle_text', 'refer_char', 'refer_index']
            if not all(k in data for k in required):
                return jsonify(status="error", message=f"Missing required fields: {required}"), 400
            
            new_riddle = self.riddle_service.add_riddle(data)
            return jsonify(status="success", data=new_riddle), 201
        except Exception as e:
            return jsonify(status="error", message=str(e)), 500

    def update_riddle(self, riddle_id):
        """Update an existing riddle."""
        try:
            data = request.get_json()
            updated_riddle = self.riddle_service.update_riddle(riddle_id, data)
            if not updated_riddle:
                return jsonify(status="error", message="Riddle not found"), 404
            return jsonify(status="success", data=updated_riddle), 200
        except Exception as e:
            return jsonify(status="error", message=str(e)), 500
