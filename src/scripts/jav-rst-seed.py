import logging
import uuid
import random
import string
from datetime import datetime, timezone
from sqlalchemy import text
from sqlmodel import Session, select
from infrastructure import engine
from models import (
    Category, Tag, Riddle, Question, Choice
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

NAMESPACE = uuid.NAMESPACE_DNS

def get_uuid(name: str) -> uuid.UUID:
    """Generate a deterministic UUID based on a string name."""
    return uuid.uuid5(NAMESPACE, name)

# Data Sets
JAVA_QUESTIONS_DATA = [
    {"title": "Java Memory Management", "text": "Which part of memory is used for objects in Java?", "choices": [("Stack", False), ("Heap", True), ("Register", False), ("Cache", False)]},
    {"title": "JVM Components", "text": "Which component is responsible for converting bytecode into machine code?", "choices": [("Compiler", False), ("Interpreter", False), ("JIT Compiler", True), ("Class Loader", False)]},
    {"title": "String Pool", "text": "Where are string literals stored in Java memory?", "choices": [("Stack", False), ("String Constant Pool", True), ("Heap directly", False), ("Static area", False)]},
    {"title": "Object Equality", "text": "Which method should be overridden when overriding equals() in Java?", "choices": [("toString()", False), ("hashCode()", True), ("clone()", False), ("finalize()", False)]},
    {"title": "Final Variable", "text": "What happens when a variable is declared as final?", "choices": [("Value cannot be changed", True), ("Method cannot be overridden", False), ("Class cannot be inherited", False), ("Memory is freed", False)]},
    {"title": "Abstract Class", "text": "An abstract class can have...", "choices": [("Only abstract methods", False), ("Only concrete methods", False), ("Both abstract and concrete methods", True), ("Neither", False)]},
    {"title": "Interface Methods", "text": "Since Java 8, interfaces can have...", "choices": [("Abstract methods only", False), ("Static methods only", False), ("Default and static methods", True), ("No methods", False)]},
    {"title": "Unchecked Exception", "text": "Which of these is an unchecked exception?", "choices": [("IOException", False), ("NullPointerException", True), ("SQLException", False), ("ClassNotFoundException", False)]},
    {"title": "Static Keyword", "text": "What does the static keyword do to a variable?", "choices": [("Makes it constant", False), ("Shares it among all instances", True), ("Makes it private", False), ("Makes it thread-safe", False)]},
    {"title": "Try-With-Resources", "text": "Try-with-resources was introduced in which Java version?", "choices": [("Java 6", False), ("Java 7", True), ("Java 8", False), ("Java 9", False)]},
    {"title": "Checked Exception", "text": "Which exception must be declared or caught at compile time?", "choices": [("NullPointerException", False), ("ArithmeticException", False), ("Checked Exception", True), ("RuntimeException", False)]},
    {"title": "List vs Set", "text": "Which collection allows duplicate elements?", "choices": [("List", True), ("Set", False), ("Map", False), ("SortedSet", False)]},
    {"title": "Garbage Collector", "text": "Can we force garbage collection in Java?", "choices": [("Yes", False), ("No", True), ("Only in Java 8", False), ("Only with System.gc()", False)]},
    {"title": "Thread Execution", "text": "Which method starts a thread's execution?", "choices": [("run()", False), ("start()", True), ("execute()", False), ("begin()", False)]},
    {"title": "Volatile Keyword", "text": "The volatile keyword ensures...", "choices": [("Mutual exclusion", False), ("Visibility of changes", True), ("Atomicity", False), ("Deadlock prevention", False)]},
    {"title": "Singleton Pattern", "text": "A singleton class has...", "choices": [("Public constructor", False), ("Private constructor", True), ("No constructor", False), ("Protected constructor", False)]},
    {"title": "Primitive Types", "text": "How many primitive data types are in Java?", "choices": [("7", False), ("8", True), ("9", False), ("10", False)]},
    {"title": "Byte Size", "text": "What is the size of a long in Java?", "choices": [("32 bits", False), ("64 bits", True), ("16 bits", False), ("128 bits", False)]},
    {"title": "Casting", "text": "Converting a smaller type to a larger type size is called...", "choices": [("Narrowing", False), ("Widening", True), ("Parsing", False), ("Wrapping", False)]},
    {"title": "Wrapper Classes", "text": "Which class is the wrapper for the 'int' primitive?", "choices": [("Int", False), ("Integer", True), ("Int32", False), ("Number", False)]},
    {"title": "Marker Interface", "text": "Which of these is a marker interface?", "choices": [("Runnable", False), ("Serializable", True), ("Comparable", False), ("List", False)]},
    {"title": "Inheritance", "text": "Java supports which type of inheritance via classes?", "choices": [("Single", True), ("Multiple", False), ("Hybrid", False), ("All", False)]},
    {"title": "Super Keyword", "text": "The super keyword is used to refer to...", "choices": [("Current class members", False), ("Parent class members", True), ("Grandparent class", False), ("Subclass", False)]},
    {"title": "This Keyword", "text": "The this keyword refers to...", "choices": [("Current instance", True), ("Parent instance", False), ("Static variable", False), ("Class name", False)]},
    {"title": "Java Compiler", "text": "Java source code is compiled into...", "choices": [("Machine code", False), ("Bytecode", True), ("Assembly", False), ("Binary", False)]},
    {"title": "File Extension", "text": "Compiled Java files have the extension...", "choices": [(".java", False), (".class", True), (".exe", False), (".obj", False)]},
    {"title": "Constructor", "text": "A class can have how many constructors?", "choices": [("One", False), ("Two", False), ("Zero", False), ("Multiple", True)]},
    {"title": "Method Overloading", "text": "Method overloading depends on change in...", "choices": [("Return type", False), ("Modifiers", False), ("Method signature/parameters", True), ("Exceptions thrown", False)]},
    {"title": "Method Overriding", "text": "Overriding occurs in...", "choices": [("Same class", False), ("Subclass", True), ("Superclass", False), ("Static block", False)]},
    {"title": "Encapsulation", "text": "Encapsulation is achieved by...", "choices": [("Inheritance", False), ("Interfaces", False), ("Private fields and public getters/setters", True), ("Static methods", False)]},
    {"title": "Polymorphism", "text": "Polymorphism which is resolved at runtime is...", "choices": [("Static Binding", False), ("Dynamic Binding", True), ("Compile-time", False), ("Late binding", False)]},
    {"title": "Packages", "text": "Which keyword is used to import a package?", "choices": [("package", False), ("using", False), ("import", True), ("include", False)]},
    {"title": "Main Method", "text": "The main method must be...", "choices": [("Static", True), ("Private", False), ("Protected", False), ("Non-static", False)]},
    {"title": "Lambda Expression", "text": "Lambdas can be used with what type of interfaces?", "choices": [("Marker", False), ("Functional", True), ("Abstract", False), ("Normal", False)]},
    {"title": "Optional Class", "text": "Optional class helps avoid...", "choices": [("OutOfMemoryError", False), ("NullPointerException", True), ("StackOverflowError", False), ("IOException", False)]},
    {"title": "Stream API", "text": "Which stream operation is a terminal operation?", "choices": [("map", False), ("filter", False), ("collect", True), ("sorted", False)]},
    {"title": "HashMap vs ConcurrentHashMap", "text": "Which one is thread-safe?", "choices": [("HashMap", False), ("ConcurrentHashMap", True), ("TreeMap", False), ("IdentityHashMap", False)]},
    {"title": "Serialization", "text": "To prevent a field from being serialized, use...", "choices": [("static", False), ("volatile", False), ("transient", True), ("final", False)]},
    {"title": "Reflection API", "text": "Reflection allows inspecting...", "choices": [("Only public members", False), ("Classes and members at runtime", True), ("Source code", False), ("Comment lines", False)]},
    {"title": "Java Versioning", "text": "LTS stands for...", "choices": [("Long Term Service", False), ("Long Term Support", True), ("List of Thread states", False), ("Local Thread Storage", False)]}
]

JAVA_RIDDLES_DATA = [
    {"text": "I was the sea and the thing you see, I will be your third char", "char": "C", "index": 3},
    {"text": "I am the heart of the bread and the end of the line, I will be your first char", "char": "B", "index": 1},
    {"text": "I am the start of the apple and the end of the sea, I will be your fifth char", "char": "A", "index": 5},
    {"text": "I am the middle of the sun and the start of the sky, I will be your second char", "char": "U", "index": 2},
    {"text": "I am the end of the day and the start of the dawn, I will be your fourth char", "char": "D", "index": 4},
    {"text": "I am the first of the eagle and the last of the tree, I will be your third char", "char": "E", "index": 3},
    {"text": "I am the middle of the fire and the start of the flame, I will be your fifth char", "char": "F", "index": 5},
    {"text": "I am the heart of the gold and the end of the bag, I will be your second char", "char": "O", "index": 2},
    {"text": "I am the start of the mountain and the end of the storm, I will be your fourth char", "char": "M", "index": 4},
    {"text": "I am the first of the light and the last of the ball, I will be your first char", "char": "L", "index": 1},
    {"text": "I am in the middle of 'Java' but not in 'Script', I will be your third char", "char": "V", "index": 3},
    {"text": "I am the start of 'Programming' and the end of 'Keep', I will be your sixth char", "char": "P", "index": 6},
    {"text": "I am the end of 'Spring' and the start of 'Green', I will be your second char", "char": "G", "index": 2},
    {"text": "I am the first of 'Maven' and the last of 'Form', I will be your fourth char", "char": "M", "index": 4},
    {"text": "I am the heart of 'Code' and the end of 'Topic', I will be your fifth char", "char": "O", "index": 5},
    {"text": "I am the start of 'System' and the end of 'Hiss', I will be your first char", "char": "S", "index": 1},
    {"text": "I am the middle of 'Thread' and the start of 'Rain', I will be your third char", "char": "R", "index": 3},
    {"text": "I am the first of 'Object' and the last of 'Echo', I will be your second char", "char": "O", "index": 2},
    {"text": "I am the end of 'Class' and the start of 'Success', I will be your fourth char", "char": "S", "index": 4},
    {"text": "I am the heart of 'Logic' and the end of 'Digital', I will be your fifth char", "char": "G", "index": 5},
    {"text": "I am the start of 'Heap' and the end of 'Bush', I will be your third char", "char": "H", "index": 3},
    {"text": "I am the middle of 'Stack' and the start of 'Table', I will be your second char", "char": "T", "index": 2},
    {"text": "I am the first of 'Queue' and the last of 'Unique', I will be your sixth char", "char": "Q", "index": 6},
    {"text": "I am the end of 'Node' and the start of 'Enter', I will be your fourth char", "char": "E", "index": 4},
    {"text": "I am the heart of 'Link' and the end of 'Hill', I will be your first char", "char": "L", "index": 1},
    {"text": "I am the start of 'Byte' and the end of 'Bob', I will be your fifth char", "char": "B", "index": 5},
    {"text": "I am the middle of 'Short' and the start of 'Ocean', I will be your third char", "char": "O", "index": 3},
    {"text": "I am the first of 'Double' and the last of 'Bed', I will be your second char", "char": "D", "index": 2},
    {"text": "I am the end of 'Float' and the start of 'Thought', I will be your fourth char", "char": "T", "index": 4},
    {"text": "I am the heart of 'Char' and the end of 'March', I will be your fifth char", "char": "A", "index": 5},
    {"text": "I am the start of 'Bool' and the end of 'Club', I will be your sixth char", "char": "B", "index": 6},
    {"text": "I am the middle of 'Enum' and the start of 'Night', I will be your third char", "char": "N", "index": 3},
    {"text": "I am the first of 'Void' and the last of 'Law', I will be your first char", "char": "V", "index": 1},
    {"text": "I am the end of 'Null' and the start of 'Lamp', I will be your second char", "char": "L", "index": 2},
    {"text": "I am the heart of 'Case' and the end of 'Sonic', I will be your fourth char", "char": "C", "index": 4},
    {"text": "I am the start of 'Switch' and the end of 'Gas', I will be your fifth char", "char": "S", "index": 5},
    {"text": "I am the middle of 'While' and the start of 'Idea', I will be your third char", "char": "I", "index": 3},
    {"text": "I am the first of 'For' and the last of 'Shelf', I will be your second char", "char": "F", "index": 2},
    {"text": "I am the end of 'Try' and the start of 'Yellow', I will be your fourth char", "char": "Y", "index": 4},
    {"text": "I am the heart of 'Catch' and the end of 'Music', I will be your sixth char", "char": "C", "index": 6}
]

def seed_jav_restroom():
    if not engine:
        logging.error("No database engine found. Skipping seeding.")
        return

    with Session(engine) as session:
        logging.info("Starting JAV_RESTROOM seeding process...")

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

        # Seed Questions
        logging.info("Seeding 40 Java MCQ questions...")
        for q_data in JAVA_QUESTIONS_DATA:
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

        # Seed Riddles
        logging.info("Seeding 40 Java-related riddles...")
        for i, r_data in enumerate(JAVA_RIDDLES_DATA):
            r_id = get_uuid(f"jav_rst_r_{i}")
            if session.exec(select(Riddle).where(Riddle.id == r_id)).first():
                continue
                
            riddle = Riddle(
                id=r_id,
                riddle_text=r_data["text"],
                refer_char=r_data["char"],
                refer_index=r_data["index"],
                difficulty=random.choice(["Easy", "Medium"]),
                created_at=datetime.now(timezone.utc)
            )
            riddle.tags = [jav_restroom_tag]
            session.add(riddle)

        session.commit()
        logging.info("JAV_RESTROOM seeding completed successfully.")

if __name__ == "__main__":
    seed_jav_restroom()
