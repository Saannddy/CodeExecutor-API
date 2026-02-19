from repositories import ProblemRepository, TestCaseRepository

class RandomService:
    def __init__(self):
        self.problem_repo = ProblemRepository()
        self.test_case_repo = TestCaseRepository()

    def get_random_problem(self):
        """Fetch a random problem with its details and public test cases."""
        problem_dict = self.problem_repo.find_random()
        if not problem_dict:
            return None

        # Filter configuration for API response
        allowed_keys = {'timeout', 'templates'}
        problem_dict['config'] = {k: v for k, v in problem_dict.get('config', {}).items() if k in allowed_keys}
        
        # Enrich with public test cases
        problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_dict['id'])

        return problem_dict