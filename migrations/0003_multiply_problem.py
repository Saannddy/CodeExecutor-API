from yoyo import step

__depends__ = {"0002_seed_data"}

steps = [
    step(
        """
        -- Seed Problem: Multiply Two Numbers
        INSERT INTO problems (id, title, description, difficulty, config)
        VALUES (
            'b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d',
            'Multiply Two Numbers',
            'Given two integers separated by a space, return their product.',
            'easy',
            '{"timeout": 2, "templates": {"python": "num1, num2 = map(int, input().split())\\nprint(num1 * num2)"}}'
        ) ON CONFLICT (id) DO NOTHING;

        -- Seed Test Cases for Multiply
        INSERT INTO test_cases (problem_id, input, output, is_hidden, sort_order)
        VALUES 
        ('b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d', '2 3', '6', false, 1),
        ('b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d', '-4 5', '-20', false, 2),
        ('b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d', '10 10', '100', true, 3)
        ON CONFLICT (id) DO NOTHING;

        -- Link Problem to Category 'Math'
        INSERT INTO problem_categories (problem_id, category_id)
        SELECT 'b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d', id FROM categories WHERE name = 'Math'
        ON CONFLICT DO NOTHING;
        """,
        """
        DELETE FROM problem_categories WHERE problem_id = 'b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d';
        DELETE FROM test_cases WHERE problem_id = 'b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d';
        DELETE FROM problems WHERE id = 'b1f2e3d4-c5b6-4a7b-8c9d-0e1f2a3b4c5d';
        """
    )
]
