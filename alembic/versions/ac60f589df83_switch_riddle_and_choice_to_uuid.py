"""Switch riddle and choice to uuid

Revision ID: ac60f589df83
Revises: 784e67f37ed2
Create Date: 2026-02-15 18:20:51.719835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ac60f589df83'
down_revision: Union[str, Sequence[str], None] = '784e67f37ed2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop tables in reverse order of dependencies
    op.drop_table('choices')
    op.drop_table('riddles')
    op.drop_table('questions')

    # Recreate questions
    op.create_table('questions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('tag', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('question_text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate riddles
    op.create_table('riddles',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('riddle_text', sa.String(), nullable=False),
        sa.Column('refer_char', sa.String(length=1), nullable=False),
        sa.Column('refer_index', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('tag', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Recreate choices
    op.create_table('choices',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('question_id', sa.Uuid(), nullable=False),
        sa.Column('choice_text', sa.String(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Reverse the order for downgrade
    op.drop_table('choices')
    op.drop_table('riddles')
    op.drop_table('questions')

    # Recreate with INTEGER IDs (simplified)
    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('tag', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('question_text', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('riddles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('riddle_text', sa.String(), nullable=False),
        sa.Column('refer_char', sa.String(length=1), nullable=False),
        sa.Column('refer_index', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('tag', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('choices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('choice_text', sa.String(), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
