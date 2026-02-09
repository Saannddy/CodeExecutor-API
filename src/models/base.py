from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship, JSON, Column

class ProblemCategoryLink(SQLModel, table=True):
    __tablename__ = "problem_categories"
    problem_id: UUID = Field(foreign_key="problems.id", primary_key=True)
    category_id: UUID = Field(foreign_key="categories.id", primary_key=True)

class ProblemTagLink(SQLModel, table=True):
    __tablename__ = "problem_tags"
    problem_id: UUID = Field(foreign_key="problems.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)

class Problem(SQLModel, table=True):
    __tablename__ = "problems"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    description: str
    difficulty: str
    config: Optional[dict] = Field(default_factory=dict, sa_column=Column(JSON))
    
    test_cases: List["TestCase"] = Relationship(back_populates="problem", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    categories: List["Category"] = Relationship(link_model=ProblemCategoryLink)
    tags: List["Tag"] = Relationship(link_model=ProblemTagLink)

class Category(SQLModel, table=True):
    __tablename__ = "categories"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)

class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)

class TestCase(SQLModel, table=True):
    __tablename__ = "test_cases"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    problem_id: UUID = Field(foreign_key="problems.id")
    input: str
    output: str
    is_hidden: bool = Field(default=True)
    sort_order: int
    
    problem: "Problem" = Relationship(back_populates="test_cases")
