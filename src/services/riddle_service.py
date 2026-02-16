from repositories.riddle_repository import RiddleRepository
from models import Riddle
from uuid import UUID
import math

class RiddleService:
    def __init__(self):
        self.riddle_repo = RiddleRepository()

    def _to_uuid(self, id_val):
        """Helper to convert str to UUID if necessary."""
        if isinstance(id_val, UUID):
            return id_val
        try:
            return UUID(str(id_val))
        except (ValueError, AttributeError):
            return None

    def list_all_riddles(self, page: int = 1, page_size: int = 10):
        """List riddles with pagination and metadata."""
        offset = (page - 1) * page_size
        riddles, total_count = self.riddle_repo.find_all(offset=offset, limit=page_size)
        
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
        
        items = [
            {
                "id": str(r.id),
                "riddle_text": r.riddle_text,
                "refer_char": r.refer_char,
                "refer_index": r.refer_index,
                "difficulty": r.difficulty,
                "tags": [t.name for t in r.tags]
            } for r in riddles
        ]
        
        return {
            "items": items,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size
        }

    def get_riddle_details(self, riddle_id: str):
        """Fetch riddle details."""
        r_uuid = self._to_uuid(riddle_id)
        if not r_uuid:
            return None
        
        riddle = self.riddle_repo.find_by_id(r_uuid)
        if not riddle:
            return None
            
        result = riddle.model_dump()
        result['tags'] = [t.name for t in riddle.tags]
        return result

    def add_riddle(self, riddle_data: dict):
        """Create a new riddle."""
        riddle = Riddle(
            riddle_text=riddle_data['riddle_text'],
            refer_char=riddle_data['refer_char'],
            refer_index=riddle_data['refer_index'],
            difficulty=riddle_data.get('difficulty')
        )
        return self.riddle_repo.create(riddle).model_dump()

    def update_riddle(self, riddle_id: str, update_data: dict):
        """Update an existing riddle."""
        r_uuid = self._to_uuid(riddle_id)
        if not r_uuid:
            return None
            
        riddle = self.riddle_repo.find_by_id(r_uuid)
        if not riddle:
            return None
        
        if 'riddle_text' in update_data:
            riddle.riddle_text = update_data['riddle_text']
        if 'refer_char' in update_data:
            riddle.refer_char = update_data['refer_char']
        if 'refer_index' in update_data:
            riddle.refer_index = update_data['refer_index']
        if 'difficulty' in update_data:
            riddle.difficulty = update_data['difficulty']
            
        return self.riddle_repo.update(riddle).model_dump()

    def get_random_riddles_group(self, amount: int):
        """Pick N random riddles (1 per refer_index) and build solution string."""
        try:
            riddles = self.riddle_repo.find_random_per_index(amount)
            
            # Build solution string by joining refer_char in order of refer_index
            solution = "".join([r.refer_char for r in riddles])
            
            return {
                "status": "success",
                "data": {
                    "riddles": [
                        {
                            "id": str(r.id),
                            "riddle_text": r.riddle_text,
                            "refer_index": r.refer_index
                        } for r in riddles
                    ],
                    "solution": solution,
                    "amount": len(riddles)
                }
            }
        except ValueError as e:
            return {"status": "error", "message": str(e)}
