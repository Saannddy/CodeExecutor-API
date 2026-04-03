import logging
import uuid
import json
import os
from datetime import datetime, timezone
from sqlmodel import Session, select
from infrastructure import engine
from models import (
    Category, Tag, Question, Choice, Chunk, ChunkTemplate, Snippet, Expectation, Problem, TestCase
)
from sqlalchemy.orm.attributes import flag_modified

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

NAMESPACE = uuid.NAMESPACE_DNS

def get_uuid(name: str) -> uuid.UUID:
    """Generate a deterministic UUID based on a string name."""
    return uuid.uuid5(NAMESPACE, name)

def load_json(filename):
    base_path = os.path.join(os.path.dirname(__file__), "..", "data", "java", "elevatorhall")
    filepath = os.path.join(base_path, filename)
    if not os.path.exists(filepath):
        logging.warning(f"File not found: {filepath}")
        return []
    with open(filepath, "r") as f:
        return json.load(f)

def seed_elevatorhall_java():
    if not engine:
        logging.error("No database engine found. Skipping seeding.")
        return

    CHUNKS = load_json("chunks.json")
    PROBLEMS = load_json("problems.json")

    with Session(engine) as session:
        logging.info("Starting JAV_ELVHALL JSON-based seeding process...")

        def get_or_create_category(name):
            cat_id = get_uuid(f"cat_{name}")
            cat = session.exec(select(Category).where(Category.id == cat_id)).first()
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
                tag = Tag(id=tag_id, name=name)
                session.add(tag)
                session.commit()
                session.refresh(tag)
            return tag

        elv_hall_tag = get_or_create_tag("JAV_ELVHALL")
        java_cat = get_or_create_category("Java")

        # 1. Seed Chunks
        logging.info(f"Seeding {len(CHUNKS)} Java chunks...")
        for c_data in CHUNKS:
            c_id = get_uuid(f"jav_elvhall_chunk_{c_data['title']}")
            chunk = session.exec(select(Chunk).where(Chunk.id == c_id)).first()
            if not chunk:
                chunk = Chunk(
                    id=c_id,
                    title=c_data["title"],
                    difficulty=c_data["difficulty"],
                    created_at=datetime.now(timezone.utc)
                )
                chunk.categories = [get_or_create_category(c_data.get("category", "Java Basics"))]
                chunk.tags = [elv_hall_tag]
                session.add(chunk)
                session.flush()
            else:
                chunk.difficulty = c_data["difficulty"]
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
                for ex in chunk.expectations:
                    session.delete(ex)
                session.flush()
                ex = Expectation(
                    chunk_id=chunk.id,
                    input=c_data["expectation"]["input"],
                    output=c_data["expectation"]["output"]
                )
                session.add(ex)

        # 2. Seed Problems
        logging.info(f"Seeding {len(PROBLEMS)} Java problems...")
        for p_data in PROBLEMS:
            p_id = get_uuid(f"jav_elvhall_prob_{p_data['title']}")
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
                problem.tags = [elv_hall_tag]
                session.add(problem)
            else:
                problem.description = p_data["description"]
                problem.difficulty = p_data["difficulty"]
                config = problem.config or {}
                config["templates"] = p_data.get("templates", {})
                problem.config = config
                flag_modified(problem, "config")
                session.add(problem)
            session.flush()

            if "test_cases" in p_data:
                for tc in problem.test_cases:
                    session.delete(tc)
                session.flush()

                for i, tc_data in enumerate(p_data["test_cases"]):
                    tc_id = get_uuid(f"jav_elvhall_tc_{p_data['title']}_{i}")
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
        logging.info("JAV_ELVHALL JSON-based seeding completed successfully.")

if __name__ == "__main__":
    seed_elevatorhall_java()
