from yoyo import step

__depends__ = {"0001_initial_schema"}

steps = [
    step(
        """
        -- Seed Categories
        INSERT INTO categories (name) VALUES ('Array'), ('String'), ('Math') ON CONFLICT (name) DO NOTHING;

        -- Seed Tags
        INSERT INTO tags (name) VALUES ('Easy'), ('LeetCode'), ('Classic') ON CONFLICT (name) DO NOTHING;

        -- Seed Problem: Two Sum
        INSERT INTO problems (id, title, description, difficulty, config)
        VALUES (
            'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
            'Two Sum',
            'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
            'easy',
            '{"timeout": 5, "templates": {"python": "def twoSum(nums, target):\\n    pass"}}'
        ) ON CONFLICT (id) DO NOTHING;

        -- Seed Test Cases for Two Sum
        INSERT INTO test_cases (problem_id, input, output, is_hidden, sort_order)
        VALUES 
        ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '[2,7,11,15]\\n9', '[0,1]', false, 1),
        ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '[3,2,4]\\n6', '[1,2]', false, 2),
        ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', '[3,3]\\n6', '[0,1]', true, 3)
        ON CONFLICT (id) DO NOTHING;

        -- Link Problem to Category and Tag
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', id FROM categories WHERE name = 'Array'
        ON CONFLICT DO NOTHING;

        INSERT INTO problem_tags (problem_id, tag_id)
        SELECT 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', id FROM tags WHERE name = 'Easy'
        ON CONFLICT DO NOTHING;
        """,
        """
        DELETE FROM problem_tags WHERE problem_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
        DELETE FROM problem_categories WHERE problem_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
        DELETE FROM test_cases WHERE problem_id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
        DELETE FROM problems WHERE id = 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11';
        """
    )
]
