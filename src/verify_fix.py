
import sys
import os
from uuid import UUID

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.question_service import QuestionService
from repositories.question_repository import QuestionRepository
from models.base import Question, Tag, Choice
from infrastructure import SessionLocal

def verify():
    service = QuestionService()
    
    # Try to find a tag to test with
    with SessionLocal() as session:
        tag = session.query(Tag).first()
        if not tag:
            print("No tags found in database. Cannot run verification. Please seed the database first.")
            return
        tag_name = tag.name
        print(f"Testing with tag: {tag_name}")

    try:
        results = service.get_random_questions(tag_name, amount=1)
        print("Success! get_random_questions executed without DetachedInstanceError.")
        print(f"Results: {results}")
        
        # Verify structure
        if results:
            q = results[0]
            if 'choices' in q and isinstance(q['choices'], list):
                print(f"Verified: 'choices' is a list with {len(q['choices'])} items.")
            else:
                print("Error: 'choices' is missing or not a list in the response.")
                
            if 'tags' in q and isinstance(q['tags'], list):
                print(f"Verified: 'tags' is a list with {len(q['tags'])} items.")
                
            if 'categories' in q and isinstance(q['categories'], list):
                print(f"Verified: 'categories' is a list with {len(q['categories'])} items.")
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
