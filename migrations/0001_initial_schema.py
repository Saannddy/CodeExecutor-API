from yoyo import step

__depends__ = {}

steps = [
    step(
        """
        CREATE EXTENSION IF NOT EXISTS "pgcrypto";

        -- Problems Table
        CREATE TABLE IF NOT EXISTS problems (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            difficulty VARCHAR(20), -- easy, medium, hard
            config JSONB, -- Stores timeout, templates, and rules
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Test Cases Table
        CREATE TABLE IF NOT EXISTS test_cases (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
            input TEXT,
            output TEXT,
            is_hidden BOOLEAN DEFAULT TRUE,
            sort_order INT
        );

        -- Categories Table
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );

        -- Tags Table
        CREATE TABLE IF NOT EXISTS tags (
            id SERIAL PRIMARY KEY,
            name VARCHAR UNIQUE NOT NULL
        );

        -- Join Table: Many-to-Many for Categories
        CREATE TABLE IF NOT EXISTS problem_categories (
            problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
            category_id INT REFERENCES categories(id) ON DELETE CASCADE,
            PRIMARY KEY (problem_id, category_id)
        );

        -- Join Table: Many-to-Many for Tags
        CREATE TABLE IF NOT EXISTS problem_tags (
            problem_id UUID REFERENCES problems(id) ON DELETE CASCADE,
            tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (problem_id, tag_id)
        );
        """,
        "DROP TABLE IF EXISTS problem_tags; DROP TABLE IF EXISTS problem_categories; DROP TABLE IF EXISTS tags; DROP TABLE IF EXISTS categories; DROP TABLE IF EXISTS test_cases; DROP TABLE IF EXISTS problems;"
    )
]
