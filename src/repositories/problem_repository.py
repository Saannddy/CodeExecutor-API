from infrastructure.database import query_one, query_all

class ProblemRepository:
    @staticmethod
    def find_all():
        """Retrieve all problems with basic info."""
        return query_all("SELECT id, title, difficulty FROM problems ORDER BY created_at DESC")

    @staticmethod
    def find_by_id(problem_id):
        """Retrieve basic problem details by ID."""
        return query_one("SELECT id, title, description, difficulty, config FROM problems WHERE id = %s", (problem_id,))

    @staticmethod
    def get_categories(problem_id):
        """Retrieve category names for a problem."""
        rows = query_all("""
            SELECT c.name FROM categories c
            JOIN problem_categories pc ON c.id = pc.category_id
            WHERE pc.problem_id = %s
        """, (problem_id,))
        return [r['name'] for r in rows]

    @staticmethod
    def get_tags(problem_id):
        """Retrieve tag names for a problem."""
        rows = query_all("""
            SELECT t.name FROM tags t
            JOIN problem_tags pt ON t.id = pt.tag_id
            WHERE pt.problem_id = %s
        """, (problem_id,))
        return [r['name'] for r in rows]
    @staticmethod
    def find_by_category(category_name):
        """Retrieve problems filtered by category name."""
        return query_all("""
            SELECT p.id, p.title, p.difficulty FROM problems p
            JOIN problem_categories pc ON p.id = pc.problem_id
            JOIN categories c ON pc.category_id = c.id
            WHERE c.name ILIKE %s
            ORDER BY p.created_at DESC
        """, (category_name,))

    @staticmethod
    def find_by_tag(tag_name):
        """Retrieve problems filtered by tag name."""
        return query_all("""
            SELECT p.id, p.title, p.difficulty FROM problems p
            JOIN problem_tags pt ON p.id = pt.problem_id
            JOIN tags t ON pt.tag_id = t.id
            WHERE t.name ILIKE %s
            ORDER BY p.created_at DESC
        """, (tag_name,))
