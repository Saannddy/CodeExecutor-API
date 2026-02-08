from yoyo import step

__depends__ = {"0004_more_problems_seed"}

def apply_step(conn):
    cursor = conn.cursor()

    # 1. Categories Migration
    # Add new UUID column
    cursor.execute("ALTER TABLE categories ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()")
    
    # Update problem_categories to use a temporary UUID column
    cursor.execute("ALTER TABLE problem_categories ADD COLUMN category_uuid UUID")
    cursor.execute("""
        UPDATE problem_categories pc
        SET category_uuid = c.uuid_id
        FROM categories c
        WHERE pc.category_id = c.id
    """)
    
    # Drop old constraints and columns for categories
    cursor.execute("ALTER TABLE problem_categories DROP CONSTRAINT problem_categories_category_id_fkey")
    cursor.execute("ALTER TABLE problem_categories DROP COLUMN category_id")
    cursor.execute("ALTER TABLE categories DROP CONSTRAINT categories_pkey CASCADE")
    cursor.execute("ALTER TABLE categories DROP COLUMN id")
    
    # Make uuid_id the new primary key and rename it
    cursor.execute("ALTER TABLE categories ADD PRIMARY KEY (uuid_id)")
    cursor.execute("ALTER TABLE categories RENAME COLUMN uuid_id TO id")
    
    # finalize problem_categories
    cursor.execute("ALTER TABLE problem_categories RENAME COLUMN category_uuid TO category_id")
    cursor.execute("ALTER TABLE problem_categories ADD CONSTRAINT problem_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE")
    cursor.execute("ALTER TABLE problem_categories ADD PRIMARY KEY (problem_id, category_id)")

    # 2. Tags Migration
    # Add new UUID column
    cursor.execute("ALTER TABLE tags ADD COLUMN uuid_id UUID DEFAULT gen_random_uuid()")
    
    # Update problem_tags to use a temporary UUID column
    cursor.execute("ALTER TABLE problem_tags ADD COLUMN tag_uuid UUID")
    cursor.execute("""
        UPDATE problem_tags pt
        SET tag_uuid = t.uuid_id
        FROM tags t
        WHERE pt.tag_id = t.id
    """)
    
    # Drop old constraints and columns for tags
    cursor.execute("ALTER TABLE problem_tags DROP CONSTRAINT problem_tags_tag_id_fkey")
    cursor.execute("ALTER TABLE problem_tags DROP COLUMN tag_id")
    cursor.execute("ALTER TABLE tags DROP CONSTRAINT tags_pkey CASCADE")
    cursor.execute("ALTER TABLE tags DROP COLUMN id")
    
    # Make uuid_id the new primary key and rename it
    cursor.execute("ALTER TABLE tags ADD PRIMARY KEY (uuid_id)")
    cursor.execute("ALTER TABLE tags RENAME COLUMN uuid_id TO id")
    
    # finalize problem_tags
    cursor.execute("ALTER TABLE problem_tags RENAME COLUMN tag_uuid TO tag_id")
    cursor.execute("ALTER TABLE problem_tags ADD CONSTRAINT problem_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE")
    cursor.execute("ALTER TABLE problem_tags ADD PRIMARY KEY (problem_id, tag_id)")

steps = [
    step(apply_step)
]
