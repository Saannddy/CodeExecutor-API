"""Redesign chunks for multi-language support

Revision ID: 922b6da97d7e
Revises: 195da80e49b0
Create Date: 2026-02-28 07:21:08.426698

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '922b6da97d7e'
down_revision: Union[str, Sequence[str], None] = '195da80e49b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Update chunk_templates
    op.add_column('chunk_templates', sa.Column('chunk_id', sa.UUID(), nullable=True))
    op.add_column('chunk_templates', sa.Column('language', sa.String(), nullable=True))
    op.create_foreign_key('fk_chunk_templates_chunk_id', 'chunk_templates', 'chunks', ['chunk_id'], ['id'])
    
    # 2. Update chunks
    op.drop_constraint('chunks_template_id_fkey', 'chunks', type_='foreignkey') # Might name differ, usually table_column_fkey
    op.drop_column('chunks', 'template_id')
    
    # 3. Update snippets
    op.add_column('snippets', sa.Column('template_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_snippets_template_id', 'snippets', 'chunk_templates', ['template_id'], ['id'])
    op.drop_constraint('snippets_snippet_id_fkey', 'snippets', type_='foreignkey')
    op.drop_column('snippets', 'snippet_id')

def downgrade() -> None:
    """Downgrade schema."""
    # Reverse snippets
    op.add_column('snippets', sa.Column('snippet_id', sa.UUID(), nullable=True))
    op.create_foreign_key('snippets_snippet_id_fkey', 'snippets', 'chunks', ['snippet_id'], ['id'])
    op.drop_constraint('fk_snippets_template_id', 'snippets', type_='foreignkey')
    op.drop_column('snippets', 'template_id')
    
    # Reverse chunks
    op.add_column('chunks', sa.Column('template_id', sa.UUID(), nullable=True))
    op.create_foreign_key('chunks_template_id_fkey', 'chunks', 'chunk_templates', ['template_id'], ['id'])
    
    # Reverse chunk_templates
    op.drop_constraint('fk_chunk_templates_chunk_id', 'chunk_templates', type_='foreignkey')
    op.drop_column('chunk_templates', 'language')
    op.drop_column('chunk_templates', 'chunk_id')
