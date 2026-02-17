from repositories import ProblemRepository, TestCaseRepository

class ProblemService:
    def __init__(self):
        self.problem_repo = ProblemRepository()
        self.test_case_repo = TestCaseRepository()

    def list_all_problems(self):
        """Retrieve a list of all problems with basic information."""
        return self.problem_repo.find_all()

    def get_problem_details(self, problem_id):
        """Fetch full problem details, including config and public test cases.

        Optional limits can be provided to restrict returned counts for
        `test_cases`, `tags`, and `categories`.
        """
        problem_dict = self.problem_repo.find_details_by_id(problem_id)
        if not problem_dict:
            return None

        # Filter configuration for API response
        allowed_keys = {'timeout', 'templates'}
        problem_dict['config'] = {k: v for k, v in problem_dict.get('config', {}).items() if k in allowed_keys}
        
        # Enrich with public test cases (apply optional limit)
        problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id)

        # Apply optional limits to tags and categories


        return problem_dict

    def list_problems_by_category(self, category_name):
        """Filter problems by category."""
        return self.problem_repo.find_by_category(category_name)

    def list_problems_by_tag(self, tag_name):
        """Filter problems by tag."""
        return self.problem_repo.find_by_tag(tag_name)
    
    def get_random_problem(self, category_name=None, tag_name=None, limit=1):   
        """Fetch `limit` random problems (optionally filtered) and include details.

        Returns a list of problem dicts (may be empty).
        """
        problems = self.problem_repo.find_random(category_name=category_name, tag_name=tag_name, limit=limit)
        if not problems:
            return []

        allowed_keys = {'timeout', 'templates'}
        enriched = []
        for problem_dict in problems:
            # Filter configuration for API response
            problem_dict['config'] = {k: v for k, v in problem_dict.get('config', {}).items() if k in allowed_keys}

            # Add public test cases (with optional limit)
            problem_id = problem_dict.get('id')
            problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id)

            # Apply optional limits to tags and categories

            enriched.append(problem_dict)

        return enriched
    

    
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