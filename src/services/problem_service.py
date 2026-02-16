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
    
    def add_test_cases(self, problem_id, testcases):
        """ Add multiple test cases to problem """
        problem = self.problem_repo.find_by_id(problem_id)
        if not problem:
            return {'status': 'error', 'message': 'Problem not found'}
        
        created_testcases = []
        for test in testcases:
            if 'input' not in test or 'output' not in test:
                return {'status': 'error', 'message': 'Testcase must have input and output'}
            testcase_data = {
                'problem_id': problem_id,
                'input': test['input'],
                'output': test['output'],
                'is_hidden': test.get('isHidden', False)
            }

            created = self.test_case_repo.create_test_case(testcase_data)

            if created:
                created_testcases.append(created)
            
        return {'status': 'success', 'data': {
            'created_count': len(created_testcases),
            'testcases': created_testcases
        }}
