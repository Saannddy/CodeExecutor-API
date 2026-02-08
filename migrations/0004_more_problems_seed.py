import uuid
import json
from yoyo import step

def apply_step(conn):
    cursor = conn.cursor()

    # Problems Data (ID, Title, Description, Difficulty, Config)
    p_ids = {
        'palindrome': str(uuid.uuid4()),
        'factorial': str(uuid.uuid4()),
        'fibonacci': str(uuid.uuid4()),
        'find_max': str(uuid.uuid4()),
        'anagram': str(uuid.uuid4())
    }

    problems = [
        (p_ids['palindrome'], 'Palindrome Check', 'Write a function that checks if a given string is a palindrome.', 'Easy', {
            'timeout': 5,
            'templates': {
                'python': 'def is_palindrome(s):\n    # __CODE_GOES_HERE__\n    pass',
                'javascript': 'function isPalindrome(s) {\n    // __CODE_GOES_HERE__\n}'
            }
        }),
        (p_ids['factorial'], 'Factorial', 'Write a function that calculates the factorial of a given non-negative integer n.', 'Easy', {
            'timeout': 5,
            'templates': {
                'python': 'def factorial(n):\n    # __CODE_GOES_HERE__\n    pass',
                'javascript': 'function factorial(n) {\n    // __CODE_GOES_HERE__\n}'
            }
        }),
        (p_ids['fibonacci'], 'Fibonacci Number', 'Write a function that returns the n-th Fibonacci number.', 'Easy', {
            'timeout': 5,
            'templates': {
                'python': 'def fib(n):\n    # __CODE_GOES_HERE__\n    pass',
                'javascript': 'function fib(n) {\n    // __CODE_GOES_HERE__\n}'
            }
        }),
        (p_ids['find_max'], 'Find Maximum', 'Write a function that returns the maximum element in a given array of integers.', 'Easy', {
            'timeout': 5,
            'templates': {
                'python': 'def find_max(arr):\n    # __CODE_GOES_HERE__\n    pass',
                'javascript': 'function findMax(arr) {\n    // __CODE_GOES_HERE__\n}'
            }
        }),
        (p_ids['anagram'], 'Valid Anagram', 'Write a function that determines if two strings are anagrams of each other.', 'Easy', {
            'timeout': 5,
            'templates': {
                'python': 'def is_anagram(s, t):\n    # __CODE_GOES_HERE__\n    pass',
                'javascript': 'function isAnagram(s, t) {\n    // __CODE_GOES_HERE__\n}'
            }
        })
    ]

    for p in problems:
        cursor.execute(
            "INSERT INTO problems (id, title, description, difficulty, config) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (p[0], p[1], p[2], p[3], json.dumps(p[4]))
        )

    # Test Cases Data
    test_cases = [
        # Palindrome Check
        (p_ids['palindrome'], '"racecar"', 'True', 1, False),
        (p_ids['palindrome'], '"hello"', 'False', 2, False),
        # Factorial
        (p_ids['factorial'], '5', '120', 1, False),
        (p_ids['factorial'], '0', '1', 2, False),
        # Fibonacci
        (p_ids['fibonacci'], '6', '8', 1, False),
        (p_ids['fibonacci'], '0', '0', 2, False),
        # Find Max
        (p_ids['find_max'], '[1, 5, 3, 9, 2]', '9', 1, False),
        (p_ids['find_max'], '[-1, -5, -3]', '-1', 2, False),
        # Valid Anagram
        (p_ids['anagram'], '"anagram", "nagaram"', 'True', 1, False),
        (p_ids['anagram'], '"rat", "car"', 'False', 2, False)
    ]

    for tc in test_cases:
        cursor.execute(
            "INSERT INTO test_cases (problem_id, input, output, sort_order, is_hidden) VALUES (%s, %s, %s, %s, %s)",
            tc
        )

    # Categories and Tags
    categories = [('Basic',), ('Array',), ('String',), ('Math',)]
    for cat in categories:
        cursor.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", cat)

    tags = [('String',), ('Math',), ('Recursion',), ('Array',)]
    for t in tags:
        cursor.execute("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", t)

    # Linking
    cursor.execute("""
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT %s, id FROM categories WHERE name = 'String'
    """, (p_ids['palindrome'],))
    cursor.execute("""
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT %s, id FROM categories WHERE name = 'Math'
    """, (p_ids['factorial'],))
    cursor.execute("""
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT %s, id FROM categories WHERE name = 'Math'
    """, (p_ids['fibonacci'],))
    cursor.execute("""
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT %s, id FROM categories WHERE name = 'Array'
    """, (p_ids['find_max'],))
    cursor.execute("""
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT %s, id FROM categories WHERE name = 'String'
    """, (p_ids['anagram'],))

    cursor.execute("""
        INSERT INTO problem_tags (problem_id, tag_id)
        SELECT %s, id FROM tags WHERE name = 'String'
    """, (p_ids['palindrome'],))
    cursor.execute("""
        INSERT INTO problem_tags (problem_id, tag_id)
        SELECT %s, id FROM tags WHERE name = 'Math'
    """, (p_ids['factorial'],))
    cursor.execute("""
        INSERT INTO problem_tags (problem_id, tag_id)
        SELECT %s, id FROM tags WHERE name = 'Recursion'
    """, (p_ids['fibonacci'],))
    cursor.execute("""
        INSERT INTO problem_tags (problem_id, tag_id)
        SELECT %s, id FROM tags WHERE name = 'Array'
    """, (p_ids['find_max'],))
    cursor.execute("""
        INSERT INTO problem_tags (problem_id, tag_id)
        SELECT %s, id FROM tags WHERE name = 'String'
    """, (p_ids['anagram'],))

steps = [
    step(apply_step)
]
