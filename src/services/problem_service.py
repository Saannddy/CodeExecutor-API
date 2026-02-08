from repositories import ProblemRepository, TestCaseRepository

class ProblemService:
    def __init__(self):
        self.problem_repo = ProblemRepository()
        self.test_case_repo = TestCaseRepository()

    def list_all_problems(self):
        """Get summary list of problems."""
        return self.problem_repo.find_all()

    def get_problem_details(self, problem_id):
        """Get full problem details for the API response."""
        problem = self.problem_repo.find_by_id(problem_id)
        if not problem:
            return None

        # Filter config (Security/Business logic)
        allowed_keys = {'timeout', 'templates'}
        original_config = problem.get('config', {})
        problem['config'] = {k: v for k, v in original_config.items() if k in allowed_keys}

        # Enrich with categories, tags, and public test cases
        problem['categories'] = self.problem_repo.get_categories(problem_id)
        problem['tags'] = self.problem_repo.get_tags(problem_id)
        problem['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id)

        return problem
    def list_problems_by_category(self, category_name):
        """Get problems filtered by category."""
        return self.problem_repo.find_by_category(category_name)

    def list_problems_by_tag(self, tag_name):
        """Get problems filtered by tag."""
        return self.problem_repo.find_by_tag(tag_name)
