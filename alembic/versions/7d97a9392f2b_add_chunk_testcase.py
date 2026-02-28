"""Add chunk testcase

Revision ID: 7d97a9392f2b
Revises: 12d232b53016
Create Date: 2026-02-28 06:33:32.364820

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '7d97a9392f2b'
down_revision: Union[str, Sequence[str], None] = '12d232b53016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('chunks', sa.Column('test_case_input', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('chunks', sa.Column('test_case_output', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # Make them not nullable if required, but default=""
    op.execute("UPDATE chunks SET test_case_input = '', test_case_output = ''")
    op.alter_column('chunks', 'test_case_input', nullable=False)
    op.alter_column('chunks', 'test_case_output', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('chunks', 'test_case_output')
    op.drop_column('chunks', 'test_case_input')
