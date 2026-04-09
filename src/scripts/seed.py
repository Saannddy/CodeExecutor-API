import logging
from tqdm import tqdm
import uuid
import random
import string
from datetime import datetime, timezone
from sqlalchemy import text
from sqlmodel import Session, select
from infrastructure import engine
from models import (
    Problem, Category, Tag, TestCase, Riddle, Question, Choice,
    RiddleTagLink, QuestionTagLink, QuestionCategoryLink,
    ChunkTemplate, Chunk, Snippet, ChunkCategoryLink, ChunkTagLink, Expectation
)
from scripts.seeders.seed_hallway_java import seed_hallway_java
from scripts.seeders.seed_lockerroom_java import seed_lockerroom_java
from scripts.seeders.seed_restroom_java import seed_restroom_java
from scripts.seeders.seed_elevatorhall_java import seed_elevatorhall_java



logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

NAMESPACE = uuid.NAMESPACE_DNS

def get_uuid(name: str) -> uuid.UUID:
    """Generate a deterministic UUID based on a string name."""
    return uuid.uuid5(NAMESPACE, name)

def seed_data():
    if not engine:
        logging.error("No database engine found. Skipping seeding.")
        return

    with Session(engine) as session:
        logging.info("Seeding initial data with deterministic UUIDs...")

        def get_or_create_category(name):
            cat_id = get_uuid(f"cat_{name}")
            # Try finding by ID first
            cat = session.exec(select(Category).where(Category.id == cat_id)).first()
            if not cat:
                # Fallback to finding by name to avoid unique constraint violations
                cat = session.exec(select(Category).where(Category.name == name)).first()
            
            if not cat:
                cat = Category(id=cat_id, name=name)
                session.add(cat)
                session.commit()
                session.refresh(cat)
            return cat

        def get_or_create_tag(name):
            tag_id = get_uuid(f"tag_{name}")
            # Try finding by ID first
            tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
            if not tag:
                # Fallback to finding by name to avoid unique constraint violations
                tag = session.exec(select(Tag).where(Tag.name == name)).first()
            
            if not tag:
                tag = Tag(id=tag_id, name=name)
                session.add(tag)
                session.commit()
                session.refresh(tag)
            return tag

        # Check if Problems already have data
        if not session.exec(select(Problem)).first():

            # 1. Categories
            math = get_or_create_category("Math")
            string_cat = get_or_create_category("String")
            algorithms = get_or_create_category("Algorithms")

            # 2. Tags
            easy = get_or_create_tag("Easy")
            medium = get_or_create_tag("Medium")
            basic = get_or_create_tag("Basic")
            array = get_or_create_tag("Array")

            # 3. Helper for Problems and Test Cases
            def add_problem(title, description, difficulty, category_list, tag_list, config=None, test_cases=None):
                p_id = get_uuid(f"prob_{title}")
                p = Problem(
                    id=p_id,
                    title=title,
                    description=description,
                    difficulty=difficulty,
                    config=config or {"timeout": 5}
                )
                p.categories = category_list
                p.tags = tag_list
                session.add(p)
                
                if test_cases:
                    for i, tc_data in enumerate(test_cases):
                        tc_id = get_uuid(f"tc_{title}_{i}")
                        tc = TestCase(
                            id=tc_id,
                            problem_id=p_id,
                            input=tc_data['input'],
                            output=tc_data['output'],
                            is_hidden=tc_data.get('is_hidden', True),
                            sort_order=i + 1
                        )
                        session.add(tc)
                
                session.commit()
                return p

            # 4. Seed Problems
            
            # Multiply Two Numbers (New)
            add_problem(
                title="Multiply Two Numbers",
                description="Read two space-separated integers from stdin and print their product.",
                difficulty="Easy",
                category_list=[math],
                tag_list=[easy, basic],
                config={
                    "timeout": 2,
                    "templates": {
                        "python": "num1, num2 = map(int, input().split())\nprint(num1 * num2)"
                    }
                },
                test_cases=[
                    {"input": "2 3", "output": "6", "is_hidden": False},
                    {"input": "5 10", "output": "50", "is_hidden": False},
                    {"input": "0 100", "output": "0", "is_hidden": True},
                    {"input": "-5 5", "output": "-25", "is_hidden": True},
                    {"input": "12 12", "output": "144", "is_hidden": True},
                ]
            )

            # Two Sum
            add_problem(
                title="Two Sum",
                description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
                difficulty="Easy",
                category_list=[math, algorithms],
                tag_list=[easy, array],
                config={
                    "timeout": 5,
                    "templates": {
                        "python": "def two_sum(nums, target):\n    # Write your code here\n    pass"
                    }
                },
                test_cases=[
                    {"input": "[2, 7, 11, 15], 9", "output": "[0, 1]", "is_hidden": False},
                    {"input": "[3, 2, 4], 6", "output": "[1, 2]", "is_hidden": False},
                    {"input": "[3, 3], 6", "output": "[0, 1]", "is_hidden": True},
                    {"input": "[1, 5, 8], 13", "output": "[1, 2]", "is_hidden": True},
                    {"input": "[-1, -2, -3, -4, -5], -8", "output": "[2, 4]", "is_hidden": True},
                ]
            )

            # Palindrome Check
            add_problem(
                title="Palindrome Check",
                description="Check if a given string is a palindrome.",
                difficulty="Easy",
                category_list=[string_cat],
                tag_list=[easy, basic],
                test_cases=[
                    {"input": "'racecar'", "output": "True", "is_hidden": False},
                    {"input": "'hello'", "output": "False", "is_hidden": False},
                    {"input": "'a'", "output": "True", "is_hidden": True},
                    {"input": "''", "output": "True", "is_hidden": True},
                    {"input": "'Was it a car or a cat I saw?'", "output": "False", "is_hidden": True}, # Case sensitive or space issues depending on logic
                ]
            )

            # Factorial
            add_problem(
                title="Factorial",
                description="Calculate the factorial of a non-negative integer `n`.",
                difficulty="Easy",
                category_list=[math],
                tag_list=[easy, basic],
                test_cases=[
                    {"input": "5", "output": "120", "is_hidden": False},
                    {"input": "0", "output": "1", "is_hidden": False},
                    {"input": "1", "output": "1", "is_hidden": True},
                    {"input": "10", "output": "3628800", "is_hidden": True},
                    {"input": "3", "output": "6", "is_hidden": True},
                ]
            )

            # Fibonacci Number
            add_problem(
                title="Fibonacci Number",
                description="Find the `n`-th Fibonacci number.",
                difficulty="Medium",
                category_list=[math, algorithms],
                tag_list=[medium],
                test_cases=[
                    {"input": "10", "output": "55", "is_hidden": False},
                    {"input": "1", "output": "1", "is_hidden": False},
                    {"input": "0", "output": "0", "is_hidden": True},
                    {"input": "2", "output": "1", "is_hidden": True},
                    {"input": "20", "output": "6765", "is_hidden": True},
                ]
            )

            # Valid Anagram
            add_problem(
                title="Valid Anagram",
                description="Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.",
                difficulty="Easy",
                category_list=[string_cat],
                tag_list=[easy],
                test_cases=[
                    {"input": "'anagram', 'nagaram'", "output": "True", "is_hidden": False},
                    {"input": "'rat', 'car'", "output": "False", "is_hidden": False},
                    {"input": "'a', 'ab'", "output": "False", "is_hidden": True},
                    {"input": "'debug', 'bugged'", "output": "False", "is_hidden": True},
                    {"input": "'listen', 'silent'", "output": "True", "is_hidden": True},
                ]
            )

            logging.info("Successfully seeded 6 problems with 5 test cases each.")



        # 5. Seed Riddles
        if not session.exec(select(RiddleTagLink)).first():
            # Clear existing riddles and their tags
            session.exec(text("DELETE FROM riddle_tags"))
            session.exec(text("DELETE FROM riddles"))
            session.commit()
            
            logging.info("Seeding 30 riddles...")
            for i in tqdm(range(1, 31), desc="Seeding Riddles"):
                riddle = Riddle(
                    riddle_text=f"This is riddle number {i}. What is it?",
                    refer_char=random.choice(string.ascii_uppercase),
                    refer_index=random.randint(1, 6),
                    difficulty=random.choice(["Easy", "Medium", "Hard"]),
                    created_at=datetime.now(timezone.utc)
                )
                tag_name = random.choice(["Logic", "Word", "Math", "Riddle"])
                riddle.tags = [get_or_create_tag(tag_name)]
                session.add(riddle)
            session.commit()
            logging.info("Successfully seeded 30 riddles.")

        # 6. Seed Questions
        if not session.exec(select(QuestionTagLink)).first():
            # Clear existing questions, choices, and their links
            session.exec(text("DELETE FROM question_tags"))
            session.exec(text("DELETE FROM question_categories"))
            session.exec(text("DELETE FROM choices"))
            session.exec(text("DELETE FROM questions"))
            session.commit()

            logging.info("Seeding 10 questions with 4 choices each...")
            for i in tqdm(range(1, 11), desc="Seeding Questions"):
                question = Question(
                    title=f"Sample Question {i}",
                    question_text=f"This is the content for question {i}. Which choice is correct?",
                    created_at=datetime.now(timezone.utc)
                )
                tag_name = random.choice(["General", "Tech", "Science", "Trivia"])
                cat_name = random.choice(["Knowledge", "Trivia", "Education"])
                question.tags = [get_or_create_tag(tag_name)]
                question.categories = [get_or_create_category(cat_name)]
                session.add(question)
                session.flush()

                correct_index = random.randint(0, 3)
                for j in range(4):
                    choice = Choice(
                        question_id=question.id,
                        choice_text=f"Choice {j+1} for question {i}",
                        is_correct=(j == correct_index)
                    )
                    session.add(choice)
            session.commit()
            logging.info("Successfully seeded 10 questions with choices.")

        # 7. Seed Chunks
        logging.info("Checking for chunks to seed...")
        
        chunks_to_seed = [
            {
                "title": "Sample Chunk 1",
                "difficulty": "Medium",
                "templates": [
                    {
                        "lang": "python",
                        "name": "Python Implementation",
                        "code": "def solution({{args}}):\n    {{logic}}\n\n# Test here\n{{test}}",
                        "snippets": [("args", "x, y"), ("logic", "return x * y"), ("test", "print(solution(1, 2))")]
                    },
                    {
                        "lang": "javascript",
                        "name": "JavaScript Implementation",
                        "code": "function solution({{{args}}}) {\n{{{logic}}}\n}\n\n// Test here\n{{{test}}}",
                        "snippets": [("args", "x, y"), ("logic", "return x * y;"), ("test", "console.log(solution(1, 2))")]
                    }
                ],
                "expectation": {"input": "1 2", "output": "2"}
            },
            {
                "title": "Sample Chunk 2",
                "difficulty": "Easy",
                "templates": [
                    {
                        "lang": "python",
                        "name": "Python Implementation",
                        "code": "def solution({{{args}}}):\n{{{logic}}}\n\n# Test here\n{{{test}}}",
                        "snippets": [("args", "x, y"), ("logic", "return x + y"), ("test", "print(solution(2, 4))")]
                    },
                    {
                        "lang": "javascript",
                        "name": "JavaScript Implementation",
                        "code": "function solution({{{args}}}) {\n{{{logic}}}\n}\n\n// Test here\n{{{test}}}",
                        "snippets": [("args", "x, y"), ("logic", "return x + y;"), ("test", "console.log(solution(2, 4))")]
                    }
                ],
                "expectation": {"input": "2 4", "output": "6"}
            },
            {
                "title": "Sample Chunk 3",
                "difficulty": "Hard",
                "templates": [
                    {
                        "lang": "python",
                        "name": "Python Implementation",
                        "code": "def solution({{{args}}}):\n{{{logic}}}\n\n# Test here\n{{{test}}}",
                        "snippets": [("args", "x, y"), ("logic", "return x * y"), ("test", "print(solution(3, 6))")]
                    },
                    {
                        "lang": "javascript",
                        "name": "JavaScript Implementation",
                        "code": "function solution({{{args}}}) {\n{{{logic}}}\n}\n\n// Test here\n{{{test}}}",
                        "snippets": [("args", "x, y"), ("logic", "return x * y;"), ("test", "console.log(solution(3, 6))")]
                    }
                ],
                "expectation": {"input": "3 6", "output": "18"}
            },
            {
                "title": "Complex Logic Builder",
                "difficulty": "Hard",
                "category": "Advanced",
                "templates": [
                    {
                        "lang": "python",
                        "name": "Complex Python Implementation",
                        "code": "{{{imports}}}\n\n{{{setup}}}\n\ndef utility(v):\n    return v * 2\n\ndef solution({{{args}}}):\n{{{validation}}}\n{{{logic}}}\n\n# Test here\n{{{test}}}",
                        "snippets": [
                            ("imports", "import math\nimport random"),
                            ("setup", "OFFSET = 100\ndef get_offset(): return OFFSET"),
                            ("args", "data_list, multiplier"),
                            ("validation", "if not isinstance(data_list, list): return None"),
                            ("logic", "result = [utility(x) * multiplier + get_offset() for x in data_list]\nreturn result"),
                            ("test", "print(solution([1, 2, 3], 5))")
                        ]
                    },
                    {
                        "lang": "javascript",
                        "name": "Complex JavaScript Implementation",
                        "code": "{{{imports}}}\n\n{{{setup}}}\n\nfunction utility(v) {\n    return v * 2;\n}\n\nfunction solution({{{args}}}) {\n{{{validation}}}\n{{{logic}}}\n}\n\n// Test here\n{{{test}}}",
                        "snippets": [
                            ("imports", "// No imports needed"),
                            ("setup", "const OFFSET = 100;\nfunction getOffset() { return OFFSET; }"),
                            ("args", "dataList, multiplier"),
                            ("validation", "if (!Array.isArray(dataList)) return null;"),
                            ("logic", "const result = dataList.map(x => utility(x) * multiplier + getOffset());\nreturn result;"),
                            ("test", "const res = solution([1, 2, 3], 5); console.log('[' + res.join(', ') + ']');")
                        ]
                    }
                ],
                "expectation": {"input": "[1, 2, 3] 5", "output": "[110, 120, 130]"}
            }
        ]

        for c_data in tqdm(chunks_to_seed, desc="Seeding Chunks"):
            existing = session.exec(select(Chunk).where(Chunk.title == c_data["title"])).first()
            if existing:
                continue

            logging.info(f"Seeding chunk: {c_data['title']}")
            chunk = Chunk(
                title=c_data["title"],
                difficulty=c_data["difficulty"],
                created_at=datetime.now(timezone.utc)
            )
            chunk.categories = [get_or_create_category(c_data.get("category", "Basics"))]
            session.add(chunk)
            session.flush()

            for t_data in c_data["templates"]:
                template = ChunkTemplate(
                    chunk_id=chunk.id,
                    language=t_data["lang"],
                    name=t_data["name"],
                    template_code=t_data["code"],
                    description=f"Standard {t_data['lang']} boilerplate"
                )
                session.add(template)
                session.flush()

                for key, content in t_data["snippets"]:
                    s = Snippet(template_id=template.id, placeholder_key=key, code_content=content)
                    session.add(s)

            if "expectation" in c_data:
                ex = Expectation(
                    chunk_id=chunk.id,
                    input=c_data["expectation"]["input"],
                    output=c_data["expectation"]["output"]
                )
                session.add(ex)
        
        session.commit()
        logging.info("Chunk seeding process completed.")

        # Seed local regional data
        logging.info("Seeding regional data...")
        seed_hallway_java()
        seed_lockerroom_java()
        seed_restroom_java()
        seed_elevatorhall_java()
        logging.info("Regional seeding process completed.")


if __name__ == "__main__":
    seed_data()
