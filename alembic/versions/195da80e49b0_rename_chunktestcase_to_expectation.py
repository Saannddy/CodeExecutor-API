"""Rename ChunkTestCase to Expectation

Revision ID: 195da80e49b0
Revises: bef4f254435d
Create Date: 2026-02-28 06:57:58.901505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '195da80e49b0'
down_revision: Union[str, Sequence[str], None] = 'bef4f254435d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table('chunk_test_cases', 'expectations')

def downgrade() -> None:
    """Downgrade schema."""
    op.rename_table('expectations', 'chunk_test_cases')
