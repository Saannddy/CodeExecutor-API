from repositories import ProblemRepository, TestCaseRepository

class ProblemService:
    def __init__(self):
        self.problem_repo = ProblemRepository()
        self.test_case_repo = TestCaseRepository()

    def list_all_problems(self):
        """Retrieve a list of all problems with basic information."""
        return self.problem_repo.find_all()

    def get_problem_details(self, problem_id):
        """Fetch full problem details, including config and public test cases."""
        problem_dict = self.problem_repo.find_details_by_id(problem_id)
        if not problem_dict:
            return None

        # Filter configuration for API response
        allowed_keys = {'timeout', 'templates'}
        problem_dict['config'] = {k: v for k, v in problem_dict.get('config', {}).items() if k in allowed_keys}
        
        # Enrich with public test cases
        problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id)

        return problem_dict

    def list_problems_by_category(self, category_name):
        """Filter problems by category."""
        return self.problem_repo.find_by_category(category_name)

    def list_problems_by_tag(self, tag_name):
        """Filter problems by tag."""
        return self.problem_repo.find_by_tag(tag_name)
