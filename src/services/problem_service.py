from repositories import ProblemRepository, TestCaseRepository

class ProblemService:
    def __init__(self):
        self.problem_repo = ProblemRepository()
        self.test_case_repo = TestCaseRepository()

    def list_all_problems(self):
        """Retrieve a list of all problems with basic information."""
        return self.problem_repo.find_all()

    def get_problem_details(self, problem_id, test_case_limit=None, tag_limit=None, category_limit=None):
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
        problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id, limit=test_case_limit)

        # Apply optional limits to tags and categories
        if problem_dict.get('tags') and tag_limit:
            problem_dict['tags'] = problem_dict['tags'][:tag_limit]
        if problem_dict.get('categories') and category_limit:
            problem_dict['categories'] = problem_dict['categories'][:category_limit]

        return problem_dict

    def list_problems_by_category(self, category_name):
        """Filter problems by category."""
        return self.problem_repo.find_by_category(category_name)

    def list_problems_by_tag(self, tag_name):
        """Filter problems by tag."""
        return self.problem_repo.find_by_tag(tag_name)
    
    def get_random_problem(self, category_name=None, tag_name=None, limit=1, test_case_limit=None, tag_limit=None, category_limit=None):   
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
            problem_dict['test_cases'] = self.test_case_repo.find_public_by_problem(problem_id, limit=test_case_limit)

            # Apply optional limits to tags and categories
            if problem_dict.get('tags') and tag_limit:
                problem_dict['tags'] = problem_dict['tags'][:tag_limit]
            if problem_dict.get('categories') and category_limit:
                problem_dict['categories'] = problem_dict['categories'][:category_limit]

            enriched.append(problem_dict)

        return enriched
    
