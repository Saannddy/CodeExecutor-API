"""Add choice limit trigger

Revision ID: 526810671b5e
Revises: fcbb89d73263
Create Date: 2026-02-15 18:36:27.433973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '526810671b5e'
down_revision: Union[str, Sequence[str], None] = 'fcbb89d73263'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the function
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION limit_choices_per_question() 
        RETURNS TRIGGER AS $$
        BEGIN
            IF (SELECT count(*) FROM choices WHERE question_id = NEW.question_id) >= 4 THEN
                RAISE EXCEPTION 'A question cannot have more than 4 choices';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """))

    # Create the trigger
    op.execute(sa.text("""
        CREATE TRIGGER enforce_choice_limit
        BEFORE INSERT ON choices
        FOR EACH ROW EXECUTE FUNCTION limit_choices_per_question();
    """))


def downgrade() -> None:
    # Drop the trigger
    op.execute(sa.text("DROP TRIGGER IF EXISTS enforce_choice_limit ON choices"))
    
    # Drop the function
    op.execute(sa.text("DROP FUNCTION IF EXISTS limit_choices_per_question()"))
