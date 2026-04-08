import logging
import uuid
import random
import json
import os
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import Session, select
from tqdm import tqdm
from infrastructure import engine
from models import (
    Category, Tag, Riddle, Question, Choice, Chunk, ChunkTemplate, Snippet, Expectation, Problem, TestCase
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

NAMESPACE = uuid.NAMESPACE_DNS

def get_uuid(name: str) -> uuid.UUID:
    """Generate a deterministic UUID based on a string name."""
    return uuid.uuid5(NAMESPACE, name)

def load_json(filename):
    # Base directory for seeding data (one level up from seeders/)
    base_path = os.path.join(os.path.dirname(__file__), "..", "data", "java", "restroom")
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        logging.warning(f"File not found: {filepath}")
        return []
    with open(filepath, "r") as f:
        return json.load(f)

def seed_restroom_java():
    if not engine:
        logging.error("No database engine found. Skipping seeding.")
        return

    # Load data from JSON files
    QUESTIONS = load_json("questions.json")
    RIDDLES = load_json("riddles.json")
    CHUNKS = load_json("chunks.json")
    PROBLEMS = load_json("problems.json")

    with Session(engine) as session:
        logging.info("Starting JAV_RESTROOM JSON-based seeding process...")

        def get_or_create_category(name):
            cat_id = get_uuid(f"cat_{name}")
            cat = session.exec(select(Category).where(Category.id == cat_id)).first()
            if not cat:
                cat = session.exec(select(Category).where(Category.name == name)).first()
            if not cat:
                cat = Category(id=cat_id, name=name)
                session.add(cat)
                session.commit()
                session.refresh(cat)
            return cat

        def get_or_create_tag(name):
            tag_id = get_uuid(f"tag_{name}")
            tag = session.exec(select(Tag).where(Tag.id == tag_id)).first()
            if not tag:
                tag = session.exec(select(Tag).where(Tag.name == name)).first()
            if not tag:
                tag = Tag(id=tag_id, name=name)
                session.add(tag)
                session.commit()
                session.refresh(tag)
            return tag

        jav_restroom_tag = get_or_create_tag("JAV_RESTROOM")
        java_cat = get_or_create_category("Java")

        logging.info(f"Seeding {len(QUESTIONS)} Java questions...")
        for q_data in tqdm(QUESTIONS, desc="Seeding Questions"):
            q_id = get_uuid(f"jav_rst_q_{q_data['title']}")
            if session.exec(select(Question).where(Question.id == q_id)).first():
                continue
            
            question = Question(
                id=q_id,
                title=q_data["title"],
                question_text=q_data["text"],
                created_at=datetime.now(timezone.utc)
            )
            question.tags = [jav_restroom_tag]
            question.categories = [java_cat]
            session.add(question)
            session.flush()

            for i, (choice_text, is_correct) in enumerate(q_data["choices"]):
                c_id = get_uuid(f"jav_rst_c_{q_data['title']}_{i}")
                choice = Choice(
                    id=c_id,
                    question_id=question.id,
                    choice_text=choice_text,
                    is_correct=is_correct
                )
                session.add(choice)

        logging.info(f"Seeding {len(RIDDLES)} Java riddles...")
        for i, r_data in enumerate(tqdm(RIDDLES, desc="Seeding Riddles")):
            r_id = get_uuid(f"jav_rst_r_{i}")
            if session.exec(select(Riddle).where(Riddle.id == r_id)).first():
                continue
                
            riddle = Riddle(
                id=r_id,
                riddle_text=r_data["text"],
                refer_char=r_data["char"],
                refer_index=r_data["index"],
                difficulty=r_data["difficulty"] or "Medium",
                created_at=datetime.now(timezone.utc)
            )
            riddle.tags = [jav_restroom_tag]
            session.add(riddle)

        logging.info(f"Seeding {len(CHUNKS)} Java chunks...")
        for c_data in tqdm(CHUNKS, desc="Seeding Chunks"):
            c_id = get_uuid(f"jav_rst_chunk_{c_data['title']}")
            chunk = session.exec(select(Chunk).where(Chunk.id == c_id)).first()
            if not chunk:
                chunk = Chunk(
                    id=c_id,
                    title=c_data["title"],
                    difficulty=c_data["difficulty"],
                    created_at=datetime.now(timezone.utc)
                )
                chunk.categories = [get_or_create_category(c_data.get("category", "Java Basics"))]
                chunk.tags = [jav_restroom_tag]
                session.add(chunk)
                session.flush()
            else:
                # Update basic info
                chunk.difficulty = c_data["difficulty"]
                # Clear existing templates to re-seed (cascades to snippets)
                for t in chunk.templates:
                    session.delete(t)
                session.flush()

            for lang, t_data in c_data["templates"].items():
                template = ChunkTemplate(
                    chunk_id=chunk.id,
                    language=lang,
                    name=t_data["name"],
                    template_code=t_data["template_code"],
                    description=t_data.get("description", f"Standard {lang} boilerplate")
                )
                session.add(template)
                session.flush()

                for key, content in t_data.get("snippets", {}).items():
                    s = Snippet(template_id=template.id, placeholder_key=key, code_content=content)
                    session.add(s)

            if "expectation" in c_data:
                # Clear existing expectations
                for ex in chunk.expectations:
                    session.delete(ex)
                session.flush()
                
                ex = Expectation(
                    chunk_id=chunk.id,
                    input=c_data["expectation"]["input"],
                    output=c_data["expectation"]["output"]
                )
                session.add(ex)

        logging.info(f"Seeding {len(PROBLEMS)} Java problems...")
        for p_data in tqdm(PROBLEMS, desc="Seeding Problems"):
            p_id = get_uuid(f"jav_rst_prob_{p_data['title']}")
            problem = session.exec(select(Problem).where(Problem.id == p_id)).first()
            
            if not problem:
                problem = Problem(
                    id=p_id,
                    title=p_data["title"],
                    description=p_data["description"],
                    difficulty=p_data["difficulty"],
                    config={"templates": p_data.get("templates", {})}
                )
                problem.categories = [get_or_create_category(p_data.get("category", "Java Algorithms"))]
                problem.tags = [jav_restroom_tag]
                session.add(problem)
            else:
                # Update existing problem
                problem.description = p_data["description"]
                problem.difficulty = p_data["difficulty"]
                # Update templates in config
                config = problem.config or {}
                config["templates"] = p_data.get("templates", {})
                problem.config = config
                flag_modified(problem, "config")
                session.add(problem)
            
            session.flush()

            if "test_cases" in p_data:
                # Clear existing test cases to avoid UniqueViolation
                for tc in problem.test_cases:
                    session.delete(tc)
                session.flush()

                for i, tc_data in enumerate(p_data["test_cases"]):
                    tc_id = get_uuid(f"jav_rst_tc_{p_data['title']}_{i}")
                    tc = TestCase(
                        id=tc_id,
                        problem_id=p_id,
                        input=str(tc_data["input"]),
                        output=str(tc_data["output"]),
                        is_hidden=tc_data.get("is_hidden", True),
                        sort_order=i + 1
                    )
                    session.add(tc)

        session.commit()
        logging.info("JAV_RESTROOM JSON-based seeding completed successfully.")

if __name__ == "__main__":
    seed_restroom_java()
