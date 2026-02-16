from repositories.question_repository import QuestionRepository
from repositories.choice_repository import ChoiceRepository
from models import Question, Choice
from uuid import UUID

class QuestionService:
    def __init__(self):
        self.question_repo = QuestionRepository()
        self.choice_repo = ChoiceRepository()

    def _to_uuid(self, id_val):
        """Helper to convert str to UUID if necessary."""
        if isinstance(id_val, UUID):
            return id_val
        try:
            return UUID(str(id_val))
        except (ValueError, AttributeError):
            return None

    def get_question_details(self, question_id: str):
        """Fetch question details with choices."""
        q_uuid = self._to_uuid(question_id)
        if not q_uuid:
            return None
        
        question = self.question_repo.find_by_id(q_uuid)
        if not question:
            return None
        
        # Format response
        result = question.model_dump()
        result['choices'] = [
            {
                "id": str(c.id),
                "choice_text": c.choice_text,
                "is_correct": c.is_correct
            } for c in question.choices
        ]
        result['tags'] = [t.name for t in question.tags]
        result['categories'] = [c.name for c in question.categories]
        return result

    def add_question(self, question_data: dict):
        """Create a new question."""
        question = Question(
            title=question_data['title'],
            question_text=question_data['question_text']
        )
        return self.question_repo.create(question).model_dump()

    def update_question(self, question_id: str, update_data: dict):
        """Update an existing question."""
        q_uuid = self._to_uuid(question_id)
        if not q_uuid:
            return None
            
        question = self.question_repo.find_by_id(q_uuid)
        if not question:
            return None
        
        if 'title' in update_data:
            question.title = update_data['title']
        if 'question_text' in update_data:
            question.question_text = update_data['question_text']
            
        return self.question_repo.update(question).model_dump()

    def add_choice(self, question_id: str, choice_data: dict):
        """Add a choice to a question with limit validation."""
        q_uuid = self._to_uuid(question_id)
        if not q_uuid:
            return {"status": "error", "message": "Invalid question ID"}
            
        question = self.question_repo.find_by_id(q_uuid)
        if not question:
            return {"status": "error", "message": "Question not found"}
            
        current_count = self.choice_repo.count_by_question_id(q_uuid)
        if current_count >= 4:
            return {"status": "error", "message": "Question already has the maximum of 4 choices"}
            
        choice = Choice(
            question_id=q_uuid,
            choice_text=choice_data['choice_text'],
            is_correct=choice_data.get('is_correct', False)
        )
        saved_choice = self.choice_repo.create(choice)
        return {"status": "success", "data": saved_choice.model_dump()}

    def update_choice(self, choice_id: str, update_data: dict):
        """Update an existing choice."""
        c_uuid = self._to_uuid(choice_id)
        if not c_uuid:
            return None
            
        choice = self.choice_repo.find_by_id(c_uuid)
        if not choice:
            return None
            
        if 'choice_text' in update_data:
            choice.choice_text = update_data['choice_text']
        if 'is_correct' in update_data:
            choice.is_correct = update_data['is_correct']
            
        return self.choice_repo.update(choice).model_dump()

    def get_random_questions(self, tag_name: str, amount: int = 1):
        """Fetch N random questions by tag."""
        questions = self.question_repo.find_random_by_tag(tag_name, amount)
        return [
            {
                "id": str(q.id),
                "title": q.title,
                "question_text": q.question_text,
                "tags": [t.name for t in q.tags]
            } for q in questions
        ]
    def list_all_questions(self, page: int = 1, page_size: int = 10):
        """List questions with pagination and metadata."""
        import math
        offset = (page - 1) * page_size
        questions, total_count = self.question_repo.find_all(offset=offset, limit=page_size)
        
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
        
        items = [
            {
                "id": str(q.id),
                "title": q.title,
                "question_text": q.question_text,
                "choice_count": len(q.choices)
            } for q in questions
        ]
        
        return {
            "items": items,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size
        }
