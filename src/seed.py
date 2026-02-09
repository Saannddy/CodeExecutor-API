import logging
import uuid
from sqlmodel import Session, select
from infrastructure.database import engine
from models import Problem, Category, Tag, TestCase

def seed_data():
    with Session(engine) as session:
        # Check if we already have data
        if session.exec(select(Problem)).first():
            logging.info("Database already seeded. Skipping.")
            return

        logging.info("Seeding initial data...")

        def get_or_create_category(name):
            cat = session.exec(select(Category).where(Category.name == name)).first()
            if not cat:
                cat = Category(name=name)
                session.add(cat)
                session.commit()
                session.refresh(cat)
            return cat

        def get_or_create_tag(name):
            tag = session.exec(select(Tag).where(Tag.name == name)).first()
            if not tag:
                tag = Tag(name=name)
                session.add(tag)
                session.commit()
                session.refresh(tag)
            return tag

        # 1. Categories
        math = get_or_create_category("Math")
        logic = get_or_create_category("Logic")
        string_cat = get_or_create_category("String")
        algorithms = get_or_create_category("Algorithms")

        # 2. Tags
        easy = get_or_create_tag("Easy")
        medium = get_or_create_tag("Medium")
        basic = get_or_create_tag("Basic")
        array = get_or_create_tag("Array")
        hash_table = get_or_create_tag("Hash Table")

        # 3. Create Problems
        p1 = Problem(
            title="Two Sum",
            description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
            difficulty="Easy",
            config={
                "timeout": 5,
                "templates": {
                    "python": "def two_sum(nums, target):\n    # Write your code here\n    pass",
                    "javascript": "function twoSum(nums, target) {\n    // Write your code here\n}"
                }
            }
        )
        p1.categories = [math, algorithms]
        p1.tags = [easy, array, hash_table]

        p2 = Problem(
            title="Palindrome Check",
            description="Check if a given string is a palindrome.",
            difficulty="Easy",
            config={"timeout": 2}
        )
        p2.categories = [string_cat]
        p2.tags = [easy, basic]

        p3 = Problem(
            title="Factorial",
            description="Calculate the factorial of a non-negative integer `n`.",
            difficulty="Easy",
            config={"timeout": 2}
        )
        p3.categories = [math]
        p3.tags = [easy, basic]

        p4 = Problem(
            title="Fibonacci Number",
            description="Find the `n`-th Fibonacci number.",
            difficulty="Medium",
            config={"timeout": 3}
        )
        p4.categories = [math, algorithms]
        p4.tags = [medium]

        p5 = Problem(
            title="Valid Anagram",
            description="Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.",
            difficulty="Easy",
            config={"timeout": 2}
        )
        p5.categories = [string_cat]
        p5.tags = [easy, hash_table]

        session.add_all([p1, p2, p3, p4, p5])
        session.commit()

        # 4. Create Test Cases
        session.add_all([
            TestCase(problem_id=p1.id, input="[2, 7, 11, 15], 9", output="[0, 1]", is_hidden=False, sort_order=1),
            TestCase(problem_id=p2.id, input="'racecar'", output="True", is_hidden=False, sort_order=1),
            TestCase(problem_id=p3.id, input="5", output="120", is_hidden=False, sort_order=1),
            TestCase(problem_id=p4.id, input="10", output="55", is_hidden=False, sort_order=1),
            TestCase(problem_id=p5.id, input="'anagram', 'nagaram'", output="True", is_hidden=False, sort_order=1),
        ])
        session.commit()
        
        logging.info("Successfully seeded 5 problems.")

if __name__ == "__main__":
    from infrastructure.database import init_db
    init_db()
    seed_data()
